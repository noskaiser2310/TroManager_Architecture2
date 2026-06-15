"""
new_12: Tìm phòng tầng 1 — Trần Văn Đức (guest)
1 turn: hỏi phòng trống tầng 1
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_floor1():
        r = chat(
            "Tôi muốn thuê phòng tầng 1 vì chân yếu. Bên mình còn phòng tầng 1 nào trống không? "
            "Cho tôi hỏi giá và diện tích."
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["103", "tầng 1", "trống"]), f"Không thấy phòng tầng 1: {ans[:200]}"
        assert any(c in ans for c in "0123456789"), f"Không thấy giá: {ans[:200]}"

    tests = [
        ("Guest: hỏi phòng tầng 1", guest_floor1),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 12 - Tìm phòng tầng 1", run)