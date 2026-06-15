"""
existing_05: Yêu cầu đổi phòng — Lê Hoàng Tuấn (tenant_id=3, phòng 201)
4 turns: hỏi chuyển phòng (muốn ban công) → xem phòng 202 → đặt lịch → hỏi thủ tục
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scenario_test_helper import test, chat, run_scenario

SESSION = "existing_05_test_session"


def run():
    def t1_ask_transfer():
        r = chat(
            "Anh ơi em muốn chuyển lên phòng có ban công. "
            "Phòng 201 thiếu ban công, quần áo phơi ẩm quá. "
            "Còn phòng trống nào có ban công không anh?",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["202", "ban công", "phòng trống"]), f"Không thấy đề xuất: {ans[:200]}"

    def t2_ask_202_details():
        r = chat(
            "Phòng 202 giá 4tr cao hơn 800k nhỉ. Nhưng 28m² rộng, ban công. "
            "Em hỏi tí: chênh lệch tính sao? Có mất phí chuyển không?",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["chênh", "phí", "chuyển", "cọc"]), f"Không thấy giải thích: {ans[:200]}"

    def t3_schedule_viewing():
        r = chat(
            "Em muốn xem phòng 202 trước. Chiều mai sau 5h được không anh?",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["xem", "lịch", "được", "mai"]) or "có" in ans, \
            f"Không xác nhận lịch: {ans[:200]}"

    def t4_transfer_procedure():
        r = chat(
            "Nếu ưng thì thủ tục chuyển sao anh? Ký hợp đồng mới hay phụ lục? "
            "Chuyển trong ngày được không?",
            tenant_id=3, session_id=SESSION
        )
        ans = r["answer"].lower()
        assert any(w in ans for w in ["thủ tục", "phụ lục", "ký", "chuyển"]), f"Không thấy thủ tục: {ans[:200]}"

    tests = [
        ("Turn 1: hỏi chuyển phòng", t1_ask_transfer),
        ("Turn 2: hỏi chi tiết phòng 202", t2_ask_202_details),
        ("Turn 3: đặt lịch xem phòng", t3_schedule_viewing),
        ("Turn 4: hỏi thủ tục chuyển", t4_transfer_procedure),
    ]
    for name, fn in tests:
        test(name, fn)


if __name__ == "__main__":
    run_scenario("Existing 05 - Tuấn đổi phòng (lên 202)", run)
