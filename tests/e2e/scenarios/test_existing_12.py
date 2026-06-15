"""
existing_12: Báo hỏng và yêu cầu thông báo tiến độ sửa — Lê Hoàng Tuấn (tenant_id=3, phòng 201)
4 turns: báo hỏng nước → đăng ký nhận thông báo → hỏi ETA → dặn lịch
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_12_test_session"


def run():
    def t1_report_leak():
        r = chat(
            "Ống nước dưới bồn rửa chén bị rò rỉ. Cho em báo luôn với. Mà tủ lạnh báo từ đợt trước chưa thấy ai qua sửa.",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["phiếu", "tiếp nhận", "ticket", "sửa"]), f"Không thấy tạo ticket: {ans[:200]}"

    def t2_request_notification():
        r = chat(
            "Nếu có thợ tới thì báo em trước qua Zalo nhé, chứ em đi làm suốt.",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["zalo", "báo trước", "nhắn"]), f"Không thấy xác nhận TB: {ans[:200]}"

    def t3_ask_eta():
        r = chat(
            "Bao lâu nữa có thợ? Tủ lạnh báo lâu rồi chưa thấy ai.",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["giờ", "ngày", "tiếng", "24"]), f"Không thấy ETA: {ans[:200]}"

    def t4_set_schedule():
        r = chat(
            "Dặn thợ sáng chủ nhật em ở nhà. Nếu rảnh sớm hơn thì gọi em trước 1 tiếng.",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["chủ nhật", "sáng", "ghi nhận", "lịch"]), f"Không thấy lịch: {ans[:200]}"

    tests = [
        ("Turn 1: báo hỏng ống nước", t1_report_leak),
        ("Turn 2: đăng ký nhận TB", t2_request_notification),
        ("Turn 3: hỏi ETA sửa chữa", t3_ask_eta),
        ("Turn 4: dặn lịch thợ", t4_set_schedule),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 12 - Tuấn báo hỏng và nhận thông báo", run)