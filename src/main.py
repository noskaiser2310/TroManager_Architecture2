"""
Main entry point - Khởi tạo FastAPI app và wire tất cả real services.

Đã được cập nhật để:
- Sử dụng LLM client thật (OpenAI-compatible)
- Kết nối PostgreSQL thật
- Load knowledge base thật
- Không có mock data
- Auto-load .env file (nếu có)
"""

from __future__ import annotations
import os
import time
import logging
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    _load_env = lambda: load_dotenv(override=False)
    _load_env()
except ImportError:
    pass

import asyncpg
import hmac
import hashlib
import yaml
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel

# Internal imports
from .gateway import RouterGateway, IncomingRequest, create_default_router
from .system1.fast_layer import FastLayer, System1Request
from .system1.semantic_cache import SemanticCache
from .system2.react_agent import ReActAgent, ReActRequest
from .system2.context_builder import ContextBuilder
from .system2.guardrails import Guardrails
from .user_modeling.services import (
    ProfileService, BehaviorTracker, MemoryManager, ConversationMemory,
    ApprovalService,
)
from .tools.tool_registry import get_default_registry
from .cron.scheduler import CronScheduler
from .cron.event_dispatcher import EventDispatcher
from .llm import get_llm_client, get_embedding_client, load_llm_config, validate_config
from .core import (
    set_db_pool, set_knowledge_lookup,
    set_zalo_client, set_sms_client,
    RateLimiter, RateLimitConfig,
    RequestIDMiddleware,
)
from .core.retry import retry_async
from .system1.knowledge_lookup import build_knowledge_lookup
from .notifications import create_zalo_client_from_config, create_sms_client_from_config
from .core import setup_json_logging

# Setup JSON structured logging (production-friendly)
# Set LOG_FORMAT=plain để dùng format text thường (dev mode)
if os.environ.get("LOG_FORMAT", "json") == "json":
    setup_json_logging(level=os.environ.get("LOG_LEVEL", "INFO"))
else:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
logger = logging.getLogger(__name__)


# ============ Config loading ============

def load_config(config_path: str) -> dict:
    """Load yaml config, support env var substitution."""
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Simple env var substitution: ${VAR}
    import re
    pattern = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")
    def replacer(m):
        return os.environ.get(m.group(1), m.group(0))
    content = pattern.sub(replacer, content)
    return yaml.safe_load(content)


# Load app config early for CORS setup (before app creation)
try:
    _APP_CONFIG = load_config("config/config.yaml")
except FileNotFoundError:
    logger.warning("config/config.yaml not found at module load; CORS will use defaults")
    _APP_CONFIG = {}


# ============ App Container ============

class AppContainer:
    """Container chứa tất cả dependencies."""

    def __init__(self):
        self.db_pool: Optional[asyncpg.Pool] = None

        # Services
        self.profile_service: Optional[ProfileService] = None
        self.behavior_tracker: Optional[BehaviorTracker] = None
        self.memory_manager: Optional[MemoryManager] = None

        # Agents
        self.router: Optional[RouterGateway] = None
        self.fast_layer: Optional[FastLayer] = None
        self.react_agent: Optional[ReActAgent] = None
        self.context_builder: Optional[ContextBuilder] = None
        self.guardrails: Optional[Guardrails] = None
        self.semantic_cache: Optional[SemanticCache] = None

        # Tools
        self.tool_registry = get_default_registry()

        # User modeling (instantiated in lifespan)
        self.profile_service = None
        self.behavior_tracker = None
        self.memory_manager = None
        self.conversation_memory = None
        self.approval_service = None

        # Cron
        self.cron_scheduler: Optional[CronScheduler] = None
        self.event_dispatcher: Optional[EventDispatcher] = None

        # Rate limiter
        self.rate_limiter: Optional[RateLimiter] = None


container = AppContainer()


