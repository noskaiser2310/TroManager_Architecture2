"""Metrics tracking for various components."""

from dataclasses import dataclass, field


@dataclass
class System1Metrics:
    """Metrics cho System 1."""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    rag_responses: int = 0
    fallbacks_to_system2: int = 0
    avg_latency_ms: float = 0.0
    avg_confidence: float = 0.0
    cost_usd: float = 0.0
    
    @property
    def cache_hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests
    
    def to_dict(self) -> dict:
        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hit_rate,
            "rag_responses": self.rag_responses,
            "fallbacks_to_system2": self.fallbacks_to_system2,
            "avg_latency_ms": self.avg_latency_ms,
            "avg_confidence": self.avg_confidence,
            "cost_usd": self.cost_usd,
        }


@dataclass
class System2Metrics:
    """Metrics cho System 2."""
    total_requests: int = 0
    avg_iterations: float = 0.0
    max_iterations_hit: int = 0
    tool_calls_total: int = 0
    tool_failures: int = 0
    tool_timeouts: int = 0
    llm_timeouts: int = 0
    llm_failures: int = 0
    sensitive_actions_approved: int = 0
    avg_latency_ms: float = 0.0
    avg_tokens_used: int = 0
    cost_usd: float = 0.0
    background_events_handled: int = 0

    def to_dict(self) -> dict:
        return {
            "total_requests": self.total_requests,
            "avg_iterations": self.avg_iterations,
            "max_iterations_hit": self.max_iterations_hit,
            "tool_calls_total": self.tool_calls_total,
            "tool_failures": self.tool_failures,
            "tool_timeouts": self.tool_timeouts,
            "llm_timeouts": self.llm_timeouts,
            "llm_failures": self.llm_failures,
            "sensitive_actions_approved": self.sensitive_actions_approved,
            "avg_latency_ms": self.avg_latency_ms,
            "avg_tokens_used": self.avg_tokens_used,
            "cost_usd": self.cost_usd,
            "background_events_handled": self.background_events_handled,
        }


@dataclass
class ProactiveMetrics:
    """Metrics cho proactive events."""
    events_dispatched_today: int = 0
    events_by_type: dict = field(default_factory=dict)
    success_rate: float = 0.0
    opt_out_rate: float = 0.0
    cost_per_event: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "events_dispatched_today": self.events_dispatched_today,
            "events_by_type": self.events_by_type,
            "success_rate": self.success_rate,
            "opt_out_rate": self.opt_out_rate,
            "cost_per_event": self.cost_per_event,
        }
