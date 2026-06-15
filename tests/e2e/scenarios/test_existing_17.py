"""
existing_17: Cài đặt thời gian nhận thông báo — Lê Hoàng Tuấn (tenant_id=3, phòng 201)
4 turns: than phiền giờ TB → cài giờ yên tĩnh → hỏi TB khẩn cấp → chọn Zalo
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_17_test_session"


def run():
    def t1_complaint_time():
        r = chat(
            "Em làm ca đêm, sáng ngủ mà toàn bị thông báo 8h sáng. Có chỉnh giờ gửi được không anh?",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["giờ", "chỉnh", "tuỳ chỉnh", "cài"]), f"Không thấy giờ: {ans[:200]}"

    def t2_set_silent_hours():
        r = chat(
            "Từ trưa 12h tới tối 8h được. Ngoài giờ đó đừng gửi gì hết nha.",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["12", "20", "giờ", "ghi nhận", "cập nhật"]), f"Không thấy cập nhật giờ: {ans[:200]}"

    def t3_emergency():
        r = chat(
            "Lỡ có cháy nổ hay rò rỉ gas gấp quá thì sao? Cũng chờ tới trưa à?",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["khẩn", "gấp", "bất kỳ", "luôn"]), f"Không thấy TB khẩn: {ans[:200]}"

    def t4_set_zalo():
        r = chat(
            "Ok vậy gửi qua Zalo cho em nhé, em ít vô app lắm. Số Zalo em là số ĐT em đăng ký.",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["zalo", "cập nhật", "xong", "số"]), f"Không thấy Zalo: {ans[:200]}"

    tests = [
        ("Turn 1: than phiền giờ TB", t1_complaint_time),
        ("Turn 2: cài giờ yên tĩnh", t2_set_silent_hours),
        ("Turn 3: hỏi TB khẩn cấp", t3_emergency),
        ("Turn 4: chọn Zalo", t4_set_zalo),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 17 - Tuấn cài giờ thông báo", run)
