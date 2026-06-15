"""
existing_08: Báo hỏng tủ lạnh + rò rỉ nước — Lê Hoàng Tuấn (tenant_id=3, phòng 201)
4 turns: nhắc ticket tủ lạnh → báo thêm rò rỉ → hẹn lịch → hỏi phí sửa
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_08_test_session"


def run():
    def t1_remind_fridge():
        r = chat(
            "Anh ơi em báo tủ lạnh kêu to (TKT-2026-0003) lâu rồi "
            "mà chưa thấy ai qua. Em mất ngủ mấy đêm rồi.",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["tkt", "bảo trì", "sửa", "kiểm tra"]), f"Không thấy ticket: {ans[:200]}"

    def t2_report_leak():
        r = chat(
            "Mà ống nước dưới bồn rửa cũng bị rò rỉ. Anh cho thợ "
            "qua sửa luôn thể cả 2 được không?",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["rò rỉ", "thợ", "sửa", "cả 2"]), f"Không thấy xử lý: {ans[:200]}"

    def t3_schedule():
        r = chat(
            "Thứ 7 này em ở nhà cả ngày. Anh sắp xếp thợ qua sáng được không?",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["thứ 7", "sáng", "lịch", "được"]), f"Không thấy lịch: {ans[:200]}"

    def t4_ask_repair_fee():
        r = chat(
            "Sửa 2 cái này có mất phí không anh?",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["miễn", "phí", "bảo trì", "hao mòn"]), f"Không thấy phí: {ans[:200]}"

    tests = [
        ("Turn 1: nhắc tủ lạnh kêu", t1_remind_fridge),
        ("Turn 2: báo rò rỉ nước", t2_report_leak),
        ("Turn 3: hẹn lịch thứ 7", t3_schedule),
        ("Turn 4: hỏi phí sửa", t4_ask_repair_fee),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 08 - Tuấn báo hỏng tủ lạnh + rò rỉ nước", run)
