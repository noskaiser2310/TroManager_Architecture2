"""
existing_06: Xin gia hạn thanh toán — Phạm Thị Lan (tenant_id=4, phòng 301)
4 turns: xin gia hạn → hỏi phí phạt → thương lượng → yêu cầu xác nhận
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_06_test_session"


def run():
    def t1_ask_extension():
        r = chat(
            "Tôi nợ 2 tháng rồi, cho tôi xin tới cuối tháng 7. "
            "Hợp đồng hết 10/7, tôi đóng hết một lúc.",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"]
        assert any(c in ans for c in "0123456789"), f"Không thấy số nợ: {ans[:200]}"

    def t2_ask_late_fee():
        r = chat(
            "Phí phạt trễ bao nhiêu? Đóng luôn bây giờ có giảm không?",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["phí", "phạt", "%"]), f"Không thấy phí phạt: {ans[:200]}"

    def t3_negotiate():
        r = chat(
            "Tôi ở gần 1.5 năm rồi, bỏ qua phí phạt được không? "
            "Không thì về quê rồi chuyển sau.",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["duyệt", "admin", "xem xét", "chờ"]), f"Không thấy thương lượng: {ans[:200]}"

    def t4_ask_confirmation():
        r = chat(
            "Gửi tôi xác nhận qua Zalo: tổng nợ, hạn thanh toán, phí phạt.",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"]
        assert any(w in ans for w in ["zalo", "sms", "gửi", "xác nhận"]), f"Không thấy xác nhận: {ans[:200]}"

    tests = [
        ("Turn 1: xin gia hạn", t1_ask_extension),
        ("Turn 2: hỏi phí phạt", t2_ask_late_fee),
        ("Turn 3: thương lượng phí", t3_negotiate),
        ("Turn 4: yêu cầu xác nhận", t4_ask_confirmation),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 06 - Lan xin gia hạn thanh toán", run)
