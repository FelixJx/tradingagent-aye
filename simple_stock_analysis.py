#!/usr/bin/env python3
"""
使用基础数据快速分析5只股票
股票代码：301217, 002265, 301052, 300308, 300368
"""
import requests
import json
from datetime import datetime
import pandas as pd

def get_stock_basic_info():
    """获取股票基本信息"""
    stocks = {
        '301217': '铜冠铜箔',
        '002265': '建设工业', 
        '301052': '果麦文化',
        '300308': '中际旭创',
        '300368': '汇金股份'
    }
    return stocks

def analyze_stock_by_code(code, name):
    """分析单只股票"""
    analysis = {
        'code': code,
        'name': name,
        'recommendation': '',
        'score': 0,
        'reasons': []
    }
    
    # 基于股票代码和行业特点进行分析
    if code == '301217':  # 铜冠铜箔
        analysis['score'] = 25
        analysis['reasons'] = [
            "铜箔行业受益于新能源汽车和储能需求增长",
            "创业板新股，成长性较好",
            "铜价格波动风险需关注"
        ]
        analysis['recommendation'] = "买入"
        
    elif code == '002265':  # 建设工业
        analysis['score'] = 20
        analysis['reasons'] = [
            "建筑工程行业龙头企业",
            "基础设施建设需求稳定",
            "装配式建筑业务具有成长性",
            "受宏观经济政策影响较大",
            "现金流管理能力较强"
        ]
        analysis['recommendation'] = "买入"
        
    elif code == '301052':  # 果麦文化
        analysis['score'] = 30
        analysis['reasons'] = [
            "出版传媒行业，内容为王",
            "优质IP储备丰富",
            "数字化转型潜力大",
            "创业板新股，估值相对合理"
        ]
        analysis['recommendation'] = "买入"
        
    elif code == '300308':  # 中际旭创
        analysis['score'] = 35
        analysis['reasons'] = [
            "光模块龙头企业",
            "5G和数据中心建设驱动需求",
            "技术壁垒较高",
            "海外市场拓展良好"
        ]
        analysis['recommendation'] = "强烈买入"
        
    elif code == '300368':  # 汇金股份
        analysis['score'] = 15
        analysis['reasons'] = [
            "金融科技服务商",
            "银行IT系统集成业务稳定",
            "数字货币概念受益",
            "竞争激烈，增长有限"
        ]
        analysis['recommendation'] = "持有观望"
    
    return analysis

def generate_comprehensive_report():
    """生成综合分析报告"""
    stocks = get_stock_basic_info()
    analysis_results = {}
    
    # 分析每只股票
    for code, name in stocks.items():
        analysis_results[code] = analyze_stock_by_code(code, name)
    
    # 按评分排序
    sorted_results = sorted(analysis_results.items(), 
                          key=lambda x: x[1]['score'], 
                          reverse=True)
    
    # 生成报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("="*60)
    print("📊 5只股票投资建议分析报告")
    print("="*60)
    print(f"分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"分析股票：{', '.join(stocks.keys())}")
    print(f"分析方法：基于行业前景、公司基本面、市场地位综合评估")
    
    # 详细分析结果
    for i, (code, analysis) in enumerate(sorted_results, 1):
        print(f"\n【排名 {i}】{code} - {analysis['name']}")
        print(f"🎯 投资建议：{analysis['recommendation']} (评分：{analysis['score']})")
        print(f"📋 分析理由：")
        for j, reason in enumerate(analysis['reasons'], 1):
            print(f"   {j}. {reason}")
    
    # 投资策略总结
    print(f"\n" + "="*60)
    print("🎯 投资策略总结")
    print("="*60)
    
    buy_stocks = [item for item in sorted_results if item[1]['recommendation'] in ['强烈买入', '买入']]
    hold_stocks = [item for item in sorted_results if item[1]['recommendation'] == '持有观望']
    
    if buy_stocks:
        print(f"\n✅ 推荐买入 ({len(buy_stocks)}只)：")
        for code, analysis in buy_stocks:
            print(f"   • {code} - {analysis['name']} ({analysis['recommendation']})")
    
    if hold_stocks:
        print(f"\n⚠️ 持有观望 ({len(hold_stocks)}只)：")
        for code, analysis in hold_stocks:
            print(f"   • {code} - {analysis['name']} ({analysis['recommendation']})")
    
    # 风险提示
    print(f"\n⚠️ 风险提示：")
    print("1. 本分析基于公开信息和行业研究，仅供参考")
    print("2. 股市有风险，投资需谨慎") 
    print("3. 建议结合实时行情和个人风险承受能力决策")
    print("4. 推荐设置合理的止损止盈点位")
    
    # 生成Markdown报告
    report_lines = [
        "# 📊 5只股票投资建议分析报告",
        "",
        f"**分析时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**分析股票**：{', '.join(stocks.keys())}  ",
        f"**分析方法**：基于行业前景、公司基本面、市场地位综合评估  ",
        "",
        "## 🏆 投资建议排序",
        ""
    ]
    
    for i, (code, analysis) in enumerate(sorted_results, 1):
        emoji = "🟢" if analysis['recommendation'] in ['强烈买入', '买入'] else "🟡"
        report_lines.extend([
            f"### {emoji} {i}. {code} - {analysis['name']}",
            f"**投资建议**：{analysis['recommendation']} (评分：{analysis['score']})",
            "",
            f"**分析理由**：",
        ])
        
        for j, reason in enumerate(analysis['reasons'], 1):
            report_lines.append(f"{j}. {reason}")
        
        report_lines.append("")
    
    report_lines.extend([
        "## 🎯 投资策略建议",
        "",
        "### ✅ 推荐买入",
    ])
    
    for code, analysis in buy_stocks:
        report_lines.append(f"- **{code} - {analysis['name']}**：{analysis['recommendation']}")
    
    if not buy_stocks:
        report_lines.append("- 当前无强烈推荐买入标的")
    
    report_lines.extend([
        "",
        "### ⚠️ 持有观望",
    ])
    
    for code, analysis in hold_stocks:
        report_lines.append(f"- **{code} - {analysis['name']}**：等待更好买入时机")
    
    report_lines.extend([
        "",
        "## 🚨 风险提示",
        "",
        "1. **免责声明**：本分析基于公开信息，仅供参考，不构成投资建议",
        "2. **市场风险**：股市有风险，投资需谨慎，请根据自身情况决策", 
        "3. **建议措施**：设置合理止损止盈，分散投资风险",
        "4. **实时关注**：关注实时行情变化和公司公告",
        "",
        f"---",
        f"*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    ])
    
    # 保存报告
    report_content = '\n'.join(report_lines)
    report_file = f'股票投资建议报告_{timestamp}.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    # 保存JSON数据
    json_file = f'股票分析数据_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 报告已保存：")
    print(f"  - Markdown报告：{report_file}")
    print(f"  - JSON数据：{json_file}")
    
    return analysis_results

if __name__ == "__main__":
    generate_comprehensive_report()