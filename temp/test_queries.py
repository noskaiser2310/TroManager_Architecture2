import urllib.request, json, sys

tests = [
    ("Danh sách tất cả phòng trọ", "ROOM LIST"),
    ("Tôi muốn xem hóa đơn của tôi", "INVOICE"),
    ("Tạo nhắc nhở đóng tiền nhà", "REMINDER"),
    ("Liệt kê khách thuê", "TENANT LIST"),
    ("Thông tin phòng 101", "ROOM 101"),
]

for msg, label in tests:
    body = json.dumps({"source": "web", "message": msg, "tenant_id": 1}).encode()
    req = urllib.request.Request("http://localhost:8000/chat", data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        with open(f"test_result_{label}.txt", "w", encoding="utf-8") as f:
            f.write(f"=== {label}: {msg} ===\n")
            f.write(f"Answer: {data['answer']}\n")
            f.write(f"System: {data['system_used']} | Conf: {data['confidence']}\n")
            f.write(f"Tools: {', '.join(data.get('tools_used', []))}\n")
            f.write(f"Actions: {', '.join(data.get('actions_taken', []))}\n")
            f.write("---\n")
        print(f"OK: {label}")
    except Exception as e:
        with open(f"test_result_{label}.txt", "w", encoding="utf-8") as f:
            f.write(f"=== {label}: {msg} ===\nERROR: {e}\n")
        print(f"FAIL: {label} - {e}")
    sys.stdout.flush()
