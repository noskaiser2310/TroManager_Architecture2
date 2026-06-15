"""
Run all 20 scenario tests sequentially, save results to corresponding .md files.
Usage: python run_all_scenarios.py
"""

import subprocess
import sys
import os
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCENARIO_DIR = os.path.join(BASE_DIR, "scenarios")
MD_DIR = os.path.join(BASE_DIR, "..", "test_scenarios")
CONDA_ENV = "tromanager"
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

# Map test file -> md file
TEST_MD_MAP = {
    "test_existing_01.py": "existing_01_hoa_don_thang.md",
    "test_existing_02.py": "existing_02_bao_tri_khan_cap.md",
    "test_existing_03.py": "existing_03_gia_han_hop_dong.md",
    "test_existing_04.py": "existing_04_khieu_nai_hoa_don.md",
    "test_existing_05.py": "existing_05_chuyen_phong.md",
    "test_existing_06.py": "existing_06_thanh_toan_tre.md",
    "test_existing_07.py": "existing_07_cau_hoi_chinh_sach.md",
    "test_existing_08.py": "existing_08_nang_cap_noi_that.md",
    "test_existing_09.py": "existing_09_khieu_nai_tieng_on.md",
    "test_existing_10.py": "existing_10_cham_dut_hop_dong_som.md",
    "test_new_01.py": "new_01_tim_phong_gia_re.md",
    "test_new_02.py": "new_02_so_sanh_phong.md",
    "test_new_03.py": "new_03_thu_tuc_dat_coc.md",
    "test_new_04.py": "new_04_dat_lich_xem_phong.md",
    "test_new_05.py": "new_05_tinh_tong_chi_phi.md",
    "test_new_06.py": "new_06_o_ghep.md",
    "test_new_07.py": "new_07_phong_tang_tret.md",
    "test_new_08.py": "new_08_tien_nghi_internet.md",
    "test_new_09.py": "new_09_van_de_an_ninh.md",
    "test_new_10.py": "new_10_khach_cu_quay_lai.md",
    "test_existing_16.py": "existing_16_kiem_tra_thong_bao.md",
    "test_existing_17.py": "existing_17_cai_dat_gio_thong_bao.md",
    "test_existing_18.py": "existing_18_bao_hong_sms.md",
    "test_existing_19.py": "existing_19_chinh_sach_thong_bao.md",
    "test_existing_20.py": "existing_20_nhac_bao_tri_dinh_ky.md",
    "test_new_16.py": "new_16_hoi_vi_tri_giao_thong.md",
    "test_new_17.py": "new_17_hoi_chi_phi_dien_nuoc.md",
    "test_new_18.py": "new_18_hoi_thu_tuc_dat_phong.md",
    "test_new_19.py": "new_19_hoi_chinh_sach_hoan_coc.md",
    "test_new_20.py": "new_20_hoi_dich_vu_tien_ich.md",
}


def run_test(test_file):
    """Run a single test file, return (stdout, returncode)."""
    test_path = os.path.join(SCENARIO_DIR, test_file)
    cmd = [
        "conda", "run", "-n", CONDA_ENV, "python", test_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_DIR)
    return result.stdout + result.stderr, result.returncode


def parse_results(output):
    """Parse PASS/FAIL from test output."""
    passes = len(re.findall(r'\[PASS\]', output))
    fails = len(re.findall(r'\[FAIL\]', output))
    errors = len(re.findall(r'\[ERROR\]', output))
    
    # Extract individual test results
    results = []
    for line in output.split('\n'):
        line = line.strip()
        for status in ['[PASS]', '[FAIL]', '[ERROR]']:
            if status in line:
                test_name = line.split(status, 1)[1].strip()
                results.append((test_name, status.strip('[]')))
                break
    
    return passes, fails, errors, results, output


def append_results_to_md(md_file, test_file, output, passes, fails, errors, results):
    """Append test results to the scenario .md file."""
    md_path = os.path.join(MD_DIR, md_file)
    
    if not os.path.exists(md_path):
        md_path = os.path.join(BASE_DIR, "..", md_file)  # fallback
    
    if not os.path.exists(md_path):
        return f"KHÔNG tìm thấy {md_file}"
    
    # Build results section
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total = passes + fails + errors
    status_icon = "✅" if fails == 0 and errors == 0 else "❌"
    
    results_block = f"""

---

## Kết quả test
*Chạy lúc: {timestamp}*
*File test: `{test_file}`*

| Trạng thái | Số lượng |
|------------|----------|
| ✅ PASS    | {passes} |
| ❌ FAIL    | {fails} |
| ⚠️ ERROR  | {errors} |
| **Tổng**   | **{total}** |

**Kết luận: {status_icon} {'TẤT CẢ PASS' if fails == 0 and errors == 0 else f'{fails} FAIL / {errors} ERROR'}**

### Chi tiết từng turn
"""
    
    for test_name, status in results:
        icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "⚠️"}.get(status, "❔")
        results_block += f"- {icon} **{test_name}**: {status}\n"
    
    # Append to .md file
    with open(md_path, 'a', encoding='utf-8') as f:
        f.write(results_block)
    
    return f"✅ Đã lưu kết quả vào {md_file}"


def main():
    print("=" * 70)
    print(f"  TroManager - Chạy tất cả {len(TEST_MD_MAP)} kịch bản test")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    total_passes = 0
    total_fails = 0
    total_errors = 0
    
    for i, (test_file, md_file) in enumerate(TEST_MD_MAP.items(), 1):
        print(f"\n[{i}/{len(TEST_MD_MAP)}] Running {test_file}...")
        sys.stdout.flush()
        
        output, returncode = run_test(test_file)
        passes, fails, errors, results, full_output = parse_results(output)
        
        total_passes += passes
        total_fails += fails
        total_errors += errors
        
        # Print output
        print(output)
        
        # Save to .md
        msg = append_results_to_md(md_file, test_file, output, passes, fails, errors, results)
        print(f"  {msg}")
        sys.stdout.flush()
    
    print("\n" + "=" * 70)
    print(f"  HOÀN THÀNH: {total_passes} PASS / {total_fails} FAIL / {total_errors} ERROR")
    if total_fails == 0 and total_errors == 0:
        print(f"  🎉 TẤT CẢ {len(TEST_MD_MAP)} KỊCH BẢN ĐỀU PASS!")
    else:
        print(f"  ❌ Có {total_fails + total_errors} lỗi cần xem xét")
    print("=" * 70)


if __name__ == "__main__":
    main()
