#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
水产股票技术面和资金流向分析
"""

import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def get_technical_indicators(symbol, days=60):
    """获取技术指标"""
    try:
        stock_code = symbol.split('.')[0]
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        
        # 获取历史数据
        hist_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                     start_date=start_date, end_date=end_date, adjust="")
        
        if hist_data.empty:
            return None
            
        # 计算技术指标
        hist_data['ma5'] = hist_data['收盘'].rolling(window=5).mean()
        hist_data['ma10'] = hist_data['收盘'].rolling(window=10).mean()
        hist_data['ma20'] = hist_data['收盘'].rolling(window=20).mean()
        
        # 计算RSI
        delta = hist_data['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist_data['rsi'] = 100 - (100 / (1 + rs))
        
        latest = hist_data.iloc[-1]
        prev = hist_data.iloc[-2] if len(hist_data) > 1 else latest
        
        return {
            "current_price": latest['收盘'],
            "change_pct": latest.get('涨跌幅', 0),
            "volume": latest['成交量'],
            "ma5": latest['ma5'],
            "ma10": latest['ma10'], 
            "ma20": latest['ma20'],
            "rsi": latest['rsi'],
            "volume_ratio": latest['成交量'] / hist_data['成交量'].mean() if len(hist_data) > 1 else 1,
            "trend_analysis": analyze_trend(hist_data)
        }
        
    except Exception as e:
        print(f"获取 {symbol} 技术指标失败: {e}")
        return None

def analyze_trend(data):
    """分析趋势"""
    if len(data) < 20:
        return "数据不足"
        
    latest = data.iloc[-1]
    
    # 均线多头排列判断
    ma5 = latest['ma5']
    ma10 = latest['ma10'] 
    ma20 = latest['ma20']
    current_price = latest['收盘']
    
    if current_price > ma5 > ma10 > ma20:
        trend = "强势上涨"
    elif current_price > ma5 > ma10:
        trend = "温和上涨"
    elif current_price < ma5 < ma10 < ma20:
        trend = "弱势下跌"
    elif ma5 < ma10 < ma20:
        trend = "下跌趋势"
    else:
        trend = "震荡整理"
        
    return trend

def get_fund_flow(symbol):
    """获取资金流向"""
    try:
        stock_code = symbol.split('.')[0]
        
        # 获取资金流向数据
        fund_flow = ak.stock_individual_fund_flow(stock=stock_code, market="sh" if symbol.endswith("SH") else "sz")
        
        if not fund_flow.empty:
            latest_flow = fund_flow.iloc[0]  # 最新一天的数据
            
            return {
                "main_net_inflow": latest_flow.get('主力净流入', 0),
                "main_net_inflow_pct": latest_flow.get('主力净流入占比', 0),
                "super_large_net_inflow": latest_flow.get('超大单净流入', 0),
                "large_net_inflow": latest_flow.get('大单净流入', 0),
                "medium_net_inflow": latest_flow.get('中单净流入', 0),
                "small_net_inflow": latest_flow.get('小单净流入', 0)
            }
    except Exception as e:
        print(f"获取 {symbol} 资金流向失败: {e}")
        return None

def comprehensive_technical_analysis():
    """综合技术面分析"""
    
    print("📊 水产股票技术面和资金流向分析")
    print("=" * 60)
    print(f"📅 分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    seafood_stocks = {
        "300094": "国联水产",
        "300268": "佳沃食品", 
        "600467": "好当家",
        "002086": "东方海洋",
        "600257": "大湖股份",
        "002069": "獐子岛",
        "002696": "百洋股份"
    }
    
    analysis_results = {}
    
    for code, name in seafood_stocks.items():
        print(f"\n📈 分析 {name}({code}) 技术面...")
        
        # 获取技术指标
        tech_data = get_technical_indicators(code)
        
        # 获取资金流向
        fund_data = get_fund_flow(code)
        
        if tech_data:
            analysis = {
                "股票名称": name,
                "当前价格": tech_data['current_price'],
                "涨跌幅": f"{tech_data['change_pct']:.2f}%",
                "技术指标": {
                    "MA5": f"{tech_data['ma5']:.2f}",
                    "MA10": f"{tech_data['ma10']:.2f}", 
                    "MA20": f"{tech_data['ma20']:.2f}",
                    "RSI": f"{tech_data['rsi']:.1f}",
                    "成交量比": f"{tech_data['volume_ratio']:.2f}",
                    "趋势分析": tech_data['trend_analysis']
                }
            }
            
            if fund_data:
                analysis["资金流向"] = {
                    "主力净流入": f"{fund_data['main_net_inflow']:.0f}万",
                    "主力净流入占比": f"{fund_data['main_net_inflow_pct']:.2f}%",
                    "超大单净流入": f"{fund_data['super_large_net_inflow']:.0f}万", 
                    "大单净流入": f"{fund_data['large_net_inflow']:.0f}万"
                }
            
            # 技术面评分
            score = calculate_technical_score(tech_data, fund_data)
            analysis["技术面评分"] = score
            
            analysis_results[code] = analysis
            
            print(f"✅ {name} - 价格: {tech_data['current_price']:.2f}, 趋势: {tech_data['trend_analysis']}, 评分: {score['总分']}")
        else:
            print(f"❌ {name} 技术分析失败")
    
    # 生成技术面排名
    print(f"\n{'='*60}")
    print("🏆 技术面综合排名")
    print("-" * 60)
    
    ranked_stocks = sorted(analysis_results.items(), 
                          key=lambda x: x[1]['技术面评分']['总分'], reverse=True)
    
    for i, (code, analysis) in enumerate(ranked_stocks, 1):
        score_info = analysis['技术面评分']
        print(f"{i}. {analysis['股票名称']}({code})")
        print(f"   总分: {score_info['总分']}/100")
        print(f"   趋势: {analysis['技术指标']['趋势分析']}")
        print(f"   RSI: {analysis['技术指标']['RSI']}")
        if '资金流向' in analysis:
            print(f"   主力资金: {analysis['资金流向']['主力净流入']}")
        print(f"   推荐度: {score_info['推荐级别']}")
        print()
    
    return analysis_results

def calculate_technical_score(tech_data, fund_data):
    """计算技术面评分"""
    score = 0
    details = {}
    
    # 趋势评分 (30分)
    trend = tech_data['trend_analysis'] 
    if trend == "强势上涨":
        trend_score = 30
    elif trend == "温和上涨":
        trend_score = 25
    elif trend == "震荡整理":
        trend_score = 15
    elif trend == "下跌趋势":
        trend_score = 5
    else:
        trend_score = 10
    
    score += trend_score
    details['趋势评分'] = trend_score
    
    # RSI评分 (20分)
    rsi = tech_data['rsi']
    if 30 <= rsi <= 70:
        rsi_score = 20  # 正常区间
    elif rsi > 70:
        rsi_score = 10  # 超买
    elif rsi < 30:
        rsi_score = 25  # 超卖机会
    else:
        rsi_score = 15
        
    score += rsi_score
    details['RSI评分'] = rsi_score
    
    # 成交量评分 (20分)
    volume_ratio = tech_data['volume_ratio']
    if volume_ratio > 2:
        volume_score = 20  # 放量
    elif volume_ratio > 1.5:
        volume_score = 15
    elif volume_ratio > 1:
        volume_score = 10
    else:
        volume_score = 5  # 缩量
        
    score += volume_score
    details['成交量评分'] = volume_score
    
    # 资金流向评分 (30分)
    if fund_data and fund_data.get('main_net_inflow_pct'):
        inflow_pct = fund_data['main_net_inflow_pct']
        if inflow_pct > 5:
            fund_score = 30
        elif inflow_pct > 2:
            fund_score = 25
        elif inflow_pct > 0:
            fund_score = 20
        elif inflow_pct > -2:
            fund_score = 15
        else:
            fund_score = 5
    else:
        fund_score = 15  # 无数据给中等分
        
    score += fund_score
    details['资金流向评分'] = fund_score
    
    # 推荐级别
    if score >= 80:
        recommendation = "强烈推荐"
    elif score >= 70:
        recommendation = "推荐"
    elif score >= 60:
        recommendation = "谨慎推荐"
    elif score >= 50:
        recommendation = "中性"
    else:
        recommendation = "不推荐"
    
    return {
        "总分": score,
        "推荐级别": recommendation,
        "详细评分": details
    }

if __name__ == "__main__":
    try:
        results = comprehensive_technical_analysis()
        
        print("\n💡 技术面分析要点:")
        print("• 关注主力资金净流入的股票")
        print("• RSI低位的股票可能存在反弹机会") 
        print("• 趋势向上且放量的股票优先考虑")
        print("• 结合基本面分析做最终决策")
        
    except Exception as e:
        print(f"❌ 技术分析失败: {e}")
        import traceback
        traceback.print_exc()