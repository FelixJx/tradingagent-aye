#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股交易代理主程序
演示如何使用A股交易代理图进行股票分析和选股
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.ashare_trading_graph import create_ashare_trading_graph
from tradingagents.ashare_config import get_ashare_config
from tradingagents.dataflows.ashare_utils import search_ashare_stocks, get_ashare_stock_list

def setup_environment():
    """
    设置环境变量
    """
    # 设置Tushare Token（请替换为您的实际token）
    if not os.getenv("TUSHARE_TOKEN"):
        # 这里使用用户提供的token
        tushare_token = "your_tushare_token_here"  # 请替换为实际token
        os.environ["TUSHARE_TOKEN"] = tushare_token
        print(f"已设置Tushare Token: {tushare_token[:10]}...")
    
    # 设置阿里云千问API密钥（请替换为您的实际密钥）
    if not os.getenv("DASHSCOPE_API_KEY"):
        # 这里使用用户提供的API密钥
        dashscope_key = "your_dashscope_api_key_here"  # 请替换为实际密钥
        os.environ["DASHSCOPE_API_KEY"] = dashscope_key
        print(f"已设置DashScope API Key: {dashscope_key[:10]}...")

def create_custom_ashare_config():
    """
    创建自定义A股配置
    """
    config = get_ashare_config()
    
    # 自定义配置
    config.update({
        # 使用阿里云千问模型
        "llm_provider": "dashscope",
        "deep_think_llm": "qwen-max",
        "quick_think_llm": "qwen-turbo",
        
        # 辩论轮数
        "max_debate_rounds": 2,
        
        # 启用在线工具
        "online_tools": True,
        
        # 风险管理配置
        "risk_management": {
            "max_position_size": 0.15,  # 单只股票最大仓位15%
            "stop_loss_threshold": 0.08,  # 8%止损
            "profit_taking_threshold": 0.25,  # 25%止盈
        },
        
        # 股票筛选配置
        "stock_universe": {
            "include_st": False,
            "min_market_cap": 2000000000,  # 最小市值20亿
            "min_daily_volume": 20000000,  # 最小日成交额2000万
        }
    })
    
    return config

def analyze_single_stock(trading_graph, stock_code: str):
    """
    分析单只股票
    
    Args:
        trading_graph: 交易代理图实例
        stock_code: 股票代码
    """
    print(f"\n{'='*60}")
    print(f"开始分析股票: {stock_code}")
    print(f"{'='*60}")
    
    try:
        # 搜索股票信息
        stock_info = search_ashare_stocks(stock_code)
        if stock_info:
            stock_name = stock_info[0].get('name', '')
            print(f"股票信息: {stock_code} - {stock_name}")
        else:
            stock_name = ""
            print(f"未找到股票 {stock_code} 的详细信息，继续分析...")
        
        # 执行分析
        result = trading_graph.analyze_stock(stock_code, stock_name)
        
        # 输出结果
        if "error" in result:
            print(f"分析失败: {result['error']}")
        else:
            print("\n分析完成！")
            print(f"股票代码: {result.get('stock_symbol', stock_code)}")
            print(f"股票名称: {result.get('stock_name', stock_name)}")
            print(f"分析日期: {result.get('analysis_date', datetime.now().strftime('%Y-%m-%d'))}")
            
            # 输出风险评估
            if 'risk_assessment' in result:
                print("\n=== 风险管理评估 ===")
                print(result['risk_assessment'])
            
            # 保存结果到文件
            save_analysis_result(result, stock_code)
    
    except Exception as e:
        print(f"分析过程中出现错误: {e}")

def screen_and_analyze_stocks(trading_graph, max_stocks: int = 5):
    """
    筛选并分析股票
    
    Args:
        trading_graph: 交易代理图实例
        max_stocks: 最大分析股票数量
    """
    print(f"\n{'='*60}")
    print(f"开始股票筛选和批量分析（最多{max_stocks}只）")
    print(f"{'='*60}")
    
    try:
        # 获取股票列表
        print("正在获取A股股票列表...")
        stock_list = get_ashare_stock_list()
        
        if not stock_list:
            print("未能获取股票列表")
            return
        
        print(f"获取到 {len(stock_list)} 只股票")
        
        # 简单筛选：选择前几只股票进行演示
        selected_stocks = [stock['symbol'] for stock in stock_list[:max_stocks]]
        print(f"选择分析的股票: {selected_stocks}")
        
        # 批量分析
        results = trading_graph.batch_analyze(selected_stocks, max_stocks)
        
        # 输出批量分析结果
        print("\n=== 批量分析结果汇总 ===")
        for i, result in enumerate(results):
            if "error" in result:
                print(f"{i+1}. {result.get('stock_symbol', 'Unknown')}: 分析失败 - {result['error']}")
            else:
                print(f"{i+1}. {result.get('stock_symbol', 'Unknown')} - {result.get('stock_name', '')}: 分析完成")
        
        # 保存批量分析结果
        save_batch_results(results)
        
    except Exception as e:
        print(f"筛选和分析过程中出现错误: {e}")

