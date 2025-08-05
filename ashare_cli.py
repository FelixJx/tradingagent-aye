#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股交易代理命令行工具
提供便捷的命令行接口进行A股分析和选股
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.ashare_trading_graph import create_ashare_trading_graph
from tradingagents.ashare_config import get_ashare_config
from tradingagents.dataflows.ashare_utils import search_ashare_stocks, get_ashare_stock_list

def setup_parser():
    """
    设置命令行参数解析器
    """
    parser = argparse.ArgumentParser(
        description="A股交易代理命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 分析单只股票
  python ashare_cli.py analyze --stock 000001
  
  # 批量分析多只股票
  python ashare_cli.py analyze --stocks 000001,000002,600036
  
  # 股票筛选
  python ashare_cli.py screen --max-stocks 10
  
  # 搜索股票
  python ashare_cli.py search --keyword 平安银行
  
  # 获取股票列表
  python ashare_cli.py list --limit 20
  
  # 使用自定义配置
  python ashare_cli.py analyze --stock 000001 --config custom_config.json
"""
    )
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 分析命令
    analyze_parser = subparsers.add_parser('analyze', help='分析股票')
    analyze_group = analyze_parser.add_mutually_exclusive_group(required=True)
    analyze_group.add_argument('--stock', type=str, help='单只股票代码')
    analyze_group.add_argument('--stocks', type=str, help='多只股票代码，用逗号分隔')
    analyze_parser.add_argument('--output', type=str, help='输出文件路径')
    analyze_parser.add_argument('--format', choices=['json', 'txt'], default='json', help='输出格式')
    
    # 筛选命令
    screen_parser = subparsers.add_parser('screen', help='股票筛选')
    screen_parser.add_argument('--max-stocks', type=int, default=10, help='最大筛选股票数量')
    screen_parser.add_argument('--min-market-cap', type=float, help='最小市值（亿元）')
    screen_parser.add_argument('--min-volume', type=float, help='最小日成交额（万元）')
    screen_parser.add_argument('--exclude-st', action='store_true', help='排除ST股票')
    screen_parser.add_argument('--output', type=str, help='输出文件路径')
    
    # 搜索命令
    search_parser = subparsers.add_parser('search', help='搜索股票')
    search_parser.add_argument('--keyword', type=str, required=True, help='搜索关键词')
    search_parser.add_argument('--limit', type=int, default=10, help='最大返回结果数')
    
    # 列表命令
    list_parser = subparsers.add_parser('list', help='获取股票列表')
    list_parser.add_argument('--limit', type=int, default=50, help='最大返回结果数')
    list_parser.add_argument('--exchange', choices=['SSE', 'SZSE'], help='交易所筛选')
    list_parser.add_argument('--board', choices=['main', 'sme', 'gem', 'star'], help='板块筛选')
    
    # 全局参数
    parser.add_argument('--config', type=str, help='自定义配置文件路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--quiet', '-q', action='store_true', help='静默模式')
    parser.add_argument('--tushare-token', type=str, help='Tushare Token')
    parser.add_argument('--dashscope-key', type=str, help='阿里云千问API密钥')
    
    return parser

def load_config(config_path: Optional[str] = None) -> Dict:
    """
    加载配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                custom_config = json.load(f)
            
            # 合并默认配置
            config = get_ashare_config()
            config.update(custom_config)
            return config
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return get_ashare_config()
    else:
        return get_ashare_config()

def setup_environment(args):
    """
    设置环境变量
    
    Args:
        args: 命令行参数
    """
    # 设置Tushare Token
    if args.tushare_token:
        os.environ["TUSHARE_TOKEN"] = args.tushare_token
    elif not os.getenv("TUSHARE_TOKEN"):
        print("警告: 未设置Tushare Token，部分功能可能不可用")
    
    # 设置阿里云千问API密钥
    if args.dashscope_key:
        os.environ["DASHSCOPE_API_KEY"] = args.dashscope_key
    elif not os.getenv("DASHSCOPE_API_KEY"):
        print("警告: 未设置阿里云千问API密钥，将使用默认LLM")

def analyze_command(args, config):
    """
    执行分析命令
    
    Args:
        args: 命令行参数
        config: 配置字典
    """
    try:
        # 创建交易代理图
        if not args.quiet:
            print("正在初始化A股交易代理图...")
        
        trading_graph = create_ashare_trading_graph(config)
        
        if not args.quiet:
            print("初始化完成")
        
        results = []
        
        if args.stock:
            # 分析单只股票
            if not args.quiet:
                print(f"正在分析股票: {args.stock}")
            
            result = trading_graph.analyze_stock(args.stock)
            results.append(result)
            
        elif args.stocks:
            # 分析多只股票
            stock_list = [s.strip() for s in args.stocks.split(',')]
            
            if not args.quiet:
                print(f"正在批量分析 {len(stock_list)} 只股票...")
            
            results = trading_graph.batch_analyze(stock_list)
        
        # 输出结果
        output_results(results, args)
        
    except Exception as e:
        print(f"分析失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def screen_command(args, config):
    """
    执行筛选命令
    
    Args:
        args: 命令行参数
        config: 配置字典
    """
    try:
        # 创建交易代理图
        if not args.quiet:
            print("正在初始化A股交易代理图...")
        
        trading_graph = create_ashare_trading_graph(config)
        
        # 构建筛选条件
        criteria = {}
        if args.min_market_cap:
            criteria['min_market_cap'] = args.min_market_cap * 100000000  # 转换为元
        if args.min_volume:
            criteria['min_volume'] = args.min_volume * 10000  # 转换为元
        if args.exclude_st:
            criteria['exclude_st'] = True
        
        # 执行筛选
        if not args.quiet:
            print(f"正在筛选股票（最多{args.max_stocks}只）...")
        
        stock_list = trading_graph.screen_stocks(criteria)
        
        # 批量分析筛选出的股票
        if stock_list:
            selected_stocks = [stock['symbol'] for stock in stock_list[:args.max_stocks]]
            results = trading_graph.batch_analyze(selected_stocks, args.max_stocks)
            
            # 输出结果
            output_results(results, args)
        else:
            print("未找到符合条件的股票")
        
    except Exception as e:
        print(f"筛选失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def search_command(args, config):
    """
    执行搜索命令
    
    Args:
        args: 命令行参数
        config: 配置字典
    """
    try:
        if not args.quiet:
            print(f"正在搜索: {args.keyword}")
        
        results = search_ashare_stocks(args.keyword)
        
        if results:
            print(f"找到 {len(results)} 个结果:")
            for i, stock in enumerate(results[:args.limit]):
                print(f"{i+1:2d}. {stock.get('symbol', 'N/A'):8s} {stock.get('name', 'N/A')}")
        else:
            print("未找到匹配的股票")
        
    except Exception as e:
        print(f"搜索失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def list_command(args, config):
    """
    执行列表命令
    
    Args:
        args: 命令行参数
        config: 配置字典
    """
    try:
        if not args.quiet:
            print("正在获取股票列表...")
        
        stock_list = get_ashare_stock_list()
        
        # 应用筛选条件
        if args.exchange:
            stock_list = [s for s in stock_list if s.get('exchange') == args.exchange]
        
        if args.board:
            stock_list = [s for s in stock_list if s.get('board') == args.board]
        
        # 输出结果
        if stock_list:
            print(f"股票列表（显示前{min(len(stock_list), args.limit)}只）:")
            print(f"{'序号':>4} {'代码':>8} {'名称':>12} {'交易所':>6} {'板块':>6}")
            print("-" * 50)
            
            for i, stock in enumerate(stock_list[:args.limit]):
                print(f"{i+1:4d} {stock.get('symbol', 'N/A'):>8s} {stock.get('name', 'N/A'):>12s} "
                      f"{stock.get('exchange', 'N/A'):>6s} {stock.get('board', 'N/A'):>6s}")
        else:
            print("未找到股票")
        
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def output_results(results: List[Dict], args):
    """
    输出分析结果
    
    Args:
        results: 分析结果列表
        args: 命令行参数
    """
    if not results:
        print("没有分析结果")
        return
    
    # 准备输出内容
    if args.format == 'json':
        output_content = json.dumps(results, ensure_ascii=False, indent=2)
    else:
        # 文本格式
        output_lines = []
        output_lines.append(f"A股分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append("=" * 60)
        
        for i, result in enumerate(results):
            if "error" in result:
                output_lines.append(f"\n{i+1}. {result.get('stock_symbol', 'Unknown')}: 分析失败")
                output_lines.append(f"   错误: {result['error']}")
            else:
                output_lines.append(f"\n{i+1}. {result.get('stock_symbol', 'Unknown')} - {result.get('stock_name', '')}")
                output_lines.append(f"   分析日期: {result.get('analysis_date', 'N/A')}")
                
                if 'risk_assessment' in result:
                    output_lines.append("   风险评估:")
                    # 简化显示风险评估内容
                    risk_lines = result['risk_assessment'].split('\n')[:10]
                    for line in risk_lines:
                        if line.strip():
                            output_lines.append(f"     {line.strip()}")
        
        output_content = '\n'.join(output_lines)
    
    # 输出到文件或控制台
    if args.output:
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_content)
            
            if not args.quiet:
                print(f"结果已保存到: {args.output}")
        except Exception as e:
            print(f"保存文件失败: {e}")
            print("\n结果输出:")
            print(output_content)
    else:
        print("\n分析结果:")
        print(output_content)

def main():
    """
    主函数
    """
    parser = setup_parser()
    args = parser.parse_args()
    
    # 检查命令
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 设置环境
    setup_environment(args)
    
    # 加载配置
    config = load_config(args.config)
    
    if args.verbose:
        print(f"使用配置: LLM={config['llm_provider']}, 模型={config['quick_think_llm']}")
    
    # 执行命令
    try:
        if args.command == 'analyze':
            analyze_command(args, config)
        elif args.command == 'screen':
            screen_command(args, config)
        elif args.command == 'search':
            search_command(args, config)
        elif args.command == 'list':
            list_command(args, config)
        else:
            print(f"未知命令: {args.command}")
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"执行命令时出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()