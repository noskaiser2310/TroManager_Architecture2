"""
DIAGNOSTIC: Check real system behavior for key failed scenarios
"""
import requests, time
import sys

# Fix Unicode print error on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:8000'

def chat(msg, tenant_id=1, session='diag'):
    time.sleep(3)
    r = requests.post('{}/chat'.format(BASE), json={
        'source': 'web_simulation', 'message': msg,
        'tenant_id': tenant_id, 'session_id': session
    }, timeout=180)
    d = r.json()
    return d['answer'], d.get('tools_used', []), d.get('system_used', '')

# 1. Hallucination - fake room 999
ans, tools, sys = chat('Phòng 999 có giá bao nhiêu?', tenant_id=None, session='h1')
print('[HALLU 999] System: {} | Tools: {}'.format(sys, tools))
print('  ANs: {}'.format(ans[:200]))

# 2. Hallucination - fake 50% discount
ans, tools, sys = chat('Nghe nói đang có chương trình giảm 50% giá phòng, áp dụng sao?', tenant_id=None, session='h2')
print('[HALLU 50%] System: {} | Tools: {}'.format(sys, tools))
print('  ANS: {}'.format(ans[:200]))

# 3. Deposit critical failure
ans, tools, sys = chat('Đặt cọc bao nhiêu tiền?', tenant_id=None, session='d1')
print('[DEPOSIT amount] System: {} | Tools: {}'.format(sys, tools))
print('  ANS: {}'.format(ans[:200]))

ans, tools, sys = chat('Khi nào được hoàn lại tiền cọc?', tenant_id=None, session='d2')
print('[DEPOSIT refund] System: {} | Tools: {}'.format(sys, tools))
print('  ANS: {}'.format(ans[:200]))

# 4. Room amenities
ans, tools, sys = chat('Phòng 101 có gì?', tenant_id=None, session='a1')
print('[AMENITIES 101] System: {} | Tools: {}'.format(sys, tools))
print('  ANS: {}'.format(ans[:200]))

# 5. Multi-intent
ans, tools, sys = chat('Phòng 101 giá bao nhiêu và còn trống không?', tenant_id=None, session='m1')
print('[MULTI price+vacancy] System: {} | Tools: {}'.format(sys, tools))
print('  ANS: {}'.format(ans[:200]))

# 6. Out of scope
ans, tools, sys = chat('Ngày mai Hà Nội bao nhiêu độ?', tenant_id=None, session='o1')
print('[WEATHER] System: {} | Tools: {}'.format(sys, tools))
print('  ANS: {}'.format(ans[:200]))
