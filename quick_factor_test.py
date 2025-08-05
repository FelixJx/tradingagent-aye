#!/usr/bin/env python3
# /Applications/tradingagent/quick_factor_test.py
"""
快速因子测试启动脚本
一键测试股票的基础因子有效性
"""

import sys
import os
import pandas as pd
import numpy as np
import tushare as ts
import warnings
warnings.filterwarnings('ignore')

# 您的tushare token
TUSHARE_TOKEN = "b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065"

def quick_factor_test(stock_code: str = "000001.SZ"):
    """
    快速因子测试 - 一键运行
    """
    print(f"""
? 快速因子测试系统
=====================
测试股票: {stock_code}
Token: {TUSHARE_TOKEN[:10]}...
=====================
""")
    
    # 初始化tushare
    try:
        ts_pro = ts.pro_api(TUSHARE_TOKEN)
        print("? Tushare API 连接成功")
    except Exception as e:
        print(f"? Tushare API 连接失败: {e}")
        return
    
    # 获取数据
    try:
        print(f"? 获取 {stock_code} 的数据...")
        end_date = pd.Timestamp.now().strftime('%Y%m%d')
        start_date = (pd.Timestamp.now() - pd.Timedelta(days=365)).strftime('%Y%m%d')
        
        data = ts_pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        
        if data.empty:
            print(f"? 无法获取 {stock_code} 的数据")
            return
        
        data['trade_date'] = pd.to_datetime(data['trade_date'])
        data = data.set_index('trade_date').sort_index()
        data.columns = [col.lower() for col in data.columns]
        
        print(f"? 获取到 {len(data)} 个交易日的数据")
        
    except Exception as e:
        print(f"? 数据获取失败: {e}")
        return
    
    # 生成基础因子
    try:
        print("? 生成基础因子...")
        
        factors = pd.DataFrame(index=data.index)
        price = data['close']
        volume = data.get('vol', pd.Series(index=data.index))
        returns = price.pct_change()
        
        # 动量因子
        factors['momentum_5'] = price.pct_change(5)
        factors['momentum_20'] = price.pct_change(20)
        
        # 反转因子
        factors['reversal_1'] = -price.pct_change(1)
        factors['reversal_5'] = -price.pct_change(5)
        
        # 波动率因子
        factors['volatility_20'] = returns.rolling(20).std()
        factors['volatility_ratio'] = factors['volatility_20'] / returns.rolling(60).std()
        
        # 成交量因子
        if not volume.isna().all():
            factors['volume_ratio'] = volume / volume.rolling(20).mean()
        
        factors = factors.replace([np.inf, -np.inf], np.nan).dropna()
        
        print(f"? 生成 {len(factors.columns)} 个因子，有效数据 {len(factors)} 行")
        
    except Exception as e:
        print(f"? 因子生成失败: {e}")
        return
    
    # 测试因子有效性
    try:
        print("? 测试因子有效性...")
        
        forward_returns = returns.shift(-10)  # 10日后收益率
        results = {}
        
        for factor_name in factors.columns:
            factor_values = factors[factor_name].dropna()
            
            if len(factor_values) < 50:
                continue
            
            # 对齐数据
            aligned_data = pd.concat([factor_values, forward_returns], axis=1).dropna()
            
            if len(aligned_data) < 30:
                continue
            
            factor_col = aligned_data.iloc[:, 0]
            return_col = aligned_data.iloc[:, 1]
            
            # 计算IC
            ic = factor_col.corr(return_col)
            rank_ic = factor_col.rank().corr(return_col.rank())
            
            results[factor_name] = {
                'IC': ic,
                'Rank_IC': rank_ic,
                'IC_abs': abs(ic),
                'sample_size': len(aligned_data)
            }
        
        # 排序
        sorted_results = dict(sorted(results.items(), key=lambda x: x[1]['IC_abs'], reverse=True))
        
        print(f"? 测试完成，有效因子 {len(sorted_results)} 个")
        
    except Exception as e:
        print(f"? 因子测试失败: {e}")
        return
    
    # 显示结果
    print(f"""
? {stock_code} 因子测试结果
==============================
""")
    
    if sorted_results:
        print("? Top 5 最有效因子:")
        for i, (factor_name, metrics) in enumerate(list(sorted_results.items())[:5], 1):
            ic = metrics['IC']
            rank_ic = metrics['Rank_IC']
            
            if abs(ic) > 0.05:
                grade = "? 优秀"
            elif abs(ic) > 0.03:
                grade = "? 良好" 
            elif abs(ic) > 0.01:
                grade = "? 一般"
            else:
                grade = "? 较差"
            
            print(f"{i}. {factor_name:<20} {grade}")
            print(f"   IC: {ic:>8.4f}   Rank IC: {rank_ic:>8.4f}   样本: {metrics['sample_size']}")
            print()
        
        # 简单建议
        best_factor = list(sorted_results.keys())[0]
        best_ic = sorted_results[best_factor]['IC']
        
        print("? 投资建议:")
        if abs(best_ic) > 0.05:
            print("? 因子效果优秀，推荐使用多因子选股策略")
        elif abs(best_ic) > 0.03:
            print("? 因子效果良好，可考虑因子选股")
        elif abs(best_ic) > 0.01:
            print("?? 因子效果一般，建议谨慎使用")
        else:
            print("? 因子效果较差，不建议使用")
        
        print(f"\n? 最佳因子: {best_factor} (IC: {best_ic:.4f})")
        
    else:
        print("? 未发现有效因子")
    
    print(f"""
==============================
测试完成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
==============================
""")
    
    return sorted_results

def batch_test():
    """
    批量测试多只股票
    """
    test_stocks = [
        "000001.SZ",  # 平安银行
        "000002.SZ",  # 万科A
        "600000.SH",  # 浦发银行
        "600036.SH",  # 招商银行
        "000858.SZ"   # 五粮液
    ]
    
    print("? 批量因子测试")
    print("="*50)
    
    all_results = {}
    
    for stock in test_stocks:
        print(f"\n? 测试 {stock}...")
        try:
            result = quick_factor_test(stock)
            if result:
                all_results[stock] = result
                print(f"? {stock} 测试成功")
            else:
                print(f"? {stock} 测试失败")
        except Exception as e:
            print(f"? {stock} 测试出错: {e}")
        
        print("-" * 30)
    
    # 汇总结果
    if all_results:
        print("\n? 批量测试汇总")
        print("="*50)
        
        for stock, results in all_results.items():
            if results:
                best_factor = list(results.keys())[0]
                best_ic = results[best_factor]['IC']
                print(f"{stock:<12} 最佳因子: {best_factor:<20} IC: {best_ic:>8.4f}")
    
    return all_results

if __name__ == "__main__":
    print("请选择测试模式:")
    print("1. 单股票测试")
    print("2. 批量测试")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        stock_code = input("请输入股票代码 (默认: 000001.SZ): ").strip()
        if not stock_code:
            stock_code = "000001.SZ"
        
        quick_factor_test(stock_code)
        
    elif choice == "2":
        batch_test()
        
    else:
        print("使用默认单股票测试...")
        quick_factor_test("000001.SZ")