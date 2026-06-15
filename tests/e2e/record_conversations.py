"""
Đọc từng file .md kịch bản, gửi từng turn lên API thật,
ghi lại câu trả lời thực tế của AI vào file .md.

Usage:
  python tests/e2e/record_conversations.py                              # all 40 files
  python tests/e2e/record_conversations.py -t existing                  # only existing_*
  python tests/e2e/record_conversations.py -t new                       # only new_*
  python tests/e2e/record_conversations.py -f existing_01 new_04        # specific files
  python tests/e2e/record_conversations.py -r 5-15                     # range 05-15 (cả 2 nhóm)
  python tests/e2e/record_conversations.py -t existing -r 1-10         # existing_01 đến existing_10
  python tests/e2e/record_conversations.py --skip-existing              # bỏ qua file đã có kết quả
  python tests/e2e/record_conversations.py --delay 3                   # delay 3s giữa các câu hỏi
"""

import os
import re
import sys
import time
import argparse
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MD_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "test_scenarios"))

# Tenant ID mapping from file prefixes
TENANT_MAP = {
    "existing_01": 1,   # Nguyễn Văn Minh
    "existing_02": 2,   # Trần Thị Hoa
    "existing_03": 5,   # Đỗ Văn Hùng
    "existing_04": 4,   # Phạm Thị Lan
    "existing_05": 3,   # Lê Hoàng Tuấn
    "existing_06": 4,   # Phạm Thị Lan
    "existing_07": 1,   # Nguyễn Văn Minh
    "existing_08": 3,   # Lê Hoàng Tuấn
    "existing_09": 2,   # Trần Thị Hoa
    "existing_10": 5,   # Đỗ Văn Hùng
    "existing_11": 1,   # Nguyễn Văn Minh
    "existing_12": 3,   # Lê Hoàng Tuấn
    "existing_13": 2,   # Trần Thị Hoa
    "existing_14": 5,   # Đỗ Văn Hùng
    "existing_15": 4,   # Phạm Thị Lan
    "existing_16": 1,   # Nguyễn Văn Minh
    "existing_17": 3,   # Lê Hoàng Tuấn
    "existing_18": 4,   # Phạm Thị Lan
    "existing_19": 5,   # Đỗ Văn Hùng
    "existing_20": 2,   # Trần Thị Hoa
}


def extract_user_questions(md_path):
    """Trích xuất user questions từ file .md (các dòng bắt đầu bằng >)."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Tìm tất cả các dòng quoted (>) - đó là câu hỏi của user
    questions = re.findall(r'^>\s*"(.+?)"', content, re.MULTILINE)
    if not questions:
        questions = re.findall(r'^>\s*(.+?)$', content, re.MULTILINE)
        questions = [q.strip('"').strip('''''').strip() for q in questions]

    return questions


def send_question(question, tenant_id=None, session_id=None, delay=6):
    """Gửi câu hỏi lên API và trả về câu trả lời."""
    time.sleep(delay)
    payload = {
        "source": "scenario_recording",
        "message": question,
    }
    if tenant_id is not None:
        payload["tenant_id"] = tenant_id
    if session_id:
        payload["session_id"] = session_id

    try:
        r = requests.post(f"{BASE_URL}/chat", json=payload, timeout=120)
        if r.status_code == 200:
            data = r.json()
            return data.get("answer", "[Không có answer trong response]")
        else:
            return f"[Lỗi HTTP {r.status_code}: {r.text[:200]}]"
    except requests.exceptions.ConnectionError:
        return "[Lỗi: Không kết nối được server. Chạy 'python -m src.main' trước.]"
    except Exception as e:
        return f"[Lỗi: {e}]"


def save_conversation_to_md(md_path, turns_data, base_name):
    """Ghi hội thoại thực tế vào file .md."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Xoá mọi phần kết quả cũ (có hoặc không có --- separator)
    # Pattern 1: có --- separator
    content = re.sub(r'\n---\s*\n\s*## Kết quả hội thoại thực tế\n.*', '\n', content, flags=re.DOTALL)
    # Pattern 2: không có ---
    content = re.sub(r'\n## Kết quả hội thoại thực tế\n.*', '\n', content, flags=re.DOTALL)
    content = content.rstrip().rstrip('-').rstrip()

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result_block = f"""

---

## Kết quả hội thoại thực tế
*Chạy lúc: {timestamp}*

"""
    for i, turn in enumerate(turns_data, 1):
        result_block += f"""**Turn {i}**
- **Câu hỏi**: "{turn['question']}"
- **Câu trả lời của AI**: {turn['answer']}

"""

    with open(md_path, 'a', encoding='utf-8') as f:
        f.write(result_block)
    return True


def has_existing_results(md_path):
    """Kiểm tra file .md đã có kết quả hội thoại chưa."""
    with open(md_path, 'r', encoding='utf-8') as f:
        return '## Kết quả hội thoại thực tế' in f.read()


