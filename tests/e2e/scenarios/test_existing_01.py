"""
existing_01: Tra cứu hoá đơn — Nguyễn Văn Minh (tenant_id=1, phòng 101)
4 turns: kiểm tra hoá đơn → lịch sử → hỏi tài khoản → hỏi chính sách đóng nhiều tháng
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_01_test_session"


def run():
    def t1_check_invoice():
        r = chat(
            "Anh ơi cho em hỏi tháng này tiền phòng của em hết bao nhiêu vậy ạ? "
            "Em muốn kiểm tra lại xem đã đóng đủ chưa.",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"]
        assert any(c in ans for c in "0123456789"), f"Không thấy số tiền: {ans[:200]}"
        assert any(w in ans for w in ["101", "Minh"]), f"Không thấy tên/phòng: {ans[:200]}"

    def t2_payment_history():
        r = chat(
            "Anh cho em xem lịch sử 3 tháng gần nhất được không?",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["tháng", "thanh toán", "đã"]), f"Không thấy lịch sử: {ans[:200]}"

    def t3_bank_account():
        r = chat(
            "Anh cho em xin lại số tài khoản Vietcombank với nội dung chuyển tiền luôn.",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"]
        assert any(w in ans for w in ["Vietcombank", "tài khoản", "chuyển khoản"]), f"Không thấy TK: {ans[:200]}"

    def t4_pay_multiple_months():
        r = chat(
            "Nếu em muốn đóng tiền 3 tháng một lần có được không ạ?",
            tenant_id=1, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["được", "có", "3 tháng"]), f"Không thấy policy: {ans[:200]}"

    tests = [
        ("Turn 1: kiểm tra hoá đơn", t1_check_invoice),
        ("Turn 2: lịch sử thanh toán", t2_payment_history),
        ("Turn 3: hỏi tài khoản", t3_bank_account),
        ("Turn 4: chính sách đóng nhiều tháng", t4_pay_multiple_months),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 01 - Minh tra cứu hoá đơn", run)
