"""
new_09: Hỏi an ninh — Hoàng Thị Thanh (guest)
1 turn: hỏi về an ninh, khoá, camera
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario


def run():
    def guest_security():
        r = chat(
            "Em là nữ ở một mình nên lo an ninh. "
            "Bên mình có khoá vân tay không? Có camera không? "
            "Có bảo vệ trực không ạ? Em làm y tá hay về khuya."
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["khoá", "camera", "an ninh", "bảo vệ"]), \
            f"Không thấy an ninh: {ans[:200]}"

    tests = [
        ("Guest: hỏi an ninh", guest_security),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("New 09 - Hỏi an ninh", run)