def save_analysis_result(result: Dict, stock_code: str):
    """
    保存分析结果到文件
    
    Args:
        result: 分析结果
        stock_code: 股票代码
    """
    try:
        # 创建结果目录
        results_dir = "ashare_results"
        os.makedirs(results_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{results_dir}/{stock_code}_{timestamp}.json"
        
        # 保存结果
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"分析结果已保存到: {filename}")
        
    except Exception as e:
        print(f"保存结果失败: {e}")

def save_batch_results(results: List[Dict]):
    """
    保存批量分析结果
    
    Args:
        results: 批量分析结果列表
    """
    try:
        # 创建结果目录
        results_dir = "ashare_results"
        os.makedirs(results_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{results_dir}/batch_analysis_{timestamp}.json"
        
        # 保存结果
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"批量分析结果已保存到: {filename}")
        
    except Exception as e:
        print(f"保存批量结果失败: {e}")

def interactive_mode(trading_graph):
    """
    交互模式
    
    Args:
        trading_graph: 交易代理图实例
    """
    print("\n进入交互模式，输入 'quit' 退出")
    
    while True:
        try:
            user_input = input("\n请输入股票代码（如 000001）或命令: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("退出交互模式")
                break
            
            if user_input.lower() == 'screen':
                # 筛选模式
                max_stocks = input("请输入要分析的股票数量（默认5）: ").strip()
                try:
                    max_stocks = int(max_stocks) if max_stocks else 5
                except ValueError:
                    max_stocks = 5
                
                screen_and_analyze_stocks(trading_graph, max_stocks)
                continue
            
            if user_input.lower() == 'help':
                print("可用命令:")
                print("  - 输入股票代码（如 000001）: 分析单只股票")
                print("  - screen: 进入筛选模式")
                print("  - help: 显示帮助")
                print("  - quit/exit/q: 退出")
                continue
            
            if user_input:
                # 分析单只股票
                analyze_single_stock(trading_graph, user_input)
            
        except KeyboardInterrupt:
            print("\n用户中断，退出交互模式")
            break
        except Exception as e:
            print(f"处理输入时出错: {e}")

def main():
    """
    主函数
    """
    print("A股交易代理系统")
    print("=" * 50)
    
    # 设置环境
    setup_environment()
    
    # 创建自定义配置
    config = create_custom_ashare_config()
    print("\n配置信息:")
    print(f"LLM提供商: {config['llm_provider']}")
    print(f"深度思考模型: {config['deep_think_llm']}")
    print(f"快速思考模型: {config['quick_think_llm']}")
    print(f"最大辩论轮数: {config['max_debate_rounds']}")
    print(f"在线工具: {config['online_tools']}")
    
    try:
        # 创建交易代理图
        print("\n正在初始化A股交易代理图...")
        trading_graph = create_ashare_trading_graph(config)
        print("A股交易代理图初始化成功！")
        
        # 演示模式选择
        print("\n请选择运行模式:")
        print("1. 分析单只股票")
        print("2. 股票筛选和批量分析")
        print("3. 交互模式")
        
        choice = input("请输入选择 (1/2/3): ").strip()
        
        if choice == "1":
            # 单股票分析模式
            stock_code = input("请输入股票代码（如 000001）: ").strip()
            if stock_code:
                analyze_single_stock(trading_graph, stock_code)
            else:
                print("未输入股票代码")
        
        elif choice == "2":
            # 批量分析模式
            max_stocks_input = input("请输入要分析的股票数量（默认5）: ").strip()
            try:
                max_stocks = int(max_stocks_input) if max_stocks_input else 5
            except ValueError:
                max_stocks = 5
            
            screen_and_analyze_stocks(trading_graph, max_stocks)
        
        elif choice == "3":
            # 交互模式
            interactive_mode(trading_graph)
        
        else:
            print("无效选择，使用默认单股票分析模式")
            # 默认分析平安银行
            analyze_single_stock(trading_graph, "000001")
    
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n程序结束")

if __name__ == "__main__":
    main()