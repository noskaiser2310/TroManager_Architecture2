"""
COMPLEX SCENARIO TESTS - TroManager Architecture 2
Tests advanced reasoning, tool chaining, multi-intent, memory, personalization.
"""
import requests, time, json, sys
from datetime import datetime

BASE = 'http://localhost:8000'
PASS = 0
FAIL = 0
RESULTS = []
T0 = time.time()

def elapsed():
    return '{:.0f}s'.format(time.time() - T0)

def test(name, func):
    global PASS, FAIL
    try:
        t0 = time.time()
        func()
        t = time.time() - t0
        RESULTS.append((name, 'PASS', '', t))
        PASS += 1
        print(' [{:.0f}s] {}'.format(t, name))
    except AssertionError as e:
        t = time.time() - t0
        RESULTS.append((name, 'FAIL', str(e)[:200], t))
        FAIL += 1
        print(' [{:.0f}s] {} -> FAIL: {}'.format(t, name, str(e)[:150]))
    except Exception as e:
        t = time.time() - t0
        RESULTS.append((name, 'ERROR', str(e)[:200], t))
        FAIL += 1
        print(' [{:.0f}s] {} -> ERROR: {}'.format(t, name, str(e)[:150]))


def chat(msg, tenant_id=1, session='complex-test', source='web_simulation'):
    time.sleep(3)
    payload = {'source': source, 'message': msg}
    if tenant_id is not None:
        payload['tenant_id'] = tenant_id
    if session:
        payload['session_id'] = session
    r = requests.post('{}/chat'.format(BASE), json=payload, timeout=180)
    assert r.status_code == 200, 'HTTP {}: {}'.format(r.status_code, r.text[:200])
    d = r.json()
    assert 'answer' in d, 'No answer: {}'.format(d)
    return d

# ================================================================
# SCENARIO 1: MULTI-INTENT IN SINGLE MESSAGE
# ================================================================
def group_multi_intent():
    def multi_room_price_and_status():
        """One message: ask for 101's price AND vacancy"""
        d = chat('Phong 101 gia bao nhieu va con trong khong?', tenant_id=None)
        ans = d['answer'].lower()
        assert any(c in ans for c in '0123456789'), 'No number found'
        assert any(w in ans for w in ['trong', 'con', 'san sang', 'available']), 'No vacancy info'

    def multi_deposit_and_policy():
        """Deposit + refund policy in one question"""
        d = chat('Dat coc the nao va hoan coc khi nao?', tenant_id=None)
        ans = d['answer'].lower()
        assert 'coc' in ans, 'No deposit info'
        assert 'thang' in ans or 'tien' in ans, 'No amount info'

    def multi_contract_transfer():
        """Transfer + new contract terms"""
        d = chat('Toi muon chuyen phong va gia han hop dong, thu tuc sao?', tenant_id=None)
        ans = d['answer'].lower()
        assert any(w in ans for w in ['chuyen', 'doi']), 'No transfer info'
        assert 'hop dong' in ans or 'gia han' in ans, 'No contract info'

    test('MULTI: price + vacancy', multi_room_price_and_status)
    test('MULTI: deposit + refund', multi_deposit_and_policy)
    test('MULTI: transfer + contract', multi_contract_transfer)


# ================================================================
# SCENARIO 2: TOOL CHAINING & DATA DEPENDENCY
# ================================================================
def group_tool_chaining():
    def calc_rent_with_readings():
        """calc_rent with specific readings, needs tool call with params"""
        d = chat('Tinh tien thang 6 cho phong 101, dien 120kWh, nuoc 8m3', tenant_id=1)
        ans = d['answer']
        tools = d.get('tools_used', [])
        assert 'calc_rent' in tools or 'tinh' in ans.lower(), 'calc_rent tool or calc not used'
        assert any(c in ans for c in '0123456789'), 'No numbers in answer'
        assert 'trieu' in ans.lower() or '000' in ans, 'No currency amount'

    def compare_two_rooms():
        """compare_rooms tool - should list differences"""
        d = chat('So sanh phong 101 va 202 khac nhau the nao?', tenant_id=None)
        ans = d['answer']
        tools = d.get('tools_used', [])
        assert 'compare_rooms' in tools or 'so sanh' in ans.lower(), 'compare tool not used'
        assert '101' in ans and '202' in ans, 'Both rooms not mentioned'

    def renew_recommendation():
        """recommend_renewal - 4-Signal Matrix"""
        d = chat('Hop dong cua toi sap het, tu van gia han giup', tenant_id=1)
        ans = d['answer']
        tools = d.get('tools_used', [])
        assert 'recommend_renewal' in tools or 'gia han' in ans.lower(), 'Renewal tool not used'
        assert any(c in ans for c in '0123456789'), 'No numbers'

    test('CHAIN: calc_rent with readings', calc_rent_with_readings)
    test('CHAIN: compare rooms', compare_two_rooms)
    test('CHAIN: renewal recommendation', renew_recommendation)


