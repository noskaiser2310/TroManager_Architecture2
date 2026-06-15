"""
new_05: Tính tổng chi phí — Đoàn Văn Khải (guest)
1 turn: tính tổng chi phí phòng 103
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_total_cost():
        r = chat(
            "Em thấy phòng 103 giá 3 triệu. Cho em hỏi thêm: "
            "tiền điện bao nhiêu 1 số? Nước bao nhiêu 1 khối? "
            "Phí wifi, rác, gửi xe mỗi tháng bao nhiêu? "
            "Giả sử dùng 50 số điện, 5 khối nước thì tổng tầm bao nhiêu?"
        )
        ans = r["answer"].lower()
        assert any(c in ans for c in "0123456789"), f"Không thấy số: {ans[:200]}"
        assert any(w in ans for w in ["103", "3.", "triệu", "tổng"]), f"Không thấy tổng: {ans[:200]}"

    tests = [
        ("Guest: tính chi phí phòng 103", guest_total_cost),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 05 - Tính tổng chi phí phòng 103", run)
