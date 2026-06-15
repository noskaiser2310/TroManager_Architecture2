"""Deep investigation tests for security audit findings."""

import asyncio
import httpx
import json

BASE = "http://localhost:8000"

async def test_tenant_access():
    print("=" * 70)
    print("DEEP TEST: Tenant data access across sessions")
    print("=" * 70)
    
    async with httpx.AsyncClient(base_url=BASE, timeout=60) as c:
        tests = [
            ("Guest - ask for room 101 invoice", {
                'source': 'api', 'message': 'Xem hoa don thang 6 cua phong 101', 'tenant_id': None
            }),
            ("Guest - ask for tenant 1 data", {
                'source': 'api', 'message': 'Toi muon xem hoa don cua khach thue so 1', 'tenant_id': None
            }),
            ("Spoof tenant_id=1", {
                'source': 'api', 'message': 'Xem hoa don cua toi', 'tenant_id': 1
            }),
            ("Direct billing with tenant_id=1", {
                'source': 'api', 'message': 'Hoa don tien dien thang nay', 'tenant_id': 1
            }),
            ("Ask about debt with tenant_id=1", {
                'source': 'api', 'message': 'Toi con no bao nhieu tien?', 'tenant_id': 1
            }),
            ("Guest asks about any tenant's invoice", {
                'source': 'api', 'message': 'Xem hoa don cua Minh', 'tenant_id': None
            }),
        ]
        
        for label, payload in tests:
            try:
                r = await c.post('/chat', json=payload)
                data = r.json()
                ans = data.get('answer', '')
                sys_used = data.get('system_used', '')
                tools = data.get('tools_used', [])
                print(f"\n[{label}]")
                print(f"  system={sys_used}, tools={tools}")
                
                # Check if contains real data
                money_indicators = ['VND', 'd', 'trieu', 'nghin', 'dong', 'tien phong', 'tien dien', 'tien nuoc']
                has_data = any(k in ans for k in money_indicators)
                has_numbers = any(c.isdigit() for c in ans)
                
                if has_data and has_numbers:
                    print(f"  ** WARNING: Answer contains financial data! **")
                elif 'Khong tim thay' in ans:
                    print(f"  INFO: No data found (expected for guest)")
                else:
                    print(f"  GUARDRAIL: Fallback message")
                print(f"  Answer: {ans[:150]}")
            except Exception as e:
                print(f"\n[{label}] ERROR: {e}")


async def test_admin_approval_flow():
    print("\n" + "=" * 70)
    print("DEEP TEST: Admin approval flow without auth")
    print("=" * 70)
    
    async with httpx.AsyncClient(base_url=BASE, timeout=10) as c:
        # List all approvals
        r = await c.get("/admin/approvals")
        data = r.json()
        print(f"Approvals list: count={data.get('count', 0)}")
        for app in data.get('approvals', []):
            print(f"  ID={app['approval_id']}, tool={app.get('tool_name')}, status={app.get('status')}, "
                  f"tenant_id={app.get('tenant_id')}")
        
        # Try approving with arbitrary reviewer
        if data.get('approvals'):
            app_id = data['approvals'][0]['approval_id']
            print(f"\nTrying to approve #{app_id} with reviewer_id=9999...")
            r2 = await c.post(f"/admin/approvals/{app_id}/approve",
                             json={"reviewer_id": 9999})
            print(f"  Result: {r2.status_code} - {r2.text[:200]}")


async def test_zalo_webhook():
    print("\n" + "=" * 70)
    print("DEEP TEST: Zalo webhook access control")
    print("=" * 70)
    
    async with httpx.AsyncClient(base_url=BASE, timeout=10) as c:
        # Test without any signature header
        r = await c.post("/webhook/zalo", json={
            "event_name": "user_send_text",
            "sender": {"id": "attacker-user-id"},
            "message": {"text": "Xin chao"}
        })
        print(f"Without signature: {r.status_code}")
        if r.status_code == 200:
            print(f"  SECURITY ISSUE: Webhook accepts requests without signature!")
            print(f"  Response: {r.text[:150]}")
        elif r.status_code == 401:
            print(f"  Protected: signature required")
        
        # Test with fake signature
        r = await c.post("/webhook/zalo", 
            json={
                "event_name": "user_send_text",
                "sender": {"id": "attacker-user-id-2"},
                "message": {"text": "Hello"}
            },
            headers={"X-Zalo-Signature": "fake_signature_12345"}
        )
        print(f"With fake signature: {r.status_code}")
        if r.status_code == 200:
            print(f"  SECURITY ISSUE: Fake signature accepted!")
        elif r.status_code == 401:
            print(f"  Protected: invalid signature rejected")


async def test_kb_write_access():
    print("\n" + "=" * 70)
    print("DEEP TEST: KB router write access")
    print("=" * 70)
    
    async with httpx.AsyncClient(base_url=BASE, timeout=10) as c:
        # Try creating a file
        print("Attempting to create file via POST /api/kb/file...")
        r = await c.post("/api/kb/file", json={
            "path": "test_write_by_attacker.md",
            "content": "# Created by security audit\nThis should not be possible without auth."
        })
        print(f"  Create file: Status={r.status_code}")
        result = r.json() if r.text else {}
        print(f"  Response: {result}")
        
        if r.status_code == 200:
            print("  SECURITY ISSUE: File created successfully without auth!")
        
        # Try reading it back
        r2 = await c.get("/api/kb/file", params={"path": "test_write_by_attacker.md"})
        print(f"  Read back: Status={r2.status_code}")
        if r2.status_code == 200:
            print(f"  Content: {r2.json().get('content', '')[:100]}")
        
        # Clean up
        r3 = await c.delete("/api/kb/file", params={"path": "test_write_by_attacker.md"})
        print(f"  Cleanup delete: Status={r3.status_code}")
        
        # List files to show impact
        r4 = await c.get("/api/kb/")
        files = r4.json() if r4.status_code == 200 else []
        print(f"\nCurrent KB files ({len(files)}):")
        for f in files:
            print(f"  - {f['path']} ({f.get('size', 0)} bytes)")


async def main():
    await test_tenant_access()
    await test_admin_approval_flow()
    await test_zalo_webhook()
    await test_kb_write_access()
    
    print("\n" + "=" * 70)
    print("Deep investigation complete.")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
