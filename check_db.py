import asyncpg, asyncio, os, sys
sys.stdout.reconfigure(encoding='utf-8')

async def check():
    conn = await asyncpg.connect(
        host=os.environ.get('DB_HOST','localhost'),
        port=int(os.environ.get('DB_PORT','5432')),
        user=os.environ.get('DB_USER','postgres'),
        password=os.environ.get('DB_PASSWORD',''),
        database=os.environ.get('DB_NAME','tromanager')
    )
    rooms = await conn.fetch('SELECT room_id, room_number, floor, area_m2, monthly_rent, amenities FROM rooms ORDER BY room_id')
    print('=== ROOMS ===')
    for r in rooms:
        rid = r["room_id"]
        rn = r["room_number"]
        fl = r["floor"]
        area = r["area_m2"]
        rent = r["monthly_rent"]
        print(f'  Room {rid}: # {rn} T{fl} - {area}m2 - {rent:,.0f}d')
        if r["amenities"]:
            print(f'    Amenities: {r["amenities"]}')
    
    tenants = await conn.fetch('SELECT tenant_id, full_name, room_id, tone_preference FROM user_profiles ORDER BY tenant_id')
    print()
    print('=== TENANTS ===')
    for t in tenants:
        tid = t["tenant_id"]
        nm = t["full_name"]
        rid = t["room_id"]
        tone = t["tone_preference"]
        print(f'  # {tid}: {nm} - Room {rid} - Tone: {tone}')
    
    await conn.close()

asyncio.run(check())
