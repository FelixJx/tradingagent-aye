#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股智能交易代理系统演示脚本

本脚本演示如何使用A股交易代理系统进行：
1. 单只股票分析
2. 股票筛选
3. 批量分析
4. 投资组合构建

作者: TradingAgents Team
日期: 2024-12-20
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tradingagents.ashare_trading_graph import AShareTradingGraph
    from tradingagents.ashare_config import get_ashare_config
    from tradingagents.dataflows.ashare_utils import (
        get_ashare_stock_list,
        search_ashare_stocks
    )
except ImportError as e:
    print("导入错误: {}".format(e))
    print("请确保已安装所有依赖: pip install -r requirements_ashare.txt")
    sys.exit(1)


def setup_environment():
    """设置环境变量和API密钥"""
    print("🔧 设置环境变量...")
    
    # 检查必需的API密钥
    required_keys = {
        "TUSHARE_TOKEN": "Tushare数据源API密钥",
        "DASHSCOPE_API_KEY": "阿里云千问模型API密钥"
    }
    
    missing_keys = []
    for key, description in required_keys.items():
        if not os.getenv(key):
            missing_keys.append(f"{key} ({description})")
    
    if missing_keys:
        print("❌ 缺少以下环境变量:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\n请设置环境变量后重新运行:")
        print("export TUSHARE_TOKEN='your_tushare_token'")
        print("export DASHSCOPE_API_KEY='your_dashscope_api_key'")
        return False
    
    print("✅ 环境变量配置完成")
    return True


def create_ashare_config() -> Dict[str, Any]:
    """创建A股专用配置"""
    print("⚙️ 创建A股配置...")
    
    config = get_ashare_config()
    
    # 自定义配置
    config.update({
        "llm": {
            "provider": "dashscope",
            "model": "qwen-max",
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
            "temperature": 0.1,
            "max_tokens": 4000
        },
        "data_sources": {
            "tushare_token": os.getenv("TUSHARE_TOKEN"),
            "enable_akshare": True,
            "enable_sina_news": True,
            "enable_cls_news": True
        },
        "debate": {
            "enable_debate": True,
            "rounds": 2,
            "max_agents_per_round": 3
        },
        "risk_management": {
            "max_position_size": 0.1,
            "stop_loss_threshold": 0.08,
            "risk_free_rate": 0.03
        },
        "analysis": {
            "lookback_days": 30,
            "technical_indicators": ["SMA", "EMA", "RSI", "MACD", "BOLL"],
            "fundamental_metrics": ["PE", "PB", "ROE", "ROA", "DEBT_RATIO"]
        }
    })
    
    print("✅ A股配置创建完成")
    return config


def demo_single_stock_analysis(trading_graph: AShareTradingGraph):
    """演示单只股票分析"""
    print("\n" + "="*60)
    print("📊 单只股票分析演示")
    print("="*60)
    
    # 分析招商银行
    stock_symbol = "600036.SH"
    stock_name = "招商银行"
    
    print(f"\n🔍 正在分析 {stock_name}({stock_symbol})...")
    
    try:
        result = trading_graph.analyze_stock(stock_symbol)
        
        print(f"\n📈 {stock_name} 分析结果:")
        print("-" * 40)
        
        if isinstance(result, dict):
            # 提取关键信息
            decision = result.get('final_decision', {})
            recommendation = decision.get('recommendation', '未知')
            confidence = decision.get('confidence', 0)
            target_price = decision.get('target_price', '未设定')
            
            print(f"投资建议: {recommendation}")
            print(f"信心度: {confidence:.1%}")
            print(f"目标价: {target_price}")
            
            # 显示主要分析要点
            if 'analysis_summary' in result:
                summary = result['analysis_summary']
                print(f"\n主要分析要点:")
                for point in summary.get('key_points', [])[:3]:
                    print(f"  • {point}")
        else:
            print(result)
            
    except Exception as e:
        print(f"❌ 分析失败: {e}")


def demo_stock_screening(trading_graph: AShareTradingGraph):
    """演示股票筛选功能"""
    print("\n" + "="*60)
    print("🎯 股票筛选演示")
    print("="*60)
    
    # 定义筛选条件
    screening_criteria = {
        "market_cap_min": 10000000000,  # 100亿市值以上
        "pe_ratio_max": 30,             # PE小于30
        "pe_ratio_min": 5,              # PE大于5
        "roe_min": 0.1,                 # ROE大于10%
        "debt_ratio_max": 0.6,          # 负债率小于60%
        "exclude_st": True,             # 排除ST股票
        "exclude_suspended": True,      # 排除停牌股票
        "volume_ratio_min": 1.0         # 量比大于1
    }
    
    print("\n📋 筛选条件:")
    print(f"  • 市值: ≥{screening_criteria['market_cap_min']/100000000:.0f}亿")
    print(f"  • PE: {screening_criteria['pe_ratio_min']}-{screening_criteria['pe_ratio_max']}")
    print(f"  • ROE: ≥{screening_criteria['roe_min']:.1%}")
    print(f"  • 负债率: ≤{screening_criteria['debt_ratio_max']:.1%}")
    print(f"  • 排除ST和停牌股票")
    
    try:
        print("\n🔍 正在筛选股票...")
        screened_stocks = trading_graph.screen_stocks(screening_criteria)
        
        print(f"\n✅ 筛选完成，共找到 {len(screened_stocks)} 只符合条件的股票:")
        print("-" * 50)
        
        # 显示前10只股票
        for i, stock in enumerate(screened_stocks[:10], 1):
            symbol = stock.get('symbol', '未知')
            name = stock.get('name', '未知')
            market_cap = stock.get('market_cap', 0) / 100000000  # 转换为亿
            pe = stock.get('pe_ratio', 0)
            roe = stock.get('roe', 0)
            
            print(f"{i:2d}. {name}({symbol}) - 市值:{market_cap:.0f}亿 PE:{pe:.1f} ROE:{roe:.1%}")
        
        if len(screened_stocks) > 10:
            print(f"    ... 还有 {len(screened_stocks) - 10} 只股票")
            
        return screened_stocks[:5]  # 返回前5只用于批量分析
        
    except Exception as e:
        print(f"❌ 筛选失败: {e}")
        return []


