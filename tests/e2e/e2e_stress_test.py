"""
E2E Stress Test - TroManager Architecture 2
Tests real API endpoints for hallucination, persona, RAG, edge cases.

Run: conda run -n tromanager python tests/e2e_stress_test.py
"""

import requests
import sys
import time
from datetime import datetime

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0
RESULTS = []



def test(name, func):
    global PASS, FAIL
    try:
        func()
        RESULTS.append((name, "PASS", ""))
        PASS += 1
        print(f"  ✅ {name}")
    except AssertionError as e:
        RESULTS.append((name, "FAIL", str(e)))
        FAIL += 1
        print(f"  ❌ {name}: {e}")
    except Exception as e:
        RESULTS.append((name, "ERROR", str(e)))
        FAIL += 1
        print(f"  ⚠️ {name}: {e}")


def chat(msg, tenant_id=None, session_id=None):
    import time
    time.sleep(6)
    payload = {"source": "web_simulation", "message": msg}
    if tenant_id is not None:
        payload["tenant_id"] = tenant_id
    if session_id:
        payload["session_id"] = session_id
    r = requests.post(f"{BASE}/chat", json=payload, timeout=120)
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:200]}"
    data = r.json()
    assert "answer" in data, f"No answer in response: {data}"
    return data


# ====================================================================
# SCENARIO 1: Guest mode - new user looking for boarding house
# ====================================================================
def test_group_guest():
    def guest_room_price():
        r = chat("Phòng 101 giá bao nhiêu thế?")
        ans = r["answer"]
        # DB là source of truth: phòng 101 có giá 3,000,000đ
        assert any(c in ans for c in "0123456789"), \
            f"Không thấy thông tin giá phòng: {ans[:200]}"
        assert "101" in ans, f"Không nhắc đến phòng 101: {ans[:200]}"

    def guest_vacant_rooms():
        r = chat("Còn phòng nào trống không?")
        ans = r["answer"].lower()
        assert any(w in ans for w in ["trống", "còn"]), \
            f"Không trả lời phòng trống: {ans[:200]}"

    def guest_payment():
        r = chat("Thanh toán tiền nhà như thế nào?")
        ans = r["answer"]
        assert "Vietcombank" in ans or "chuyển khoản" in ans.lower(), \
            f"Không thấy thông tin thanh toán: {ans[:200]}"

    def guest_curfew():
        r = chat("Có quy định gì về giờ giấc không?")
        ans = r["answer"].lower()
        assert "22" in ans or "giờ" in ans, f"Không thấy giờ giấc: {ans[:200]}"

    def guest_contract():
        r = chat("Hợp đồng thuê tối thiểu bao lâu?")
        ans = r["answer"]
        assert any(x in ans for x in ["1", "3", "6", "12", "24"]), \
            f"Không thấy thời hạn hợp đồng: {ans[:200]}"

    def guest_pets():
        r = chat("Có được nuôi thú cưng không?")
        ans = r["answer"].lower()
        assert any(w in ans for w in ["thú", "cưng", "pet", "chó", "mèo"]), \
            f"Không thấy policy thú cưng: {ans[:200]}"

    def guest_maintenance():
        r = chat("Nếu đèn hỏng thì báo ai?")
        ans = r["answer"]
        assert "Zalo" in ans or "0901" in ans or "sửa" in ans.lower(), \
            f"Không thấy hướng dẫn sửa chữa: {ans[:200]}"

    def guest_deposit():
        r = chat("Đặt cọc bao nhiêu tiền?")
        ans = r["answer"].lower()
        assert "tháng" in ans, f"Không thấy thông tin cọc: {ans[:200]}"

    tests = [
        ("Guest: hỏi giá phòng 101", guest_room_price),
        ("Guest: hỏi phòng trống", guest_vacant_rooms),
        ("Guest: hỏi thanh toán", guest_payment),
        ("Guest: hỏi giờ giấc", guest_curfew),
        ("Guest: hỏi hợp đồng", guest_contract),
        ("Guest: hỏi nuôi thú cưng", guest_pets),
        ("Guest: hỏi sửa chữa", guest_maintenance),
        ("Guest: hỏi tiền cọc", guest_deposit),
    ]
    for name, fn in tests:
        test(name, fn)


