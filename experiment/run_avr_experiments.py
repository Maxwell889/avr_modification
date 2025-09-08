#!/usr/bin/env python3
"""
AVR实验脚本 - 求解tests/crafted中的所有case
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

# 配置参数
TIMEOUT = 1  # 1秒超时
BASE_DIR = Path(__file__).parent.parent  # avr_modification目录
TESTS_DIR = BASE_DIR / "tests" / "crafted"
OUTPUT_DIR = Path(__file__).parent / "avr_output"
AVR_SCRIPT = BASE_DIR / "avr.py"

def find_verilog_files():
    """查找所有的Verilog文件"""
    verilog_files = []
    for root, dirs, files in os.walk(TESTS_DIR):
        for file in files:
            if file.endswith('.v'):
                verilog_files.append(Path(root) / file)
    return verilog_files

def run_avr_on_file(verilog_file):
    """
    使用AVR求解单个Verilog文件
    返回: (success, result_info)
    """
    case_name = verilog_file.stem
    case_dir = verilog_file.parent.name
    full_case_name = f"{case_dir}_{case_name}"
    
    print(f"运行AVR求解: {full_case_name}")
    
    # 构建AVR命令
    cmd = [
        "python", str(AVR_SCRIPT),
        "--timeout", str(TIMEOUT),
        "-n", full_case_name,
        "-o", str(OUTPUT_DIR),
        str(verilog_file)
    ]
    
    start_time = time.time()
    try:
        # 运行AVR
        result = subprocess.run(
            cmd, 
            cwd=BASE_DIR,
            capture_output=True, 
            text=True, 
            timeout=TIMEOUT + 5  # 给一点额外时间
        )
        end_time = time.time()
        
        runtime = end_time - start_time
        
        # 解析结果
        output = result.stdout
        stderr = result.stderr
        
        success = False
        verification_result = "unknown"
        
        # 检查输出中的结果
        if "h" in output or "safe" in output.lower():
            success = True
            verification_result = "safe"
        elif "cea" in output or "unsafe" in output.lower():
            success = True
            verification_result = "unsafe"
        elif "timeout" in output.lower() or result.returncode != 0:
            verification_result = "timeout"
        
        return success, {
            "case": full_case_name,
            "file": str(verilog_file),
            "success": success,
            "result": verification_result,
            "runtime": runtime,
            "returncode": result.returncode,
            "stdout": output,
            "stderr": stderr
        }
        
    except subprocess.TimeoutExpired:
        end_time = time.time()
        runtime = end_time - start_time
        print(f"  超时: {full_case_name}")
        return False, {
            "case": full_case_name,
            "file": str(verilog_file),
            "success": False,
            "result": "timeout",
            "runtime": runtime,
            "returncode": -1,
            "stdout": "",
            "stderr": "Timeout"
        }
    except Exception as e:
        print(f"  错误: {full_case_name} - {str(e)}")
        return False, {
            "case": full_case_name,
            "file": str(verilog_file),
            "success": False,
            "result": "error",
            "runtime": 0,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e)
        }

def main():
    print("开始AVR实验...")
    print(f"基础目录: {BASE_DIR}")
    print(f"测试目录: {TESTS_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"超时设置: {TIMEOUT}秒")
    print("-" * 50)
    
    # 查找所有Verilog文件
    verilog_files = find_verilog_files()
    print(f"找到 {len(verilog_files)} 个Verilog文件")
    
    if not verilog_files:
        print("没有找到Verilog文件!")
        return
    
    # 运行实验
    results = []
    solved_cases = []
    timeout_cases = []
    error_cases = []
    unsolved_cases = []
    
    total_files = len(verilog_files)
    
    for i, verilog_file in enumerate(verilog_files, 1):
        print(f"\n[{i}/{total_files}] ", end="")
        success, result_info = run_avr_on_file(verilog_file)
        
        results.append(result_info)
        
        if success:
            solved_cases.append(result_info)
            print(f"  ✓ 成功: {result_info['result']} ({result_info['runtime']:.2f}s)")
        else:
            if result_info['result'] == 'timeout':
                timeout_cases.append(result_info)
                print(f"  ⏱ 超时: ({result_info['runtime']:.2f}s)")
            elif result_info['result'] == 'error':
                error_cases.append(result_info)
                print(f"  ✗ 错误: {result_info.get('stderr', 'Unknown error')[:50]}")
            else:
                unsolved_cases.append(result_info)
                print(f"  ✗ 失败: {result_info['result']} ({result_info['runtime']:.2f}s)")
    
    # 保存结果
    summary = {
        "experiment": "AVR Crafted Cases",
        "timeout": TIMEOUT,
        "total_cases": len(verilog_files),
        "solved_count": len(solved_cases),
        "timeout_count": len(timeout_cases),
        "error_count": len(error_cases),
        "unsolved_count": len(unsolved_cases),
        "solved_cases": [case["case"] for case in solved_cases],
        "timeout_cases": [case["case"] for case in timeout_cases],
        "error_cases": [case["case"] for case in error_cases],
        "unsolved_cases": [case["case"] for case in unsolved_cases],
        "detailed_results": results
    }
    
    # 保存到JSON文件
    results_file = Path(__file__).parent / "avr_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # 保存简单的统计信息
    stats_file = Path(__file__).parent / "avr_stats.txt"
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write(f"AVR实验结果统计\n")
        f.write(f"================\n")
        f.write(f"总测试案例: {len(verilog_files)}\n")
        f.write(f"成功求解: {len(solved_cases)} ({len(solved_cases)/len(verilog_files)*100:.1f}%)\n")
        f.write(f"超时案例: {len(timeout_cases)} ({len(timeout_cases)/len(verilog_files)*100:.1f}%)\n")
        f.write(f"错误案例: {len(error_cases)} ({len(error_cases)/len(verilog_files)*100:.1f}%)\n")
        f.write(f"其他失败: {len(unsolved_cases)} ({len(unsolved_cases)/len(verilog_files)*100:.1f}%)\n\n")
        
        if solved_cases:
            f.write("✓ 成功求解的案例:\n")
            for case in solved_cases:
                f.write(f"  {case['case']} - {case['result']} ({case['runtime']:.2f}s)\n")
        
        if timeout_cases:
            f.write("\n⏱ 超时的案例:\n")
            for case in timeout_cases:
                f.write(f"  {case['case']} - timeout ({case['runtime']:.2f}s)\n")
        
        if error_cases:
            f.write("\n✗ 错误的案例:\n")
            for case in error_cases:
                f.write(f"  {case['case']} - error\n")
        
        if unsolved_cases:
            f.write("\n✗ 其他失败的案例:\n")
            for case in unsolved_cases:
                f.write(f"  {case['case']} - {case['result']} ({case['runtime']:.2f}s)\n")
    
    # 打印总结
    print("\n" + "="*60)
    print("🎯 AVR实验完成!")
    print("="*60)
    print(f"📊 总测试案例: {len(verilog_files)}")
    print(f"✅ 成功求解: {len(solved_cases)} ({len(solved_cases)/len(verilog_files)*100:.1f}%)")
    print(f"⏱️ 超时案例: {len(timeout_cases)} ({len(timeout_cases)/len(verilog_files)*100:.1f}%)")
    print(f"🚫 错误案例: {len(error_cases)} ({len(error_cases)/len(verilog_files)*100:.1f}%)")
    print(f"❌ 其他失败: {len(unsolved_cases)} ({len(unsolved_cases)/len(verilog_files)*100:.1f}%)")
    print(f"📄 详细结果: {results_file}")
    print(f"📈 统计文件: {stats_file}")
    
    # 列出各类案例
    if solved_cases:
        print(f"\n✅ 成功案例 ({len(solved_cases)}个):")
        for case in solved_cases[:10]:  # 最多显示10个
            print(f"  - {case['case']} ({case['result']}, {case['runtime']:.2f}s)")
        if len(solved_cases) > 10:
            print(f"  ... 还有 {len(solved_cases)-10} 个案例")
    
    if timeout_cases:
        print(f"\n⏱️ 超时案例 ({len(timeout_cases)}个):")
        for case in timeout_cases:
            print(f"  - {case['case']}")
    
    if error_cases:
        print(f"\n🚫 错误案例 ({len(error_cases)}个):")
        for case in error_cases:
            print(f"  - {case['case']}")
    
    if unsolved_cases:
        print(f"\n❌ 其他失败案例 ({len(unsolved_cases)}个):")
        for case in unsolved_cases:
            print(f"  - {case['case']} ({case['result']})")

if __name__ == "__main__":
    main()