def demo_batch_analysis(trading_graph: AShareTradingGraph, stocks: List[Dict]):
    """演示批量分析功能"""
    if not stocks:
        print("\n⚠️ 没有股票可供批量分析")
        return
    
    print("\n" + "="*60)
    print("📊 批量分析演示")
    print("="*60)
    
    stock_symbols = [stock['symbol'] for stock in stocks]
    print(f"\n🔍 正在批量分析 {len(stock_symbols)} 只股票...")
    
    try:
        batch_results = trading_graph.batch_analyze(stock_symbols)
        
        print("\n📈 批量分析结果:")
        print("-" * 60)
        
        for symbol, result in batch_results.items():
            stock_name = next((s['name'] for s in stocks if s['symbol'] == symbol), '未知')
            
            if isinstance(result, dict) and 'final_decision' in result:
                decision = result['final_decision']
                recommendation = decision.get('recommendation', '未知')
                confidence = decision.get('confidence', 0)
                
                print(f"{stock_name}({symbol}): {recommendation} (信心度: {confidence:.1%})")
            else:
                print(f"{stock_name}({symbol}): 分析失败")
                
    except Exception as e:
        print(f"❌ 批量分析失败: {e}")


def demo_portfolio_construction(trading_graph: AShareTradingGraph):
    """演示投资组合构建"""
    print("\n" + "="*60)
    print("💼 投资组合构建演示")
    print("="*60)
    
    # 定义不同策略的股票池
    strategies = {
        "价值投资": {
            "pe_ratio_max": 15,
            "pb_ratio_max": 2,
            "roe_min": 0.15,
            "debt_ratio_max": 0.4
        },
        "成长投资": {
            "revenue_growth_min": 0.2,
            "profit_growth_min": 0.3,
            "market_cap_min": 5000000000
        },
        "政策受益": {
            "industries": ["新能源", "半导体", "生物医药"],
            "exclude_st": True,
            "volume_ratio_min": 1.2
        }
    }
    
    portfolio = {}
    
    for strategy_name, criteria in strategies.items():
        print(f"\n🎯 {strategy_name}策略筛选...")
        
        try:
            stocks = trading_graph.screen_stocks(criteria)
            portfolio[strategy_name] = stocks[:3]  # 每个策略选3只股票
            
            print(f"  选中 {len(portfolio[strategy_name])} 只股票:")
            for stock in portfolio[strategy_name]:
                name = stock.get('name', '未知')
                symbol = stock.get('symbol', '未知')
                print(f"    • {name}({symbol})")
                
        except Exception as e:
            print(f"  ❌ {strategy_name}策略筛选失败: {e}")
            portfolio[strategy_name] = []
    
    # 保存投资组合
    portfolio_file = f"ashare_portfolio_{datetime.now().strftime('%Y%m%d')}.json"
    try:
        with open(portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(portfolio, f, ensure_ascii=False, indent=2)
        print(f"\n💾 投资组合已保存到: {portfolio_file}")
    except Exception as e:
        print(f"❌ 保存投资组合失败: {e}")


def demo_search_stocks():
    """演示股票搜索功能"""
    print("\n" + "="*60)
    print("🔍 股票搜索演示")
    print("="*60)
    
    search_terms = ["招商银行", "茅台", "比亚迪", "宁德时代"]
    
    for term in search_terms:
        print(f"\n🔍 搜索: {term}")
        try:
            results = search_ashare_stocks(term)
            if results:
                for result in results[:3]:  # 显示前3个结果
                    symbol = result.get('symbol', '未知')
                    name = result.get('name', '未知')
                    industry = result.get('industry', '未知')
                    print(f"  • {name}({symbol}) - {industry}")
            else:
                print(f"  未找到相关股票")
        except Exception as e:
            print(f"  ❌ 搜索失败: {e}")


def main():
    """主函数"""
    print("🚀 A股智能交易代理系统演示")
    print("=" * 60)
    
    # 1. 设置环境
    if not setup_environment():
        return
    
    # 2. 创建配置
    config = create_ashare_config()
    
    # 3. 初始化交易图
    print("\n🤖 初始化A股交易代理...")
    try:
        trading_graph = AShareTradingGraph(config)
        print("✅ A股交易代理初始化完成")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 4. 演示功能
    try:
        # 股票搜索演示
        demo_search_stocks()
        
        # 单只股票分析演示
        demo_single_stock_analysis(trading_graph)
        
        # 股票筛选演示
        screened_stocks = demo_stock_screening(trading_graph)
        
        # 批量分析演示
        if screened_stocks:
            demo_batch_analysis(trading_graph, screened_stocks)
        
        # 投资组合构建演示
        demo_portfolio_construction(trading_graph)
        
        print("\n" + "="*60)
        print("🎉 演示完成！")
        print("="*60)
        print("\n📚 更多功能请参考:")
        print("  • 详细文档: README_ASHARE.md")
        print("  • 命令行工具: python ashare_cli.py --help")
        print("  • 主程序: python ashare_main.py")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()