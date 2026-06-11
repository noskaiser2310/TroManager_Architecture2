"""
Metrics aggregator với Prometheus-style output.

Cung cấp:
- Counter: tăng dần (vd: request count, error count)
- Gauge: giá trị hiện tại (vd: active connections, in-flight requests)
- Histogram: phân phối giá trị (vd: latency, token count)

Output format: Prometheus text exposition format (compatible với PromQL)
http://localhost:8000/metrics → scrape được bởi Prometheus/Grafana

Example usage:
    from src.core.metrics_aggregator import (
        metrics_counter, metrics_gauge, metrics_histogram,
    )

    # Tăng counter
    metrics_counter("chat_requests_total", labels={"source": "zalo"}).inc()

    # Set gauge
    metrics_gauge("in_flight_requests").set(5)

    # Observe histogram
    metrics_histogram("request_latency_ms").observe(123)

    # Render to text
    from src.core.metrics_aggregator import render_prometheus
    text = render_prometheus()
"""
from __future__ import annotations

import logging
import threading
from collections import defaultdict
from typing import Optional

logger = logging.getLogger(__name__)


# ============ Metric types ============

class Counter:
    """
    Counter chỉ tăng (Prometheus-style).
    Hỗ trợ labels (key-value pairs).
    """

    def __init__(self, name: str, help_text: str = "", labels: Optional[list[str]] = None):
        self.name = name
        self.help_text = help_text
        self.label_names = labels or []
        # Storage: tuple(labels_values) -> value
        self._values: dict[tuple, float] = defaultdict(float)
        self._lock = threading.Lock()

    def inc(self, amount: float = 1.0, **labels):
        """Tăng counter."""
        label_values = tuple(labels.get(k, "") for k in self.label_names)
        with self._lock:
            self._values[label_values] += amount

    def value(self, **labels) -> float:
        """Đọc giá trị counter."""
        label_values = tuple(labels.get(k, "") for k in self.label_names)
        return self._values.get(label_values, 0.0)

    def render(self) -> str:
        """Render theo Prometheus format."""
        lines = []
        if self.help_text:
            lines.append(f"# HELP {self.name} {self.help_text}")
        if self.label_names:
            label_str = "{" + ",".join(f'{n}=""' for n in self.label_names) + "}"
            lines.append(f"# TYPE {self.name} counter{label_str}")
            lines.append(f"# TYPE {self.name} counter")
        else:
            lines.append(f"# TYPE {self.name} counter")

        with self._lock:
            if not self._values:
                # Counter phải có ít nhất 1 sample (Prom yêu cầu)
                if self.label_names:
                    labels_str = ",".join(f'{n}=""' for n in self.label_names)
                    lines.append(f"{self.name}{{{labels_str}}} 0")
                else:
                    lines.append(f"{self.name} 0")
            else:
                for label_values, val in sorted(self._values.items()):
                    if self.label_names:
                        label_pairs = ",".join(
                            f'{n}="{v}"' for n, v in zip(self.label_names, label_values)
                        )
                        lines.append(f"{self.name}{{{label_pairs}}} {val}")
                    else:
                        lines.append(f"{self.name} {val}")
        return "\n".join(lines)


class Gauge:
    """
    Gauge có thể tăng/giảm/set (Prometheus-style).
    """

    def __init__(self, name: str, help_text: str = "", labels: Optional[list[str]] = None):
        self.name = name
        self.help_text = help_text
        self.label_names = labels or []
        self._values: dict[tuple, float] = defaultdict(float)
        self._lock = threading.Lock()

    def set(self, value: float, **labels):
        """Set giá trị tuyệt đối."""
        label_values = tuple(labels.get(k, "") for k in self.label_names)
        with self._lock:
            self._values[label_values] = float(value)

    def inc(self, amount: float = 1.0, **labels):
        """Tăng gauge."""
        label_values = tuple(labels.get(k, "") for k in self.label_names)
        with self._lock:
            self._values[label_values] += amount

    def dec(self, amount: float = 1.0, **labels):
        """Giảm gauge."""
        self.inc(-amount, **labels)

    def value(self, **labels) -> float:
        """Đọc giá trị gauge."""
        label_values = tuple(labels.get(k, "") for k in self.label_names)
        return self._values.get(label_values, 0.0)

    def render(self) -> str:
        lines = []
        if self.help_text:
            lines.append(f"# HELP {self.name} {self.help_text}")
        lines.append(f"# TYPE {self.name} gauge")

        with self._lock:
            if not self._values:
                if self.label_names:
                    labels_str = ",".join(f'{n}=""' for n in self.label_names)
                    lines.append(f"{self.name}{{{labels_str}}} 0")
                else:
                    lines.append(f"{self.name} 0")
            else:
                for label_values, val in sorted(self._values.items()):
                    if self.label_names:
                        label_pairs = ",".join(
                            f'{n}="{v}"' for n, v in zip(self.label_names, label_values)
                        )
                        lines.append(f"{self.name}{{{label_pairs}}} {val}")
                    else:
                        lines.append(f"{self.name} {val}")
        return "\n".join(lines)


