"""
new_07: Phòng tầng trệt cho người già — Lâm Văn Đông (guest)
1 turn: hỏi phòng tầng 1 (103) cho mẹ già
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_ground_floor():
        r = chat(
            "Tôi tìm phòng cho mẹ già 70 tuổi, cần phòng tầng trệt. "
            "Thấy có phòng 103 tầng 1. Phòng đó gần nhà vệ sinh không? "
            "Có thoáng mát không? An ninh thế nào? "
            "Giá 3tr có thêm phí gì không ạ?"
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["103", "tầng", "1"]), f"Không thấy phòng 103: {ans[:200]}"
        assert any(w in ans for w in ["vệ sinh", "an ninh", "yên tĩnh"]), f"Không thấy chi tiết: {ans[:200]}"

    tests = [
        ("Guest: phòng tầng trệt", guest_ground_floor),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 07 - Phòng tầng trệt cho mẹ già", run)
