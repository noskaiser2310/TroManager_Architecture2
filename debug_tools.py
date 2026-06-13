import requests, sys, json

sys.stdout.reconfigure(encoding='utf-8')

# Test: does AI call tools when appropriate?
queries = [
    ("Guest: policy room price", {"source": "test", "message": "Phong 101 gia bao nhieu?"}),
    ("Tenant1: room info", {"source": "test", "tenant_id": 1, "message": "Phong toi the nao?"}),
    ("Guest: deposit", {"source": "test", "message": "Dat coc the nao?"}),
]

for label, payload in queries:
    r = requests.post('http://localhost:8000/chat', json=payload, timeout=30)
    data = r.json()
    print(f'=== {label} ===')
    print(f'  System: {data.get("system_used")}')
    print(f'  Tools: {data.get("tools_used")}')
    ans = data.get("answer","")[:300]
    print(f'  Answer: {ans}')
    print()
