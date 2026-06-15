"""
new_17: Hỏi chi phí điện nước và dịch vụ — Trần Văn Đạt (guest)
1 turn: hỏi tổng chi phí ngoài tiền phòng
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_utility_costs():
        r = chat(
            "Ngoài tiền phòng còn đóng gì nữa? Điện nước tính riêng đúng không? Bao nhiêu một số? "
            "Có phí gửi xe, phí dịch vụ gì không? Tổng mỗi tháng hết cỡ nào?"
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["điện", "nước", "phí", "dịch vụ"]), f"Không thấy chi phí: {ans[:200]}"
        assert any(c in ans for c in "0123456789"), f"Không thấy số liệu: {ans[:200]}"

    tests = [
        ("Guest: hỏi chi phí điện nước", guest_utility_costs),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 17 - Hỏi chi phí điện nước", run)
