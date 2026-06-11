"""
Setup helper - Khởi tạo môi trường dev nhanh.

Usage:
  python scripts/setup_env.py
"""

from __future__ import annotations
import shutil
import sys
from pathlib import Path

# Force UTF-8 stdout/stderr for Windows console
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main():
    print("=" * 60)
    print("TroManager Environment Setup")
    print("=" * 60)
    print(f"Project root: {PROJECT_ROOT}\n")
    
    # 1. Check Python version
    py_version = sys.version_info
    print(f"Python version: {py_version.major}.{py_version.minor}.{py_version.micro}")
    if py_version < (3, 11):
        print("[WARN] Recommended Python 3.11+. Một số features có thể không hoạt động.")
    
    # 2. Create .env from .env.example if not exists
    env_file = PROJECT_ROOT / ".env"
    env_example = PROJECT_ROOT / ".env.example"
    
    if env_file.exists():
        print(f"\n[OK] .env đã tồn tại: {env_file}")
    elif env_example.exists():
        shutil.copy(env_example, env_file)
        print(f"\n[CREATED] Đã tạo .env từ .env.example")
        print(f"   [ACTION REQUIRED] Điền GEMINI_API_KEY và các giá trị khác vào {env_file}")
    else:
        print(f"\n[FAIL] .env.example không tồn tại!")
        return 1
    
    # 3. Create llm_config.local.yaml from template if not exists
    llm_local = PROJECT_ROOT / "config" / "llm_config.local.yaml"
    llm_template = PROJECT_ROOT / "config" / "llm_config.yaml"
    
    if llm_local.exists():
        print(f"[OK] llm_config.local.yaml đã tồn tại")
    elif llm_template.exists():
        shutil.copy(llm_template, llm_local)
        print(f"[CREATED] Đã tạo config/llm_config.local.yaml từ template")
        print(f"   [ACTION REQUIRED] Điền API key hoặc set trong .env")
    else:
        print(f"[FAIL] config/llm_config.yaml không tồn tại!")
    
    # 4. Create knowledge base dir if not exists
    kb_dir = PROJECT_ROOT / "knowledge_base"
    if kb_dir.exists():
        md_count = len(list(kb_dir.rglob("*.md")))
        print(f"[OK] Knowledge base: {md_count} file .md")
    else:
        print(f"[FAIL] Knowledge base dir không tồn tại: {kb_dir}")
    
    # 5. Check for system prompts
    prompts_dir = PROJECT_ROOT / "config" / "prompts"
    if not prompts_dir.exists() or not list(prompts_dir.glob("*.txt")):
        print(f"\n[WARN] Chưa có system prompts ở {prompts_dir}")
        print("   Sẽ tự tạo khi chạy lần đầu. Hoặc copy từ template nếu có.")
    
    # 6. Summary
    print("\n" + "=" * 60)
    print("Next steps:")
    print("=" * 60)
    print("1. Điền GEMINI_API_KEY vào file .env")
    print("2. (Optional) Cấu hình DATABASE_URL, ZALO_ACCESS_TOKEN, v.v.")
    print("3. Chạy smoke test (không cần API key):")
    print("   python scripts/run_smoke_test.py")
    print("4. Chạy test thật với API key:")
    print("   python scripts/test_real_llm.py")
    print("5. Khởi động server:")
    print("   uvicorn src.main:app --reload")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
