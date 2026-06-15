"""
new_19: Hỏi chính sách hoàn cọc và hủy phòng — Nguyễn Văn Tùng (guest)
1 turn: hỏi cọc, hủy phòng trước hạn, phí phạt
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_deposit_policy():
        r = chat(
            "Nếu lỡ phải chuyển đi sớm thì cọc có được hoàn lại không? Hợp đồng tối thiểu bao lâu? "
            "Có phí phạt nếu hủy trước hạn không?"
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["cọc", "hoàn", "phạt", "hợp đồng"]), f"Không thấy chính sách cọc: {ans[:200]}"

    tests = [
        ("Guest: hỏi chính sách hoàn cọc", guest_deposit_policy),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 19 - Hỏi chính sách cọc", run)
