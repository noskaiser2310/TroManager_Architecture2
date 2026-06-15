"""
existing_03: Gia hạn hợp đồng — Đỗ Văn Hùng (tenant_id=5, phòng 302)
4 turns: hỏi hạn hợp đồng → thương lượng giá → hỏi điều khoản → chờ duyệt
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_03_test_session"


def run():
    def t1_check_contract():
        r = chat(
            "Hợp đồng của em sắp hết hạn vào tháng 9. Em muốn ở tiếp. "
            "Có chính sách ưu đãi cho khách ở lâu không?",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["hợp đồng", "302", "2026", "gia hạn"]), f"Không thấy hợp đồng: {ans[:200]}"

    def t2_negotiate_price():
        r = chat(
            "Anh xem giảm cho em 200-300k/tháng được không? "
            "Em ở gần 2 năm chưa từng đóng trễ.",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["giảm", "duyệt", "admin", "xem xét"]), f"Không thấy thương lượng: {ans[:200]}"

    def t3_terms():
        r = chat(
            "Ký tiếp có phải đóng cọc lại không? Có thay đổi điều khoản gì không?",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["cọc", "điều khoản", "giữ nguyên", "không"]), f"Không thấy điều khoản: {ans[:200]}"

    def t4_wait():
        r = chat(
            "Bao lâu có kết quả duyệt vậy anh? Nếu ok em ký từ 1/9.",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"]
        assert any(c in ans for c in "0123456789"), f"Không thấy thời gian: {ans[:200]}"

    tests = [
        ("Turn 1: hỏi hợp đồng", t1_check_contract),
        ("Turn 2: thương lượng giá", t2_negotiate_price),
        ("Turn 3: hỏi điều khoản", t3_terms),
        ("Turn 4: hỏi thời gian duyệt", t4_wait),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 03 - Hùng gia hạn hợp đồng", run)
