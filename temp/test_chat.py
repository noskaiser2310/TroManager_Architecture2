import urllib.request, json, sys, time

tests = [
    (2, "Phòng 101 còn trống không?"),
    (3, "Hóa đơn tháng này của tôi bao nhiêu?"),
    (4, "Có bao nhiêu khách thuê đang ở?"),
    (5, "Nhắc tôi đóng tiền nhà cuối tháng"),
    (6, "Tôi là ai?"),
    (7, "Chủ trọ là ai?"),
]

for n, msg in tests:
    body = json.dumps({"source": "web", "message": msg, "tenant_id": 1}).encode()
    print(f"=== TEST {n}: {msg} ===")
    try:
        req = urllib.request.Request("http://localhost:8000/chat", data=body, headers={"Content-Type": "application/json"}, method="POST")
        t0 = time.time()
        resp = urllib.request.urlopen(req, timeout=30)
        t1 = time.time()
        data = json.loads(resp.read())
        print(f"System: {data['system_used']} | Conf: {data['confidence']} | {(t1-t0)*1000:.0f}ms")
        print(f"Answer: {data['answer']}")
        if data.get('tools_used'):
            print(f"Tools: {', '.join(data['tools_used'])}")
        if data.get('session_id'):
            print(f"Session: {data['session_id']}")
    except Exception as e:
        print(f"ERROR: {e}")
    print("---")
    sys.stdout.flush()
