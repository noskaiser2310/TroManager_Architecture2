"""
LLM Config Loader - Load và validate config từ yaml.

Hỗ trợ environment variable substitution: ${VAR_NAME}
"""

from __future__ import annotations
import os
import re
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

try:
    from dotenv import load_dotenv
    _DOTENV_AVAILABLE = True
except ImportError:
    _DOTENV_AVAILABLE = False
    def load_dotenv(*args, **kwargs):
        return False

logger = logging.getLogger(__name__)


def _load_env_file(env_path: Optional[str] = None) -> bool:
    """
    Load .env file vào os.environ. Tìm theo thứ tự:
    1. Path được truyền vào
    2. .env ở working directory
    3. .env ở project root (parent của src/)
    Returns True nếu load thành công.
    """
    if not _DOTENV_AVAILABLE:
        logger.debug("python-dotenv not installed, skipping .env loading")
        return False
    
    candidates = []
    if env_path:
        candidates.append(env_path)
    candidates.append(".env")
    
    src_dir = Path(__file__).resolve().parent
    project_root = src_dir.parent
    candidates.append(str(project_root / ".env"))
    
    for candidate in candidates:
        if Path(candidate).exists():
            result = load_dotenv(candidate, override=False)
            if result:
                logger.info(f"Loaded environment from: {candidate}")
                return True
    
    logger.debug("No .env file found")
    return False


# Auto-load .env khi module import
_load_env_file()


@dataclass
class LLMProviderConfig:
    """Config cho một provider (LLM hoặc embedding)."""
    provider: str
    base_url: str
    api_key: str
    model: str
    request_timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit_rpm: int = 60
    rate_limit_tpm: int = 1_000_000
    extra: dict = field(default_factory=dict)


def _substitute_env(value: str) -> str:
    """Replace ${VAR_NAME} với environment variable."""
    if not isinstance(value, str):
        return value
    
    pattern = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")
    
    def replacer(match):
        var_name = match.group(1)
        env_value = os.environ.get(var_name)
        if env_value is None:
            logger.warning(f"Environment variable {var_name} not set")
            return ""
        return env_value
    
    return pattern.sub(replacer, value)


def _deep_substitute(obj):
    """Recursively substitute env vars trong dict/list."""
    if isinstance(obj, dict):
        return {k: _deep_substitute(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_deep_substitute(item) for item in obj]
    elif isinstance(obj, str):
        return _substitute_env(obj)
    else:
        return obj


@dataclass
class LLMConfig:
    """Top-level LLM config."""
    llm: LLMProviderConfig
    embedding: LLMProviderConfig
    
    @property
    def flash_model(self) -> str:
        return self.llm.model
    
    @property
    def pro_model(self) -> str:
        # Nếu extra có pro_model riêng, dùng nó; không thì dùng model chính
        return self.llm.extra.get("pro_model", self.llm.model)

    @property
    def router_model(self) -> str:
        return self.llm.extra.get("router_model", self.llm.model)
    
    @property
    def embedding_model(self) -> str:
        return self.embedding.model
    
    @property
    def embedding_dim(self) -> int:
        return self.embedding.extra.get("dimension", 768)


def load_llm_config(config_path: Optional[str] = None) -> LLMConfig:
    """
    Load LLM config từ yaml file.
    
    Args:
        config_path: Đường dẫn tới config file. Nếu None, sẽ:
            1. Check env LLM_CONFIG_PATH
            2. Fall back to config/llm_config.yaml
            3. Fall back to config/llm_config.local.yaml
    
    Returns:
        LLMConfig object
    """
    if config_path is None:
        config_path = os.environ.get("LLM_CONFIG_PATH")
    
    if config_path is None:
        candidates = [
            "config/llm_config.local.yaml",
            "config/llm_config.yaml",
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                config_path = candidate
                break
    
    if config_path is None or not Path(config_path).exists():
        raise FileNotFoundError(
            f"LLM config not found. Tìm ở:\n"
            f"  - $LLM_CONFIG_PATH env var\n"
            f"  - config/llm_config.local.yaml\n"
            f"  - config/llm_config.yaml\n"
            f"Hãy tạo file llm_config.local.yaml dựa trên llm_config.yaml.example"
        )
    
    logger.info(f"Loading LLM config from: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    
    raw = _deep_substitute(raw)
    
    if "llm" not in raw:
        raise ValueError("Config thiếu section 'llm'")
    if "embedding" not in raw:
        raise ValueError("Config thiếu section 'embedding'")
    
    llm_raw = raw["llm"]
    llm_cfg = LLMProviderConfig(
        provider=llm_raw.get("provider", "openai_compatible"),
        base_url=llm_raw.get("base_url", ""),
        api_key=llm_raw.get("api_key", ""),
        model=llm_raw.get("flash_model") or llm_raw.get("model", ""),
        request_timeout=llm_raw.get("request_timeout", 60),
        max_retries=llm_raw.get("max_retries", 3),
        retry_delay=llm_raw.get("retry_delay", 1.0),
        rate_limit_rpm=llm_raw.get("rate_limit", {}).get("requests_per_minute", 60),
        rate_limit_tpm=llm_raw.get("rate_limit", {}).get("tokens_per_minute", 1_000_000),
        extra={
            "pro_model": llm_raw.get("pro_model"),
            "router_model": llm_raw.get("router_model"),
            "generation": llm_raw.get("advanced", {}).get("generation", {}),
            "safety": llm_raw.get("advanced", {}).get("safety_settings", {}),
        },
    )
    
    emb_raw = raw["embedding"]
    emb_cfg = LLMProviderConfig(
        provider=emb_raw.get("provider", "openai_compatible"),
        base_url=emb_raw.get("base_url", ""),
        api_key=emb_raw.get("api_key", ""),
        model=emb_raw.get("model", "text-embedding-004"),
        request_timeout=emb_raw.get("request_timeout", 30),
        rate_limit_rpm=emb_raw.get("rate_limit", {}).get("requests_per_minute", 300),
        extra={
            "dimension": emb_raw.get("dimension", 768),
            "batch_size": emb_raw.get("batch_size", 32),
            "enable_cache": emb_raw.get("enable_cache", True),
        },
    )

    return LLMConfig(llm=llm_cfg, embedding=emb_cfg)


def validate_config(config: LLMConfig) -> list[str]:
    """
    Validate config và trả về list các warnings/errors.
    Empty list = OK.
    """
    issues = []
    
    if not config.llm.api_key:
        issues.append("LLM api_key chưa được set (đặt GEMINI_API_KEY env var hoặc điền trực tiếp)")
    
    if not config.llm.base_url:
        issues.append("LLM base_url chưa được set")
    
    if not config.llm.model:
        issues.append("LLM model name chưa được set")
    
    if not config.embedding.api_key:
        issues.append("Embedding api_key chưa được set")
    
    if not config.embedding.base_url:
        issues.append("Embedding base_url chưa được set")
    
    if not config.embedding.model:
        issues.append("Embedding model name chưa được set")
    
    return issues
