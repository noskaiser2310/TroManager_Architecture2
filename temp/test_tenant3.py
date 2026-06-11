import urllib.request, json, sys

# Test with tenant 3 who has paid invoice for 2026-06
body = json.dumps({"source": "web", "message": "Xem hóa đơn tháng 6 của tôi", "tenant_id": 3}).encode()
req = urllib.request.Request("http://localhost:8000/chat", data=body, headers={"Content-Type": "application/json"}, method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read())
    with open("test_tenant3.txt", "w", encoding="utf-8") as f:
        f.write(f"=== tenant 3 ===\n")
        f.write(f"Answer: {data['answer']}\n")
        f.write(f"System: {data['system_used']} | Conf: {data['confidence']}\n")
        f.write(f"Tools: {', '.join(data.get('tools_used', []))}\n")
        f.write(f"Actions: {', '.join(data.get('actions_taken', []))}\n")
        f.write(f"Latency: {data['latency_ms']}ms\n")
    print(f"OK: tenant 3 ({data['latency_ms']}ms) tools={data.get('tools_used', [])} actions={data.get('actions_taken', [])}")
except Exception as e:
    print(f"FAIL: {e}")
