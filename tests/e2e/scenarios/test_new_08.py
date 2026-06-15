"""
new_08: Hỏi tiện nghi internet — Trịnh Hoàng Long (guest)
1 turn: hỏi internet, máy lạnh, phòng 202
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_internet():
        r = chat(
            "Tôi làm remote IT, cần internet ổn định. "
            "Bên bạn mạng gì? Bao nhiêu Mbps? Có LAN không? "
            "Tôi thấy phòng 202 có máy lạnh Daikin, ban công. "
            "Giá 4tr đã gồm những gì? Phòng còn trống không?"
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["internet", "mạng", "mbps", "wifi"]), f"Không thấy internet: {ans[:200]}"
        assert any(w in ans for w in ["202", "4"]), f"Không thấy phòng 202: {ans[:200]}"

    tests = [
        ("Guest: hỏi internet + phòng 202", guest_internet),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 08 - Hỏi internet + phòng 202", run)
