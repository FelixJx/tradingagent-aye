#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模拟A股选股工具
兼容Python 3.3+
使用模拟数据演示选股功能
"""

import os
import json
import random
from datetime import datetime

# 设置环境变量
os.environ['TUSHARE_TOKEN'] = 'b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065'
os.environ['DASHSCOPE_API_KEY'] = 'sk-e050041b41674ed7b87644895ebae718'

print("🚀 A股模拟选股工具")
print("=" * 40)
print("📝 注意: 使用模拟数据进行演示")

# 模拟股票数据
MOCK_STOCKS = [
    {'ts_code': '000001.SZ', 'name': '平安银行', 'pe': 5.2, 'pb': 0.8, 'market_cap': 280000000000},
    {'ts_code': '000002.SZ', 'name': '万科A', 'pe': 8.5, 'pb': 1.2, 'market_cap': 120000000000},
    {'ts_code': '600000.SH', 'name': '浦发银行', 'pe': 4.8, 'pb': 0.6, 'market_cap': 180000000000},
    {'ts_code': '600036.SH', 'name': '招商银行', 'pe': 6.2, 'pb': 1.1, 'market_cap': 950000000000},
    {'ts_code': '600519.SH', 'name': '贵州茅台', 'pe': 28.5, 'pb': 12.8, 'market_cap': 2200000000000},
    {'ts_code': '000858.SZ', 'name': '五粮液', 'pe': 22.3, 'pb': 5.6, 'market_cap': 680000000000},
    {'ts_code': '002415.SZ', 'name': '海康威视', 'pe': 15.2, 'pb': 3.2, 'market_cap': 320000000000},
    {'ts_code': '300059.SZ', 'name': '东方财富', 'pe': 35.8, 'pb': 4.5, 'market_cap': 280000000000},
    {'ts_code': '000858.SZ', 'name': 'ST康美', 'pe': 45.2, 'pb': 2.1, 'market_cap': 15000000000},
    {'ts_code': '600887.SH', 'name': '伊利股份', 'pe': 18.6, 'pb': 4.2, 'market_cap': 260000000000},
    {'ts_code': '000776.SZ', 'name': '广发证券', 'pe': 12.5, 'pb': 1.8, 'market_cap': 95000000000},
    {'ts_code': '002594.SZ', 'name': 'BYD', 'pe': 42.1, 'pb': 6.8, 'market_cap': 850000000000},
    {'ts_code': '600276.SH', 'name': '恒瑞医药', 'pe': 26.8, 'pb': 7.2, 'market_cap': 380000000000},
    {'ts_code': '000063.SZ', 'name': '中兴通讯', 'pe': 19.5, 'pb': 2.9, 'market_cap': 160000000000},
    {'ts_code': '002230.SZ', 'name': '科大讯飞', 'pe': 55.2, 'pb': 8.1, 'market_cap': 140000000000}
]

def get_mock_stock_list():
    """获取模拟股票列表"""
    print("📋 获取模拟股票列表...")
    print("✅ 获取到 {} 只股票".format(len(MOCK_STOCKS)))
    return MOCK_STOCKS

def screen_stocks(criteria):
    """筛选股票"""
    print("\n🔍 开始筛选股票...")
    print("-" * 30)
    
    # 获取股票列表
    stock_list = get_mock_stock_list()
    
    # 筛选结果
    results = []
    
    print("⏳ 正在应用筛选条件...")
    
    # 处理股票
    for stock in stock_list:
        ts_code = stock['ts_code']
        name = stock['name']
        pe = stock['pe']
        pb = stock['pb']
        market_cap = stock['market_cap']
        
        # 跳过ST股票
        if criteria.get('exclude_st', True) and 'ST' in name:
            print("❌ 排除ST股票: {}".format(name))
            continue
        
        # PE比率筛选
        if criteria.get('pe_ratio_max') and pe > criteria['pe_ratio_max']:
            print("❌ PE过高: {} (PE: {:.1f})".format(name, pe))
            continue
        
        # 市值筛选
        if criteria.get('market_cap_min') and market_cap < criteria['market_cap_min']:
            print("❌ 市值过小: {} (市值: {:.0f}亿)".format(name, market_cap/100000000))
            continue
        
        # PB筛选
        if criteria.get('pb_ratio_max') and pb > criteria['pb_ratio_max']:
            print("❌ PB过高: {} (PB: {:.1f})".format(name, pb))
            continue
        
        # 通过筛选
        print("✅ 符合条件: {} (PE: {:.1f}, PB: {:.1f}, 市值: {:.0f}亿)".format(
            name, pe, pb, market_cap/100000000))
        
        results.append({
            'ts_code': ts_code,
            'name': name,
            'pe': pe,
            'pb': pb,
            'market_cap': market_cap,
            'market_cap_billion': market_cap/100000000
        })
    
    print("\n✅ 筛选完成! 找到 {} 只符合条件的股票".format(len(results)))
    return results

def analyze_stock(stock):
    """简单的股票分析"""
    score = 0
    reasons = []
    
    # PE评分
    if stock['pe'] < 10:
        score += 30
        reasons.append("PE较低({:.1f})".format(stock['pe']))
    elif stock['pe'] < 20:
        score += 20
        reasons.append("PE适中({:.1f})".format(stock['pe']))
    
    # PB评分
    if stock['pb'] < 2:
        score += 25
        reasons.append("PB较低({:.1f})".format(stock['pb']))
    elif stock['pb'] < 5:
        score += 15
        reasons.append("PB适中({:.1f})".format(stock['pb']))
    
    # 市值评分
    if stock['market_cap_billion'] > 1000:
        score += 20
        reasons.append("大盘股({:.0f}亿)".format(stock['market_cap_billion']))
    elif stock['market_cap_billion'] > 100:
        score += 15
        reasons.append("中盘股({:.0f}亿)".format(stock['market_cap_billion']))
    
    # 随机因子（模拟其他分析）
    random_score = random.randint(0, 25)
    score += random_score
    if random_score > 15:
        reasons.append("技术面良好")
    elif random_score > 10:
        reasons.append("基本面稳定")
    
    return score, reasons

def main():
    """主函数"""
    # 设置筛选条件
    criteria = {
        'pe_ratio_max': 25,        # PE比率最大值
        'pb_ratio_max': 10,        # PB比率最大值
        'market_cap_min': 50000000000,  # 最小市值500亿
        'exclude_st': True,        # 排除ST股票
    }
    
    print("📋 筛选条件:")
    print("- PE比率 ≤ {}".format(criteria['pe_ratio_max']))
    print("- PB比率 ≤ {}".format(criteria['pb_ratio_max']))
    print("- 市值 ≥ {:.0f}亿".format(criteria['market_cap_min']/100000000))
    print("- 排除ST股票: {}".format("是" if criteria['exclude_st'] else "否"))
    
    # 执行筛选
    results = screen_stocks(criteria)
    
    # 输出结果
    if results:
        print("\n📊 筛选结果分析:")
        print("-" * 50)
        print("{:<12} {:<10} {:<8} {:<8} {:<10} {:<8} {}".format(
            "代码", "名称", "PE", "PB", "市值(亿)", "评分", "分析理由"))
        print("-" * 50)
        
        # 分析每只股票
        analyzed_results = []
        for stock in results:
            score, reasons = analyze_stock(stock)
            stock['score'] = score
            stock['reasons'] = reasons
            analyzed_results.append(stock)
        
        # 按评分排序
        analyzed_results.sort(key=lambda x: x['score'], reverse=True)
        
        # 显示结果
        for stock in analyzed_results:
            print("{:<12} {:<10} {:<8.1f} {:<8.1f} {:<10.0f} {:<8} {}".format(
                stock['ts_code'], 
                stock['name'], 
                stock['pe'], 
                stock['pb'],
                stock['market_cap_billion'],
                stock['score'],
                ", ".join(stock['reasons'][:2])  # 只显示前2个理由
            ))
        
        # 推荐前3名
        print("\n🏆 推荐股票 (前3名):")
        print("-" * 30)
        for i, stock in enumerate(analyzed_results[:3], 1):
            print("{}. {} ({}) - 评分: {}".format(
                i, stock['name'], stock['ts_code'], stock['score']))
            print("   理由: {}".format(", ".join(stock['reasons'])))
        
        # 保存结果
        result_file = "stock_screening_result_{}.json".format(
            datetime.now().strftime("%Y%m%d_%H%M%S"))
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(analyzed_results, f, ensure_ascii=False, indent=2)
        print("\n💾 完整结果已保存至: {}".format(result_file))
        
        # 生成选股报告
        print("\n📈 选股报告:")
        print("-" * 30)
        print("- 筛选股票总数: {} 只".format(len(analyzed_results)))
        print("- 平均PE: {:.1f}".format(sum(s['pe'] for s in analyzed_results) / len(analyzed_results)))
        print("- 平均PB: {:.1f}".format(sum(s['pb'] for s in analyzed_results) / len(analyzed_results)))
        print("- 平均市值: {:.0f}亿".format(sum(s['market_cap_billion'] for s in analyzed_results) / len(analyzed_results)))
        print("- 最高评分: {}".format(analyzed_results[0]['score']))
        print("- 推荐关注: {}".format(analyzed_results[0]['name']))
    
    else:
        print("\n❌ 没有找到符合条件的股票")
        print("💡 建议放宽筛选条件")
    
    print("\n🎉 选股完成！")
    print("\n💡 提示:")
    print("- 本工具使用模拟数据")
    print("- 实际投资请使用真实数据")
    print("- 投资有风险，决策需谨慎")

if __name__ == "__main__":
    main()