"""
existing_10: Chấm dứt hợp đồng sớm — Đỗ Văn Hùng (tenant_id=5, phòng 302)
4 turns: báo nghỉ sớm → hỏi phí phạt → đề xuất người thế → hỏi checklist
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_10_test_session"


def run():
    def t1_notify_early_termination():
        r = chat(
            "Em chuyển công tác vào Đà Nẵng gấp, phải đi tháng 7. "
            "Hợp đồng 302 còn tới tháng 9. Chấm dứt sớm thì bị phạt sao? "
            "Có mất cọc không ạ?",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["phạt", "cọc", "hợp đồng", "chấm dứt"]), f"Không thấy phạt: {ans[:200]}"

    def t2_ask_penalty():
        r = chat(
            "Mất 1 tháng cọc (9tr) hay toàn bộ? "
            "Cần báo trước 30 ngày đúng không?",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["30", "cọc", "báo trước", "tháng"]), f"Không thấy chi tiết: {ans[:200]}"

    def t3_suggest_replacement():
        r = chat(
            "Em có ông bạn đồng nghiệp đang tìm phòng. "
            "Nếu ổng vào ở thế thì có miễn phí phạt không?",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["thế", "giới thiệu", "miễn", "giảm"]), f"Không thấy thương lượng: {ans[:200]}"

    def t4_ask_checklist():
        r = chat(
            "Checklist trả phòng gồm những gì? "
            "Còn cái bàn ọp ẹp (TKT-0009) có ảnh hưởng không?",
            tenant_id=5, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["bàn giao", "checklist", "dọn", "chìa khoá"]), f"Không thấy checklist: {ans[:200]}"

    tests = [
        ("Turn 1: báo nghỉ sớm", t1_notify_early_termination),
        ("Turn 2: hỏi phí phạt", t2_ask_penalty),
        ("Turn 3: đề xuất người thế", t3_suggest_replacement),
        ("Turn 4: hỏi bàn giao", t4_ask_checklist),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 10 - Hùng chấm dứt hợp đồng sớm", run)
