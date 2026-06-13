import asyncio
import sys
sys.path.insert(0, ".")
from src.core.db import get_db_pool
from src.llm.config_loader import load_llm_config

async def main():
    config = load_llm_config()
    pool = await get_db_pool("postgresql://postgres:postgres@localhost:5432/tromanager")
    async with pool.acquire() as conn:
        print("Dropping schema...")
        await conn.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
        print("Running schema.sql...")
        with open('database/schema.sql', encoding='utf-8') as f:
            sql = f.read()
        await conn.execute(sql)
        print("DB Reset Done!")

if __name__ == "__main__":
    asyncio.run(main())
