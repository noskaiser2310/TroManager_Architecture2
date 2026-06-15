"""
new_03: Hỏi thủ tục đặt cọc — Lý Văn Phát (guest)
1 turn: hỏi về cọc, hợp đồng, các loại phí
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_deposit():
        r = chat(
            "Tôi đang quan tâm phòng 202. "
            "Tiền cọc bao nhiêu tháng? Có hoàn lại không? "
            "Hợp đồng tối thiểu bao lâu? "
            "Ngoài 4tr tiền phòng còn phí gì nữa không?"
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["cọc", "tháng", "hợp đồng"]), f"Không thấy cọc/hợp đồng: {ans[:200]}"
        assert any(c in ans for c in "0123456789"), f"Không thấy số: {ans[:200]}"

    tests = [
        ("Guest: hỏi thủ tục cọc", guest_deposit),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 03 - Thủ tục đặt cọc", run)