# ============ Lifespan ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize và cleanup resources."""
    logger.info("=" * 60)
    logger.info("Starting TroManager (Architecture #2 - Router-Centric ReAct)")
    logger.info("=" * 60)
    
    # 1. Load main config
    try:
        config = load_config("config/config.yaml")
    except FileNotFoundError:
        logger.error("config/config.yaml not found!")
        raise
    
    # 2. Load & validate LLM config
    try:
        llm_config = load_llm_config()
        issues = validate_config(llm_config)
        if issues:
            logger.warning("LLM config issues:")
            for issue in issues:
                logger.warning(f"  - {issue}")
    except FileNotFoundError as e:
        logger.error(f"LLM config not found: {e}")
        logger.error("Create file config/llm_config.local.yaml dựa trên llm_config.local.yaml.example")
        raise
    
    # 3. Initialize database pool (with retry on transient startup failures)
    db_cfg = config.get("database", {})
    db_retry_cfg = config.get("database", {}).get("retry", {}) or {}
    max_attempts = int(db_retry_cfg.get("max_attempts", 5))
    initial_delay = float(db_retry_cfg.get("initial_delay", 1.0))
    max_delay = float(db_retry_cfg.get("max_delay", 10.0))

    async def _create_pool():
        return await asyncpg.create_pool(
            host=db_cfg.get("host", "localhost"),
            port=db_cfg.get("port", 5432),
            database=db_cfg.get("name", "tromanager"),
            user=db_cfg.get("user", "postgres"),
            password=os.environ.get("DB_PASSWORD", db_cfg.get("password", "")),
            min_size=2,
            max_size=db_cfg.get("pool_size", 10),
        )

    try:
        container.db_pool = await retry_async(
            _create_pool,
            max_attempts=max_attempts,
            initial_delay=initial_delay,
            max_delay=max_delay,
            operation_name="create DB pool",
            exceptions=(Exception,),
        )
        set_db_pool(container.db_pool)
        logger.info("PostgreSQL pool created")
    except Exception as e:
        logger.error(
            f"Failed to connect to DB after {max_attempts} attempts: {e}"
        )
        raise
    
    # 4. Initialize LLM clients
    flash_client = get_llm_client("flash")
    pro_client = get_llm_client("pro")
    embedding_client = get_embedding_client()
    logger.info(f"LLM clients ready: flash={flash_client.model_name}, pro={pro_client.model_name}")
    
    # 5. Initialize User Modeling services
    container.profile_service = ProfileService(container.db_pool)
    container.behavior_tracker = BehaviorTracker(container.db_pool)
    container.memory_manager = MemoryManager(container.db_pool, embedding_client)
    container.conversation_memory = ConversationMemory(container.db_pool)

    # Approval service (zalo_client được set sau khi notification init)
    container.approval_service = ApprovalService(
        db_pool=container.db_pool,
        zalo_client=None,
        behavior_tracker=container.behavior_tracker,
    )
    logger.info("User modeling services initialized (incl. ConversationMemory + ApprovalService)")
    
    # 6. Build knowledge lookup
    knowledge_dir = config.get("knowledge_base", {}).get("dir", "knowledge_base")
    knowledge_lookup = build_knowledge_lookup(
        embedding_client=embedding_client,
        config=config.get("system1", {}),
        knowledge_base_dir=knowledge_dir,
        db_pool=container.db_pool,
    )
    set_knowledge_lookup(knowledge_lookup)
    logger.info(f"Knowledge lookup ready (dir={knowledge_dir})")
    
    # 7. Initialize System 1 (Fast Layer)
    embedding_dim = embedding_client.dimension
    container.semantic_cache = SemanticCache(
        db_pool=container.db_pool,
        embedding_dim=embedding_dim,
    )
    container.fast_layer = FastLayer(
        config=config.get("system1", {}),
        semantic_cache=container.semantic_cache,
        knowledge_lookup=knowledge_lookup,
        profile_service=container.profile_service,
        llm_client=flash_client,
        embedding_model=embedding_client,
    )
    
    # 8. Initialize System 2 (ReAct Agent)
    container.context_builder = ContextBuilder(
        profile_service=container.profile_service,
        behavior_tracker=container.behavior_tracker,
        memory_manager=container.memory_manager,
    )
    container.guardrails = Guardrails(
        approval_service=container.approval_service,
        max_tokens=config.get("system2", {}).get("max_tokens", 8000),
        fallback_config=config.get("system2", {}).get("guardrails", {}).get("fallback", {}),
    )
    container.react_agent = ReActAgent(
        config=config.get("system2", {}),
        llm_client=pro_client,
        context_builder=container.context_builder,
        guardrails=container.guardrails,
        profile_service=container.profile_service,
        behavior_tracker=container.behavior_tracker,
    )
    logger.info("System 1 & 2 ready")
    
    # 9. Initialize Router
    container.router = create_default_router()
    logger.info("Router Gateway ready")
    
    # 10. Initialize Notifications
    try:
        notif_config = load_config("config/notifications.yaml")
        
        if notif_config.get("zalo", {}).get("enabled", False):
            zalo = create_zalo_client_from_config(notif_config["zalo"])
            set_zalo_client(zalo)
            logger.info("Zalo client ready")
        
        if notif_config.get("sms", {}).get("enabled", False):
            sms = create_sms_client_from_config(notif_config["sms"])
            set_sms_client(sms)
            logger.info("SMS client ready")
    except FileNotFoundError:
        logger.warning("config/notifications.yaml not found, notifications disabled")
    except Exception as e:
        logger.warning(f"Notification setup failed: {e}")
    
    # 11. Setup Cron
    container.event_dispatcher = EventDispatcher(
        react_agent=container.react_agent,
        behavior_tracker=container.behavior_tracker,
        tool_registry=container.tool_registry,
    )
    container.cron_scheduler = CronScheduler(
        event_dispatcher=container.event_dispatcher,
        config=config.get("cron", {}),
        db_pool=container.db_pool,
        profile_service=container.profile_service,
        behavior_tracker=container.behavior_tracker,
        memory_manager=container.memory_manager,
        llm_client=get_llm_client("pro"),
        conversation_memory=container.conversation_memory,
    )
    if config.get("cron", {}).get("enabled", True):
        container.cron_scheduler.start()
        logger.info("Cron scheduler started")

    # 12. Initialize Rate Limiter
    rate_cfg_dict = config.get("security", {}).get("rate_limit", {})
    container.rate_limiter = RateLimiter(RateLimitConfig(
        requests_per_minute=rate_cfg_dict.get("requests_per_minute", 60),
        requests_per_hour=rate_cfg_dict.get("requests_per_hour", 1000),
        enabled=rate_cfg_dict.get("enabled", True),
    ))
    logger.info(
        f"Rate limiter ready: {container.rate_limiter.config.requests_per_minute}/min, "
        f"{container.rate_limiter.config.requests_per_hour}/hour"
    )

    logger.info("=" * 60)
    logger.info("TroManager started successfully")
    logger.info("=" * 60)

    # Track in-flight requests cho graceful drain khi shutdown
    app.state.in_flight_requests = 0
    app.state.shutdown_event = asyncio.Event()
    app.state.start_time = time.time()

    yield

    # ============ Graceful shutdown ============
    logger.info("=" * 60)
    logger.info("Shutting down TroManager (graceful)...")

    shutdown_cfg = config.get("app", {}).get("shutdown", {})
    drain_timeout = float(shutdown_cfg.get("drain_timeout_seconds", 30.0))
    cron_timeout = float(shutdown_cfg.get("cron_timeout_seconds", 10.0))
    db_timeout = float(shutdown_cfg.get("db_timeout_seconds", 5.0))

    # 1. Đánh dấu shutdown + chờ in-flight requests drain
    app.state.shutdown_event.set()
    in_flight = app.state.in_flight_requests
    if in_flight > 0:
        logger.info(
            f"Waiting for {in_flight} in-flight request(s) to complete "
            f"(timeout={drain_timeout}s)..."
        )
        drained = await _drain_with_timeout(
            lambda: app.state.in_flight_requests == 0,
            timeout=drain_timeout,
            poll_interval=0.1,
        )
        if not drained:
            logger.warning(
                f"Shutdown timeout: {app.state.in_flight_requests} "
                f"request(s) still in-flight after {drain_timeout}s"
            )
        else:
            logger.info("All in-flight requests drained")
    else:
        logger.info("No in-flight requests")

    # 2. Stop cron scheduler (chờ job hiện tại kết thúc, không nhận job mới)
    if container.cron_scheduler:
        logger.info(f"Stopping cron scheduler (timeout={cron_timeout}s)...")
        try:
            await asyncio.wait_for(
                _stop_cron_async(container.cron_scheduler),
                timeout=cron_timeout,
            )
            logger.info("Cron scheduler stopped")
        except asyncio.TimeoutError:
            logger.warning(
                f"Cron shutdown timeout after {cron_timeout}s, "
                f"forcing shutdown"
            )
        except Exception as e:
            logger.exception(f"Error stopping cron scheduler: {e}")

    # 3. Close DB pool (chờ connections drain)
    if container.db_pool:
        logger.info(f"Closing DB pool (timeout={db_timeout}s)...")
        try:
            await asyncio.wait_for(
                container.db_pool.close(),
                timeout=db_timeout,
            )
            logger.info("DB pool closed")
        except asyncio.TimeoutError:
            logger.warning(
                f"DB pool close timeout after {db_timeout}s"
            )
        except Exception as e:
            logger.exception(f"Error closing DB pool: {e}")

    # 4. Cleanup rate limiter
    if hasattr(container, "rate_limiter") and container.rate_limiter:
        try:
            container.rate_limiter.reset_all()
            logger.info("Rate limiter reset")
        except Exception as e:
            logger.warning(f"Error resetting rate limiter: {e}")

    # 5. LLM clients cleanup (close HTTP connections)
    from .llm.llm_client import _default_flash, _default_pro
    for name, client in [("flash", _default_flash), ("pro", _default_pro)]:
        if client is None:
            continue
        try:
            # AsyncOpenAI has aclose() method
            if hasattr(client, "_client") and hasattr(client._client, "close"):
                await client._client.close()
                logger.debug(f"LLM client '{name}' closed")
        except Exception as e:
            logger.warning(f"Error closing LLM client '{name}': {e}")

    # 6. Zalo/SMS clients cleanup
    for client_name in ("zalo", "sms"):
        client = None
        try:
            if client_name == "zalo":
                from .core import get_zalo_client
                try:
                    client = get_zalo_client()
                except RuntimeError:
                    pass
            else:
                from .core import get_sms_client
                try:
                    client = get_sms_client()
                except RuntimeError:
                    pass
            if client and hasattr(client, "close"):
                close_coro = client.close()
                if asyncio.iscoroutine(close_coro):
                    await close_coro
        except Exception as e:
            logger.warning(f"Error closing {client_name} client: {e}")

    uptime = int(time.time() - app.state.start_time)
    logger.info(f"Shutdown complete (uptime={uptime}s)")
    logger.info("=" * 60)


