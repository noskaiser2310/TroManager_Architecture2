"""
ReAct Agent - Core ReAct loop cho System 2.
"""

from __future__ import annotations
import asyncio
import logging
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool

from .context_builder import ContextBuilder, AgentContext
from .guardrails import Guardrails
from ..user_modeling.services import (
    ProfileService,
    BehaviorTracker,
    ActionTypes,
)
from ..notifications.metrics import System2Metrics

logger = logging.getLogger(__name__)


class ReActState(str, Enum):
    PENDING = "pending"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    COMPLETED = "completed"
    FAILED = "failed"
    LOOP_BREAK = "loop_break"


@dataclass
class ReActRequest:
    query: str
    tenant_id: int
    intent: Optional[str] = None
    tools: list[BaseTool] = field(default_factory=list)
    max_iterations: int = 4
    history_context: str = ""  # Formatted history từ ConversationMemory


@dataclass
class ReActResponse:
    answer: str
    iterations: int
    tool_calls: list[dict]
    state: ReActState
    latency_ms: int
    actions_taken: list[str] = field(default_factory=list)
    tone_used: str = "professional"
    personalization_applied: bool = False
    confidence: float = 1.0
    cost_usd: float = 0.0


class ReActAgent:
    """
    Core ReAct Agent thực hiện suy luận đa bước.
    
    Loop:
    1. Context Injection
    2. Thought → Action → Observation (lặp lại)
    3. Loop Breaker nếu quá max_iterations
    """
    
    def __init__(
        self,
        config: dict,
        llm_client,  # Gemini Pro
        context_builder: ContextBuilder,
        guardrails: Guardrails,
        profile_service: ProfileService,
        behavior_tracker: BehaviorTracker,
    ):
        self.config = config
        self.llm = llm_client
        self.context_builder = context_builder
        self.guardrails = guardrails
        self.profiles = profile_service
        self.behaviors = behavior_tracker
        
        self.max_iterations = config.get("max_iterations", 4)
        self.max_tokens = config.get("max_tokens", 8000)
        self.temperature = config.get("temperature", 0.4)
        # Tool execution timeout (giây). Tools nào chậm hơn sẽ bị cancel.
        # Default 10s — phù hợp với DB query bình thường.
        self.tool_timeout_seconds = float(config.get("tool_timeout_seconds", 10.0))
        # LLM call timeout (giây) cho mỗi iteration. Default 30s.
        # OpenAI client cũng có timeout riêng (config.llm.request_timeout),
        # đây là layer thứ 2 phòng trường hợp LLM API treo.
        self.llm_timeout_seconds = float(config.get("llm_timeout_seconds", 30.0))

        self.metrics = System2Metrics()
        
        # Load system prompt
        with open("config/prompts/system2_prompt.txt", "r", encoding="utf-8") as f:
            self.system_prompt_template = f.read()
    
    async def run(self, request: ReActRequest) -> ReActResponse:
        """
        Thực thi ReAct loop.
        """
        start_time = time.time()
        self.metrics.total_requests += 1
        
        actions_taken = []
        tool_calls_log = []
        
        try:
            # 1. Build context
            context = await self.context_builder.build(
                tenant_id=request.tenant_id,
                query=request.query,
            )
            
            # 2. Build system prompt
            system_prompt = self._build_system_prompt(context, request)
            
            # 3. Initialize conversation
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=request.query),
            ]
            
            # 4. ReAct loop
            iterations = 0
            for iteration in range(self.max_iterations):
                iterations = iteration + 1
                
                # Token limit check
                messages = self.guardrails.check_token_limit(
                    messages, self.max_tokens
                )
                
                # Chỉ pass tools ở iteration 1 để tránh lỗi thought_signature của Gemini API
                tools_for_this_iteration = request.tools if iteration == 0 else None
                
                # a. LLM reasoning (wrap in timeout để tránh hang khi API treo)
                try:
                    response = await asyncio.wait_for(
                        self.llm.ainvoke(messages, tools=tools_for_this_iteration),
                        timeout=self.llm_timeout_seconds,
                    )
                except asyncio.TimeoutError:
                    logger.warning(
                        f"[tenant {request.tenant_id}] LLM call timeout "
                        f"({self.llm_timeout_seconds}s) at iteration {iterations}"
                    )
                    self.metrics.llm_timeouts += 1
                    # Trả về fallback message thay vì break
                    return await self._handle_llm_timeout(
                        request, context, iterations, start_time, tool_calls_log, actions_taken
                    )
                except Exception as e:
                    logger.exception(
                        f"[tenant {request.tenant_id}] LLM call error "
                        f"at iteration {iterations}: {e}"
                    )
                    self.metrics.llm_failures += 1
                    return await self._handle_llm_timeout(
                        request, context, iterations, start_time, tool_calls_log, actions_taken
                    )
                messages.append(response)
                
                # b. Check if final answer
                if not response.tool_calls:
                    answer = response.content
                    try:
                        await self._log_response(request, context, answer, iterations, tool_calls_log)
                    except Exception as e:
                        logger.warning(f"Failed to log response: {e}")
                    latency = int((time.time() - start_time) * 1000)
                    self._update_metrics(iterations, latency, len(tool_calls_log))
                    
                    return ReActResponse(
                        answer=answer,
                        iterations=iterations,
                        tool_calls=tool_calls_log,
                        state=ReActState.COMPLETED,
                        latency_ms=latency,
                        actions_taken=actions_taken,
                        tone_used=context.profile.tone_preference if context.profile else "professional",
                        personalization_applied=context.has_personalization(),
                    )
                
                # c. Execute tools
                for tool_call in response.tool_calls:
                    # Normalize: LangChain returns tool_calls as dicts,
                    # but tests/mocks may pass objects. Support both.
                    tc = self._normalize_tool_call(tool_call)
                    try:
                        # Validate input
                        is_valid, error = self.guardrails.validate_tool_input(tc)
                        if not is_valid:
                            observation = ToolMessage(
                                content=f"Invalid input: {error}",
                                tool_call_id=tc.get("id", ""),
                                name=tc.get("name", ""),
                            )
                            self.metrics.tool_failures += 1
                        else:
                            # Check sensitive
                            if self.guardrails.is_sensitive_tool(tc.get("name", "")):
                                tc = await self.guardrails.request_approval(
                                    tc, request.tenant_id
                                )
                                if tc.get("requires_approval"):
                                    observation = ToolMessage(
                                        content=tc.get("approval_message", "Đang chờ duyệt"),
                                        tool_call_id=tc.get("id", ""),
                                        name=tc.get("name", ""),
                                    )
                                else:
                                    result = await self._execute_tool(tc, request.tools)
                                    observation = ToolMessage(
                                        content=str(result),
                                        tool_call_id=tc.get("id", ""),
                                        name=tc.get("name", ""),
                                    )
                                    actions_taken.append(tc.get("name", ""))
                            else:
                                # Execute normal tool
                                result = await self._execute_tool(tc, request.tools)
                                observation = ToolMessage(
                                    content=str(result),
                                    tool_call_id=tc.get("id", ""),
                                    name=tc.get("name", ""),
                                )
                                actions_taken.append(tc.get("name", ""))

                            self.metrics.tool_calls_total += 1
                            tool_calls_log.append({
                                "name": tc.get("name", ""),
                                "args": tc.get("args", {}),
                                "iteration": iterations,
                            })

                    except Exception as e:
                        # Phân biệt timeout error vs lỗi khác để log/message rõ ràng
                        if isinstance(e, asyncio.TimeoutError):
                            err_msg = (
                                f"Tool '{tc.get('name', '?')}' exceeded timeout "
                                f"({self.tool_timeout_seconds}s)"
                            )
                            logger.warning(
                                f"[tenant {request.tenant_id}] {err_msg}"
                            )
                            # Track riêng timeout metric
                            self.metrics.tool_timeouts += 1
                        else:
                            err_msg = f"Tool error: {str(e)}"
                            logger.exception(
                                f"[tenant {request.tenant_id}] Tool "
                                f"'{tc.get('name', '?')}' error: {e}"
                            )

                        observation = ToolMessage(
                            content=err_msg,
                            tool_call_id=tc.get("id", ""),
                            name=tc.get("name", ""),
                        )
                        self.metrics.tool_failures += 1

                    messages.append(observation)
            
            # 5. Loop breaker - max iterations hit
            logger.warning(
                f"ReAct loop exceeded max iterations ({self.max_iterations}) "
                f"for tenant {request.tenant_id}"
            )
            self.metrics.max_iterations_hit += 1
            
            fallback = self.guardrails.get_fallback_message()
            
            # Log behavior
            await self.behaviors.log(
                tenant_id=request.tenant_id,
                action_type=ActionTypes.AI_RESPONSE,
                description=f"ReAct loop break: {iterations} iterations",
            )
            
            latency = int((time.time() - start_time) * 1000)
            return ReActResponse(
                answer=fallback,
                iterations=iterations,
                tool_calls=tool_calls_log,
                state=ReActState.LOOP_BREAK,
                latency_ms=latency,
                actions_taken=actions_taken,
            )
        
        except Exception as e:
            logger.exception(f"ReAct agent error: {e}")
            latency = int((time.time() - start_time) * 1000)
            return ReActResponse(
                answer="Hệ thống đang gặp sự cố, vui lòng thử lại sau.",
                iterations=0,
                tool_calls=tool_calls_log,
                state=ReActState.FAILED,
                latency_ms=latency,
                actions_taken=actions_taken,
            )

    async def _handle_llm_timeout(
        self,
        request: ReActRequest,
        context: AgentContext,
        iterations: int,
        start_time: float,
        tool_calls_log: list,
        actions_taken: Optional[list] = None,
    ) -> ReActResponse:
        """
        Xử lý khi LLM call timeout. Trả về fallback message
        nhưng log + track metric để debug.
        """
        fallback = self.guardrails.get_fallback_message()
        await self.behaviors.log(
            tenant_id=request.tenant_id,
            action_type=ActionTypes.AI_RESPONSE,
            description=f"LLM timeout at iteration {iterations}",
        )
        latency = int((time.time() - start_time) * 1000)
        return ReActResponse(
            answer=fallback,
            iterations=iterations,
            tool_calls=tool_calls_log,
            state=ReActState.FAILED,
            latency_ms=latency,
            actions_taken=actions_taken or [],
            tone_used=context.profile.tone_preference if context.profile else "professional",
            personalization_applied=False,
            confidence=0.0,
        )

    async def _execute_tool(self, tool_call, tools: list[BaseTool]):
        """
        Execute một tool call với timeout protection.

        Raises:
            ValueError: Nếu tool không tồn tại.
            asyncio.TimeoutError: Nếu tool chạy quá tool_timeout_seconds.
        """
        # Normalize: dict hoặc object đều OK
        tc = self._normalize_tool_call(tool_call)
        tool_name = tc.get("name", "")
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")

        # Wrap trong asyncio.wait_for để tránh tool treo vô hạn
        # (vd: DB query bị stuck do connection pool exhausted)
        return await asyncio.wait_for(
            tool.ainvoke(tc.get("args", {})),
            timeout=self.tool_timeout_seconds,
        )

    @staticmethod
    def _normalize_tool_call(tool_call) -> dict:
        """
        Normalize tool_call thành dict, hỗ trợ cả 2 dạng:
        - LangChain mới: tool_call là dict (ToolCall kế thừa dict)
        - Tests/mocks: tool_call là object có .name/.id/.args

        Returns:
            dict với keys: id, name, args
        """
        if isinstance(tool_call, dict):
            return tool_call
        # Object access fallback
        return {
            "id": getattr(tool_call, "id", ""),
            "name": getattr(tool_call, "name", ""),
            "args": getattr(tool_call, "args", {}),
        }
    
    def _build_system_prompt(self, context: AgentContext, request: ReActRequest) -> str:
        """Build system prompt với context injection."""
        from ..tools.tool_registry import get_default_registry
        registry = get_default_registry()
        tool_descriptions = registry.describe_tools(request.tools) if request.tools else "Không có công cụ nào"

        memories_text = "\n".join([f"- {m['memory_text']}" for m in context.memories]) if context.memories else "Chưa có ký ức"
        from datetime import date
        current_date = date.today().strftime("%d/%m/%Y")

        return self.system_prompt_template.format(
            tenant_name=context.profile.full_name if context.profile else "khách",
            tenant_id=request.tenant_id,
            tone=context.profile.tone_preference if context.profile else "professional",
            lease_end=context.profile.lease_end.isoformat() if context.profile and context.profile.lease_end else "Chưa có",
            payment_delay_days=int(context.behavior.avg_payment_delay_days) if context.behavior else 0,
            memories=memories_text,
            behavior_summary=context.behavior_summary_text(),
            tool_descriptions=tool_descriptions,
            query=request.query,
            history_context=request.history_context or "(Không có lịch sử hội thoại trước đó)",
            current_date=current_date,
        )
    
    async def _log_response(
        self,
        request: ReActRequest,
        context: AgentContext,
        answer: str,
        iterations: int,
        tool_calls: list[dict],
    ):
        """Log response to conversation history."""
        # Log to conversation history (implementation in conversation_service)
        logger.info(
            f"ReAct completed: tenant={request.tenant_id}, "
            f"iterations={iterations}, tools={len(tool_calls)}"
        )
        
        # Log behavior
        await self.behaviors.log(
            tenant_id=request.tenant_id,
            action_type=ActionTypes.AI_RESPONSE,
            description=answer[:200],
            metadata={
                "iterations": iterations,
                "tool_count": len(tool_calls),
            },
        )
    
    def _update_metrics(self, iterations: int, latency: int, tool_count: int):
        """Update metrics sau mỗi request."""
        n = self.metrics.total_requests
        self.metrics.avg_iterations = (
            (self.metrics.avg_iterations * (n - 1) + iterations) / n
        )
        self.metrics.avg_latency_ms = (
            (self.metrics.avg_latency_ms * (n - 1) + latency) / n
        )
