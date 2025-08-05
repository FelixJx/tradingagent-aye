#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强数据采集系统演示
展示如何使用不达目的不罢休的A股数据采集agent
"""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from tradingagents.agents.enhanced_ashare_data_agent import create_enhanced_ashare_data_agent
from tradingagents.agents.data_collector_agent import DataCollectionTask, DataSourceType
from tradingagents.ashare_config import get_ashare_config
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama

def setup_llm():
    """设置语言模型"""
    # 尝试使用阿里云千问模型
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    if dashscope_key:
        try:
            from langchain_community.chat_models import ChatTongyi
            print("✅ 使用阿里云千问模型")
            return ChatTongyi(
                dashscope_api_key=dashscope_key,
                model_name="qwen-turbo",
                temperature=0.7
            )
        except ImportError:
            print("⚠️ 千问模型包未安装，尝试其他模型")
    
    # 尝试使用OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ 使用OpenAI模型")
        return ChatOpenAI(
            api_key=openai_key,
            model="gpt-4o-mini",
            temperature=0.7
        )
    
    # 尝试使用本地Ollama
    try:
        print("✅ 使用本地Ollama模型")
        return Ollama(model="qwen2:7b")
    except:
        print("❌ 无可用模型，请配置API密钥")
        sys.exit(1)

def demo_comprehensive_news_collection():
    """演示综合新闻采集"""
    print("\n" + "="*60)
    print("📰 综合新闻采集演示")
    print("="*60)
    
    llm = setup_llm()
    data_agent = create_enhanced_ashare_data_agent(llm)
    
    # 测试股票列表
    test_stocks = ["000001", "600036", "000002"]  # 平安银行、招商银行、万科A
    
    for stock_code in test_stocks:
        print(f"\n🔍 正在采集 {stock_code} 的综合新闻...")
        
        try:
            result = data_agent.get_comprehensive_stock_news(stock_code, days_back=7)
            print(f"\n📊 {stock_code} 新闻采集结果:")
            print("-" * 40)
            print(result[:1000] + "..." if len(result) > 1000 else result)
            
        except Exception as e:
            print(f"❌ {stock_code} 新闻采集失败: {str(e)}")
        
        print("\n" + "-"*40)

def demo_announcement_collection():
    """演示公告采集"""
    print("\n" + "="*60)
    print("📋 公告数据采集演示")
    print("="*60)
    
    llm = setup_llm()
    data_agent = create_enhanced_ashare_data_agent(llm)
    
    test_stock = "000001"  # 平安银行
    print(f"\n🔍 正在采集 {test_stock} 的公告数据...")
    
    try:
        result = data_agent.get_stock_announcements(test_stock, days_back=30)
        print(f"\n📊 {test_stock} 公告采集结果:")
        print("-" * 40)
        print(result[:1000] + "..." if len(result) > 1000 else result)
        
    except Exception as e:
        print(f"❌ {test_stock} 公告采集失败: {str(e)}")

def demo_interactive_qa():
    """演示互动问答采集"""
    print("\n" + "="*60)
    print("💬 互动问答采集演示")
    print("="*60)
    
    llm = setup_llm()
    data_agent = create_enhanced_ashare_data_agent(llm)
    
    test_stock = "000002"  # 万科A
    print(f"\n🔍 正在采集 {test_stock} 的互动问答...")
    
    try:
        result = data_agent.get_interactive_qa(test_stock, days_back=30)
        print(f"\n📊 {test_stock} 互动问答结果:")
        print("-" * 40)
        print(result[:1000] + "..." if len(result) > 1000 else result)
        
    except Exception as e:
        print(f"❌ {test_stock} 互动问答采集失败: {str(e)}")

def demo_market_sentiment():
    """演示市场情绪分析"""
    print("\n" + "="*60)
    print("📈 市场情绪分析演示")
    print("="*60)
    
    llm = setup_llm()
    data_agent = create_enhanced_ashare_data_agent(llm)
    
    test_keywords = ["银行", "科技", "新能源"]
    
    for keyword in test_keywords:
        print(f"\n🔍 正在分析 {keyword} 的市场情绪...")
        
        try:
            result = data_agent.get_market_sentiment_analysis(keyword, days_back=7)
            print(f"\n📊 {keyword} 市场情绪分析:")
            print("-" * 40)
            print(result[:800] + "..." if len(result) > 800 else result)
            
        except Exception as e:
            print(f"❌ {keyword} 市场情绪分析失败: {str(e)}")
        
        print("\n" + "-"*40)

def demo_industry_analysis():
    """演示行业分析"""
    print("\n" + "="*60)
    print("🏭 行业分析演示")
    print("="*60)
    
    llm = setup_llm()
    data_agent = create_enhanced_ashare_data_agent(llm)
    
    test_industries = ["银行", "医药", "新能源"]
    
    for industry in test_industries:
        print(f"\n🔍 正在分析 {industry} 行业...")
        
        try:
            result = data_agent.get_industry_analysis(industry, days_back=14)
            print(f"\n📊 {industry} 行业分析:")
            print("-" * 40)
            print(result[:800] + "..." if len(result) > 800 else result)
            
        except Exception as e:
            print(f"❌ {industry} 行业分析失败: {str(e)}")
        
        print("\n" + "-"*40)

def demo_data_search():
    """演示数据搜索"""
    print("\n" + "="*60)
    print("🔍 数据搜索演示")
    print("="*60)
    
    llm = setup_llm()
    data_agent = create_enhanced_ashare_data_agent(llm)
    
    test_queries = ["平安银行", "招商银行", "万科"]
    
    for query in test_queries:
        print(f"\n🔍 正在搜索 '{query}' 相关数据...")
        
        try:
            result = data_agent.search_stock_data(query, data_types="news,announcement,interaction")
            print(f"\n📊 '{query}' 搜索结果:")
            print("-" * 40)
            print(result[:800] + "..." if len(result) > 800 else result)
            
        except Exception as e:
            print(f"❌ '{query}' 搜索失败: {str(e)}")
        
        print("\n" + "-"*40)

def demo_quality_report():
    """演示数据质量报告"""
    print("\n" + "="*60)
    print("📊 数据质量报告演示")
    print("="*60)
    
    llm = setup_llm()
    data_agent = create_enhanced_ashare_data_agent(llm)
    
    try:
        result = data_agent.get_data_quality_report()
        print("\n📊 数据质量报告:")
        print("-" * 40)
        print(result)
        
    except Exception as e:
        print(f"❌ 数据质量报告生成失败: {str(e)}")

def demo_data_export():
    """演示数据导出"""
    print("\n" + "="*60)
    print("📤 数据导出演示")
    print("="*60)
    
    llm = setup_llm()
    data_agent = create_enhanced_ashare_data_agent(llm)
    
    try:
        output_file = f"ashare_data_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        result = data_agent.export_data_excel(output_file)
        print(f"\n📊 数据导出结果: {result}")
        
        if "成功" in result:
            print(f"✅ 数据已导出到: {output_file}")
        
    except Exception as e:
        print(f"❌ 数据导出失败: {str(e)}")

def show_system_info():
    """显示系统信息"""
    print("🚀 增强版A股数据采集系统")
    print("="*60)
    print("支持的数据源:")
    print("• 📈 巨潮信息网 - 官方公告数据")
    print("• 📰 新浪财经 - 实时财经新闻")
    print("• 💰 东方财富网 - 综合金融数据")
    print("• 📋 中国证券网 - 权威证券资讯")
    print("• 💬 深交所互动易 - 投资者互动")
    print("• 📺 第一财经 - 专业财经媒体")
    print("• 🥬 韭研公社 - 投资研究社区")
    print()
    print("系统特色:")
    print("• 🔄 不达目的不罢休的重试机制")
    print("• 🧠 LangChain智能分析和决策")
    print("• 🐙 自动搜索GitHub爬虫工具")
    print("• 📊 全面的数据质量管理")
    print("• 🗄️ 结构化数据存储系统")
    print("• 🔍 强大的数据搜索功能")
    print()

def main():
    """主函数"""
    show_system_info()
    
    # 检查必要的环境变量
    print("🔧 检查环境配置...")
    
    tushare_token = os.getenv("TUSHARE_TOKEN")
    if not tushare_token:
        print("⚠️ 建议设置 TUSHARE_TOKEN 环境变量以获得更好的数据质量")
    else:
        print("✅ Tushare配置正常")
    
    # 创建数据目录
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ 数据目录已准备: {data_dir.absolute()}")
    
    # 运行演示
    demos = [
        ("综合新闻采集", demo_comprehensive_news_collection),
        ("公告数据采集", demo_announcement_collection),
        ("互动问答采集", demo_interactive_qa),
        ("市场情绪分析", demo_market_sentiment),
        ("行业分析", demo_industry_analysis),
        ("数据搜索", demo_data_search),
        ("数据质量报告", demo_quality_report),
        ("数据导出", demo_data_export)
    ]
    
    print("\n可用的演示:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"{i}. {name}")
    print("0. 运行所有演示")
    print("q. 退出")
    
    while True:
        try:
            choice = input("\n请选择要运行的演示 (0-8, q): ").strip()
            
            if choice.lower() == 'q':
                print("👋 再见!")
                break
            elif choice == '0':
                print("\n🚀 运行所有演示...")
                for name, demo_func in demos:
                    print(f"\n⏳ 正在运行: {name}")
                    try:
                        demo_func()
                    except Exception as e:
                        print(f"❌ {name} 演示失败: {str(e)}")
                    input("\n按回车键继续...")
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(demos):
                idx = int(choice) - 1
                name, demo_func = demos[idx]
                print(f"\n⏳ 正在运行: {name}")
                try:
                    demo_func()
                except Exception as e:
                    print(f"❌ {name} 演示失败: {str(e)}")
                input("\n按回车键继续...")
            else:
                print("❌ 无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 程序错误: {str(e)}")

if __name__ == "__main__":
    main()