async def _drain_with_timeout(
    predicate: callable,
    timeout: float,
    poll_interval: float = 0.1,
) -> bool:
    """
    Chờ predicate() trở thành True, hoặc timeout.

    Returns:
        True nếu predicate satisfied trước timeout, False nếu timeout.
    """
    start = asyncio.get_event_loop().time()
    while not predicate():
        elapsed = asyncio.get_event_loop().time() - start
        if elapsed >= timeout:
            return False
        await asyncio.sleep(poll_interval)
    return True


async def _stop_cron_async(scheduler) -> None:
    """
    Stop APScheduler gracefully (chờ job hiện tại kết thúc).
    APScheduler.shutdown() blocking → wrap trong to_thread.
    """
    import functools
    await asyncio.get_event_loop().run_in_executor(
        None, scheduler.shutdown, True  # wait=True: chờ job hiện tại
    )


# ============ CORS middleware ============

def _setup_cors(app_cfg: dict):
    """Setup CORS middleware từ app config."""
    cors_cfg = app_cfg.get("cors", {})
    if not cors_cfg.get("enabled", False):
        logger.info("CORS disabled by config")
        return

    origins = cors_cfg.get("allowed_origins", [])
    if "*" in origins and cors_cfg.get("allow_credentials", False):
        logger.warning(
            "CORS: allow_credentials=true với origin='*' không hợp lệ. "
            "Force allow_credentials=false."
        )
        cors_cfg["allow_credentials"] = False

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=cors_cfg.get("allow_credentials", False),
        allow_methods=cors_cfg.get("allowed_methods", ["*"]),
        allow_headers=cors_cfg.get("allowed_headers", ["*"]),
    )
    logger.info(
        f"CORS enabled: origins={origins[:3]}{'...' if len(origins) > 3 else ''}, "
        f"methods={cors_cfg.get('allowed_methods', ['*'])}"
    )


