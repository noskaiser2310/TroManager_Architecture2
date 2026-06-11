import asyncio, asyncpg

async def test():
    conn = await asyncpg.connect("postgresql://postgres@localhost:5432/tromanager")
    rows = await conn.fetch("SELECT tenant_id, invoice_month, total_amount, status FROM invoices ORDER BY tenant_id, invoice_month")
    for r in rows:
        print(f'tenant={r["tenant_id"]}, month={r["invoice_month"]}, amount={r["total_amount"]}, status={r["status"]}')
    await conn.close()

asyncio.run(test())
