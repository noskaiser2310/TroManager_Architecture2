"""
existing_16: Kiểm tra lịch sử thông báo đã nhận — Nguyễn Văn Minh (tenant_id=1, phòng 101)
4 turns: xem thông báo cũ → check bảo trì → yêu cầu gửi lại → đăng ký Zalo
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_16_test_session"


def run():
    def t1_check_notifications():
        r = chat(
            "Dạo này app có báo gì cho em không? Em lỡ tay gạt mất mấy cái thông báo không đọc được.",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["thông báo", "nhắc", "bảo trì"]), f"Không thấy thông báo: {ans[:200]}"

    def t2_check_maintenance():
        r = chat(
            "Em thấy có thông báo bảo trì đầu tháng. Lịch bảo trì thang máy đã xong chưa anh?",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["bảo trì", "thang máy", "lịch"]), f"Không thấy bảo trì: {ans[:200]}"

    def t3_request_resend():
        r = chat(
            "Anh gửi lại em cái thông báo bảo trì đó được không? Em muốn coi lại lịch.",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["không", "gửi lại", "app", "xem"]), f"Không thấy trả lời: {ans[:200]}"

    def t4_setup_zalo():
        r = chat(
            "Thôi cho em xin nhận qua Zalo luôn cho chắc. Mấy cái quan trọng như bảo trì với nhắc nợ thôi.",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["zalo", "cập nhật", "thiết lập", "xong"]), f"Không thấy xác nhận Zalo: {ans[:200]}"

    tests = [
        ("Turn 1: kiểm tra thông báo cũ", t1_check_notifications),
        ("Turn 2: xem lịch bảo trì", t2_check_maintenance),
        ("Turn 3: yêu cầu gửi lại", t3_request_resend),
        ("Turn 4: đăng ký Zalo", t4_setup_zalo),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 16 - Minh kiểm tra thông báo", run)