def process_file(md_file, delay=6):
    """Xử lý 1 file .md: gửi câu hỏi, ghi kết quả."""
    md_path = os.path.join(MD_DIR, md_file)
    if not os.path.exists(md_path):
        print(f"  ❌ Không tìm thấy {md_path}")
        return False

    # Xác định tenant từ prefix existing_NN
    base_name = md_file.replace('.md', '')
    prefix = '_'.join(base_name.split('_')[:2]) if base_name.startswith('existing') else base_name.rsplit('_', 1)[0]
    tenant_id = TENANT_MAP.get(prefix, None)

    # Trích xuất câu hỏi
    questions = extract_user_questions(md_path)
    if not questions:
        print(f"  ⚠️ Không tìm thấy câu hỏi nào trong {md_file}")
        return False

    print(f"\n  📤 Gửi {len(questions)} turn cho {md_file} (tenant_id={tenant_id})...")

    session_id = f"record_{base_name}"
    turns_data = []

    for i, question in enumerate(questions, 1):
        print(f"    Turn {i}/{len(questions)}: {question[:60]}...")
        answer = send_question(question, tenant_id=tenant_id, session_id=session_id, delay=delay)
        print(f"      → {answer[:80]}...")
        turns_data.append({"question": question, "answer": answer})

    # Ghi vào file
    save_conversation_to_md(md_path, turns_data, base_name)
    print(f"  ✅ Đã lưu hội thoại vào {md_file}")
    return True


def parse_args():
    parser = argparse.ArgumentParser(
        description="TroManager - Ghi lại hội thoại thực tế từ API vào file .md"
    )
    parser.add_argument(
        "-t", "--type", choices=["existing", "new"],
        help="Chỉ chạy kịch bản existing hoặc new"
    )
    parser.add_argument(
        "-f", "--files", nargs="+",
        help="Danh sách kịch bản cụ thể (vd: existing_01 new_04)"
    )
    parser.add_argument(
        "-r", "--range",
        help="Khoảng số kịch bản (vd: 1-10 chạy từ 01 đến 10)"
    )
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Bỏ qua file đã có kết quả hội thoại"
    )
    parser.add_argument(
        "--delay", type=float, default=6,
        help="Delay giữa các câu hỏi (giây, mặc định 6)"
    )
    return parser.parse_args()


def filter_files(args):
    """Lọc danh sách file .md theo arguments."""
    all_files = sorted(
        f for f in os.listdir(MD_DIR)
        if f.endswith('.md') and (f.startswith("existing_") or f.startswith("new_"))
    )

    if not all_files:
        print("❌ Không tìm thấy file .md nào trong test_scenarios/")
        return []

    # Lọc theo --type
    if args.type:
        all_files = [f for f in all_files if f.startswith(args.type + "_")]

    # Lọc theo --files
    if args.files:
        selected = []
        for name in args.files:
            # Tìm file khớp (có thể khớp prefix như existing_01 → existing_01_hoa_don_thang.md)
            matches = [f for f in all_files if f.startswith(name)]
            if not matches:
                print(f"  ⚠️ Không tìm thấy file nào khớp '{name}'")
            selected.extend(matches)
        all_files = sorted(set(selected))

    # Lọc theo --range
    if args.range:
        try:
            start_n, end_n = args.range.split("-")
            start_n, end_n = int(start_n), int(end_n)
        except ValueError:
            print(f"  ❌ --range phải có dạng 'start-end' (vd: 1-10)")
            return []

        def in_range(f):
            # Trích số từ tên file (existing_13_cap_nhat... → 13)
            parts = f.split("_")
            if len(parts) >= 2:
                try:
                    n = int(parts[1])
                    return start_n <= n <= end_n
                except ValueError:
                    return False
            return False

        all_files = sorted([f for f in all_files if in_range(f)])

    # Lọc theo --skip-existing
    if args.skip_existing:
        skipped = []
        kept = []
        for f in all_files:
            md_path = os.path.join(MD_DIR, f)
            if has_existing_results(md_path):
                skipped.append(f)
            else:
                kept.append(f)
        if skipped:
            print(f"  ⏭️ Bỏ qua {len(skipped)} file đã có kết quả: {', '.join(skipped)}")
        all_files = kept

    return all_files


def main():
    args = parse_args()
    md_files = filter_files(args)

    if not md_files:
        print("❌ Không có file nào để xử lý.")
        return

    total_turns = sum(len(extract_user_questions(os.path.join(MD_DIR, f))) for f in md_files)
    estimated_secs = total_turns * (args.delay + 5)

    print("=" * 70)
    print("  TroManager - Ghi lại hội thoại thực tế từ API")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Số file: {len(md_files)}, tổng turns: {total_turns}")
    print(f"  Delay: {args.delay}s/turn, ước tính ~{estimated_secs // 60}:{estimated_secs % 60:02d} phút")
    print("=" * 70)

    success = 0
    for md_file in md_files:
        if process_file(md_file, delay=args.delay):
            success += 1

    print(f"\n{'=' * 70}")
    print(f"  Hoàn thành: {success}/{len(md_files)} file")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
