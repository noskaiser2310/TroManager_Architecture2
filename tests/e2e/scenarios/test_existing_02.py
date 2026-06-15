"""
existing_02: Báo wifi chập chờn — Trần Thị Hoa (tenant_id=2, phòng 102)
4 turns: báo wifi → xin số IT → mượn modem → hỏi phí
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_02_test_session"


def run():
    def t1_complain_wifi():
        r = chat(
            "Tôi đã báo wifi chập chờn từ tuần trước (TKT-2026-0002), "
            "tối qua từ 20h-23h vẫn mất kết nối. Có tiến độ gì chưa?",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["tkt", "tiến độ", "đang xử lý", "bảo trì"]), f"Không thấy ticket: {ans[:200]}"

    def t2_ask_it_contact():
        r = chat(
            "Tôi có thể liên hệ trực tiếp anh Tú bên IT được không? "
            "Cho tôi số điện thoại.",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"]
        assert any(w in ans for w in ["liên hệ", "số", "gọi", "zalo"]), f"Không thấy số liên hệ: {ans[:200]}"

    def t3_borrow_modem():
        r = chat(
            "Bên mình có cho mượn modem tạm không? Tôi cần mạng để họp sáng mai.",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["modem", "mượn", "dự phòng", "có"]), f"Không thấy modem: {ans[:200]}"

    def t4_borrow_fee():
        r = chat(
            "Có mất phí mượn modem không? Sửa xong thì trả lại chứ?",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["miễn", "không mất", "trả", "phí"]), f"Không thấy phí: {ans[:200]}"

    tests = [
        ("Turn 1: báo wifi chập chờn", t1_complain_wifi),
        ("Turn 2: xin số IT", t2_ask_it_contact),
        ("Turn 3: hỏi mượn modem", t3_borrow_modem),
        ("Turn 4: hỏi phí mượn", t4_borrow_fee),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 02 - Hoa báo wifi chập chờn", run)
