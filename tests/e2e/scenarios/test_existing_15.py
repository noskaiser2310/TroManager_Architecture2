"""
existing_15: Yêu cầu gửi xác nhận thanh toán qua SMS — Phạm Thị Lan (tenant_id=4, phòng 301)
4 turns: báo đã chuyển khoản → xác nhận số tiền → sốt ruột chưa có SMS → hủy tự ra VP
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_15_test_session"


def run():
    def t1_confirm_payment():
        r = chat(
            "Tôi chuyển khoản xong 2 tháng nợ rồi. Cho tôi xin biên nhận qua SMS được không?",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(c in ans for c in "0123456789"), f"Không thấy số tiền: {ans[:200]}"

    def t2_verify_amount():
        r = chat(
            "Tôi chuyển 8.930.000đ đúng không? Kiểm tra giúp tôi xem đã khớp chưa.",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(c in ans for c in "0123456789"), f"Không thấy xác nhận: {ans[:200]}"

    def t3_impatient():
        r = chat(
            "Sao lâu vậy? Chưa thấy SMS đâu. Tôi cần biên nhận để đối chiếu.",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["admin", "duyệt", "chờ", "gửi"]), f"Không thấy giải thích: {ans[:200]}"

    def t4_cancel_request():
        r = chat(
            "Thôi chờ lâu quá, tôi tự ra văn phòng lấy biên nhận giấy. Mấy giờ mở cửa?",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["giờ", "sáng", "chiều", "làm việc"]), f"Không thấy giờ làm việc: {ans[:200]}"

    tests = [
        ("Turn 1: báo đã chuyển khoản", t1_confirm_payment),
        ("Turn 2: xác nhận số tiền", t2_verify_amount),
        ("Turn 3: sốt ruột chưa có SMS", t3_impatient),
        ("Turn 4: hủy yêu cầu, hỏi giờ VP", t4_cancel_request),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 15 - Lan yêu cầu xác nhận thanh toán SMS", run)