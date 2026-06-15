"""
new_10: Khách cũ quay lại — Trương Minh Tâm (guest)
1 turn: từng ở phòng 201, muốn thuê lại
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_returning():
        r = chat(
            "Anh chị còn nhớ em không? Em Tâm hồi trước ở phòng 201 "
            "với ông Tuấn. Nay em quay lại thành phố, muốn thuê phòng riêng. "
            "Còn phòng nào đẹp không ạ? Ưu tiên tầng 2-3, có máy lạnh. "
            "Khách cũ có được giảm gì không?"
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["chào", "mừng", "quay lại", "nhớ"]), f"Không chào khách cũ: {ans[:200]}"
        assert any(w in ans for w in ["203", "303", "trống"]), f"Không thấy phòng: {ans[:200]}"

    tests = [
        ("Guest: khách cũ quay lại", guest_returning),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 10 - Khách cũ quay lại", run)
