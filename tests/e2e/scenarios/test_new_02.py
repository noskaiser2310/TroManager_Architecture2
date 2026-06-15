"""
new_02: So sánh phòng — Trần Thị Hạnh (guest)
1 turn: so sánh phòng 202 vs 303
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_compare():
        r = chat(
            "Em phân vân giữa phòng 202 và 303. "
            "Phòng nào rộng hơn? Có máy lạnh không? "
            "Hướng phòng có bị nắng chiều không? "
            "Giá chênh lệch nhiều không ạ?"
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["202", "303"]), f"Không thấy 2 phòng: {ans[:200]}"
        assert any(c in ans for c in "0123456789"), f"Không thấy giá: {ans[:200]}"
        assert any(w in ans for w in ["máy lạnh", "diện tích", "mét"]), f"Không thấy so sánh: {ans[:200]}"

    tests = [
        ("Guest: so sánh 202 vs 303", guest_compare),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 02 - So sánh phòng 202 vs 303", run)
