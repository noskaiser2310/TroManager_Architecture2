"""Quick integration smoke test"""
import requests, time

BASE = 'http://localhost:8000'

def chat(msg, tenant_id=1, session=None):
    body = {'source': 'test', 'message': msg}
    if tenant_id is not None:
        body['tenant_id'] = tenant_id
    if session:
        body['session_id'] = session
    t0 = time.time()
    r = requests.post('{}/chat'.format(BASE), json=body, timeout=180)
    t = time.time() - t0
    return r.json(), t

# 1. Health
r = requests.get('{}/health'.format(BASE), timeout=5)
print('[HEALTH] {}'.format(r.json()))

# 2. Guest - room price
print('\n[T1 Guest - room price]')
d, t = chat('Phong 101 gia bao nhieu?', tenant_id=None)
print('  Latency: {}s'.format(int(t)))
print('  System: {}'.format(d.get('system_used')))
print('  Tools: {}'.format(d.get('tools_used')))
ans = d.get('answer', '')
print('  Answer (first 150): {}'.format(ans[:150]))

# 3. Tenant 1 - invoice
print('\n[T2 Tenant 1 - invoice]')
d, t = chat('Toi con no bao nhieu?', tenant_id=1)
print('  Latency: {}s'.format(int(t)))
ans = d.get('answer', '')
print('  Answer: {}'.format(ans[:150]))

# 4. Available rooms (guest)
print('\n[T3 Available rooms]')
d, t = chat('Con phong trong khong?', tenant_id=None)
print('  Latency: {}s'.format(int(t)))
print('  Tools: {}'.format(d.get('tools_used')))
ans = d.get('answer', '')
print('  Answer: {}'.format(ans[:150]))

# 5. Conversation history - check personalization
print('\n[T4 Tenant 4 - complaint tone]')
d, t = chat('Sao thang nay tien dien cao vay?', tenant_id=4)
print('  Latency: {}s'.format(int(t)))
print('  System: {}'.format(d.get('system_used')))
ans = d.get('answer', '')
print('  Answer: {}'.format(ans[:150]))

# Summary
print('\n\n=== DONE ===")
