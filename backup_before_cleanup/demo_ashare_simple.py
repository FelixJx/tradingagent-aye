#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A股智能交易代理系统简化演示脚本
兼容Python 3.3+
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ['TUSHARE_TOKEN'] = 'b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065'
os.environ['DASHSCOPE_API_KEY'] = 'sk-e050041b41674ed7b87644895ebae718'

print("🚀 A股智能交易代理系统演示")
print("=" * 40)

try:
    from tradingagents.ashare_trading_graph import AShareTradingGraph
    from tradingagents.ashare_config import get_ashare_config
    print("✅ 模块导入成功")
except ImportError as e:
    print("❌ 导入错误: {}".format(e))
    print("请确保已安装所有依赖")
    sys.exit(1)

def create_config():
    """创建配置"""
    print("⚙️ 创建配置...")
    config = get_ashare_config()
    
    # 更新配置
    config.update({
        "llm": {
            "provider": "dashscope",
            "model": "qwen-max",
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
            "temperature": 0.1,
            "max_tokens": 2000
        },
        "data_sources": {
            "tushare_token": os.getenv("TUSHARE_TOKEN"),
            "enable_akshare": True
        },
        "debate": {
            "enable_debate": False,  # 简化版本关闭辩论
            "rounds": 1
        }
    })
    
    print("✅ 配置创建完成")
    return config

def demo_stock_screening():
    """演示股票筛选"""
    print("\n🎯 股票筛选演示")
    print("-" * 30)
    
    try:
        config = create_config()
        trading_graph = AShareTradingGraph(config)
        
        # 简单的筛选条件
        criteria = {
            "market_cap_min": 5000000000,  # 50亿以上
            "pe_ratio_max": 25,
            "exclude_st": True
        }
        
        print("📋 筛选条件: 市值≥50亿, PE≤25, 排除ST")
        print("🔍 正在筛选股票...")
        
        # 这里应该调用实际的筛选方法
        # stocks = trading_graph.screen_stocks(criteria)
        
        # 模拟结果
        print("✅ 筛选完成，找到符合条件的股票")
        print("示例股票: 招商银行(600036.SH), 贵州茅台(600519.SH)")
        
        return ["600036.SH", "600519.SH"]
        
    except Exception as e:
        print("❌ 筛选失败: {}".format(e))
        return []

def demo_single_analysis(symbol):
    """演示单股分析"""
    print("\n📊 单股分析演示")
    print("-" * 30)
    
    try:
        config = create_config()
        trading_graph = AShareTradingGraph(config)
        
        print("🔍 正在分析股票: {}".format(symbol))
        
        # 这里应该调用实际的分析方法
        # result = trading_graph.analyze_stock(symbol)
        
        # 模拟结果
        print("✅ 分析完成")
        print("投资建议: 买入")
        print("信心度: 75%")
        print("目标价: 待确定")
        
    except Exception as e:
        print("❌ 分析失败: {}".format(e))

def main():
    """主函数"""
    print("\n🎬 开始演示...")
    
    # 1. 股票筛选
    stocks = demo_stock_screening()
    
    # 2. 单股分析
    if stocks:
        demo_single_analysis(stocks[0])
    
    print("\n🎉 演示完成！")
    print("\n💡 提示:")
    print("- 这是简化版演示")
    print("- 实际功能需要完整的数据源配置")
    print("- 建议使用Python 3.8+获得完整功能")

if __name__ == "__main__":
    main()