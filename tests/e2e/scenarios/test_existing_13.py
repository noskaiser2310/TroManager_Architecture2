"""
existing_13: Đổi kênh thông báo sang SMS — Trần Thị Hoa (tenant_id=2, phòng 102)
4 turns: hỏi đổi kênh → xác nhận số ĐT → hỏi thêm số phụ → hỏi thời gian áp dụng
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_13_test_session"


def run():
    def t1_ask_switch_sms():
        r = chat(
            "Có thể chuyển thông báo từ Zalo sang SMS được không? Tôi ít check Zalo lắm.",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["sms", "chuyển", "đổi"]), f"Không thấy SMS: {ans[:200]}"

    def t2_check_phone():
        r = chat(
            "Đổi cho tôi sang SMS nhé. Mà số tôi đăng ký là số nào nhỉ?",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(c in ans for c in "0123456789"), f"Không thấy số ĐT: {ans[:200]}"

    def t3_add_secondary():
        r = chat(
            "Cho tôi cập nhật thêm số của chồng tôi làm số dự phòng được không?",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["số", "điện thoại", "liên hệ", "thêm"]), f"Không thấy thông tin: {ans[:200]}"

    def t4_effective_date():
        r = chat(
            "Từ bao giờ thì tôi nhận SMS vậy? Thông báo sắp tới là SMS hết hả?",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["hiệu lực", "áp dụng", "ngay", "sms"]), f"Không thấy xác nhận: {ans[:200]}"

    tests = [
        ("Turn 1: hỏi đổi sang SMS", t1_ask_switch_sms),
        ("Turn 2: xác nhận số ĐT", t2_check_phone),
        ("Turn 3: thêm số phụ", t3_add_secondary),
        ("Turn 4: hỏi thời gian áp dụng", t4_effective_date),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 13 - Hoa đổi kênh thông báo SMS", run)