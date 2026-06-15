"""
new_13: So sánh 103 và 203 — Lê Thị Hương (guest)
1 turn: hỏi so sánh 2 phòng
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_compare_103_203():
        r = chat(
            "Em đang phân vân giữa phòng 103 giá 3tr và phòng 203 giá 3.2tr. "
            "Phòng nào rộng hơn, thoáng hơn? Em cần yên tĩnh để soạn giáo án."
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["103", "203"]), f"Không thấy 2 phòng: {ans[:200]}"
        assert any(w in ans for w in ["khác", "hơn", "so sánh"]), f"Không thấy so sánh: {ans[:200]}"

    tests = [
        ("Guest: so sánh 103 vs 203", guest_compare_103_203),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 13 - So sánh phòng 103 và 203", run)