"""
new_15: Hỏi tiện nghi phòng 202 — Đặng Hoàng Long (guest)
1 turn: hỏi chi tiết phòng 202 (ban công, máy lạnh, tiện nghi)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_room_202_details():
        r = chat(
            "Em nghe nói phòng 202 đẹp lắm, có ban công rộng. Còn trống không ạ? "
            "Cho em hỏi chi tiết — ban công rộng bao nhiêu, hướng nào, máy lạnh hiệu gì, "
            "có tủ quần áo lớn không? Giá 4tr đã bao gồm những gì?"
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["202", "ban công", "máy lạnh"]), f"Không thấy tiện nghi: {ans[:200]}"
        assert any(c in ans for c in "0123456789"), f"Không thấy giá: {ans[:200]}"

    tests = [
        ("Guest: hỏi tiện nghi phòng 202", guest_room_202_details),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 15 - Hỏi tiện nghi phòng 202", run)