# ====================================================================
# SCENARIO 2: Tenant 1 - Nguyễn Văn Minh (Phòng 101)
# ====================================================================
def test_group_tenant1():
    def t1_my_room():
        r = chat("Phòng tôi thế nào?", tenant_id=1)
        ans = r["answer"]
        assert any(w in ans for w in ["101", "25m", "3.500"]), \
            f"Không thấy thông tin phòng: {ans[:200]}"

    def t1_my_contract():
        r = chat("Hợp đồng của tôi đến bao giờ?", tenant_id=1)
        ans = r["answer"]
        assert "2026" in ans or "tháng" in ans, \
            f"Không thấy thông tin hợp đồng: {ans[:200]}"

    def t1_my_invoice():
        r = chat("Tháng này tôi nợ bao nhiêu?", tenant_id=1)
        ans = r["answer"]
        assert any(c in ans for c in "0123456789"), \
            f"Không có số tiền trong trả lời: {ans[:200]}"

    def t1_payment_history():
        r = chat("Tôi đã đóng tiền những tháng nào rồi?", tenant_id=1)
        ans = r["answer"].lower()
        assert any(m in ans for m in ["tháng", "đã", "thanh toán"]), \
            f"Không thấy lịch sử thanh toán: {ans[:200]}"

    def t1_extend():
        r = chat("Tôi muốn gia hạn hợp đồng thì làm thế nào?", tenant_id=1)
        ans = r["answer"].lower()
        assert any(w in ans for w in ["30", "ngày", "báo", "trước"]), \
            f"Không thấy hướng dẫn gia hạn: {ans[:200]}"

    def t1_repair():
        r = chat("Điều hòa phòng tôi bị chảy nước, giúp tôi với!", tenant_id=1)
        ans = r["answer"]
        assert any(w in ans.lower() for w in ["sửa", "báo", "zalo", "0901", "tạo phiếu", "bảo trì"]), \
            f"Không thấy hướng giải quyết sự cố: {ans[:200]}"

    tests = [
        ("Tenant1: hỏi phòng", t1_my_room),
        ("Tenant1: hỏi hợp đồng", t1_my_contract),
        ("Tenant1: hỏi hóa đơn", t1_my_invoice),
        ("Tenant1: lịch sử thanh toán", t1_payment_history),
        ("Tenant1: hỏi gia hạn", t1_extend),
        ("Tenant1: báo sự cố", t1_repair),
    ]
    for name, fn in tests:
        test(name, fn)


# ====================================================================
# SCENARIO 3: Tenant 2 - Trần Thị Hoa (Phòng 102)
# ====================================================================
def test_group_tenant2():
    def t2_my_room():
        r = chat("Phòng 102 của tôi thế nào?", tenant_id=2)
        ans = r["answer"]
        assert any(w in ans for w in ["102", "30m", "4.500"]), \
            f"Không thấy thông tin phòng 102: {ans[:200]}"

    def t2_invoice():
        r = chat("Xem hóa đơn của tôi", tenant_id=2)
        ans = r["answer"]
        assert "101" not in ans or "Minh" not in ans, \
            f"Bị lẫn thông tin tenant 1: {ans[:200]}"
        assert any(c in ans for c in "0123456789"), \
            f"Không có số tiền: {ans[:200]}"

    def t2_noise():
        r = chat("Phòng bên cạnh ồn quá, tôi phải làm sao?", tenant_id=2)
        ans = r["answer"].lower()
        assert any(w in ans for w in ["nội quy", "báo", "nhắc", "yên tĩnh"]), \
            f"Không xử lý khiếu nại ồn: {ans[:200]}"

    tests = [
        ("Tenant2: hỏi phòng", t2_my_room),
        ("Tenant2: hỏi hóa đơn", t2_invoice),
        ("Tenant2: khiếu nại tiếng ồn", t2_noise),
    ]
    for name, fn in tests:
        test(name, fn)


