"""
Shared test helper for scenario-based multi-turn conversation tests.
All 20 test files import from here.

Usage:
    from scenario_test_helper import test, chat, BASE, run_scenario

Run all scenarios:
    python -m pytest tests/e2e/scenarios/ -v
"""

import requests
import time
import sys
from datetime import datetime

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0
ALL_RESULTS = []


def test(name, func):
    """Run a single test assertion."""
    global PASS, FAIL
    try:
        func()
        ALL_RESULTS.append((name, "PASS", ""))
        PASS += 1
        print(f"  [PASS] {name}")
    except AssertionError as e:
        ALL_RESULTS.append((name, "FAIL", str(e)))
        FAIL += 1
        print(f"  [FAIL] {name}: {e}")
    except Exception as e:
        ALL_RESULTS.append((name, "ERROR", str(e)))
        FAIL += 1
        print(f"  [ERROR] {name}: {e}")


def chat(msg, tenant_id=None, session_id=None):
    """Send a chat message to the API with rate limiting (6s between calls)."""
    time.sleep(6)
    payload = {"source": "scenario_test", "message": msg}
    if tenant_id is not None:
        payload["tenant_id"] = tenant_id
    if session_id:
        payload["session_id"] = session_id
    r = requests.post(f"{BASE}/chat", json=payload, timeout=120)
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:200]}"
    data = r.json()
    assert "answer" in data, f"No answer field: {data}"
    return data


def run_scenario(scenario_name, test_fn):
    """Run a full scenario group and print results."""
    global PASS, FAIL, ALL_RESULTS
    PASS = 0
    FAIL = 0
    ALL_RESULTS = []

    print(f"\n{'='*60}")
    print(f"  Kịch bản: {scenario_name}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    try:
        test_fn()
    except Exception as e:
        print(f"  [GROUP ERROR] {e}")
        FAIL += 1

    print(f"\n  KẾT QUẢ: {PASS} PASS / {FAIL} FAIL / {PASS+FAIL} TOTAL")

    if FAIL > 0:
        for name, status, reason in ALL_RESULTS:
            if status != "PASS":
                print(f"    - {name}: {reason}")

    return PASS, FAIL
