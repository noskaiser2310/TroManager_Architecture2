"""
new_20: Hỏi các dịch vụ và tiện ích đi kèm — Vũ Thị Mai Lan (guest)
1 turn: hỏi giặt ủi, dọn vệ sinh, gửi xe, wifi
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_amenities():
        r = chat(
            "Bên mình có dịch vụ giặt ủi không? Có dọn vệ sinh định kỳ không? "
            "Gửi xe máy có mất phí không? Wifi riêng hay dùng chung? Có máy giặt chung không ạ?"
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["giặt", "dịch vụ", "gửi xe", "wifi", "tiện ích"]), f"Không thấy tiện ích: {ans[:200]}"

    tests = [
        ("Guest: hỏi dịch vụ tiện ích", guest_amenities),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 20 - Hỏi dịch vụ tiện ích", run)
