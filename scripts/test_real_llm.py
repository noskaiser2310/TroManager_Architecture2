"""
Test LLM thật - Gọi Gemini API (hoặc OpenAI) để verify model hoạt động.

Yêu cầu:
- Đã set GEMINI_API_KEY trong .env (không in ra giá trị)
- Hoặc đã điền api_key vào config/llm_config.local.yaml

Chạy: python scripts/test_real_llm.py

LƯU Ý BẢO MẬT:
- Script này KHÔNG BAO GIỜ in ra giá trị API key (kể cả một phần)
- Tự động skip nếu key là placeholder/empty
"""

from __future__ import annotations
import asyncio
import sys
import os
import time
from pathlib import Path

# Force UTF-8 stdout/stderr for Windows console
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _is_placeholder_key(key: str) -> bool:
    """
    Check xem key có phải placeholder/empty không.
    KHÔNG BAO GIỜ log giá trị key.
    """
    if not key:
        return True
    bad_patterns = [
        "MISSING", "paste", "your-key", "your_key",
        "your password", "yourpassword", "xxx",
    ]
    key_lower = key.lower()
    for pattern in bad_patterns:
        if pattern.lower() in key_lower:
            return True
    if len(key) < 20:
        return True
    return False


async def test_flash_model():
    """Test gemma-4-26b-a4b-it với câu hỏi đơn giản."""
    from src.llm import get_llm_client, reset_clients
    from src.llm.config_loader import load_llm_config, validate_config

    print("\n" + "=" * 60)
    print("Test 1: Flash model")
    print("=" * 60)

    config = load_llm_config()
    issues = validate_config(config)
    if issues:
        print("[WARN] Config co issues:")
        for issue in issues:
            print(f"  - {issue}")

    if _is_placeholder_key(config.llm.api_key):
        print("\n[SKIP] API key chua set hoac van la placeholder.")
        print("       Set GEMINI_API_KEY that trong .env roi chay lai.")
        return False

    reset_clients()
    client = get_llm_client("flash")
    print(f"Model: {client.model_name}")
    print(f"Base URL: {config.llm.base_url}")

    try:
        start = time.time()
        response = await client.generate([
            {"role": "user", "content": "Xin chao, ban co khoe khong? Tra loi ngan gon trong 1 cau."}
        ], temperature=0.4, max_tokens=8192)
        latency = (time.time() - start) * 1000

        print(f"\n[OK] Response nhan duoc trong {latency:.0f}ms")
        print(f"  Tokens: {response.total_tokens} (prompt={response.prompt_tokens}, completion={response.completion_tokens})")
        print(f"  Finish reason: {response.finish_reason}")
        print(f"  Content: {response.content[:200]}")
        return True
    except Exception as e:
        print(f"\n[FAIL] Loi khi goi LLM: {e}")
        return False


async def test_pro_model():
    """Test gemini-3.1-flash-lite với câu hỏi phức tạp hơn."""
    from src.llm import get_llm_client, reset_clients
    from src.llm.config_loader import load_llm_config

    print("\n" + "=" * 60)
    print("Test 2: Pro model")
    print("=" * 60)

    config = load_llm_config()
    if _is_placeholder_key(config.llm.api_key):
        print("\n[SKIP] API key chua set hoac van la placeholder.")
        return False

    reset_clients()
    client = get_llm_client("pro")
    print(f"Model: {client.model_name}")

    try:
        start = time.time()
        response = await client.generate([
            {
                "role": "system",
                "content": "Ban la tro ly AI cho he thong quan ly nha tro. Tra loi bang tieng Viet, ngan gon."
            },
            {
                "role": "user",
                "content": "Mot phong tro 20m² o Ha Noi, tien thue 3.5 trieu, dien 3.5k/kWh, nuoc 25k/m³. Thang nay dung 100kWh dien va 5m³ nuoc. Phi dich vu 200k. Tinh tong tien va giai thich."
            }
        ], temperature=0.4, max_tokens=500)
        latency = (time.time() - start) * 1000

        print(f"\n[OK] Response nhan duoc trong {latency:.0f}ms")
        print(f"  Tokens: {response.total_tokens}")
        print(f"  Content:\n{response.content[:500]}")
        return True
    except Exception as e:
        print(f"\n[FAIL] Loi: {e}")
        return False


