#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终项目清理脚本
清理无关文件，保留核心项目代码
"""

import os
import shutil
import glob
from pathlib import Path

def cleanup_project():
    """清理项目无关文件"""
    print("🧹 开始清理项目...")
    
    # 当前目录
    project_dir = Path("/Applications/tradingagent")
    os.chdir(project_dir)
    
    removed_count = 0
    
    # 1. 清理分析结果文件
    print("📊 清理分析结果文件...")
    analysis_patterns = [
        "*分析报告*.json",
        "*测试报告*.json", 
        "*analysis*.json",
        "*backtest*.json",
        "*comprehensive*.json",
        "*evaluation*.json"
    ]
    
    for pattern in analysis_patterns:
        files = glob.glob(pattern)
        for file in files:
            try:
                os.remove(file)
                print(f"  ✅ 删除: {file}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ 删除失败: {file} - {e}")
    
    # 2. 清理临时测试脚本
    print("🧪 清理临时测试脚本...")
    test_patterns = [
        "analyze_*.py",
        "test_*.py", 
        "demo_*.py",
        "quick_*.py",
        "simple_*.py",
        "enhanced_*.py",
        "comprehensive_*.py",
        "*_analysis.py",
        "*_test.py"
    ]
    
    # 保留的核心文件
    keep_files = [
        "enhanced_agent_architecture.py",  # 核心架构
        "dongyang_simple_test.py",        # 主要测试
        "cleanup_and_security_fixes.py"   # 安全修复
    ]
    
    for pattern in test_patterns:
        files = glob.glob(pattern)
        for file in files:
            if file not in keep_files:
                try:
                    os.remove(file)
                    print(f"  ✅ 删除: {file}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ❌ 删除失败: {file} - {e}")
    
    # 3. 清理日志文件
    print("📝 清理日志文件...")
    log_patterns = ["*.log", "*.txt"]
    
    for pattern in log_patterns:
        files = glob.glob(pattern)
        for file in files:
            # 保留重要的README文件
            if not file.startswith("README"):
                try:
                    os.remove(file)
                    print(f"  ✅ 删除: {file}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ❌ 删除失败: {file} - {e}")
    
    # 4. 清理Excel和图片文件
    print("📊 清理Excel和图片文件...")
    media_patterns = ["*.xlsx", "*.png", "*.jpg"]
    
    for pattern in media_patterns:
        files = glob.glob(pattern)
        for file in files:
            try:
                os.remove(file)
                print(f"  ✅ 删除: {file}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ 删除失败: {file} - {e}")
    
    # 5. 清理数据库文件
    print("🗄️ 清理数据库文件...")
    db_files = glob.glob("*.db")
    for file in db_files:
        try:
            os.remove(file)
            print(f"  ✅ 删除: {file}")
            removed_count += 1
        except Exception as e:
            print(f"  ❌ 删除失败: {file} - {e}")
    
    # 6. 清理虚拟环境目录
    print("🐍 清理虚拟环境...")
    venv_dirs = ["venv_ashare"]
    for venv_dir in venv_dirs:
        if os.path.exists(venv_dir):
            try:
                shutil.rmtree(venv_dir)
                print(f"  ✅ 删除目录: {venv_dir}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ 删除失败: {venv_dir} - {e}")
    
    # 7. 清理下载的爬虫目录
    print("🕷️ 清理下载目录...")
    download_dirs = ["downloaded_crawlers"]
    for dl_dir in download_dirs:
        if os.path.exists(dl_dir):
            try:
                shutil.rmtree(dl_dir)
                print(f"  ✅ 删除目录: {dl_dir}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ 删除失败: {dl_dir} - {e}")
    
    print(f"\n✅ 清理完成！共删除 {removed_count} 个文件/目录")
    
    # 8. 显示保留的核心文件
    print("\n📁 保留的核心文件：")
    core_files = [
        "tradingagents/",
        "web_app.py", 
        "enhanced_agent_architecture.py",
        "dongyang_simple_test.py",
        "cleanup_and_security_fixes.py",
        "futuristic_ai_dashboard.html",
        "config.py",
        "requirements.txt",
        "README.md"
    ]
    
    for file in core_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
    
    return removed_count

if __name__ == "__main__":
    count = cleanup_project()
    print(f"\n🎉 项目清理完成，删除了 {count} 个无关文件")