"""
new_04: Đặt lịch xem phòng — Phạm Thị Nhung (guest)
1 turn: đặt lịch xem phòng 303 chủ nhật
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_schedule_viewing():
        r = chat(
            "Em có xem phòng 303 trên web, thấy cũng ưng. "
            "Chủ nhật này em rảnh, bên mình sắp xếp cho em "
            "qua xem được không ạ? Khoảng 10h sáng."
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["303", "xem", "chủ nhật", "lịch"]), f"Không thấy lịch hẹn: {ans[:200]}"
        assert any(w in ans for w in ["được", "có", "ok", "sắp xếp"]), f"Không xác nhận: {ans[:200]}"

    tests = [
        ("Guest: đặt lịch xem 303", guest_schedule_viewing),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 04 - Đặt lịch xem phòng 303", run)