async def test_embedding():
    """Test embedding model."""
    from src.llm import get_embedding_client
    from src.llm.config_loader import load_llm_config

    print("\n" + "=" * 60)
    print("Test 3: Embedding model")
    print("=" * 60)

    config = load_llm_config()
    if _is_placeholder_key(config.embedding.api_key):
        print("\n[SKIP] API key chua set hoac van la placeholder.")
        return False

    client = get_embedding_client()
    print(f"Model: {client.model}")
    print(f"Dimension: {client.dimension}")

    try:
        start = time.time()
        vector = await client.encode("Dieu hoa phong toi bi hong, lam sao de sua?")
        latency = (time.time() - start) * 1000

        print(f"\n[OK] Embedding nhan duoc trong {latency:.0f}ms")
        print(f"  Vector length: {len(vector)}")
        print(f"  First 5 values: {vector[:5]}")
        return True
    except Exception as e:
        print(f"\n[FAIL] Loi: {e}")
        return False


async def test_semantic_similarity():
    """Test semantic similarity giữa 2 câu tiếng Việt."""
    from src.llm import get_embedding_client
    from src.llm.config_loader import load_llm_config
    import math

    print("\n" + "=" * 60)
    print("Test 4: Semantic similarity (tieng Viet)")
    print("=" * 60)

    config = load_llm_config()
    if _is_placeholder_key(config.embedding.api_key):
        print("\n[SKIP] API key chua set hoac van la placeholder.")
        return False

    client = get_embedding_client()

    pairs = [
        ("Wifi mat khau gi?", "Cho toi xin password wifi", "Tuong duong"),
        ("Wifi mat khau gi?", "Phong toi bi ngap nuoc", "Khac nhau"),
        ("Gio yen tinh la may gio?", "Khi nao thi khong duoc gay on?", "Tuong duong"),
        ("Toi muon chuyen phong", "Phong nay qua chat, cho toi doi phong khac", "Tuong duong"),
    ]

    try:
        all_texts = [t for pair in pairs for t in (pair[0], pair[1])]
        all_vectors = await client.encode_batch(all_texts)

        def cosine(v1, v2):
            dot = sum(a * b for a, b in zip(v1, v2))
            n1 = math.sqrt(sum(a * a for a in v1))
            n2 = math.sqrt(sum(b * b for b in v2))
            return dot / (n1 * n2) if n1 and n2 else 0

        print()
        for i, (q1, q2, expected) in enumerate(pairs):
            v1 = all_vectors[i * 2]
            v2 = all_vectors[i * 2 + 1]
            sim = cosine(v1, v2)

            print(f"  Sim={sim:.3f}  ({expected})")
            print(f"    Q1: {q1}")
            print(f"    Q2: {q2}")

        return True
    except Exception as e:
        print(f"\n[FAIL] Loi: {e}")
        return False


async def main():
    print("\n" + "#" * 60)
    print("# Real LLM Test - Verify model API calls work")
    print("#" * 60)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Working dir: {Path.cwd()}")

    # Check .env exists (không in nội dung)
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        size = env_file.stat().st_size
        print(f".env found: {env_file} ({size} bytes)")
    else:
        print(f"[WARN] .env not found. Tao file .env tu .env.example")

    # Check API key presence (không in giá trị)
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if _is_placeholder_key(api_key):
        print("[WARN] GEMINI_API_KEY chua set trong env shell")
        print("       Set bang cach: $env:GEMINI_API_KEY='AIza...' (PowerShell)")
        print("       Hoac dien vao file .env (se duoc load tu dong)")
    else:
        print("GEMINI_API_KEY: da duoc set trong env (khong hien thi gia tri)")

    results = []
    results.append(("Flash model", await test_flash_model()))
    results.append(("Pro model", await test_pro_model()))
    results.append(("Embedding", await test_embedding()))
    results.append(("Semantic similarity", await test_semantic_similarity()))

    # Summary
    print("\n" + "#" * 60)
    print("# SUMMARY")
    print("#" * 60)

    passed = sum(1 for _, ok in results if ok)
    total = len(results)

    for name, ok in results:
        status = "[PASS]" if ok else "[FAIL/SKIP]"
        print(f"  {status} {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[OK] Tat ca models hoat dong binh thuong!")
        return 0
    else:
        print(f"\n[WARN] Co {total - passed} test(s) failed hoac skipped")
        if passed == 0:
            print("\nHuong dan:")
            print("  1. Kiem tra .env co GEMINI_API_KEY chua placeholder")
            print("  2. Chay lai: python scripts/test_real_llm.py")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