# ============ FastAPI app ============

app = FastAPI(
    title="TroManager API",
    version="0.2.0",
    description="AI-powered boarding house management system - Architecture #2 (Router-Centric ReAct)",
    lifespan=lifespan,
)

# Setup CORS (uses module-level _APP_CONFIG loaded before app)
_setup_cors(_APP_CONFIG.get("app", {}))

# Setup RequestID middleware - thêm SAU CORS để trở thành outermost wrapper.
# Starlette chạy middleware theo thứ tự add ngược lại: middleware add SAU
# chạy TRƯỚC, thấy request đầu tiên và response cuối cùng. Điều này đảm bảo
# request_id được set trước khi CORS preflight xử lý.
_request_id_cfg = _APP_CONFIG.get("app", {}).get("observability", {}).get("request_id", {})
app.add_middleware(RequestIDMiddleware, config=_request_id_cfg)


# ============ Request/Response models ============

class ChatRequest(BaseModel):
    source: str  # zalo, sms, app, api
    tenant_id: Optional[int] = None
    message: str
    session_id: Optional[str] = None  # Nếu không có, sẽ tạo mới
    metadata: dict = {}


class ChatResponse(BaseModel):
    answer: str
    system_used: str
    confidence: float
    latency_ms: int
    tools_used: list[str] = []
    actions_taken: list[str] = []
    session_id: str = ""  # Echo lại cho client


