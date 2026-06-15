"""
existing_19: Hỏi chính sách thông báo và tần suất — Đỗ Văn Hùng (tenant_id=5, phòng 302)
4 turns: hỏi chính sách TB → giới hạn tần suất → gộp TB → chọn lọc loại TB
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_19_test_session"


def run():
    def t1_ask_notification_policy():
        r = chat(
            "Anh muốn hỏi bên mình gửi thông báo cho khách thuê với tần suất thế nào? Bao lâu một lần, gồm những loại gì?",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["thông báo", "nhắc", "tần suất", "loại"]), f"Không thấy chính sách: {ans[:200]}"

    def t2_limit_frequency():
        r = chat(
            "Có cách nào giới hạn số lần nhận TB trong tuần không? Anh họp suốt, reo hoài phiền lắm.",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["gộp", "giới hạn", "tần suất", "tuỳ chỉnh"]), f"Không thấy hướng giải quyết: {ans[:200]}"

    def t3_digest_question():
        r = chat(
            "Gộp TB gửi 1 lần cuối ngày cũng được. Mà gộp có bỏ sót TB quan trọng không?",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["khẩn", "gấp", "quan trọng", "ngay"]), f"Không thấy phân biệt TB: {ans[:200]}"

    def t4_set_digest():
        r = chat(
            "Ok vậy gộp giúp anh. Giữ lại nhắc nợ với bảo trì thôi. Khuyến mãi, sinh nhật tắt hết.",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["cập nhật", "thiết lập", "xong", "gộp"]), f"Không thấy xác nhận: {ans[:200]}"

    tests = [
        ("Turn 1: hỏi chính sách TB", t1_ask_notification_policy),
        ("Turn 2: giới hạn tần suất", t2_limit_frequency),
        ("Turn 3: hỏi gộp TB", t3_digest_question),
        ("Turn 4: thiết lập gộp TB", t4_set_digest),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 19 - Hùng hỏi chính sách TB", run)
