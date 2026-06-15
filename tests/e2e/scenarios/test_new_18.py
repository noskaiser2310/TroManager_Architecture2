"""
new_18: Hỏi thủ tục đặt phòng và giấy tờ — Lê Thị Phương (guest)
1 turn: hỏi đặt phòng online, cọc, giấy tờ
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_booking_procedure():
        r = chat(
            "Em muốn hỏi thủ tục đặt phòng như thế nào? Có đặt cọc online được không? "
            "Cần CMND hay giấy tờ gì không ạ? Có cần ký hợp đồng không?"
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["cọc", "hợp đồng", "thủ tục", "giấy tờ", "cmnd"]), f"Không thấy thủ tục: {ans[:200]}"

    tests = [
        ("Guest: hỏi thủ tục đặt phòng", guest_booking_procedure),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 18 - Hỏi thủ tục đặt phòng", run)
