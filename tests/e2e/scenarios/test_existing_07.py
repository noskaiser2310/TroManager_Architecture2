"""
existing_07: Hỏi chính sách thú cưng + giới thiệu bạn — Nguyễn Văn Minh (tenant_id=1, phòng 101)
4 turns: hỏi nuôi mèo → điều kiện → giới thiệu bạn → xin SĐT quản lý
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_07_test_session"


def run():
    def t1_ask_pet_policy():
        r = chat(
            "Anh ơi em ở 101, em tính nuôi một bé mèo. "
            "Bên mình có cho phép nuôi thú cưng không ạ?",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["thú", "cưng", "mèo", "nuôi"]), f"Không thấy policy: {ans[:200]}"

    def t2_ask_pet_conditions():
        r = chat(
            "Nếu được thì có cần đóng thêm cọc không ạ? "
            "Giới hạn mấy con? Cần ký giấy tờ gì không?",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["cọc", "phụ lục", "ký", "500"]), f"Không thấy điều kiện: {ans[:200]}"

    def t3_refer_friend():
        r = chat(
            "Em có thằng bạn đang tìm phòng. Bên mình còn phòng nào "
            "tầm 3-4tr, rộng rộng, có máy lạnh không anh?",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"]
        assert any(w in ans for w in ["202", "303", "phòng trống"]), f"Không thấy phòng trống: {ans[:200]}"

    def t4_ask_contact():
        r = chat(
            "Anh cho em xin Zalo quản lý để bạn em liên hệ nhé. "
            "Cảm ơn anh!",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"]
        assert len(ans) > 20, f"Trả lời quá ngắn: {ans[:100]}"

    tests = [
        ("Turn 1: hỏi nuôi mèo", t1_ask_pet_policy),
        ("Turn 2: hỏi điều kiện", t2_ask_pet_conditions),
        ("Turn 3: giới thiệu bạn", t3_refer_friend),
        ("Turn 4: xin liên hệ", t4_ask_contact),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 07 - Minh hỏi thú cưng + giới thiệu bạn", run)
