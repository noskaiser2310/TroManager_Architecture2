"""
new_16: Hỏi vị trí và giao thông xung quanh — Nguyễn Hoàng Anh (guest)
1 turn: hỏi vị trí, giao thông, an ninh
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_location():
        r = chat(
            "Bên mình ở khu vực nào vậy? Gần bến xe buýt không? Khu này tối có an ninh không ạ?"
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["vị trí", "khu vực", "gần", "xe buýt", "an ninh"]), f"Không thấy thông tin vị trí: {ans[:200]}"

    tests = [
        ("Guest: hỏi vị trí và giao thông", guest_location),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 16 - Hỏi vị trí giao thông", run)
