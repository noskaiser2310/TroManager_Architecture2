"""
existing_18: Báo mất điện thoại và cập nhật số SMS — Phạm Thị Lan (tenant_id=4, phòng 301)
4 turns: mất ĐT → cập nhật số mới → xem TB cũ → xác nhận SMS
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_18_test_session"


def run():
    def t1_lost_phone():
        r = chat(
            "Em mất điện thoại rồi anh ơi! Sắp tới ngày đóng phòng mà không thấy nhắc SMS nữa. Bên mình còn cách nào nhắn em không?",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["số", "cập nhật", "liên lạc", "email"]), f"Không thấy hướng dẫn: {ans[:200]}"

    def t2_update_phone():
        r = chat(
            "Em mua SIM mới rồi. Số mới 0911223344, anh cập nhật giúp em với.",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["cập nhật", "xong", "số", "0911"]), f"Không thấy cập nhật số: {ans[:200]}"

    def t3_check_old_notif():
        r = chat(
            "Hồi đầu tháng em thấy có sms báo gì đó. Anh coi giúp em nội dung được không?",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["thông báo", "nhắc", "nợ"]), f"Không thấy nội dung: {ans[:200]}"

    def t4_confirm_payment():
        r = chat(
            "Dạ để em đóng luôn tiền tháng này cho khỏi quên. Anh cho em xin số tài khoản.",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["tài khoản", "stk", "ngân hàng", "chuyển"]), f"Không thấy STK: {ans[:200]}"

    tests = [
        ("Turn 1: báo mất điện thoại", t1_lost_phone),
        ("Turn 2: cập nhật số mới", t2_update_phone),
        ("Turn 3: xem thông báo cũ", t3_check_old_notif),
        ("Turn 4: hỏi STK thanh toán", t4_confirm_payment),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 18 - Lan cập nhật SMS", run)
