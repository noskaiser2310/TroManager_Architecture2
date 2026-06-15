"""
new_11: Hỏi thông tin phòng 103 — Nguyễn Thị Mai (guest)
1 turn: hỏi chi tiết phòng 103 (giá, diện tích, cửa sổ, phơi đồ)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_room_103():
        r = chat(
            "Cho em hỏi phòng 103 còn trống không? Diện tích bao nhiêu, có cửa sổ không? "
            "Có chỗ phơi đồ riêng không ạ? Em định qua xem cuối tuần."
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["103", "trống", "còn"]), f"Không thấy phòng 103: {ans[:200]}"
        assert any(c in ans for c in "0123456789"), f"Không thấy giá/diện tích: {ans[:200]}"

    tests = [
        ("Guest: hỏi thông tin phòng 103", guest_room_103),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 11 - Hỏi thông tin phòng 103", run)