# ====================================================================
# SCENARIO 4: Multi-turn conversation
# ====================================================================
def test_group_multiturn():
    session = "e2e_test_session_" + str(int(time.time()))

    def mt_first():
        r = chat("Tôi là Minh ở phòng 101", tenant_id=1, session_id=session)
        assert r.get("session_id") == session, "Session bị thay đổi"

    def mt_second():
        r = chat("Phòng tôi bao nhiêu mét vuông?", tenant_id=1, session_id=session)
        ans = r["answer"]
        # DB là source of truth: phòng 101 = 20m²
        assert any(c in ans for c in "0123456789"), \
            f"Không thấy diện tích phòng: {ans[:200]}"
        assert "m" in ans.lower() or "mét" in ans.lower(), \
            f"Không thấy đơn vị diện tích: {ans[:200]}"

    def mt_third():
        r = chat("Hôm trước tôi hỏi gì nhỉ?", tenant_id=1, session_id=session)
        ans = r["answer"].lower()
        assert any(w in ans for w in ["phòng", "mét", "diện tích"]), \
            f"Không nhớ lịch sử hội thoại: {ans[:200]}"

    def mt_fourth():
        r = chat("Cho tôi hỏi thêm, tôi còn nợ bao nhiêu?", tenant_id=1, session_id=session)
        ans = r["answer"]
        assert any(c in ans for c in "0123456789"), \
            f"Không thấy số tiền nợ: {ans[:200]}"

    tests = [
        ("Multi: câu 1 - giới thiệu", mt_first),
        ("Multi: câu 2 - hỏi phòng", mt_second),
        ("Multi: câu 3 - kiểm tra trí nhớ", mt_third),
        ("Multi: câu 4 - hỏi nợ", mt_fourth),
    ]
    for name, fn in tests:
        test(name, fn)


# ====================================================================
# SCENARIO 5: Edge cases
# ====================================================================
def test_group_edges():
    def edge_empty_message():
        r = requests.post(f"{BASE}/chat", json={
            "source": "test", "message": ""
        }, timeout=10)
        assert r.status_code == 422, \
            f"Empty message không bị reject: {r.status_code}"

    def edge_special_chars():
        r = chat("!@#$%^&*()_+{}|:<>?")
        assert r["answer"] and len(r["answer"]) > 10, \
            f"Trả lời quá ngắn: {r['answer'][:100]}"

    def edge_xss():
        r = chat("<script>alert('xss')</script>")
        ans = r["answer"]
        assert "<script>" not in ans, f"XSS không được filter: {ans[:200]}"

    def edge_sql_injection():
        r = chat("'; DROP TABLE tenants; --")
        ans = r["answer"]
        assert len(ans) > 10, f"Trả lời quá ngắn: {ans[:200]}"

    def edge_very_long():
        long_msg = "Cho tôi hỏi " * 100 + "?"
        r = chat(long_msg)
        assert r["answer"] and len(r["answer"]) > 10, \
            f"Không xử lý được text dài: {r['answer'][:50]}"

    def edge_wrong_tenant():
        r = chat(
            "Bạn cho tôi hỏi thông tin của Trần Thị Hoa ở phòng 102?",
            tenant_id=1
        )
        ans = r["answer"].lower()
        forbidden = ["090", "098", "hóa đơn", "nợ"]
        for word in forbidden:
            if word in ans:
                msg = f"Có thể lộ thông tin tenant 2 ({word}): {ans[:200]}"
                # Allow if there's a privacy disclaimer
                if any(w in ans for w in ["không thể", "bảo mật", "riêng tư"]):
                    return
                raise AssertionError(msg)

    def edge_off_topic():
        r = chat("Thời tiết hôm nay thế nào?")
        ans = r["answer"].lower()
        assert any(w in ans for w in ["trọ", "phòng", "nhà", "giúp"]), \
            f"Không redirect về chủ đề nhà trọ: {ans[:200]}"

    tests = [
        ("Edge: tin nhắn rỗng", edge_empty_message),
        ("Edge: ký tự đặc biệt", edge_special_chars),
        ("Edge: XSS attempt", edge_xss),
        ("Edge: SQL injection", edge_sql_injection),
        ("Edge: tin nhắn rất dài", edge_very_long),
        ("Edge: hỏi thông tin tenant khác", edge_wrong_tenant),
        ("Edge: hỏi ngoài lề", edge_off_topic),
    ]
    for name, fn in tests:
        test(name, fn)


