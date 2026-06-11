"""
LLM Client - Real implementation using OpenAI-compatible API.

Hỗ trợ:
- Google Gemini (qua OpenAI-compatible endpoint)
- OpenAI
- Bất kỳ provider nào có OpenAI-compatible API
- Tool calling (function calling)
- Streaming
- Auto retry
- Token counting
"""

from __future__ import annotations
import os
import json
import time
import logging
import asyncio
from dataclasses import dataclass, field
from typing import Any, Optional

from openai import AsyncOpenAI, APIError, RateLimitError, APITimeoutError

from .config_loader import LLMConfig, load_llm_config
from .thought_stripper import strip_thought_blocks, has_thought_block, extract_thought_and_answer

logger = logging.getLogger(__name__)


@dataclass
class LLMMessage:
    """Một message trong conversation."""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_calls: Optional[list[dict]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class ToolDefinition:
    """Definition của một tool cho LLM."""
    name: str
    description: str
    parameters: dict  # JSON schema


@dataclass
class LLMResponse:
    """Response từ LLM."""
    content: str
    tool_calls: list[dict] = field(default_factory=list)
    finish_reason: str = "stop"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model: str = ""
    latency_ms: int = 0
    raw: Any = None


class LLMClient:
    """
    Real LLM client với OpenAI-compatible interface.
    
    Sử dụng:
        client = LLMClient()  # Auto-load config
        # Hoặc
        client = LLMClient(config=my_config)
        
        response = await client.generate([
            LLMMessage(role="user", content="Hello"),
        ])
    """
    
    def __init__(self, config: Optional[LLMConfig] = None, model: Optional[str] = None):
        """
        Args:
            config: LLMConfig. Nếu None sẽ auto-load từ file.
            model: Tên model cụ thể (flash hoặc pro). Nếu None sẽ dùng flash.
        """
        if config is None:
            config = load_llm_config()
        self.config = config
        self.model_name = model or config.flash_model

        # Khởi tạo OpenAI client
        if not config.llm.api_key:
            logger.warning(
                "LLM api_key chưa được set. Set GEMINI_API_KEY env var "
                "hoặc tạo file config/llm_config.local.yaml"
            )

        self._client = AsyncOpenAI(
            api_key=config.llm.api_key or "MISSING_API_KEY",
            base_url=config.llm.base_url,
            timeout=config.llm.request_timeout,
            max_retries=config.llm.max_retries,
        )

        # Thought stripping: bật mặc định cho thinking models
        # Có thể tắt qua config: extra.strip_thought = false
        self._strip_thought = config.llm.extra.get("strip_thought", True)

        logger.info(
            f"LLMClient initialized: model={self.model_name}, "
            f"base_url={config.llm.base_url}, "
            f"strip_thought={self._strip_thought}"
        )
    
    def with_model(self, model: str) -> "LLMClient":
        """Tạo client mới với model khác (flash/pro)."""
        return LLMClient(config=self.config, model=model)
    
    def for_flash(self) -> "LLMClient":
        """Client dùng flash model (System 1)."""
        return self.with_model(self.config.flash_model)
    
    def for_pro(self) -> "LLMClient":
        """Client dùng pro model (System 2)."""
        return self.with_model(self.config.pro_model)
    
    async def generate(
        self,
        messages: list[LLMMessage] | list[dict],
        temperature: float = 0.4,
        max_tokens: int = 2048,
        tools: Optional[list[ToolDefinition | dict]] = None,
        tool_choice: str | dict = "auto",
        response_format: Optional[dict] = None,
    ) -> LLMResponse:
        """
        Generate response từ LLM.
        
        Args:
            messages: list các messages (LLMMessage hoặc dict)
            temperature: 0.0 - 1.0
            max_tokens: max tokens in response
            tools: list ToolDefinition hoặc dict (OpenAI tool format)
            tool_choice: "auto", "none", hoặc {"name": "tool_name"}
            response_format: {"type": "json_object"} cho JSON output
        
        Returns:
            LLMResponse
        """
        start = time.time()
        
        # Convert LLMMessage to dict nếu cần
        msg_dicts = [m if isinstance(m, dict) else self._msg_to_dict(m) for m in messages]
        
        # Build request params
        params = {
            "model": self.model_name,
            "messages": msg_dicts,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if tools:
            params["tools"] = [self._tool_to_dict(t) for t in tools]
            params["tool_choice"] = tool_choice
        
        if response_format:
            params["response_format"] = response_format
        
        try:
            response = await self._client.chat.completions.create(**params)
        except RateLimitError as e:
            logger.warning(f"Rate limit hit: {e}")
            # Wait and retry
            await asyncio.sleep(self.config.llm.retry_delay * 2)
            response = await self._client.chat.completions.create(**params)
        except APITimeoutError as e:
            logger.error(f"API timeout: {e}")
            raise
        except APIError as e:
            logger.error(f"API error: {e}")
            raise
        
        latency = int((time.time() - start) * 1000)
        
        # Parse response
        choice = response.choices[0]
        message = choice.message

        tool_calls = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "args": self._parse_tool_args(tc.function.arguments),
                    "type": "function",
                })

        # Strip <thought>...</thought> blocks từ thinking models
        raw_content = message.content or ""
        cleaned_content = strip_thought_blocks(
            raw_content,
            enabled=self._strip_thought,
        )

        return LLMResponse(
            content=cleaned_content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason or "stop",
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
            model=response.model,
            latency_ms=latency,
            raw=response,
        )
    
    async def ainvoke(
        self,
        messages: list,
        tools: Optional[list] = None,
    ) -> Any:
        """
        LangChain-compatible async invoke.
        Returns AIMessage-like object.
        """
        msg_dicts = []
        include_tool_calls_in_history = tools is not None
        for m in messages:
            if hasattr(m, "type"):
                role_map = {
                    "system": "system",
                    "human": "user",
                    "ai": "assistant",
                    "tool": "tool",
                }
                role = role_map.get(m.type, "user")
                d = {
                    "role": role,
                    "content": m.content if hasattr(m, "content") else str(m),
                }
                # Only include tool_calls in history if we're allowing new tool calls this iteration
                if include_tool_calls_in_history and hasattr(m, "tool_calls") and m.tool_calls:
                    raw_tool_calls = m.additional_kwargs.get("raw_tool_calls") if hasattr(m, "additional_kwargs") else None
                    if raw_tool_calls:
                        d["tool_calls"] = raw_tool_calls
                    else:
                        openai_calls = []
                        for tc in m.tool_calls:
                            tc_name = tc.get("name", "") if isinstance(tc, dict) else getattr(tc, "name", "")
                            tc_args = tc.get("args", {}) if isinstance(tc, dict) else getattr(tc, "args", {})
                            tc_id = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", None)
                            if not tc_id:
                                import uuid
                                tc_id = f"call_{uuid.uuid4().hex[:8]}"
                            openai_calls.append({
                                "id": tc_id,
                                "type": "function",
                                "function": {
                                    "name": tc_name,
                                    "arguments": json.dumps(tc_args, ensure_ascii=False),
                                },
                            })
                        d["tool_calls"] = openai_calls
                # When not making new tool calls, convert ToolMessage to UserMessage
                # (Gemini converter can't match tool_call_id without assistant tool_calls present)
                if not include_tool_calls_in_history and role == "tool":
                    d["role"] = "user"
                    if hasattr(m, "name") and m.name is not None:
                        fn_name = m.name
                    else:
                        fn_name = "unknown"
                    d["content"] = f"[Kết quả từ {fn_name}]\n{m.content}"
                else:
                    # Preserve tool_call_id for tool messages
                    if hasattr(m, "tool_call_id") and m.tool_call_id is not None:
                        d["tool_call_id"] = m.tool_call_id if isinstance(m.tool_call_id, str) else str(m.tool_call_id)
                    # Preserve name - CRITICAL for tool messages (function_response.name cannot be empty)
                    if hasattr(m, "name") and m.name is not None:
                        d["name"] = m.name if isinstance(m.name, str) else str(m.name)
                    elif role == "tool":
                        if hasattr(m, "tool_call_id") and m.tool_call_id is not None:
                            d["name"] = str(m.tool_call_id)
                        else:
                            d["name"] = "unknown_function"
                msg_dicts.append(d)
            elif isinstance(m, dict):
                msg_dicts.append(m)
            else:
                msg_dicts.append({"role": "user", "content": str(m)})
        
        response = await self.generate(msg_dicts, tools=tools)
        
        # Return LangChain-compatible object
        from langchain_core.messages import AIMessage
        
        additional_kwargs = {}
        if response.raw and response.raw.choices and response.raw.choices[0].message.tool_calls:
            additional_kwargs["raw_tool_calls"] = [tc.model_dump() for tc in response.raw.choices[0].message.tool_calls]
            
        return AIMessage(
            content=response.content,
            tool_calls=response.tool_calls,
            additional_kwargs=additional_kwargs,
        )
    
    async def stream(self, messages: list[LLMMessage] | list[dict], **kwargs):
        """Stream response từ LLM (async generator)."""
        msg_dicts = [m if isinstance(m, dict) else self._msg_to_dict(m) for m in messages]
        
        stream = await self._client.chat.completions.create(
            model=self.model_name,
            messages=msg_dicts,
            stream=True,
            **kwargs,
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def _msg_to_dict(self, msg: LLMMessage) -> dict:
        """Convert LLMMessage to OpenAI dict format."""
        d = {"role": msg.role, "content": msg.content}
        if msg.tool_calls:
            d["tool_calls"] = msg.tool_calls
        if msg.tool_call_id:
            d["tool_call_id"] = msg.tool_call_id
        if msg.name:
            d["name"] = msg.name
        return d
    
    def _tool_to_dict(self, tool) -> dict:
        """Convert ToolDefinition or LangChain BaseTool to OpenAI tool format."""
        if isinstance(tool, dict):
            return tool
        # LangChain BaseTool detection
        if hasattr(tool, "get_input_schema") and callable(tool.get_input_schema):
            schema = tool.get_input_schema().model_json_schema()
            return {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": schema,
                },
            }
        # ToolDefinition or similar
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters if hasattr(tool, "parameters") else {"type": "object", "properties": {}},
            },
        }
    
    def _parse_tool_args(self, args_str: str) -> dict:
        """Parse tool arguments từ JSON string."""
        import json
        try:
            return json.loads(args_str)
        except (json.JSONDecodeError, TypeError):
            return {}


# ============ Singleton accessors ============

_default_flash: Optional[LLMClient] = None
_default_pro: Optional[LLMClient] = None


def get_llm_client(model: str = "flash") -> LLMClient:
    """
    Get hoặc create singleton LLM client.
    
    Args:
        model: "flash" hoặc "pro"
    """
    global _default_flash, _default_pro
    
    if model == "pro":
        if _default_pro is None:
            config = load_llm_config()
            _default_pro = LLMClient(config=config, model=config.pro_model)
        return _default_pro
    else:
        if _default_flash is None:
            config = load_llm_config()
            _default_flash = LLMClient(config=config, model=config.flash_model)
        return _default_flash


def reset_clients():
    """Reset singletons (dùng cho testing)."""
    global _default_flash, _default_pro
    _default_flash = None
    _default_pro = None
