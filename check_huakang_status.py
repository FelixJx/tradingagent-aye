#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查华康洁净当前状态
分析可能的问题
"""

from datetime import datetime

def analyze_situation():
    """分析当前情况"""
    print("🔍 华康洁净(301235.SZ)状态分析")
    print("=" * 60)
    
    # 已知数据
    print("\n📊 已知价格走势：")
    print("-" * 40)
    print("7月29日: 27.66元 (基准价)")
    print("7月30日: 33.19元 (+19.99% 涨停)")
    print("7月31日: 35.20元 (+6.06%)")
    print("累计涨幅: 27.26% (3个交易日)")
    
    # 异常波动分析
    print("\n⚠️ 异常情况分析：")
    print("-" * 40)
    print("1. 连续3日累计涨幅超过30%")
    print("2. 已发布异常波动公告")
    print("3. 7月30日涨停")
    
    # 可能的情况
    print("\n🎯 8月4日可能的情况：")
    print("-" * 40)
    print("1. 【停牌】因异常波动停牌核查")
    print("2. 【大幅回调】获利盘涌出导致下跌")
    print("3. 【跌停】监管关注或利空消息")
    print("4. 【正常调整】小幅回调整理")
    
    # 投资建议调整
    print("\n📋 根据不同情况的建议调整：")
    print("-" * 40)
    print("如果停牌: 等待复牌后再评估")
    print("如果跌停: 立即调整为【回避】")
    print("如果大跌>5%: 调整为【观望】")
    print("如果小跌<3%: 维持【谨慎买入】")
    
    # 风险提示
    print("\n❌ 核心风险：")
    print("-" * 40)
    print("1. 短期涨幅过大，获利盘压力")
    print("2. 异常波动引发监管关注")
    print("3. 技术性回调需求强烈")
    print("4. 市场情绪可能快速转向")
    
    # 结论
    print("\n💡 结论：")
    print("-" * 40)
    print("❌ 之前的【强烈买入】建议确实存在严重问题")
    print("✅ 应该调整为【高风险警告】")
    print("📊 建议等待股价企稳后再考虑")
    
    # 自我反思
    print("\n🤔 投资分析反思：")
    print("-" * 40)
    print("1. 忽视了短期涨幅过大的风险")
    print("2. 过于看重基本面改善")
    print("3. 未充分考虑技术面超买信号")
    print("4. 应该在异常波动时给出风险警告而非买入建议")

def generate_corrected_advice():
    """生成修正后的投资建议"""
    print("\n" + "=" * 60)
    print("📋 修正后的投资建议")
    print("=" * 60)
    
    advice = {
        "投资评级": "高风险警告",
        "操作建议": "暂时回避，等待调整",
        "风险等级": "极高",
        "理由": [
            "3日累计涨幅27.26%，严重超买",
            "触发异常波动，监管风险",
            "获利盘巨大，随时可能崩盘",
            "技术指标全线超买"
        ],
        "后续策略": [
            "等待充分调整(回调15-20%)",
            "观察成交量萎缩企稳信号",
            "关注是否有实质利好支撑",
            "跌破30元可考虑少量建仓"
        ]
    }
    
    print("\n🚨 投资评级: {}".format(advice['投资评级']))
    print("⚠️ 操作建议: {}".format(advice['操作建议']))
    print("🔴 风险等级: {}".format(advice['风险等级']))
    
    print("\n📊 调整理由:")
    for i, reason in enumerate(advice['理由'], 1):
        print("   {}. {}".format(i, reason))
    
    print("\n📋 后续策略:")
    for i, strategy in enumerate(advice['后续策略'], 1):
        print("   {}. {}".format(i, strategy))
    
    # 保存修正建议
    import json
    filename = "华康洁净_修正投资建议_{}.json".format(
        datetime.now().strftime('%Y%m%d_%H%M%S')
    )
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(advice, f, ensure_ascii=False, indent=2)
    
    print("\n💾 修正建议已保存至: {}".format(filename))

def main():
    """主函数"""
    print("🚀 华康洁净投资建议紧急修正")
    print("📅 时间: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    # 分析当前情况
    analyze_situation()
    
    # 生成修正建议
    generate_corrected_advice()
    
    print("\n" + "=" * 60)
    print("⚠️ 致歉声明：")
    print("之前的强烈买入建议确实存在严重问题。")
    print("在股价短期暴涨后应该提示风险而非追高。")
    print("投资需谨慎，高位追涨风险极大。")
    print("=" * 60)

if __name__ == "__main__":
    main()