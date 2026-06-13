"""Generate diverse Q&A pairs from KB and populate semantic cache with real embeddings"""
import asyncio, sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
from src.llm.embedding_client import EmbeddingClient

DB_DSN = "postgresql://postgres@localhost/tromanager"

# Q&A pairs crafted from KB files — accurate, diverse, covers all domains
CACHE_ENTRIES = [
    # ── Room info ──
    ("Các phòng đang trống", "Hiện có 4 phòng trống: 103 (20m², 3.000.000đ), 202 (28m², 4.000.000đ), 203 (22m², 3.200.000đ), 303 (25m², 3.500.000đ)."),
    ("Phòng nào rẻ nhất", "Phòng rẻ nhất hiện tại là 103 (tầng 1, 20m², 3.000.000đ/tháng)."),
    ("Phòng 101 có ban công không", "Phòng 101 không có ban công. Các phòng có ban công: 102 (ban công nhỏ), 202 (ban công rộng), 302 (ban công nhỏ)."),
    ("Phòng 202 có gì đặc biệt", "Phòng 202 là phòng rộng nhất còn trống: 28m², giá 4.000.000đ/tháng, có ban công rộng, điều hòa Daikin 12000BTU, nóng lạnh năng lượng mặt trời, tủ 4 cánh, giường 1m8x2m."),

    # ── Contract / Deposit ──
    ("Đặt cọc bao nhiêu tháng", "Tiền cọc là 2 tháng tiền phòng (1 tháng cọc + 1 tháng trả trước). Khi trả phòng, nếu không vi phạm hợp đồng và phòng còn nguyên trạng, sẽ được hoàn lại 100% tiền cọc trong vòng 7 ngày làm việc."),
    ("Hoàn cọc khi nào", "Tiền cọc được hoàn trong vòng 7 ngày làm việc sau khi bạn trả phòng, bàn giao đầy đủ chìa khóa và thiết bị, không hư hại gì thêm so với biên bản bàn giao ban đầu."),
    ("Mất cọc khi nào", "Bạn sẽ bị mất tiền cọc nếu: tự ý chấm dứt hợp đồng trước hạn (mất tối đa 50%), làm hư hỏng thiết bị nội thất trong phòng, không thanh toán các khoản nợ tồn đọng, hoặc vi phạm nội quy nhà trọ."),
    ("Thủ tục gia hạn hợp đồng", "Bạn cần báo trước ít nhất 30 ngày trước ngày hết hạn. Điều kiện: không vi phạm nội quy, không nợ tiền thuê. Giá thuê mới có thể tăng 5-10% tuỳ thị trường, khách ở lâu dài có ưu đãi giảm thêm."),
    ("Chấm dứt hợp đồng sớm", "Báo trước tối thiểu 30 ngày, thanh toán đầy đủ đến ngày chấm dứt, trả phòng nguyên trạng. Có thể mất tối đa 50% tiền cọc."),

    # ── Payment ──
    ("Hạn đóng tiền phòng", "Hàng tháng, thanh toán trước ngày 05 của tháng thuê. Ví dụ: tiền tháng 6 phải đóng trước ngày 05/06. Có thể chuyển khoản Vietcombank, tiền mặt hoặc Momo/ZaloPay."),
    ("Số tài khoản Vietcombank", "Ngân hàng Vietcombank, số tài khoản 1234567890, chủ tài khoản Đặng Văn Nhuận. Nội dung chuyển khoản: TT phong [số phòng] thang [MM/YYYY]."),
    ("Phí phạt trễ hạn", "Trễ 1-3 ngày: nhắc nhở qua Zalo. Trễ 4-7 ngày: phí 50.000đ. Trễ 8-14 ngày: phí 100.000đ + cảnh cáo. Trên 14 ngày: xem xét chấm dứt hợp đồng."),
    ("Tiền điện tính thế nào", "Tiền điện = số kWh × 3.500đ. Chỉ số được ghi vào ngày 25 hàng tháng. Hoá đơn chi tiết được gửi qua Zalo ngày 27-28."),
    ("Tiền nước tính thế nào", "Tiền nước = số m³ × 100.000đ. Chỉ số được ghi cùng ngày với điện (ngày 25 hàng tháng)."),
    ("Phí dịch vụ gồm những gì", "Phí dịch vụ 50.000đ/tháng bao gồm: rác, wifi, vệ sinh chung khu vực hành lang và cầu thang."),

    # ── Maintenance / Repair ──
    ("Báo hỏng điều hòa", "Gửi tin nhắn Zalo 0901-234-567 hoặc vào mục Báo sửa chữa trên app. Sự cố hỏng điều hòa thuộc loại bình thường, xử lý trong 24h. Nếu hỏng tự nhiên, nhà trọ chịu phí 100%."),
    ("Số điện thợ sửa chữa", "Liên hệ quản lý qua Zalo 0901-234-567 để được điều phối thợ. Không tự ý gọi thợ bên ngoài nếu chưa được phép."),
    ("Hỏng vòi nước gọi ai", "Báo qua Zalo 0901-234-567. Vòi nước rỉ là sự cố bình thường, xử lý trong 24h, nhà trọ chịu phí."),
    ("Trường hợp khẩn cấp về điện", "Nếu có sự cố về điện như chập điện, mất điện hoàn toàn, gọi ngay 0901-234-567 (24/7). Đội kỹ thuật sẽ có mặt trong 2h."),

    # ── Rules ──
    ("Giờ yên tĩnh", "Khung giờ yên tĩnh tuyệt đối là 22:00 - 06:00 (Thứ 2-Thứ 6) và 22:00 - 07:00 (Cuối tuần). Không hát karaoke, không hội họp đông người, không kéo lê đồ đạc."),
    ("Giờ đóng cổng", "Cổng chính đóng lúc 23:00. Sau 23:00 vui lòng đi cổng phụ và tự khóa cổng lại. Khách qua đêm phải đăng ký trước với quản lý."),
    ("Gửi xe máy bao nhiêu", "Phí gửi xe máy là 100.000đ/tháng. Xe điện là 150.000đ/tháng (đã bao gồm sạc). Khu để xe ở tầng hầm, ra vào 24/7. Mỗi phòng được gửi tối đa 2 xe."),
    ("Có được nuôi thú cưng không", "Vui lòng thông báo trước với quản lý nếu bạn muốn nuôi thú cưng. Một số phòng có thể được phép nuôi thú nhỏ (dưới 5kg) với điều kiện đảm bảo vệ sinh và không ảnh hưởng đến người khác."),
    ("Khách đến chơi có được ngủ lại không", "Khách qua đêm phải đăng ký trước với quản lý. Không được tự ý cho người lạ ở lại qua đêm mà không báo. Vi phạm có thể bị phạt hoặc chấm dứt hợp đồng."),

    # ── Facilities ──
    ("Wifi mật khẩu", "Mật khẩu wifi được cấp riêng khi bạn nhận phòng. Tên mạng: TROHAIDANG_5G hoặc TROHAIDANG_2.4G. Nếu quên mật khẩu, liên hệ quản lý 0901-234-567."),
    ("Máy giặt dùng giờ nào", "Máy giặt khu vực chung được sử dụng từ 07:00 - 22:00 hàng ngày. Không giặt sau 22:00 để tránh ồn. Phí giặt: 10.000đ/lần (tự phục vụ)."),
    ("Có chỗ để xe đạp không", "Có, khu để xe tầng hầm có chỗ để xe đạp miễn phí. Vui lòng để đúng khu vực quy định, không để xe đạp ở hành lang hay trước cửa phòng."),

    # ── Moving in/out ──
    ("Thủ tục thuê phòng mới", "Bước 1: Xem phòng trống. Bước 2: Chuẩn bị hồ sơ (CCCD, sổ hộ khẩu, ảnh 3x4, giấy xác nhận công việc). Bước 3: Đặt cọc 2 tháng. Bước 4: Ký hợp đồng. Bước 5: Nhận phòng + bàn giao thiết bị."),
    ("Thủ tục trả phòng", "Báo trước 30 ngày. Thanh toán hết các khoản nợ. Bàn giao phòng sạch sẽ, đầy đủ thiết bị. Ký biên bản thanh lý. Nhận lại cọc trong 7 ngày làm việc."),
    ("Cần chuẩn bị gì khi xem phòng", "Mang theo CCCD để đăng ký nếu ưng. Có thể xem nhiều phòng để so sánh. Lịch xem: sáng 9h-11h, chiều 14h-17h (thứ 2-thứ 7). Xem phòng miễn phí."),
]