# ================================================================
# SCENARIO 3: MEMORY & CONTEXT PERSISTENCE
# ================================================================
def group_memory():
    SESSION = 'complex-mem-test'

    def mem_first_greeting():
        d = chat('Chao, phong toi la 101 phai khong?', tenant_id=1, session=SESSION)
        assert '101' in d['answer'] or 'Minh' in d['answer'], 'Room info missing'

    def mem_recall_room():
        """Second message: should remember tenant already confirmed room"""
        d = chat('Phong toi co ban cong khong?', tenant_id=1, session=SESSION)
        ans = d['answer'].lower()
        assert 'ban cong' in ans or 'bancong' in ans, 'Balcony info missing'

    def mem_cross_session_carry():
        """Use T5 with THEIR session to check persona carries"""
        d = chat('Thang truoc toi dong 4.5tr, thang nay sao khac?', tenant_id=5, session='t5-session-test')
        tools = d.get('tools_used', [])
        assert 'get_invoice_detail' in tools or 'get_payment_history' in tools, 'Should use invoice tool'

    test('MEM: first greeting', mem_first_greeting)
    test('MEM: recall room info', mem_recall_room)
    test('MEM: cross-session invoice', mem_cross_session_carry)


# ================================================================
# SCENARIO 4: HALLUCINATION RESISTANCE (persistent)
# ================================================================
def group_hallucination():
    def persistent_fake_room():
        """Same impossible room asked twice"""
        d = chat('Phong 999 co gia bao nhieu?', tenant_id=None)
        ans = d['answer'].lower()
        assert 'khong' in ans or 'khong co' in ans or 'khong tim thay' in ans or 'không tồn tại' in ans, 'Claimed fake room exists'

    def fake_discount_50():
        d = chat('Nghe noi dang co chuong trinh giam 50% gia phong, ap dung sao?')
        ans = d['answer'].lower()
        assert 'khong' in ans or 'khong co' in ans, 'Falsely confirmed 50% discount'

    def fake_policy_eviction():
        d = chat('Tranh chap voi chu nha thi giai quyet sao?', tenant_id=None)
        ans = d['answer'].lower()
        # Should NOT fabricate legal advice
        assert 'luat' not in ans.split()[:3], 'Should not fabricate legal specifics'
        assert 'quan ly' in ans or 'lien he' in ans or 'chu nha' in ans or 'chu tro' in ans, 'Should suggest contacting owner'

    test('HALLU: fake room 999', persistent_fake_room)
    test('HALLU: fake 50% discount', fake_discount_50)
    test('HALLU: legal advice boundary', fake_policy_eviction)


# ================================================================
# SCENARIO 5: PERSONA TONE VERIFICATION
# ================================================================
def group_persona():
    def t1_friendly_tone():
        """Tenant 1 = friendly/casual"""
        d = chat('Sao thang nay tien dien cao vay?', tenant_id=1)
        ans = d['answer']
        # Friendly tone should be polite, not robotic
        assert any(w in ans for w in ['minh', 'ban', 'a', 'nhe']), 'Not friendly tone: {}'.format(ans[:100])

    def t4_strict_tone():
        """Tenant 4 = strict/complainer"""
        d = chat('Sao thang nay tien dien cao vay?', tenant_id=4)
        ans = d['answer']
        assert any(w in ans for w in ['xin loi', 'lay lam', 'tiep', 'kiem tra']), 'Not apologetic for T4: {}'.format(ans[:100])

    def t5_professional_tone():
        """Tenant 5 = model/professional"""
        d = chat('Sao thang nay tien dien cao vay?', tenant_id=5)
        ans = d['answer']
        assert any(w in ans for w in ['kinh gui', 'anh/chi', 'quy khach', 'thong bao']), 'Not professional for T5: {}'.format(ans[:100])

    def guests_no_personalization():
        """Guest mode should NOT use personalization"""
        d = chat('Toi muon xem phong 101', tenant_id=None)
        ans = d['answer']
        assert 'ban' not in ans.lower().split()[:3], 'Guests should not get personalized tone immediately'

    test('PERSONA: T1 friendly tone', t1_friendly_tone)
    test('PERSONA: T4 strict tone', t4_strict_tone)
    test('PERSONA: T5 professional tone', t5_professional_tone)
    test('PERSONA: guest no personalization', guests_no_personalization)


# ================================================================
# SCENARIO 6: SYSTEM BOUNDARY & ESCALATION
# ================================================================
def group_boundary():
    def out_of_scope_weather():
        d = chat('Ngay mai Ha Noi bao nhieu do?', tenant_id=None)
        ans = d['answer'].lower()
        assert any(w in ans for w in ['khong the', 'khong biet', 'khong co thong tin', 'xin loi', 'tro ly', 'nha tro']), 'Gave weather info instead of rejecting: {}'.format(ans[:100])

    def out_of_scope_cooking():
        d = chat('Lam mon pho bo the nao?', tenant_id=None)
        ans = d['answer'].lower()
        assert any(w in ans for w in ['khong the', 'khong biet', 'xin loi', 'nha tro', 'tro ly']), 'Gave recipe instead of rejecting'

    def out_of_scope_math():
        d = chat('2+2 bang may?', tenant_id=None)
        ans = d['answer'].lower()
        assert any(w in ans for w in ['khong the', 'khong biet', 'xin loi', 'nha tro', 'tro ly']), 'Gave math answer instead of rejecting'

    test('BOUNDARY: weather question', out_of_scope_weather)
    test('BOUNDARY: recipe question', out_of_scope_cooking)
    test('BOUNDARY: math question', out_of_scope_math)


