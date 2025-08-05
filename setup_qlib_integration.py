#!/usr/bin/env python3
# /Applications/tradingagent/setup_qlib_integration.py
"""
Qlib集成设置脚本
利用您在/Users/jx/Downloads/qlib-main的qlib安装
"""

import subprocess
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

def install_dependencies():
    """
    安装必要依赖
    """
    print("? 安装必要依赖...")
    
    packages = [
        "scikit-learn>=1.0.0",
        "xgboost", 
        "lightgbm",
        "catboost",
        "statsmodels",
        "scipy"
    ]
    
    for package in packages:
        try:
            print(f"  ? 安装 {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"  ? {package} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"  ?? {package} 安装失败: {e}")
            continue
    
    print("? 依赖安装完成")

def setup_qlib_path():
    """
    设置qlib路径
    """
    qlib_path = '/Users/jx/Downloads/qlib-main'
    
    if os.path.exists(qlib_path):
        print(f"? 发现Qlib路径: {qlib_path}")
        
        # 添加到Python路径
        if qlib_path not in sys.path:
            sys.path.insert(0, qlib_path)
        
        return True
    else:
        print(f"? Qlib路径不存在: {qlib_path}")
        return False

if __name__ == '__main__':
    print("? 开始设置Qlib集成环境")
    print("="*50)
    
    # 安装依赖
    install_dependencies()
    
    # 设置qlib路径
    if setup_qlib_path():
        print("\n? Qlib集成环境设置完成!")
        print("\n? 下一步:")
        print("cd /Applications/tradingagent")
        print("python3 qlib_integrated_factor_system.py")
    else:
        print("\n? 环境设置失败")
