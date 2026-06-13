import requests, json, sys

tests = [
    {'tenant_id': 1, 'msg': 'tôi muốn gia hạn hợp đồng'},
    {'tenant_id': 0, 'msg': 'tôi muốn gia hạn hợp đồng'},
]

for item in tests:
    tenant_id = item['tenant_id']
    msg = item['msg']
    r = requests.post('http://localhost:8000/chat', json={
        'source': 'test',
        'tenant_id': tenant_id,
        'message': msg
    }, timeout=30)
    data = r.json()
    sys.stdout.reconfigure(encoding='utf-8')
    print(f'\n=== Tenant: {tenant_id} | Query: {msg} ===')
    print(f'System: {data.get("system_used")}')
    print(f'Tools: {data.get("tools_used")}')
    print(f'Actions: {data.get("actions_taken")}')
    print(f'Answer:\n{data.get("answer")}')
