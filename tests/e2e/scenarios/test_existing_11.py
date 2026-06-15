"""
existing_11: Đăng ký nhận thông báo qua Zalo — Nguyễn Văn Minh (tenant_id=1, phòng 101)
4 turns: hỏi về thông báo → đăng ký Zalo → hỏi loại TB → chọn lọc
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_11_test_session"


def run():
    def t1_ask_about_notification():
        r = chat(
            "Bên mình có nhắc nợ tự động qua Zalo không? Em hay quên ngày đóng phòng.",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["zalo", "nhắc", "thông báo"]), f"Không thấy thông tin TB: {ans[:200]}"

    def t2_register_zalo():
        r = chat(
            "Cho em đăng ký nhận thông báo qua Zalo luôn đi. Em dùng Zalo thường xuyên.",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["đăng ký", "zalo", "thành công"]), f"Không thấy đăng ký: {ans[:200]}"

    def t3_notification_types():
        r = chat(
            "Em sẽ nhận được những loại thông báo nào vậy?",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["nhắc", "bảo trì", "gia hạn", "thông báo"]), f"Không thấy loại TB: {ans[:200]}"

    def t4_opt_out_marketing():
        r = chat(
            "Cho em chỉ nhận mấy cái quan trọng như nhắc nợ, bảo trì thôi nhé. Khuyến mãi với sinh nhật thì thôi.",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["chỉnh", "cập nhật", "xong", "thiết lập"]), f"Không thấy xác nhận: {ans[:200]}"

    tests = [
        ("Turn 1: hỏi về thông báo Zalo", t1_ask_about_notification),
        ("Turn 2: đăng ký Zalo", t2_register_zalo),
        ("Turn 3: hỏi loại thông báo", t3_notification_types),
        ("Turn 4: chọn lọc thông báo", t4_opt_out_marketing),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 11 - Minh đăng ký nhận thông báo Zalo", run)