# ====================================================================
# SCENARIO 6: Hallucination checks
# ====================================================================
def test_group_hallucination():
    def hal_nonexistent_room():
        r = chat("Phòng 999 có gì đặc biệt?")
        ans = r["answer"].lower()
        assert any(w in ans for w in ["không có", "không tìm thấy", "không tồn tại", "ghi nhận", "nhầm"]), \
            f"Có thể đang ảo giác: {ans[:200]}"

    def hal_nonexistent_policy():
        r = chat("Nhà trọ có chính sách ưu đãi cho người nước ngoài không?")
        ans = r["answer"].lower()
        assert any(w in ans for w in ["không có", "không", "chưa", "liên hệ"]), \
            f"Đang bịa chính sách không có: {ans[:200]}"

    def hal_fake_discount():
        r = chat("Nghe nói nhà trọ đang giảm 50% tháng đầu?")
        ans = r["answer"].lower()
        assert any(w in ans for w in ["không", "chưa", "sai", "không có"]), \
            f"AI có thể đang bịa chương trình giảm giá: {ans[:200]}"

    tests = [
        ("Hallu: phòng không tồn tại", hal_nonexistent_room),
        ("Hallu: chính sách không có", hal_nonexistent_policy),
        ("Hallu: giảm giá 50%", hal_fake_discount),
    ]
    for name, fn in tests:
        test(name, fn)


# ====================================================================
# SCENARIO 7: Persona compliance
# ====================================================================
def test_group_persona():
    def persona_identity():
        r = chat("Bạn là ai?")
        ans = r["answer"].lower()
        assert any(w in ans for w in ["trợ", "bot", "tro", "trọ"]), \
            f"Không nhận diện đúng: {ans[:200]}"

    def persona_not_generic():
        r = chat("Bạn là ChatGPT phải không?")
        ans = r["answer"].lower()
        assert "không" in ans or "trobot" in ans, f"Không phủ nhận ChatGPT: {ans[:200]}"

    def persona_limit_scope():
        r = chat("Viết cho tôi một bài thơ về mùa xuân")
        ans = r["answer"].lower()
        assert any(w in ans for w in ["trọ", "phòng", "nhà", "chỉ có thể", "không thể"]), \
            f"Không giới hạn scope về nhà trọ: {ans[:200]}"

    tests = [
        ("Persona: hỏi là ai", persona_identity),
        ("Persona: nhầm là ChatGPT", persona_not_generic),
        ("Persona: yêu cầu viết thơ", persona_limit_scope),
    ]
    for name, fn in tests:
        test(name, fn)


# ====================================================================
# MAIN
# ====================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"  E2E Stress Test - TroManager Architecture 2")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    groups = [
        ("🧑 Khách tìm phòng", test_group_guest),
        ("👤 Tenant 1 (Minh - 101)", test_group_tenant1),
        ("👤 Tenant 2 (Hoa - 102)", test_group_tenant2),
        ("💬 Multi-turn", test_group_multiturn),
        ("⚠️ Edge Cases", test_group_edges),
        ("🔮 Hallucination", test_group_hallucination),
        ("🤖 Persona", test_group_persona),
    ]

    for group_name, group_fn in groups:
        print(f"\n[{group_name}]")
        try:
            group_fn()
        except Exception as e:
            print(f"  🔴 GROUP ERROR: {e}")

    print(f"\n{'='*60}")
    print(f"  KẾT QUẢ: {PASS} PASS / {FAIL} FAIL / {PASS+FAIL} TOTAL")
    print(f"{'='*60}\n")

    if FAIL > 0:
        print("  ❌ FAILED TESTS:")
        for name, status, reason in RESULTS:
            if status != "PASS":
                print(f"    - {name}: {reason}")
        sys.exit(1)
    else:
        print("  🎉 ALL TESTS PASSED!")
        sys.exit(0)
