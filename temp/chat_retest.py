import urllib.request, json, sys

tests = [
    ("Xin chào, bạn là ai?", "GREETING"),
    ("Tôi muốn xem hóa đơn của tôi", "INVOICE"),
    ("Tạo nhắc nhở đóng tiền nhà cuối tháng", "REMINDER"),
    ("Phòng 101 còn trống không?", "ROOM"),
    ("Danh sách khách thuê", "TENANTS"),
    ("Thông tin hợp đồng của tôi", "CONTRACT"),
]

for msg, label in tests:
    body = json.dumps({"source": "web", "message": msg, "tenant_id": 1}).encode()
    req = urllib.request.Request("http://localhost:8000/chat", data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        with open(f"chat_test_{label}.txt", "w", encoding="utf-8") as f:
            f.write(f"=== {label}: {msg} ===\n")
            f.write(f"Answer: {data['answer']}\n")
            f.write(f"System: {data['system_used']} | Conf: {data['confidence']}\n")
            f.write(f"Tools: {', '.join(data.get('tools_used', []))}\n")
            f.write(f"Actions: {', '.join(data.get('actions_taken', []))}\n")
            f.write(f"Latency: {data['latency_ms']}ms\n")
            f.write("---\n")
        print(f"OK: {label} ({data['latency_ms']}ms)")
    except Exception as e:
        with open(f"chat_test_{label}.txt", "w", encoding="utf-8") as f:
            f.write(f"=== {label}: {msg} ===\nERROR: {e}\n")
        print(f"FAIL: {label} - {e}")
    sys.stdout.flush()
