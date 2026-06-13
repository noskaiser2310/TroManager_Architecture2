import requests, json, sys

r = requests.post('http://localhost:8000/chat', json={
    'source': 'test',
    'tenant_id': 0, # guest
    'message': 'giá phòng 101'
}, timeout=30)
data = r.json()
text = data.get('answer','')
sys.stdout.reconfigure(encoding='utf-8')
print(f'System: {data.get("system_used")}')
print(f'Tools: {data.get("tools_used")}')
print(f'Actions: {data.get("actions_taken")}')
print(f'Answer:\n{text}')
