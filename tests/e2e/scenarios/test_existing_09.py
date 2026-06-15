"""
existing_09: Khiếu nại tiếng ồn — Trần Thị Hoa (tenant_id=2, phòng 102)
4 turns: báo ồn → hỏi quy định → vẫn còn ồn → yêu cầu đổi phòng
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_09_test_session"


def run():
    def t1_noise_complaint():
        r = chat(
            "Tôi ở 102, tối nào cũng có nhạc ầm ĩ từ tầng trên. "
            "Tôi lên gõ cửa không ai mở. Nhờ admin xử lý.",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["yên tĩnh", "nhắc", "nội quy", "22"]), f"Không xử lý ồn: {ans[:200]}"

    def t2_ask_regulations():
        r = chat(
            "Nội quy quy định giờ yên tĩnh thế nào? "
            "Nếu tái phạm thì xử lý ra sao?",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["22", "cảnh cáo", "phạt", "lần"]), f"Không thấy nội quy: {ans[:200]}"

    def t3_still_noisy():
        r = chat(
            "Tối qua họ vẫn ồn tới 1h sáng. Admin đã nhắc nhở chưa? "
            "Tôi yêu cầu phản hồi trong hôm nay.",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["xin lỗi", "đã", "cảnh báo", "tiếp"]), f"Không thấy cập nhật: {ans[:200]}"

    def t4_request_transfer():
        r = chat(
            "Nếu kéo dài tôi yêu cầu đổi phòng yên tĩnh hơn. "
            "Còn phòng nào tầng cao hoặc cuối dãy không?",
            tenant_id=2, session_id=SESSION
        )
        ans = r["answer"]
        assert any(w in ans for w in ["202", "203", "303", "đổi", "chuyển"]), f"Không thấy phòng: {ans[:200]}"

    tests = [
        ("Turn 1: báo tiếng ồn", t1_noise_complaint),
        ("Turn 2: hỏi nội quy", t2_ask_regulations),
        ("Turn 3: vẫn còn ồn", t3_still_noisy),
        ("Turn 4: yêu cầu đổi phòng", t4_request_transfer),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 09 - Hoa khiếu nại tiếng ồn", run)
