"""Test if query_policies (RAG) tool works directly."""
import asyncio, sys
sys.stdout.reconfigure(encoding='utf-8')

async def test():
    from src.tools.knowledge_tools import query_policies
    
    tests = [
        "Phòng 101 giá bao nhiêu?",
        "Phương thức thanh toán tiền nhà",
        "Tiền đặt cọc",
        "Gia hạn hợp đồng",
        "Giờ giấc yên tĩnh",
        "Sửa điều hòa",
    ]
    for q in tests:
        result = await query_policies(query=q)
        print(f"\n=== Query: {q} ===")
        print(f"Result (first 300): {result[:300]}")

asyncio.run(test())
