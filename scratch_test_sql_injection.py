import requests, sys

payloads = [
    "'; DROP TABLE behavior_logs; --",
    "'; SELECT * FROM user_profiles; --",
    "1' OR '1'='1",
]

for p in payloads:
    print(f"\n--- Testing SQL injection payload: {p} ---")
    try:
        r = requests.post('http://localhost:8000/chat', json={
            'source': 'test',
            'tenant_id': 1,
            'message': p
        }, timeout=15)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"CRASH / ERROR: {e}")
