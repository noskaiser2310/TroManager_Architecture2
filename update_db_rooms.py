import asyncpg, asyncio, os, sys
sys.stdout.reconfigure(encoding='utf-8')

async def update():
    conn = await asyncpg.connect(
        host=os.environ.get('DB_HOST','localhost'),
        port=int(os.environ.get('DB_PORT','5432')),
        user=os.environ.get('DB_USER','postgres'),
        password=os.environ.get('DB_PASSWORD','123456'),
        database=os.environ.get('DB_NAME','tromanager')
    )

    # Cập nhật amenities cho các phòng
    amenities_data = {
        1: {"giuong_1m6x2m": True, "tu_3_canh": True, "dieu_hoa": True, "nong_lanh": True, "voi_tam_kinh": True, "ban_bep": True, "cua_so": True},
        2: {"giuong_1m8x2m": True, "tu_4_canh": True, "dieu_hoa": True, "nong_lanh": True, "voi_tam_kinh": True, "ban_cong": True, "tu_lanh": True},
        3: {"giuong_1m6x2m": True, "tu_3_canh": True, "dieu_hoa": True, "nong_lanh": True, "cua_so": True},
        4: {"giuong_1m6x2m": True, "tu_3_canh": True, "dieu_hoa": True, "nong_lanh": True, "voi_tam_kinh": True, "ban_cong": True},
        5: {"giuong_1m8x2m": True, "tu_4_canh": True, "dieu_hoa": True, "nong_lanh": True, "voi_tam_kinh": True, "tu_lanh": True, "may_giat": True},
        6: {"giuong_1m6x2m": True, "tu_3_canh": True, "dieu_hoa": True, "cua_so": True},
        7: {"giuong_1m8x2m": True, "tu_4_canh": True, "dieu_hoa": True, "nong_lanh": True, "ban_cong": True, "tu_lanh": True},
        8: {"giuong_1m8x2m": True, "tu_4_canh": True, "dieu_hoa": True, "nong_lanh": True, "voi_tam_kinh": True, "may_giat": True, "tu_lanh": True},
        9: {"giuong_1m6x2m": True, "tu_3_canh": True, "dieu_hoa": True, "nong_lanh": True, "cua_so": True},
    }

    import json
    for room_id, amenities in amenities_data.items():
        await conn.execute(
            'UPDATE rooms SET amenities = $1 WHERE room_id = $2',
            json.dumps(amenities, ensure_ascii=False), room_id
        )
        print(f'  Updated amenities for room {room_id}')

    await conn.close()
    print('Done!')

asyncio.run(update())
