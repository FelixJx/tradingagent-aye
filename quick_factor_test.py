#!/usr/bin/env python3
# /Applications/tradingagent/quick_factor_test.py
"""
�������Ӳ��������ű�
һ�����Թ�Ʊ�Ļ���������Ч��
"""

import sys
import os
import pandas as pd
import numpy as np
import tushare as ts
import warnings
warnings.filterwarnings('ignore')

# ����tushare token
TUSHARE_TOKEN = "b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065"

def quick_factor_test(stock_code: str = "000001.SZ"):
    """
    �������Ӳ��� - һ������
    """
    print(f"""
? �������Ӳ���ϵͳ
=====================
���Թ�Ʊ: {stock_code}
Token: {TUSHARE_TOKEN[:10]}...
=====================
""")
    
    # ��ʼ��tushare
    try:
        ts_pro = ts.pro_api(TUSHARE_TOKEN)
        print("? Tushare API ���ӳɹ�")
    except Exception as e:
        print(f"? Tushare API ����ʧ��: {e}")
        return
    
    # ��ȡ����
    try:
        print(f"? ��ȡ {stock_code} ������...")
        end_date = pd.Timestamp.now().strftime('%Y%m%d')
        start_date = (pd.Timestamp.now() - pd.Timedelta(days=365)).strftime('%Y%m%d')
        
        data = ts_pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        
        if data.empty:
            print(f"? �޷���ȡ {stock_code} ������")
            return
        
        data['trade_date'] = pd.to_datetime(data['trade_date'])
        data = data.set_index('trade_date').sort_index()
        data.columns = [col.lower() for col in data.columns]
        
        print(f"? ��ȡ�� {len(data)} �������յ�����")
        
    except Exception as e:
        print(f"? ���ݻ�ȡʧ��: {e}")
        return
    
    # ���ɻ�������
    try:
        print("? ���ɻ�������...")
        
        factors = pd.DataFrame(index=data.index)
        price = data['close']
        volume = data.get('vol', pd.Series(index=data.index))
        returns = price.pct_change()
        
        # ��������
        factors['momentum_5'] = price.pct_change(5)
        factors['momentum_20'] = price.pct_change(20)
        
        # ��ת����
        factors['reversal_1'] = -price.pct_change(1)
        factors['reversal_5'] = -price.pct_change(5)
        
        # ����������
        factors['volatility_20'] = returns.rolling(20).std()
        factors['volatility_ratio'] = factors['volatility_20'] / returns.rolling(60).std()
        
        # �ɽ�������
        if not volume.isna().all():
            factors['volume_ratio'] = volume / volume.rolling(20).mean()
        
        factors = factors.replace([np.inf, -np.inf], np.nan).dropna()
        
        print(f"? ���� {len(factors.columns)} �����ӣ���Ч���� {len(factors)} ��")
        
    except Exception as e:
        print(f"? ��������ʧ��: {e}")
        return
    
    # ����������Ч��
    try:
        print("? ����������Ч��...")
        
        forward_returns = returns.shift(-10)  # 10�պ�������
        results = {}
        
        for factor_name in factors.columns:
            factor_values = factors[factor_name].dropna()
            
            if len(factor_values) < 50:
                continue
            
            # ��������
            aligned_data = pd.concat([factor_values, forward_returns], axis=1).dropna()
            
            if len(aligned_data) < 30:
                continue
            
            factor_col = aligned_data.iloc[:, 0]
            return_col = aligned_data.iloc[:, 1]
            
            # ����IC
            ic = factor_col.corr(return_col)
            rank_ic = factor_col.rank().corr(return_col.rank())
            
            results[factor_name] = {
                'IC': ic,
                'Rank_IC': rank_ic,
                'IC_abs': abs(ic),
                'sample_size': len(aligned_data)
            }
        
        # ����
        sorted_results = dict(sorted(results.items(), key=lambda x: x[1]['IC_abs'], reverse=True))
        
        print(f"? ������ɣ���Ч���� {len(sorted_results)} ��")
        
    except Exception as e:
        print(f"? ���Ӳ���ʧ��: {e}")
        return
    
    # ��ʾ���
    print(f"""
? {stock_code} ���Ӳ��Խ��
==============================
""")
    
    if sorted_results:
        print("? Top 5 ����Ч����:")
        for i, (factor_name, metrics) in enumerate(list(sorted_results.items())[:5], 1):
            ic = metrics['IC']
            rank_ic = metrics['Rank_IC']
            
            if abs(ic) > 0.05:
                grade = "? ����"
            elif abs(ic) > 0.03:
                grade = "? ����" 
            elif abs(ic) > 0.01:
                grade = "? һ��"
            else:
                grade = "? �ϲ�"
            
            print(f"{i}. {factor_name:<20} {grade}")
            print(f"   IC: {ic:>8.4f}   Rank IC: {rank_ic:>8.4f}   ����: {metrics['sample_size']}")
            print()
        
        # �򵥽���
        best_factor = list(sorted_results.keys())[0]
        best_ic = sorted_results[best_factor]['IC']
        
        print("? Ͷ�ʽ���:")
        if abs(best_ic) > 0.05:
            print("? ����Ч�����㣬�Ƽ�ʹ�ö�����ѡ�ɲ���")
        elif abs(best_ic) > 0.03:
            print("? ����Ч�����ã��ɿ�������ѡ��")
        elif abs(best_ic) > 0.01:
            print("?? ����Ч��һ�㣬�������ʹ��")
        else:
            print("? ����Ч���ϲ������ʹ��")
        
        print(f"\n? �������: {best_factor} (IC: {best_ic:.4f})")
        
    else:
        print("? δ������Ч����")
    
    print(f"""
==============================
�������ʱ��: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
==============================
""")
    
    return sorted_results

def batch_test():
    """
    �������Զ�ֻ��Ʊ
    """
    test_stocks = [
        "000001.SZ",  # ƽ������
        "000002.SZ",  # ���A
        "600000.SH",  # �ַ�����
        "600036.SH",  # ��������
        "000858.SZ"   # ����Һ
    ]
    
    print("? �������Ӳ���")
    print("="*50)
    
    all_results = {}
    
    for stock in test_stocks:
        print(f"\n? ���� {stock}...")
        try:
            result = quick_factor_test(stock)
            if result:
                all_results[stock] = result
                print(f"? {stock} ���Գɹ�")
            else:
                print(f"? {stock} ����ʧ��")
        except Exception as e:
            print(f"? {stock} ���Գ���: {e}")
        
        print("-" * 30)
    
    # ���ܽ��
    if all_results:
        print("\n? �������Ի���")
        print("="*50)
        
        for stock, results in all_results.items():
            if results:
                best_factor = list(results.keys())[0]
                best_ic = results[best_factor]['IC']
                print(f"{stock:<12} �������: {best_factor:<20} IC: {best_ic:>8.4f}")
    
    return all_results

if __name__ == "__main__":
    print("��ѡ�����ģʽ:")
    print("1. ����Ʊ����")
    print("2. ��������")
    
    choice = input("������ѡ�� (1/2): ").strip()
    
    if choice == "1":
        stock_code = input("�������Ʊ���� (Ĭ��: 000001.SZ): ").strip()
        if not stock_code:
            stock_code = "000001.SZ"
        
        quick_factor_test(stock_code)
        
    elif choice == "2":
        batch_test()
        
    else:
        print("ʹ��Ĭ�ϵ���Ʊ����...")
        quick_factor_test("000001.SZ")