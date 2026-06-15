"""
existing_04: Khiếu nại hoá đơn — Phạm Thị Lan (tenant_id=4, phòng 301)
4 turns: khiếu nại tiền điện → kiểm tra đồng hồ → đòi giảm tiền → dọa chuyển đi
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_04_test_session"


def run():
    def t1_complain_bill():
        r = chat(
            "Sao tháng này tiền điện 90 kWh mà tính 315.000đ? "
            "Rồi nước 6 khối 600.000đ nữa. Tính nhầm hay sao?",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"]
        assert any(c in ans for c in "0123456789"), f"Không thấy số tiền: {ans[:200]}"
        assert any(w in ans for w in ["315", "600", "điện", "nước"]), f"Không thấy chi tiết: {ans[:200]}"

    def t2_request_meter_check():
        r = chat(
            "Tôi yêu cầu kiểm tra đồng hồ điện nước. Bao giờ có người qua?",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["kiểm tra", "đồng hồ", "lịch", "hẹn"]), f"Không thấy kiểm tra: {ans[:200]}"

    def t3_complain_noise_and_repair():
        r = chat(
            "Tôi yêu cầu giảm tiền phòng vì ồn quá. Mà ổ cắm điện báo cả tháng "
            "rồi chưa thấy ai qua sửa. Làm ăn kiểu gì vậy?",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["xin lỗi", "xử lý", "giải quyết", "bảo trì"]), f"Không thấy xử lý: {ans[:200]}"

    def t4_threaten_move():
        r = chat(
            "Nếu không giải quyết thì tôi đi. Mà tiền tháng 5 và tháng 6 tôi nợ "
            "bao nhiêu? Bao lâu phải đóng?",
            tenant_id=4, session_id=SESSION
        )
        ans = r["answer"]
        assert any(c in ans for c in "0123456789"), f"Không thấy số nợ: {ans[:200]}"

    tests = [
        ("Turn 1: khiếu nại hoá đơn", t1_complain_bill),
        ("Turn 2: yêu cầu kiểm tra đồng hồ", t2_request_meter_check),
        ("Turn 3: đòi giảm tiền + bảo trì", t3_complain_noise_and_repair),
        ("Turn 4: dọa chuyển + hỏi nợ", t4_threaten_move),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 04 - Lan khiếu nại hoá đơn", run)
