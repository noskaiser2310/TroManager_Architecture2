import requests, json, sys

tests = [
    'tiền cọc thế nào',
    'giá phòng chung thế nào',
]

for msg in tests:
    r = requests.post('http://localhost:8000/chat', json={
        'source': 'test',
        'tenant_id': 0, # guest
        'message': msg
    }, timeout=30)
    data = r.json()
    sys.stdout.reconfigure(encoding='utf-8')
    print(f'\n=== Query: {msg} ===')
    print(f'System: {data.get("system_used")}')
    print(f'Tools: {data.get("tools_used")}')
    print(f'Actions: {data.get("actions_taken")}')
    print(f'Answer:\n{data.get("answer")}')
