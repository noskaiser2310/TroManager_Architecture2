import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

# Test tools availability for guest
r = requests.post('http://localhost:8000/chat', json={
    'source': 'test',
    'tenant_id': 1,
    'message': 'Tôi muốn xem thông tin phòng của tôi, dùng tool get_room_info nhé'
}, timeout=30)
data = r.json()
print(f'Tools: {data.get("tools_used")}')
print(f'System: {data.get("system_used")}')
print(f'Answer (first 400):')
print(data.get("answer","")[:400])
print()

# Also check tenant2 invoice 
r2 = requests.post('http://localhost:8000/chat', json={
    'source': 'test',
    'tenant_id': 2,
    'message': 'Xem hoa don thang nay cua toi'
}, timeout=30)
data2 = r2.json()
print(f'=== Tenant2 invoice ===')
print(f'Tools: {data2.get("tools_used")}')
print(f'Answer (first 300):')
print(data2.get("answer","")[:300])
