#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
海啸影响下的水产股票深度分析
分析海啸对水产行业的影响及投资机会
"""

import os
import sys
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ['TUSHARE_TOKEN'] = 'b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065'
os.environ['DASHSCOPE_API_KEY'] = 'sk-e050041b41674ed7b87644895ebae718'

from tradingagents.ashare_trading_graph import AShareTradingGraph
from tradingagents.ashare_config import get_ashare_config

def create_analysis_config():
    """创建分析配置"""
    config = get_ashare_config()
    
    config.update({
        "llm": {
            "provider": "dashscope",
            "model": "qwen-max",
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
            "temperature": 0.1,
            "max_tokens": 3000
        },
        "data_sources": {
            "tushare_token": os.getenv("TUSHARE_TOKEN"),
            "enable_akshare": True
        },
        "debate": {
            "enable_debate": True,
            "rounds": 2
        }
    })
    
    return config

def analyze_seafood_stocks():
    """分析受海啸影响的水产股票"""
    
    print("🌊 海啸影响下的水产股票深度分析")
    print("=" * 50)
    print("📅 分析时间：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("\n📌 背景：2025年7月30日俄罗斯东部8.8级地震引发海啸")
    print("影响范围：俄罗斯远东、日本、菲律宾、印尼等太平洋沿岸地区")
    print("-" * 50)
    
    # 重点分析的水产股票
    seafood_stocks = {
        "300094.SZ": "国联水产",
        "002086.SZ": "东方海洋", 
        "600257.SH": "大湖股份",
        "002069.SZ": "獐子岛",
        "600467.SH": "好当家",
        "300268.SZ": "佳沃食品",
        "002173.SZ": "创新医疗",  # 原山下湖，有珍珠养殖业务
        "002696.SZ": "百洋股份"
    }
    
    try:
        config = create_analysis_config()
        trading_graph = AShareTradingGraph(config)
        
        analysis_results = {}
        
        for symbol, name in seafood_stocks.items():
            print(f"\n🐟 正在分析 {name}({symbol})...")
            
            try:
                # 分析股票基本面和技术面
                result = trading_graph.run(
                    f"""深度分析{name}({symbol})在全球海啸频发背景下的投资价值：
                    1. 公司主营业务和产品结构
                    2. 养殖基地和产能分布（重点关注是否远离海啸影响区）
                    3. 近期财务表现和盈利能力
                    4. 当前股价走势和资金流向
                    5. 海啸对该公司的具体影响（正面或负面）
                    6. 投资建议和目标价位
                    """
                )
                
                analysis_results[symbol] = {
                    "name": name,
                    "analysis": result,
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"✅ {name} 分析完成")
                
            except Exception as e:
                print(f"❌ {name} 分析失败: {e}")
                analysis_results[symbol] = {
                    "name": name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        # 生成综合投资建议
        print("\n📊 生成综合投资建议...")
        
        comprehensive_analysis = trading_graph.run(
            f"""基于海啸对水产行业的影响，综合分析以下股票的投资价值并给出排序：
            {json.dumps(list(seafood_stocks.values()), ensure_ascii=False)}
            
            请从以下维度进行分析：
            1. 海啸影响下的受益程度排序
            2. 短期（1-3个月）投资机会
            3. 中长期（6-12个月）投资价值
            4. 风险提示和注意事项
            """
        )
        
        # 保存分析结果
        output_filename = f"海啸影响水产股票分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        final_report = {
            "analysis_time": datetime.now().isoformat(),
            "background": "2025年7月30日俄罗斯东部8.8级地震引发海啸",
            "individual_analysis": analysis_results,
            "comprehensive_analysis": comprehensive_analysis,
            "recommendations": {
                "immediate_action": "关注供给端受损带来的价格上涨机会",
                "key_factors": [
                    "产能分布远离海啸影响区",
                    "具备快速补充市场供给能力",
                    "成本转嫁能力强",
                    "资金流入明显"
                ]
            }
        }
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 分析报告已保存至：{output_filename}")
        
        # 生成投资总结
        print("\n" + "=" * 50)
        print("📈 投资建议总结")
        print("-" * 50)
        print("🎯 重点关注：")
        print("1. 国联水产(300094) - 国内水产龙头，产能分布广泛")
        print("2. 佳沃食品(300268) - 三文鱼业务受益于供给短缺")
        print("3. 好当家(600467) - 海参等高端海产品价格有望上涨")
        print("\n⚠️ 风险提示：")
        print("- 海啸影响的持续时间存在不确定性")
        print("- 需关注后续余震和次生灾害")
        print("- 部分公司可能面临原料成本上涨压力")
        
        return final_report
        
    except Exception as e:
        print(f"\n❌ 分析过程出错: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = analyze_seafood_stocks()
    
    if result:
        print("\n🎉 分析完成！请查看生成的详细报告文件。")
    else:
        print("\n❌ 分析失败，请检查配置和网络连接。")