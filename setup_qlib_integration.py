#!/usr/bin/env python3
# /Applications/tradingagent/setup_qlib_integration.py
"""
Qlib�������ýű�
��������/Users/jx/Downloads/qlib-main��qlib��װ
"""

import subprocess
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

def install_dependencies():
    """
    ��װ��Ҫ����
    """
    print("? ��װ��Ҫ����...")
    
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
            print(f"  ? ��װ {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"  ? {package} ��װ�ɹ�")
        except subprocess.CalledProcessError as e:
            print(f"  ?? {package} ��װʧ��: {e}")
            continue
    
    print("? ������װ���")

def setup_qlib_path():
    """
    ����qlib·��
    """
    qlib_path = '/Users/jx/Downloads/qlib-main'
    
    if os.path.exists(qlib_path):
        print(f"? ����Qlib·��: {qlib_path}")
        
        # ��ӵ�Python·��
        if qlib_path not in sys.path:
            sys.path.insert(0, qlib_path)
        
        return True
    else:
        print(f"? Qlib·��������: {qlib_path}")
        return False

if __name__ == '__main__':
    print("? ��ʼ����Qlib���ɻ���")
    print("="*50)
    
    # ��װ����
    install_dependencies()
    
    # ����qlib·��
    if setup_qlib_path():
        print("\n? Qlib���ɻ����������!")
        print("\n? ��һ��:")
        print("cd /Applications/tradingagent")
        print("python3 qlib_integrated_factor_system.py")
    else:
        print("\n? ��������ʧ��")
