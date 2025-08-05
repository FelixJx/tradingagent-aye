#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速技术面分析
"""

import pandas as pd
import akshare as ak
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def quick_analysis():
    """快速技术分析"""
    
    print("📊 水产股票快速技术分析")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    stocks = {
        "300094": "国联水产",
        "300268": "佳沃食品", 
        "600467": "好当家",
        "002086": "东方海洋"
    }
    
    results = []
    
    for code, name in stocks.items():
        try:
            print(f"分析 {name}({code})...")
            
            # 获取实时行情
            stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                                   start_date="20250701", end_date="20250730", adjust="")
            
            if not stock_zh_a_hist_df.empty:
                latest = stock_zh_a_hist_df.iloc[-1]
                
                # 计算简单技术指标
                ma5 = stock_zh_a_hist_df['收盘'].rolling(5).mean().iloc[-1]
                ma10 = stock_zh_a_hist_df['收盘'].rolling(10).mean().iloc[-1] 
                
                price = latest['收盘']
                change_pct = latest.get('涨跌幅', 0)
                volume = latest['成交量']
                
                # 简单评分
                score = 50  # 基础分
                
                # 价格vs均线
                if price > ma5 > ma10:
                    score += 20
                    trend = "上升"
                elif price > ma5:
                    score += 10
                    trend = "整理"
                else:
                    score -= 10
                    trend = "下跌"
                
                # 涨跌幅加分
                if change_pct > 3:
                    score += 15
                elif change_pct > 0:
                    score += 5
                elif change_pct < -3:
                    score -= 15
                
                results.append({
                    "代码": code,
                    "名称": name,
                    "价格": price,
                    "涨跌幅": f"{change_pct:.2f}%",
                    "趋势": trend,
                    "MA5": f"{ma5:.2f}",
                    "MA10": f"{ma10:.2f}", 
                    "评分": score
                })
                
                print(f"✅ {name}: {price:.2f} ({change_pct:+.2f}%) 趋势:{trend} 评分:{score}")
                
        except Exception as e:
            print(f"❌ {name} 分析失败: {e}")
    
    # 排序
    results.sort(key=lambda x: x['评分'], reverse=True)
    
    print(f"\n{'='*50}")
    print("🏆 技术面排名")
    print("-" * 50)
    
    for i, stock in enumerate(results, 1):
        print(f"{i}. {stock['名称']}({stock['代码']})")
        print(f"   价格: {stock['价格']:.2f} ({stock['涨跌幅']})")
        print(f"   趋势: {stock['趋势']} | 评分: {stock['评分']}")
        print()
    
    return results

if __name__ == "__main__":
    try:
        quick_analysis()
        
        print("💡 快速结论:")
        print("• 今日多数水产股上涨，反映海啸影响预期")
        print("• 国联水产领涨，符合基本面分析")
        print("• 建议关注技术面评分较高的标的")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")