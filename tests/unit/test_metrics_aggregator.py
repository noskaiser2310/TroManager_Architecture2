"""Tests cho metrics aggregator (Counter, Gauge, Histogram, Registry)."""
import pytest

from src.core.metrics_aggregator import (
    Counter,
    Gauge,
    Histogram,
    MetricsRegistry,
    render_prometheus,
    render_json,
    reset_metrics,
    get_registry,
    metrics_counter,
)


@pytest.fixture(autouse=True)
def reset_after_test():
    """Reset global metrics after mỗi test."""
    yield
    reset_metrics()


# ============ Counter tests ============

class TestCounter:
    def test_basic_increment(self):
        c = Counter("test_counter", "Test help")
        c.inc()
        c.inc()
        c.inc(5)
        assert c.value() == 7

    def test_with_labels(self):
        c = Counter("requests", labels=["method", "status"])
        c.inc(method="GET", status="200")
        c.inc(method="GET", status="200")
        c.inc(method="POST", status="201")
        assert c.value(method="GET", status="200") == 2
        assert c.value(method="POST", status="201") == 1
        assert c.value(method="GET", status="404") == 0

    def test_render_prometheus(self):
        c = Counter("test_total", "Test help")
        c.inc(3)
        output = c.render()
        assert "# HELP test_total Test help" in output
        assert "# TYPE test_total counter" in output
        assert "test_total 3" in output

    def test_render_with_labels(self):
        c = Counter("http_total", labels=["method"])
        c.inc(method="GET")
        c.inc(2, method="POST")
        output = c.render()
        assert 'http_total{method="GET"} 1' in output
        assert 'http_total{method="POST"} 2' in output

    def test_render_empty_counter_has_zero(self):
        """Counter chưa inc() phải render 0 (Prom yêu cầu)."""
        c = Counter("empty_counter")
        output = c.render()
        assert "empty_counter 0" in output

    def test_render_empty_counter_with_labels(self):
        c = Counter("empty", labels=["x"])
        output = c.render()
        assert 'empty{x=""} 0' in output

    def test_thread_safe(self):
        """Multiple threads increment → không mất count."""
        import threading
        c = Counter("thread_test")
        def inc_many():
            for _ in range(1000):
                c.inc()
        threads = [threading.Thread(target=inc_many) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert c.value() == 10000


# ============ Gauge tests ============

class TestGauge:
    def test_set(self):
        g = Gauge("test_gauge")
        g.set(42)
        assert g.value() == 42

    def test_inc_dec(self):
        g = Gauge("test")
        g.set(10)
        g.inc(5)
        assert g.value() == 15
        g.dec(3)
        assert g.value() == 12

    def test_with_labels(self):
        g = Gauge("connections", labels=["pool"])
        g.set(5, pool="main")
        g.set(2, pool="backup")
        assert g.value(pool="main") == 5
        assert g.value(pool="backup") == 2

    def test_render(self):
        g = Gauge("active", "Active connections")
        g.set(7)
        output = g.render()
        assert "# TYPE active gauge" in output
        assert "active 7" in output


# ============ Histogram tests ============

class TestHistogram:
    def test_observe_and_count(self):
        h = Histogram("test", buckets=(1, 5, 10))
        h.observe(0.5)  # <=1
        h.observe(3)    # <=5
        h.observe(7)    # <=10
        h.observe(100)  # +Inf
        # Verify buckets
        output = h.render()
        assert 'test_bucket{le="1"} 1' in output
        assert 'test_bucket{le="5"} 2' in output
        assert 'test_bucket{le="10"} 3' in output
        assert 'test_bucket{le="+Inf"} 4' in output
        assert "test_count 4" in output
        assert "test_sum 110.5" in output

    def test_with_labels(self):
        h = Histogram("latency", labels=["endpoint"], buckets=(10, 100))
        h.observe(5, endpoint="/chat")
        h.observe(50, endpoint="/chat")
        h.observe(200, endpoint="/admin")
        output = h.render()
        assert 'latency_count{endpoint="/chat"} 2' in output
        assert 'latency_count{endpoint="/admin"} 1' in output

    def test_default_buckets(self):
        """Default buckets là latency-friendly."""
        h = Histogram("default")
        for val in [1, 50, 200, 1000, 5000, 50000]:
            h.observe(val)
        # Verify count
        output = h.render()
        assert "default_count 6" in output

    def test_empty_histogram_renders_nothing(self):
        """Histogram chưa observe → không có samples."""
        h = Histogram("empty")
        output = h.render()
        # Empty histogram không có _count, _sum, _bucket
        assert "_count" not in output


# ============ Registry tests ============

class TestRegistry:
    def test_singleton(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_register_and_get(self):
        r = MetricsRegistry()
        c = r.counter("test", "Help", labels=["x"])
        c.inc(x="a")
        assert c is r.counter("test")  # Trả về existing

    def test_render_prometheus_combines_all(self):
        r = MetricsRegistry()
        r.counter("c1").inc()
        r.gauge("g1").set(5)
        r.histogram("h1").observe(10)
        output = r.render_prometheus()
        assert "c1 1" in output
        assert "g1 5" in output
        assert "h1_count 1" in output

    def test_render_json(self):
        r = MetricsRegistry()
        r.counter("c1").inc(3)
        r.gauge("g1").set(7)
        r.histogram("h1").observe(10)
        data = r.render_json()
        assert "counters" in data
        assert "gauges" in data
        assert "histograms" in data
        assert data["counters"]["c1"]["values"]["()"] == 3


# ============ Global helpers tests ============

class TestGlobalHelpers:
    def test_metrics_counter_returns_same_instance(self):
        name = "global_test_counter_x"
        c1 = metrics_counter(name)
        c2 = metrics_counter(name)
        assert c1 is c2

    def test_render_prometheus_uses_global(self):
        metrics_counter("test_aa").inc()
        output = render_prometheus()
        assert "test_aa 1" in output

    def test_reset_clears_all(self):
        metrics_counter("will_reset_global").inc(5)
        reset_metrics()
        output = render_prometheus()
        assert "will_reset_global" not in output