class Histogram:
    """
    Histogram quan sát distribution của values (Prometheus-style).

    Buckets mặc định cho latency_ms: 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000
    """

    DEFAULT_BUCKETS = (5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000)

    def __init__(
        self,
        name: str,
        help_text: str = "",
        buckets: Optional[tuple[float, ...]] = None,
        labels: Optional[list[str]] = None,
    ):
        self.name = name
        self.help_text = help_text
        self.buckets = sorted(buckets or self.DEFAULT_BUCKETS)
        self.label_names = labels or []
        # Storage: tuple(labels_values) -> {bucket_count, total_count, total_sum, bucket_counts}
        self._observations: dict[tuple, dict] = {}
        self._lock = threading.Lock()

    def observe(self, value: float, **labels):
        """Ghi nhận 1 observation."""
        label_values = tuple(labels.get(k, "") for k in self.label_names)
        with self._lock:
            if label_values not in self._observations:
                self._observations[label_values] = {
                    "count": 0,
                    "sum": 0.0,
                    "buckets": {b: 0 for b in self.buckets},
                }
            obs = self._observations[label_values]
            obs["count"] += 1
            obs["sum"] += value
            for b in self.buckets:
                if value <= b:
                    obs["buckets"][b] += 1

    def render(self) -> str:
        lines = []
        if self.help_text:
            lines.append(f"# HELP {self.name} {self.help_text}")
        lines.append(f"# TYPE {self.name} histogram")

        with self._lock:
            for label_values, obs in sorted(self._observations.items()):
                base_labels = dict(zip(self.label_names, label_values))
                for b in self.buckets:
                    labels = {**base_labels, "le": str(b)}
                    label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
                    lines.append(f'{self.name}_bucket{{{label_str}}} {obs["buckets"][b]}')
                # +Inf bucket
                labels = {**base_labels, "le": "+Inf"}
                label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
                lines.append(f'{self.name}_bucket{{{label_str}}} {obs["count"]}')

                if base_labels:
                    label_str = ",".join(f'{k}="{v}"' for k, v in base_labels.items())
                    lines.append(f'{self.name}_count{{{label_str}}} {obs["count"]}')
                    lines.append(f'{self.name}_sum{{{label_str}}} {obs["sum"]:.6f}')
                else:
                    lines.append(f'{self.name}_count {obs["count"]}')
                    lines.append(f'{self.name}_sum {obs["sum"]:.6f}')
        return "\n".join(lines)


# ============ Registry ============

