"""
new_01: Tìm phòng giá rẻ — Hoàng Văn Nam (guest, không tenant_id)
1 turn: hỏi phòng giá rẻ (2.5-3.5tr)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_cheap_room():
        r = chat(
            "Bên mình còn phòng nào giá tầm 2.5 đến 3.5 triệu không ạ? "
            "Phòng hơi rộng rộng tí, có cửa sổ. Với cho em hỏi có chỗ gửi xe không?"
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["103", "203", "trống", "còn"]), f"Không thấy phòng trống: {ans[:200]}"
        assert any(c in ans for c in "0123456789"), f"Không thấy giá: {ans[:200]}"

    tests = [
        ("Guest: hỏi phòng giá rẻ", guest_cheap_room),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 01 - Tìm phòng giá rẻ", run)
