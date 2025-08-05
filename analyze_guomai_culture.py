#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
果麦文化股票分析脚本
使用ashare_news_utils.py的所有功能进行全面分析
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append('/Applications/tradingagent')

from tradingagents.dataflows.ashare_news_utils import (
    get_ashare_company_news,
    get_ashare_market_news,
    get_ashare_policy_news,
    get_ashare_industry_news,
    AShareNewsCollector
)

def analyze_guomai_culture():
    """
    全面分析果麦文化股票
    """
    print("="*80)
    print("🔍 果麦文化(股票代码待确认)全面分析报告")
    print("="*80)
    
    # 当前日期
    curr_date = datetime.now().strftime('%Y-%m-%d')
    
    # 果麦文化相关信息
    # 根据公开信息，果麦文化是一家文化传媒公司
    company_name = "果麦文化"
    # 常见的文化传媒股票代码格式，我们先尝试几个可能的代码
    possible_codes = ["301052", "300052", "002052"]  # 这些是可能的代码
    
    print(f"\n📅 分析日期: {curr_date}")
    print(f"🏢 目标公司: {company_name}")
    
    # 1. 使用所有新闻获取功能
    print("\n" + "="*60)
    print("📰 第一部分：公司新闻分析")
    print("="*60)
    
    for stock_code in possible_codes:
        print(f"\n🔍 尝试股票代码: {stock_code}")
        try:
            company_news = get_ashare_company_news(
                stock_code=stock_code,
                company_name=company_name,
                curr_date=curr_date,
                lookback_days=7
            )
            print(company_news)
            break  # 如果成功获取到新闻，就使用这个代码
        except Exception as e:
            print(f"❌ 股票代码 {stock_code} 获取失败: {e}")
            continue
    
    # 2. 市场整体新闻分析
    print("\n" + "="*60)
    print("📈 第二部分：市场整体新闻分析")
    print("="*60)
    
    try:
        market_news = get_ashare_market_news(
            curr_date=curr_date,
            lookback_days=3,
            limit=15
        )
        print(market_news)
    except Exception as e:
        print(f"❌ 获取市场新闻失败: {e}")
    
    # 3. 政策新闻分析
    print("\n" + "="*60)
    print("📋 第三部分：相关政策新闻分析")
    print("="*60)
    
    try:
        policy_news = get_ashare_policy_news(
            curr_date=curr_date,
            lookback_days=7
        )
        print(policy_news)
    except Exception as e:
        print(f"❌ 获取政策新闻失败: {e}")
    
    # 4. 行业新闻分析
    print("\n" + "="*60)
    print("🏭 第四部分：文化传媒行业新闻分析")
    print("="*60)
    
    # 果麦文化属于文化传媒行业
    industries = ["文化传媒", "出版", "图书", "文化"]
    
    for industry in industries:
        print(f"\n📊 {industry}行业分析:")
        try:
            industry_news = get_ashare_industry_news(
                industry=industry,
                curr_date=curr_date,
                lookback_days=5
            )
            print(industry_news)
        except Exception as e:
            print(f"❌ 获取{industry}行业新闻失败: {e}")
    
    # 5. 使用新闻收集器类的功能
    print("\n" + "="*60)
    print("🔧 第五部分：新闻收集器详细功能测试")
    print("="*60)
    
    collector = AShareNewsCollector()
    
    # 测试各个新闻源
    news_sources = [
        ("新浪财经", collector.get_sina_finance_news),
        ("财联社", collector.get_cailianshe_news),
        ("东方财富", collector.get_eastmoney_news)
    ]
    
    for source_name, source_func in news_sources:
        print(f"\n📡 {source_name}新闻源测试:")
        try:
            if source_name == "东方财富":
                news_data = source_func(keyword=company_name, limit=5)
            else:
                news_data = source_func(keyword=company_name, limit=5, days_back=7)
            
            if news_data:
                for i, news in enumerate(news_data, 1):
                    print(f"  {i}. {news['title']}")
                    print(f"     来源: {news['source']} | 时间: {news['publish_time']}")
                    if news['content']:
                        content_preview = news['content'][:100] + "..." if len(news['content']) > 100 else news['content']
                        print(f"     内容: {content_preview}")
                    print()
            else:
                print(f"  ❌ 未获取到{source_name}的新闻数据")
        except Exception as e:
            print(f"  ❌ {source_name}测试失败: {e}")
    
    # 6. 综合分析总结
    print("\n" + "="*60)
    print("📊 第六部分：综合分析总结")
    print("="*60)
    
    print(f"""
🎯 果麦文化分析工具功能总结:

✅ 已测试的功能模块:
1. get_ashare_company_news() - 获取公司特定新闻
2. get_ashare_market_news() - 获取市场整体新闻
3. get_ashare_policy_news() - 获取政策相关新闻
4. get_ashare_industry_news() - 获取行业新闻
5. AShareNewsCollector类的所有方法:
   - get_sina_finance_news() - 新浪财经新闻
   - get_cailianshe_news() - 财联社新闻
   - get_eastmoney_news() - 东方财富新闻

📈 分析维度:
- 公司层面：特定公司新闻和公告
- 市场层面：A股整体市场动态
- 政策层面：监管政策和行业政策
- 行业层面：文化传媒行业趋势

🔍 数据源覆盖:
- 新浪财经：主流财经媒体
- 财联社：专业财经快讯
- 东方财富：综合金融信息平台

⚠️  注意事项:
- 部分功能可能需要有效的股票代码
- 网络爬虫功能依赖于目标网站的可访问性
- 建议在实际使用时配置代理和请求频率限制
    """)

if __name__ == "__main__":
    analyze_guomai_culture()