class MetricsRegistry:
    """
    Global registry cho tất cả metrics.

    Thread-safe, có thể được access từ bất kỳ module nào.
    """

    def __init__(self):
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._histograms: dict[str, Histogram] = {}
        self._lock = threading.Lock()

    def counter(self, name: str, help_text: str = "", labels: Optional[list[str]] = None) -> Counter:
        """Get hoặc create counter."""
        with self._lock:
            if name not in self._counters:
                self._counters[name] = Counter(name, help_text, labels)
            return self._counters[name]

    def gauge(self, name: str, help_text: str = "", labels: Optional[list[str]] = None) -> Gauge:
        """Get hoặc create gauge."""
        with self._lock:
            if name not in self._gauges:
                self._gauges[name] = Gauge(name, help_text, labels)
            return self._gauges[name]

    def histogram(
        self,
        name: str,
        help_text: str = "",
        buckets: Optional[tuple[float, ...]] = None,
        labels: Optional[list[str]] = None,
    ) -> Histogram:
        """Get hoặc create histogram."""
        with self._lock:
            if name not in self._histograms:
                self._histograms[name] = Histogram(name, help_text, buckets, labels)
            return self._histograms[name]

    def reset(self):
        """Reset tất cả metrics (cho test)."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()

    def render_prometheus(self) -> str:
        """Render toàn bộ metrics theo Prometheus text format."""
        sections = []
        for counter in self._counters.values():
            sections.append(counter.render())
        for gauge in self._gauges.values():
            sections.append(gauge.render())
        for histogram in self._histograms.values():
            sections.append(histogram.render())
        return "\n\n".join(s for s in sections if s)

    def render_json(self) -> dict:
        """Render toàn bộ metrics dạng JSON (cho /metrics?format=json)."""
        result = {
            "counters": {},
            "gauges": {},
            "histograms": {},
        }
        for name, counter in self._counters.items():
            with counter._lock:
                result["counters"][name] = {
                    "values": {str(k): v for k, v in counter._values.items()}
                }
        for name, gauge in self._gauges.items():
            with gauge._lock:
                result["gauges"][name] = {
                    "values": {str(k): v for k, v in gauge._values.items()}
                }
        for name, histogram in self._histograms.items():
            with histogram._lock:
                result["histograms"][name] = {
                    "count": sum(obs["count"] for obs in histogram._observations.values()),
                    "sum": sum(obs["sum"] for obs in histogram._observations.values()),
                }
        return result


# Global registry
_REGISTRY = MetricsRegistry()


def get_registry() -> MetricsRegistry:
    """Get global metrics registry."""
    return _REGISTRY


def metrics_counter(name: str, help_text: str = "", labels: Optional[list[str]] = None) -> Counter:
    """Shortcut cho global counter."""
    return _REGISTRY.counter(name, help_text, labels)


def metrics_gauge(name: str, help_text: str = "", labels: Optional[list[str]] = None) -> Gauge:
    """Shortcut cho global gauge."""
    return _REGISTRY.gauge(name, help_text, labels)


def metrics_histogram(
    name: str,
    help_text: str = "",
    buckets: Optional[tuple[float, ...]] = None,
    labels: Optional[list[str]] = None,
) -> Histogram:
    """Shortcut cho global histogram."""
    return _REGISTRY.histogram(name, help_text, buckets, labels)


def render_prometheus() -> str:
    """Render global registry to Prometheus text format."""
    return _REGISTRY.render_prometheus()


def render_json() -> dict:
    """Render global registry to JSON."""
    return _REGISTRY.render_json()


def reset_metrics():
    """Reset tất cả metrics (cho test)."""
    _REGISTRY.reset()


# ============ Pre-registered metrics ============

# HTTP request metrics
HTTP_REQUESTS_TOTAL = metrics_counter(
    "http_requests_total",
    "Tổng số HTTP request",
    labels=["method", "path", "status"],
)
HTTP_REQUEST_LATENCY = metrics_histogram(
    "http_request_duration_ms",
    "HTTP request latency (ms)",
    buckets=(5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000),
    labels=["method", "path"],
)
HTTP_REQUESTS_IN_FLIGHT = metrics_gauge(
    "http_requests_in_flight",
    "Số request đang xử lý",
)

# LLM metrics
LLM_CALLS_TOTAL = metrics_counter(
    "llm_calls_total",
    "Tổng số LLM calls",
    labels=["model", "status"],  # status: success/error/timeout
)
LLM_TOKENS_TOTAL = metrics_counter(
    "llm_tokens_total",
    "Tổng số tokens (input + output)",
    labels=["model", "type"],  # type: input/output
)
LLM_LATENCY = metrics_histogram(
    "llm_call_duration_ms",
    "LLM call latency (ms)",
    buckets=(100, 250, 500, 1000, 2000, 5000, 10000, 30000),
    labels=["model"],
)
LLM_COST_USD = metrics_counter(
    "llm_cost_usd_total",
    "Tổng chi phí LLM (USD)",
    labels=["model"],
)

# Tool metrics
TOOL_CALLS_TOTAL = metrics_counter(
    "tool_calls_total",
    "Tổng số tool calls",
    labels=["tool_name", "status"],  # status: success/error/timeout
)
TOOL_LATENCY = metrics_histogram(
    "tool_call_duration_ms",
    "Tool call latency (ms)",
    buckets=(10, 50, 100, 250, 500, 1000, 2500, 5000, 10000),
    labels=["tool_name"],
)

# System 1 / System 2 metrics
SYSTEM1_REQUESTS = metrics_counter(
    "system1_requests_total",
    "System 1 requests",
    labels=["source"],
)
SYSTEM1_CACHE_HITS = metrics_counter(
    "system1_cache_hits_total",
    "System 1 cache hits",
)
SYSTEM2_REQUESTS = metrics_counter(
    "system2_requests_total",
    "System 2 (ReAct) requests",
    labels=["status"],  # completed/failed/max_iterations
)
SYSTEM2_ITERATIONS = metrics_histogram(
    "system2_iterations",
    "ReAct iterations per request",
    buckets=(1, 2, 3, 4, 5, 6, 7, 8),
)

# Cron / Proactive metrics
CRON_JOBS_TOTAL = metrics_counter(
    "cron_jobs_total",
    "Tổng số cron job runs",
    labels=["job_name", "status"],
)
CRON_JOB_DURATION = metrics_histogram(
    "cron_job_duration_ms",
    "Cron job duration (ms)",
    buckets=(100, 500, 1000, 5000, 30000, 60000, 300000),
    labels=["job_name"],
)
PROACTIVE_EVENTS = metrics_counter(
    "proactive_events_total",
    "Proactive events dispatched",
    labels=["event_type", "status"],
)

# Notification metrics
NOTIFICATIONS_SENT = metrics_counter(
    "notifications_sent_total",
    "Notifications sent",
    labels=["channel", "status"],  # channel: zalo/sms, status: success/error
)
