"""
existing_14: Đăng ký nhận nhắc gia hạn hợp đồng — Đỗ Văn Hùng (tenant_id=5, phòng 302)
4 turns: hỏi hạn hợp đồng → đăng ký nhắc SMS → hỏi ưu đãi → ghi chú
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_14_test_session"


def run():
    def t1_check_contract():
        r = chat(
            "Anh xem giúp hợp đồng còn bao lâu nữa hết hạn? Anh tính gia hạn tiếp nhưng sợ quên.",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["hợp đồng", "hết hạn", "tháng"]), f"Không thấy hạn hợp đồng: {ans[:200]}"

    def t2_register_sms_reminder():
        r = chat(
            "Anh muốn được nhắc qua SMS trước 1 tháng khi hết hạn. Cho anh đăng ký nhé.",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["sms", "nhắc", "tháng", "30 ngày"]), f"Không thấy nhắc: {ans[:200]}"

    def t3_renewal_policy():
        r = chat(
            "Gia hạn có ưu đãi gì cho khách cũ không? Anh nghe nói mới có chính sách giữ phòng.",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["ưu đãi", "giữ phòng", "gia hạn"]), f"Không thấy policy: {ans[:200]}"

    def t4_note_reminder():
        r = chat(
            "Ghi chú tới tháng 8 nhắc anh, gửi kèm thông tin ưu đãi gia hạn nhé.",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["tháng 8", "ghi nhận", "nhắc"]), f"Không thấy ghi chú: {ans[:200]}"

    tests = [
        ("Turn 1: hỏi hạn hợp đồng", t1_check_contract),
        ("Turn 2: đăng ký nhắc SMS", t2_register_sms_reminder),
        ("Turn 3: hỏi ưu đãi gia hạn", t3_renewal_policy),
        ("Turn 4: ghi chú nhắc kèm ưu đãi", t4_note_reminder),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 14 - Hùng đăng ký nhắc gia hạn hợp đồng", run)