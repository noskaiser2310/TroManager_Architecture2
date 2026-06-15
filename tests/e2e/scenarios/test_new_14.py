"""
new_14: Tìm phòng cho 2 người ở — Võ Hoàng Nam (guest)
1 turn: hỏi phòng rộng >25m² cho 2 SV
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_2person_room():
        r = chat(
            "Tụi em 2 đứa ở chung, cần phòng hơn 25m², có chỗ để 2 cái bàn học. "
            "Giá tầm 4tr đổ lại. Bên mình có phòng nào không ạ?"
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["202", "303", "trống", "còn"]), f"Không thấy phòng phù hợp: {ans[:200]}"
        assert any(c in ans for c in "0123456789"), f"Không thấy giá/diện tích: {ans[:200]}"

    tests = [
        ("Guest: tìm phòng 2 người", guest_2person_room),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 14 - Tìm phòng cho 2 người", run)