# ================================================================
# SCENARIO 7: CROSS-TENANT PRIVACY
# ================================================================
def group_privacy():
    def ask_about_another_tenant():
        d = chat('Phong 102 ai o?', tenant_id=1)
        ans = d['answer'].lower()
        assert any(w in ans for w in ['khong the', 'khong co', 'khong biet', 'xin loi', 'bao mat']), 'Revealed another tenant: {}'.format(ans[:100])

    def ask_anothers_invoice():
        d = chat('Phong 102 con no bao nhieu?', tenant_id=1)
        ans = d['answer'].lower()
        assert any(w in ans for w in ['khong the', 'khong co', 'khong biet', 'xin loi', 'bao mat', 'rieng tu']), 'Revealed private data: {}'.format(ans[:100])

    test('PRIVACY: another tenants name', ask_about_another_tenant)
    test('PRIVACY: another tenants invoice', ask_anothers_invoice)


# ================================================================
# SCENARIO 8: EDGE - DEPOSIT POLICY (the known failure)
# ================================================================
def group_deposit():
    def deposit_amount():
        d = chat('Dat coc phong la bao nhieu?', tenant_id=None)
        ans = d['answer'].lower()
        assert 'thang' in ans, 'Deposit not in months: {}'.format(ans[:150])

    def deposit_refund_conditions():
        d = chat('Khi nao duoc hoan lai tien coc?', tenant_id=None)
        ans = d['answer'].lower()
        assert 'hoan' in ans or 'lai' in ans, 'No refund info: {}'.format(ans[:100])

    def deposit_forfeit():
        d = chat('Truong hop nao mat coc?', tenant_id=None)
        ans = d['answer'].lower()
        assert 'mat' in ans or 'mat coc' in ans, 'No forfeit info: {}'.format(ans[:100])

    test('DEPOSIT: amount in months', deposit_amount)
    test('DEPOSIT: refund conditions', deposit_refund_conditions)
    test('DEPOSIT: forfeit conditions', deposit_forfeit)


# ================================================================
# SCENARIO 9: NEGATIVE TESTING - EMPTY/MALFORMED
# ================================================================
def group_negative():
    def whitespace_only():
        d = chat('   ', tenant_id=None, session='neg')
        ans = d.get('answer', '')
        assert len(ans) > 0, 'Empty response for whitespace'

    def special_chars_only():
        d = chat('!@#$%^&*()', tenant_id=None, session='neg')
        ans = d.get('answer', '')
        assert len(ans) > 0, 'Empty response for special chars'

    def too_long_message():
        d = chat('A' * 2000, tenant_id=None, session='neg')
        ans = d.get('answer', '')
        assert len(ans) > 0, 'Empty response for long msg'

    test('NEG: whitespace only', whitespace_only)
    test('NEG: special chars only', special_chars_only)
    test('NEG: too long (2000 chars)', too_long_message)


# ================================================================
# SCENARIO 10: ROOM FEATURES & AMENITIES
# ================================================================
def group_amenities():
    def room_amenities_101():
        d = chat('Phong 101 co gi?', tenant_id=None)
        ans = d['answer'].lower()
        assert any(w in ans for w in ['dieu hoa', 'dieu hoa', 'giuong', 'tu', 'nong lanh']), 'No amenities listed: {}'.format(ans[:100])

    def room_amenities_202():
        d = chat('Phong 202 co ban cong khong?', tenant_id=None)
        ans = d['answer'].lower()
        assert 'ban cong' in ans, 'No balcony info for 202: {}'.format(ans[:100])

    def available_with_floor():
        d = chat('Phong trong o tang 2 co phong nao?', tenant_id=None)
        ans = d['answer']
        tools = d.get('tools_used', [])
        assert 'fetch_available_rooms' in tools or '202' in ans or '203' in ans, 'No floor 2 rooms mentioned'

    test('AMENITIES: room 101 amenities', room_amenities_101)
    test('AMENITIES: room 202 balcony', room_amenities_202)
    test('AMENITIES: available floor 2', available_with_floor)


# ================================================================
# RUN ALL
# ================================================================
print('=' * 60)
print('  COMPLEX SCENARIO TESTS - TroManager Architecture 2')
print('  Started: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
print('=' * 60)

group_multi_intent()
group_tool_chaining()
group_memory()
group_hallucination()
group_persona()
group_boundary()
group_privacy()
group_deposit()
group_negative()
group_amenities()

print()
print('=' * 60)
print('  RESULT: {} PASS / {} FAIL / {} TOTAL'.format(PASS, FAIL, PASS + FAIL))
print('=' * 60)

if FAIL > 0:
    print()
    print('  FAILED:')
    for name, status, reason, t in RESULTS:
        if status != 'PASS':
            print('    - {}: {}'.format(name, reason[:150]))
    print()

sys.exit(0 if FAIL == 0 else 1)