async def main():
    embed = EmbeddingClient()
    conn = await asyncpg.connect(DB_DSN)

    print("Adding {} cache entries with real embeddings...".format(len(CACHE_ENTRIES)))
    added = 0

    for i, (query, response) in enumerate(CACHE_ENTRIES):
        text = query + ' ' + response
        try:
            vec = await embed.encode(text)
            # Check if query already exists
            existing = await conn.fetchval(
                "SELECT cache_id FROM semantic_cache WHERE query_text = $1", query
            )
            if existing:
                await conn.execute(
                    "UPDATE semantic_cache SET query_embedding = $1::vector, response_text = $2 WHERE cache_id = $3",
                    str(vec), response, existing
                )
            else:
                await conn.execute(
                    "INSERT INTO semantic_cache (query_text, query_embedding, response_text) VALUES ($1, $2::vector, $3)",
                    query, str(vec), response
                )
            added += 1
            print("  [{}/{}] {}".format(added, len(CACHE_ENTRIES), query[:50]))
        except Exception as e:
            print("  [{}/{}] {} -> ERROR: {}".format(i+1, len(CACHE_ENTRIES), query[:40], e))

    total = await conn.fetchval("SELECT COUNT(*) FROM semantic_cache")
    print("\nDone! {} entries added. Total cache: {} entries.".format(added, total))

    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
