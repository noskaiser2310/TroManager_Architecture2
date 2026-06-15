"""
new_06: Hỏi ở ghép — Mai Thị Yến (guest)
1 turn: hỏi chính sách ở 2 người, phòng 202
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_shared_room():
        r = chat(
            "Em với bạn định thuê chung một phòng. "
            "Bên mình có cho 2 người ở cùng không? "
            "Bọn em thấy phòng 202 rộng 28m², giá 4tr. "
            "Có bị tính thêm phí người không ạ?"
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["202", "2", "hai", "người"]), f"Không thấy policy: {ans[:200]}"

    tests = [
        ("Guest: hỏi ở ghép", guest_shared_room),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 06 - Hỏi ở ghép phòng 202", run)
