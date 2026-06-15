"""
existing_20: Đăng ký nhận thông báo bảo trì định kỳ — Trần Thị Hoa (tenant_id=2, phòng 102)
4 turns: hỏi lịch bảo trì → ĐK nhận báo trước → hỏi hạng mục → yêu cầu KT bình nóng lạnh
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_20_test_session"


def run():
    def t1_maintenance_schedule():
        r = chat(
            "Bên mình có lịch bảo trì định kỳ không? Hồi tháng 4 điều hòa hỏng giữa mùa nóng chịu không nổi.",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["bảo trì", "lịch", "định kỳ"]), f"Không thấy lịch bảo trì: {ans[:200]}"

    def t2_register_notice():
        r = chat(
            "Nếu có lịch bảo trì em báo chị trước 1 tuần qua app nhé. Để chị thu xếp công việc.",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["tuần", "ngày", "báo", "trước"]), f"Không thấy xác nhận: {ans[:200]}"

    def t3_maintenance_items():
        r = chat(
            "Bảo trì có kiểm tra máy lạnh, tủ lạnh, bình nóng lạnh không? Hay chỉ thang máy với chung thôi?",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["máy lạnh", "thiết bị", "phòng", "điện"]), f"Không thấy hạng mục: {ans[:200]}"

    def t4_request_water_heater():
        r = chat(
            "Vậy lần tới bảo trì cho thợ kiểm tra bình nóng lạnh phòng em luôn nhé. Nước ấm yếu quá.",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["tiếp nhận", "ghi nhận", "thợ", "ticket"]), f"Không thấy tiếp nhận: {ans[:200]}"

    tests = [
        ("Turn 1: hỏi lịch bảo trì", t1_maintenance_schedule),
        ("Turn 2: đăng ký báo trước", t2_register_notice),
        ("Turn 3: hỏi hạng mục bảo trì", t3_maintenance_items),
        ("Turn 4: yêu cầu kiểm tra bình nóng lạnh", t4_request_water_heater),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 20 - Hoa đăng ký bảo trì", run)