# ============ Routes ============


async def _check_chat_rate_limit(request: ChatRequest, http_request: Request):
    """Check rate limit cho /chat. Raise 429 nếu vượt."""
    if not container.rate_limiter:
        return
    if request.tenant_id is not None:
        rate_key = f"tenant:{request.tenant_id}"
    else:
        client_ip = (
            http_request.client.host
            if http_request and http_request.client
            else "unknown"
        )
        rate_key = f"ip:{client_ip}:{request.source}"
    allowed, reason = await container.rate_limiter.check(rate_key)
    if not allowed:
        logger.warning(f"Rate limit blocked request: key={rate_key}, reason={reason}")
        raise HTTPException(status_code=429, detail=reason)


async def _process_chat(request: ChatRequest, session_id: str) -> ChatResponse:
    """
    Core chat processing logic (không bao gồm rate limit / session_id setup).
    Được share giữa /chat endpoint và Zalo webhook.
    """
    start = asyncio.get_event_loop().time()

    # History context: lấy N turn gần nhất của tenant (nếu có tenant_id)
    history_context = ""
    if container.conversation_memory and request.tenant_id:
        try:
            history_context = await container.conversation_memory.format_for_context(
                tenant_id=request.tenant_id,
                max_turns=5,
            )
        except Exception as e:
            logger.warning(f"Failed to load history context: {e}")

    incoming = IncomingRequest(
        source=request.source,
        query=request.message,
        tenant_id=request.tenant_id,
        metadata=request.metadata,
    )

    # Route
    decision = container.router.route(incoming)

    # Process
    if decision.target_system.value == "system1":
        sys1_request = System1Request(
            query=request.message,
            tenant_id=request.tenant_id,
            history_context=history_context,
        )
        response = await container.fast_layer.process(sys1_request)

        if response.should_fallback:
            logger.info(f"Falling back to System 2: {response.fallback_reason}")
            sys2_request = ReActRequest(
                query=request.message,
                tenant_id=request.tenant_id or 0,
                tools=container.tool_registry.get_for_intent(decision.intent or "general_chat"),
                history_context=history_context,
            )
            sys2_response = await container.react_agent.run(sys2_request)
            response_answer = sys2_response.answer
            system_used = "system2"
            tools_used = [tc["name"] for tc in sys2_response.tool_calls]
            actions_taken = sys2_response.actions_taken
        else:
            response_answer = response.answer
            system_used = "system1"
            tools_used = []
            actions_taken = []

        confidence = response.confidence
    else:
        sys2_request = ReActRequest(
            query=request.message,
            tenant_id=request.tenant_id or 0,
            tools=container.tool_registry.get_for_intent(decision.intent or "general_chat"),
            history_context=history_context,
        )
        sys2_response = await container.react_agent.run(sys2_request)
        response_answer = sys2_response.answer
        system_used = "system2"
        tools_used = [tc["name"] for tc in sys2_response.tool_calls]
        actions_taken = sys2_response.actions_taken
        confidence = 1.0

    latency = int((asyncio.get_event_loop().time() - start) * 1000)

    # Save turn to conversation history
    if container.conversation_memory and request.tenant_id:
        try:
            await container.conversation_memory.add_turn(
                tenant_id=request.tenant_id,
                user_message=request.message,
                ai_response=response_answer,
                session_id=session_id,
                source=request.source,
                system_used=system_used,
                iterations=len(actions_taken),
                tool_calls=[{"name": t} for t in tools_used],
                latency_ms=latency,
            )
        except Exception as e:
            logger.warning(f"Failed to save conversation turn: {e}")

    return ChatResponse(
        answer=response_answer,
        system_used=system_used,
        confidence=confidence,
        latency_ms=latency,
        tools_used=tools_used,
        actions_taken=actions_taken,
        session_id=session_id,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    """Main chat endpoint."""
    await _check_chat_rate_limit(request, http_request)
    session_id = request.session_id or (
        container.conversation_memory.new_session_id()
        if container.conversation_memory else ""
    )
    try:
        return await _process_chat(request, session_id)
    except Exception as e:
        logger.exception(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "db": container.db_pool is not None,
        "llm": get_llm_client("flash") is not None,
        "rate_limiter": container.rate_limiter is not None,
    }


@app.get("/", response_class=HTMLResponse)
async def ui():
    """Serve test UI."""
    ui_path = Path(__file__).resolve().parent.parent / "test_ui.html"
    if ui_path.exists():
        return HTMLResponse(content=ui_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>UI not found</h1><p>Run from project root</p>", status_code=404)


@app.post("/webhook/zalo")
async def zalo_webhook(
    request: Request,
    x_zalo_signature: Optional[str] = Header(None, alias="X-Zalo-Signature"),
):
    """
    Zalo webhook handler.

    Security: nếu ZALO_WEBHOOK_SECRET được set trong env, verify HMAC-SHA256 signature
    trên raw body. Nếu secret không set, log warning nhưng vẫn accept (dev mode).
    """
    raw_body = await request.body()
    webhook_secret = os.environ.get("ZALO_WEBHOOK_SECRET")

    if webhook_secret:
        if not x_zalo_signature:
            logger.warning("Zalo webhook missing signature header")
            raise HTTPException(status_code=401, detail="Missing signature")
        expected = hmac.new(
            webhook_secret.encode("utf-8"),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, x_zalo_signature or ""):
            logger.warning("Zalo webhook signature mismatch")
            raise HTTPException(status_code=401, detail="Invalid signature")
    else:
        logger.debug("ZALO_WEBHOOK_SECRET not set; skipping signature check (dev mode)")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Rate limit theo sender_id (Zalo user) để chống spam bot
    sender_id = payload.get("sender", {}).get("id", "unknown")
    if container.rate_limiter:
        allowed, reason = await container.rate_limiter.check(f"zalo:{sender_id}")
        if not allowed:
            logger.warning(f"Zalo rate limit blocked: sender={sender_id}")
            raise HTTPException(status_code=429, detail=reason)

    event = payload.get("event_name")

    if event == "user_send_text":
        message = payload.get("message", {}).get("text", "")

        # Find tenant by zalo_id
        tenant_id = None
        if container.profile_service and sender_id:
            profile = await container.profile_service.get_profile_by_zalo_id(sender_id)
            if profile:
                tenant_id = profile.tenant_id

        # Zalo không gửi session_id, dùng sender_id làm session marker
        # (mỗi sender có 1 ongoing session — simple approach)
        chat_req = ChatRequest(
            source="zalo",
            tenant_id=tenant_id,
            message=message,
            session_id=f"zalo-{sender_id}" if sender_id else None,
        )
        # Skip /chat rate limit since webhook already rate-limited
        try:
            return await _process_chat(chat_req, chat_req.session_id or "")
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Zalo webhook chat processing error: {e}")
            raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

    return JSONResponse({"status": "ignored", "event": event})


# ============ Admin endpoints ============

@app.get("/admin/metrics")
async def get_metrics():
    """System metrics (legacy format, xem thêm /metrics)."""
    return {
        "system1": container.fast_layer.metrics.to_dict() if container.fast_layer else {},
        "system2": container.react_agent.metrics.to_dict() if container.react_agent else {},
        "proactive": container.event_dispatcher.metrics.to_dict() if container.event_dispatcher else {},
    }


@app.get("/metrics")
async def prometheus_metrics(format: str = "prometheus"):
    """
    Prometheus-style metrics endpoint.

    Args:
        format: "prometheus" (default, text exposition) | "json"

    Returns:
        - format="prometheus": text/plain với format Prometheus
        - format="json": application/json với tất cả metrics
    """
    from fastapi.responses import PlainTextResponse, JSONResponse
    from .core import render_prometheus, render_json

    if format == "json":
        data = render_json()
        # Thêm legacy metrics
        data["legacy"] = {
            "system1": container.fast_layer.metrics.to_dict() if container.fast_layer else {},
            "system2": container.react_agent.metrics.to_dict() if container.react_agent else {},
            "proactive": container.event_dispatcher.metrics.to_dict() if container.event_dispatcher else {},
        }
        return JSONResponse(content=data)
    else:
        text = render_prometheus()
        return PlainTextResponse(
            content=text,
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )


@app.get("/admin/knowledge/stats")
async def knowledge_stats():
    """Knowledge base statistics."""
    from .core import get_knowledge_lookup
    lookup = get_knowledge_lookup()
    return lookup.get_stats()


@app.post("/admin/knowledge/reload")
async def knowledge_reload():
    """Reload knowledge index."""
    from .core import get_knowledge_lookup
    lookup = get_knowledge_lookup()
    success = await lookup.reload()
    return {"success": success}


# ============ Approval admin endpoints ============

class ApprovalDecisionRequest(BaseModel):
    reviewer_id: Optional[int] = None
    notes: Optional[str] = None


def _approval_to_dict(req) -> dict:
    """Convert ApprovalRequest to JSON-serializable dict."""
    return {
        "approval_id": req.approval_id,
        "tool_name": req.tool_name,
        "tool_args": req.tool_args,
        "tenant_id": req.tenant_id,
        "requested_by": req.requested_by,
        "approver_role": req.approver_role,
        "status": req.status,
        "requested_at": req.requested_at.isoformat() if req.requested_at else None,
        "reviewed_at": req.reviewed_at.isoformat() if req.reviewed_at else None,
        "reviewer_id": req.reviewer_id,
        "notes": req.notes,
    }


@app.get("/admin/approvals")
async def list_approvals(
    status: Optional[str] = None,
    tenant_id: Optional[int] = None,
    limit: int = 50,
):
    """
    List approval requests.

    Query params:
        status: 'pending' | 'approved' | 'rejected' (optional, mặc định = all)
        tenant_id: filter theo tenant (optional)
        limit: số lượng tối đa (default 50, max 200)
    """
    if not container.approval_service:
        raise HTTPException(status_code=503, detail="ApprovalService not initialized")

    if limit > 200:
        limit = 200

    if status == "pending":
        requests = await container.approval_service.list_pending(
            limit=limit, tenant_id=tenant_id,
        )
    else:
        requests = await container.approval_service.list_all(
            status=status, limit=limit,
        )

    return {
        "count": len(requests),
        "approvals": [_approval_to_dict(r) for r in requests],
    }


@app.get("/admin/approvals/{approval_id}")
async def get_approval(approval_id: int):
    """Lấy chi tiết 1 approval request."""
    if not container.approval_service:
        raise HTTPException(status_code=503, detail="ApprovalService not initialized")

    req = await container.approval_service.get(approval_id)
    if not req:
        raise HTTPException(status_code=404, detail=f"Approval {approval_id} not found")
    return _approval_to_dict(req)


@app.post("/admin/approvals/{approval_id}/approve")
async def approve_request(approval_id: int, body: ApprovalDecisionRequest):
    """
    Duyệt approval request.

    Side effect: execute original action (gửi Zalo, log behavior).
    """
    if not container.approval_service:
        raise HTTPException(status_code=503, detail="ApprovalService not initialized")

    success, message = await container.approval_service.approve(
        approval_id=approval_id,
        reviewer_id=body.reviewer_id,
        notes=body.notes,
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"approval_id": approval_id, "status": "approved", "message": message}


@app.post("/admin/approvals/{approval_id}/reject")
async def reject_request(approval_id: int, body: ApprovalDecisionRequest):
    """Từ chối approval request."""
    if not container.approval_service:
        raise HTTPException(status_code=503, detail="ApprovalService not initialized")

    success, message = await container.approval_service.reject(
        approval_id=approval_id,
        reviewer_id=body.reviewer_id,
        notes=body.notes,
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"approval_id": approval_id, "status": "rejected", "message": message}


# ============ Appointments admin endpoints ============

@app.get("/admin/appointments")
async def list_appointments(
    status: Optional[str] = None,
    tenant_id: Optional[int] = None,
    limit: int = 50,
):
    """
    List appointments (lịch hẹn xem phòng).

    Query params:
        status: 'pending' | 'confirmed' | 'cancelled' | 'completed' (optional)
        tenant_id: filter theo tenant (optional)
        limit: số lượng tối đa (default 50, max 200)
    """
    if not container.db_pool:
        raise HTTPException(status_code=503, detail="DB pool not initialized")

    sql = """
    SELECT a.appointment_id, a.tenant_id, t.full_name, t.phone_number,
           a.room_id, r.room_number,
           a.scheduled_at, a.status, a.notes,
           a.created_by, a.created_at, a.updated_at
    FROM appointments a
    JOIN user_profiles t ON a.tenant_id = t.tenant_id
    LEFT JOIN rooms r ON a.room_id = r.room_id
    WHERE 1=1
    """
    params: list = []
    param_idx = 1

    if status:
        sql += f" AND a.status = ${param_idx}"
        params.append(status)
        param_idx += 1
    if tenant_id is not None:
        sql += f" AND a.tenant_id = ${param_idx}"
        params.append(tenant_id)
        param_idx += 1

    sql += f" ORDER BY a.scheduled_at ASC LIMIT ${param_idx}"
    params.append(min(limit, 200))

    async with container.db_pool.acquire() as conn:
        rows = await conn.fetch(sql, *params)

    appointments = []
    for row in rows:
        appointments.append({
            "appointment_id": row["appointment_id"],
            "tenant_id": row["tenant_id"],
            "tenant_name": row["full_name"],
            "tenant_phone": row["phone_number"],
            "room_id": row["room_id"],
            "room_number": row["room_number"],
            "scheduled_at": row["scheduled_at"].isoformat(),
            "status": row["status"],
            "notes": row["notes"],
            "created_by": row["created_by"],
            "created_at": row["created_at"].isoformat(),
            "updated_at": row["updated_at"].isoformat(),
        })
    return {"count": len(appointments), "appointments": appointments}


class AppointmentUpdateRequest(BaseModel):
    status: str  # 'confirmed' | 'cancelled' | 'completed'
    notes: Optional[str] = None


@app.post("/admin/appointments/{appointment_id}/update")
async def update_appointment(appointment_id: int, body: AppointmentUpdateRequest):
    """Update trạng thái appointment."""
    valid_statuses = {"pending", "confirmed", "cancelled", "completed"}
    if body.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}",
        )

    if not container.db_pool:
        raise HTTPException(status_code=503, detail="DB pool not initialized")

    sql = """
    UPDATE appointments
    SET status = $2, notes = COALESCE($3, notes), updated_at = CURRENT_TIMESTAMP
    WHERE appointment_id = $1
    RETURNING appointment_id, status
    """
    async with container.db_pool.acquire() as conn:
        row = await conn.fetchrow(sql, appointment_id, body.status, body.notes)
    if not row:
        raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
    return {"appointment_id": row["appointment_id"], "status": row["status"]}


# ============ Rate limit admin endpoint ============

@app.get("/admin/rate-limit/stats/{key}")
async def rate_limit_stats(key: str):
    """Xem stats rate limit cho 1 key (tenant:id, ip:..., zalo:...)."""
    if not container.rate_limiter:
        raise HTTPException(status_code=503, detail="RateLimiter not initialized")
    return container.rate_limiter.get_stats(key)


@app.post("/admin/rate-limit/reset/{key}")
async def rate_limit_reset(key: str):
    """Reset rate limit bucket cho 1 key."""
    if not container.rate_limiter:
        raise HTTPException(status_code=503, detail="RateLimiter not initialized")
    await container.rate_limiter.reset(key)
    return {"key": key, "status": "reset"}


# ============ Run ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
