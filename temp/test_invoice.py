import urllib.request, json, sys

# Test invoice query
msg = "Tôi muốn xem hóa đơn tiền trọ của tôi"
body = json.dumps({"source": "web", "message": msg, "tenant_id": 1}).encode()
print(f"=== INVOICE TEST ===")
req = urllib.request.Request("http://localhost:8000/chat", data=body, headers={"Content-Type": "application/json"}, method="POST")
resp = urllib.request.urlopen(req, timeout=30)
data = json.loads(resp.read())
print(f"Answer: {data['answer']}")
print(f"Conf: {data['confidence']} | Sys: {data['system_used']}")
print(f"Tools: {data.get('tools_used', [])}")
print(f"Actions: {data.get('actions_taken', [])}")
print("---")

# Test reminder  
msg2 = "Tạo nhắc nhở đóng tiền nhà ngày 30 hàng tháng"
body2 = json.dumps({"source": "web", "message": msg2, "tenant_id": 1}).encode()
print(f"=== REMINDER TEST ===")
req2 = urllib.request.Request("http://localhost:8000/chat", data=body2, headers={"Content-Type": "application/json"}, method="POST")
resp2 = urllib.request.urlopen(req2, timeout=30)
data2 = json.loads(resp2.read())
print(f"Answer: {data2['answer']}")
print(f"Conf: {data2['confidence']} | Sys: {data2['system_used']}")
print(f"Tools: {data2.get('tools_used', [])}")
print("---")
