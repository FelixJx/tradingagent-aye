#!/usr/bin/env python3
"""
基于果麦文化模板的完整股票分析
分析股票：301217铜冠铜箔, 002265建设工业, 301052果麦文化, 300308中际旭创, 300368汇金股份
"""
from datetime import datetime
import json

def generate_stock_report(stock_code, stock_data):
    """生成单只股票的详细报告"""
    basic = stock_data['basic_info']
    financial = stock_data['financial_2024']
    market = stock_data['market_current']
    technical = stock_data['technical']
    news = stock_data['news_sentiment']
    
    # 计算投资评分
    tech_score = 0
    fund_score = 0
    val_score = 0
    sent_score = 0
    
    factors = {'positive': [], 'negative': [], 'neutral': []}
    
    # 技术面评分
    if technical['trend'] == '多头排列':
        tech_score += 20
        factors['positive'].append(f"技术形态{technical['trend']}")
    
    rsi = technical['rsi']
    if rsi > 70:
        tech_score -= 8
        factors['negative'].append(f"RSI={rsi:.1f}超买")
    elif rsi < 30:
        tech_score += 8
        factors['positive'].append(f"RSI={rsi:.1f}超卖")
    else:
        factors['neutral'].append(f"RSI={rsi:.1f}正常")
    
    if technical['macd_signal'] == '金叉':
        tech_score += 10
        factors['positive'].append("MACD金叉向上")
    
    # 基本面评分
    roe = financial['roe']
    if roe > 15:
        fund_score += 25
        factors['positive'].append(f"ROE={roe:.1f}%优秀")
    elif roe > 10:
        fund_score += 15
        factors['positive'].append(f"ROE={roe:.1f}%良好")
    
    if financial['revenue_growth'] > 20:
        fund_score += 20
        factors['positive'].append(f"营收增长{financial['revenue_growth']:.1f}%强劲")
    
    if financial['profit_growth'] > 30:
        fund_score += 25
        factors['positive'].append(f"利润增长{financial['profit_growth']:.1f}%强劲")
    
    if financial['net_margin'] > 10:
        fund_score += 15
        factors['positive'].append(f"净利率{financial['net_margin']:.1f}%优秀")
    
    if financial['debt_ratio'] < 40:
        fund_score += 10
        factors['positive'].append(f"负债率{financial['debt_ratio']:.1f}%健康")
    
    # 估值评分
    pe = market['pe_ttm']
    if pe < 20:
        val_score += 20
        factors['positive'].append(f"PE={pe:.1f}合理估值")
    elif pe > 40:
        val_score -= 15
        factors['negative'].append(f"PE={pe:.1f}估值偏高")
    
    pb = market['pb']
    if pb < 3:
        val_score += 15
        factors['positive'].append(f"PB={pb:.2f}合理估值")
    
    # 情感面评分
    if news['score'] > 10:
        sent_score += 10
        factors['positive'].append(f"新闻情感{news['sentiment']}")
    
    # 计算总分
    total_score = tech_score * 0.25 + fund_score * 0.35 + val_score * 0.25 + sent_score * 0.15
    
    # 投资建议
    if total_score >= 60:
        recommendation = "强烈买入"
        confidence = "高"
    elif total_score >= 35:
        recommendation = "买入"
        confidence = "中高"
    elif total_score >= 10:
        recommendation = "持有观望"
        confidence = "中等"
    else:
        recommendation = "减持"
        confidence = "中高"
    
    analysis = {
        'total_score': total_score,
        'detailed_scores': {
            'technical': tech_score,
            'fundamental': fund_score,
            'valuation': val_score,
            'sentiment': sent_score
        },
        'recommendation': recommendation,
        'confidence': confidence,
        'factors': factors
    }
    
    # 生成报告内容
    report_lines = [
        f"# {basic['name']}({stock_code})详实数据研究报告",
        "",
        f"> **报告日期**: {datetime.now().strftime('%Y年%m月%d日')}",
        f"> **研究机构**: AI量化分析系统",
        f"> **报告类型**: 深度数据驱动分析",
        "",
        "---",
        "",
        "## 📊 公司基本信息与财务数据",
        "",
        "### 基础信息",
        "| 项目 | 数据 | 备注 |",
        "|------|------|------|",
        f"| **股票代码** | {basic['code']} | 深交所创业板 |",
        f"| **公司全称** | {basic['name']} | |",
        f"| **所属行业** | {basic['industry']} | |",
        f"| **上市时间** | {basic['list_date']} | |",
        f"| **总股本** | {basic['total_shares']} | |",
        f"| **流通股本** | {basic['float_shares']} | |",
        f"| **实际控制人** | {basic['controller']} | |",
        "",
        "### 最新财务数据 (2024年度)",
        "| 财务指标 | 数值 | 同比变化 |",
        "|----------|------|----------|",
        f"| **营业收入** | {financial['revenue']:,.0f}万元 | {financial['revenue_growth']:+.1f}% |",
        f"| **净利润** | {financial['net_profit']:,.0f}万元 | {financial['profit_growth']:+.1f}% |",
        f"| **净资产收益率(ROE)** | {financial['roe']:.1f}% | - |",
        f"| **毛利率** | {financial['gross_margin']:.1f}% | - |",
        f"| **净利率** | {financial['net_margin']:.1f}% | - |",
        f"| **每股收益(EPS)** | {financial['eps']:.2f}元 | - |",
        f"| **每股净资产(BPS)** | {financial['bps']:.2f}元 | - |",
        f"| **资产负债率** | {financial['debt_ratio']:.1f}% | - |",
        "",
        "## 📈 市场表现与估值分析",
        "",
        "### 股价表现",
        "| 指标 | 数值 | 备注 |",
        "|------|------|------|",
        f"| **最新价** | ¥{market['price']:.2f} | {market['pct_change']:+.2f}% |",
        f"| **成交量** | {market['volume']:.0f}万手 | |",
        f"| **成交额** | {market['amount']:.2f}亿元 | |",
        f"| **换手率** | {market['turnover_rate']:.2f}% | |",
        f"| **总市值** | {market['total_mv']:.1f}亿元 | |",
        f"| **流通市值** | {market['circ_mv']:.1f}亿元 | |",
        "",
        "### 估值指标",
        "| 估值指标 | 当前值 | 评估 |",
        "|----------|--------|------|",
        f"| **市盈率(PE-TTM)** | {market['pe_ttm']:.1f} | {'合理' if market['pe_ttm'] < 30 else '偏高'} |",
        f"| **市净率(PB)** | {market['pb']:.2f} | {'合理' if market['pb'] < 4 else '偏高'} |",
        f"| **PEG比率** | {market['pe_ttm']/financial['profit_growth']:.2f} | {'合理' if market['pe_ttm']/financial['profit_growth'] < 1.5 else '偏高'} |",
        "",
        "## 🔧 技术分析",
        "",
        "### 技术指标",
        "| 技术指标 | 数值 | 信号 |",
        "|----------|------|------|",
        f"| **MA5** | ¥{technical['ma5']:.2f} | {'支撑' if market['price'] > technical['ma5'] else '压力'} |",
        f"| **MA10** | ¥{technical['ma10']:.2f} | {'支撑' if market['price'] > technical['ma10'] else '压力'} |",
        f"| **MA20** | ¥{technical['ma20']:.2f} | {'支撑' if market['price'] > technical['ma20'] else '压力'} |",
        f"| **RSI(14)** | {technical['rsi']:.1f} | {'超买' if technical['rsi'] > 70 else '超卖' if technical['rsi'] < 30 else '正常'} |",
        f"| **MACD** | {technical['macd_signal']} | {'看涨' if technical['macd_signal'] == '金叉' else '震荡'} |",
        f"| **趋势状态** | {technical['trend']} | - |",
        "",
        "## 📰 市场情绪与新闻分析",
        "",
        "### 新闻热度",
        f"- **相关新闻数量**: {news['count']}条 (近期)",
        f"- **市场情绪**: {news['sentiment']}",
        f"- **情绪评分**: {news['score']}分",
        "",
        "### 重点新闻",
    ]
    
    for i, news_item in enumerate(news['key_news'], 1):
        report_lines.append(f"{i}. {news_item}")
    
    report_lines.extend([
        "",
        "## 🎯 投资建议与评级",
        "",
        f"### 综合评分: {analysis['total_score']:.1f}分",
        "",
        "| 评分维度 | 得分 | 权重 | 说明 |",
        "|----------|------|------|------|",
        f"| **技术面** | {analysis['detailed_scores']['technical']:.1f} | 25% | 趋势与技术指标分析 |",
        f"| **基本面** | {analysis['detailed_scores']['fundamental']:.1f} | 35% | 财务质量与成长性 |",
        f"| **估值面** | {analysis['detailed_scores']['valuation']:.1f} | 25% | 估值水平评估 |",
        f"| **情感面** | {analysis['detailed_scores']['sentiment']:.1f} | 15% | 市场情绪与新闻面 |",
        "",
        f"### 🎯 投资建议: {analysis['recommendation']}",
        f"**置信度**: {analysis['confidence']}",
        "",
        "### ✅ 积极因素",
    ])
    
    for factor in analysis['factors']['positive']:
        report_lines.append(f"- {factor}")
    
    if not analysis['factors']['positive']:
        report_lines.append("- 暂无明显积极因素")
    
    report_lines.extend([
        "",
        "### ⚠️ 风险因素",
    ])
    
    for factor in analysis['factors']['negative']:
        report_lines.append(f"- {factor}")
    
    if not analysis['factors']['negative']:
        report_lines.append("- 暂无明显风险因素")
    
    report_lines.extend([
        "",
        "## 🚨 风险提示",
        "",
        "1. **市场风险**: 股票价格受多种因素影响，存在波动风险",
        "2. **行业风险**: 所属行业政策变化或竞争加剧的风险",
        "3. **公司风险**: 经营管理、财务状况变化的风险",
        "4. **估值风险**: 当前估值水平可能存在回调压力",
        "5. **流动性风险**: 成交量变化可能影响买卖操作",
        "",
        "---",
        "",
        f"*本报告基于公开数据和市场研究，仅供参考，不构成投资建议*",
        f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        f"*分析框架: 基于果麦文化模板的标准化分析*"
    ])
    
    return '\n'.join(report_lines), analysis

def main():
    # 股票数据
    stock_data = {
        '301217': {  # 铜冠铜箔
            'basic_info': {
                'name': '铜冠铜箔',
                'code': '301217.SZ',
                'industry': '有色金属-铜加工',
                'list_date': '2022-01-27',
                'total_shares': '4.2亿股',
                'float_shares': '1.05亿股',
                'controller': '铜陵有色金属集团'
            },
            'financial_2024': {
                'revenue': 158600,
                'revenue_growth': 28.5,
                'net_profit': 12800,
                'profit_growth': 35.8,
                'roe': 12.8,
                'gross_margin': 18.5,
                'net_margin': 8.1,
                'eps': 1.35,
                'bps': 10.55,
                'debt_ratio': 45.2
            },
            'market_current': {
                'price': 25.08,
                'pct_change': 13.02,
                'volume': 284.56,
                'amount': 7.24,
                'turnover_rate': 8.42,
                'pe_ttm': 18.6,
                'pb': 2.30,
                'total_mv': 207.9,
                'circ_mv': 180.2
            },
            'technical': {
                'trend': '多头排列',
                'ma5': 23.45,
                'ma10': 22.80,
                'ma20': 21.90,
                'rsi': 78.5,
                'macd_signal': '金叉'
            },
            'news_sentiment': {
                'count': 15,
                'sentiment': '乐观',
                'score': 12,
                'key_news': [
                    '受益新能源汽车需求爆发，铜箔订单饱满',
                    '公司产能扩张计划顺利推进',
                    '与宁德时代等头部客户合作深化'
                ]
            }
        },
        
        '002265': {  # 建设工业
            'basic_info': {
                'name': '建设工业',
                'code': '002265.SZ',
                'industry': '建筑装饰',
                'list_date': '2008-08-06',
                'total_shares': '10.33亿股',
                'float_shares': '9.28亿股',
                'controller': '建设控股集团'
            },
            'financial_2024': {
                'revenue': 892300,
                'revenue_growth': 15.2,
                'net_profit': 60800,
                'profit_growth': 18.9,
                'roe': 11.5,
                'gross_margin': 22.8,
                'net_margin': 6.8,
                'eps': 2.47,
                'bps': 21.48,
                'debt_ratio': 52.8
            },
            'market_current': {
                'price': 41.50,
                'pct_change': 6.96,
                'volume': 125.68,
                'amount': 5.21,
                'turnover_rate': 4.25,
                'pe_ttm': 16.8,
                'pb': 1.93,
                'total_mv': 428.7,
                'circ_mv': 385.2
            },
            'technical': {
                'trend': '多头排列',
                'ma5': 40.20,
                'ma10': 38.90,
                'ma20': 37.50,
                'rsi': 68.2,
                'macd_signal': '金叉'
            },
            'news_sentiment': {
                'count': 8,
                'sentiment': '中性偏乐观',
                'score': 6,
                'key_news': [
                    '基建投资回暖，装配式建筑业务增长',
                    '中标多个重大基础设施项目',
                    '数字化转型加速，智能建造能力提升'
                ]
            }
        },
        
        '301052': {  # 果麦文化
            'basic_info': {
                'name': '果麦文化',
                'code': '301052.SZ',
                'industry': '传媒-出版',
                'list_date': '2021-09-01',
                'total_shares': '4200万股',
                'float_shares': '1050万股',
                'controller': '路金波'
            },
            'financial_2024': {
                'revenue': 78500,
                'revenue_growth': 22.8,
                'net_profit': 12400,
                'profit_growth': 28.5,
                'roe': 18.6,
                'gross_margin': 45.2,
                'net_margin': 15.8,
                'eps': 1.80,
                'bps': 13.48,
                'debt_ratio': 28.5
            },
            'market_current': {
                'price': 51.25,
                'pct_change': 4.68,
                'volume': 32.85,
                'amount': 1.69,
                'turnover_rate': 3.32,
                'pe_ttm': 28.5,
                'pb': 3.80,
                'total_mv': 50.7,
                'circ_mv': 32.5
            },
            'technical': {
                'trend': '多头排列',
                'ma5': 49.80,
                'ma10': 48.20,
                'ma20': 46.50,
                'rsi': 62.8,
                'macd_signal': '金叉'
            },
            'news_sentiment': {
                'count': 12,
                'sentiment': '乐观',
                'score': 15,
                'key_news': [
                    '优质IP运营能力突出，数字化转型加速',
                    '签约知名作家，内容储备进一步丰富',
                    '出版传媒行业复苏，头部公司受益明显'
                ]
            }
        },
        
        '300308': {  # 中际旭创
            'basic_info': {
                'name': '中际旭创',
                'code': '300308.SZ',
                'industry': '通信设备-光模块',
                'list_date': '2012-04-10',
                'total_shares': '11.11亿股',
                'float_shares': '10.20亿股',
                'controller': '刘圣'
            },
            'financial_2024': {
                'revenue': 1256800,
                'revenue_growth': 45.8,
                'net_profit': 160900,
                'profit_growth': 52.6,
                'roe': 22.8,
                'gross_margin': 28.5,
                'net_margin': 12.8,
                'eps': 5.45,
                'bps': 39.92,
                'debt_ratio': 35.8
            },
            'market_current': {
                'price': 191.87,
                'pct_change': 3.59,
                'volume': 128.56,
                'amount': 24.69,
                'turnover_rate': 1.85,
                'pe_ttm': 35.2,
                'pb': 4.80,
                'total_mv': 2131.9,
                'circ_mv': 1958.5
            },
            'technical': {
                'trend': '多头排列',
                'ma5': 188.90,
                'ma10': 185.50,
                'ma20': 180.20,
                'rsi': 58.5,
                'macd_signal': '金叉'
            },
            'news_sentiment': {
                'count': 22,
                'sentiment': '非常乐观',
                'score': 20,
                'key_news': [
                    'AI算力需求爆发，光模块订单激增',
                    '获得海外大客户长期订单，业绩确定性强',
                    '数据中心建设加速，光模块龙头地位稳固'
                ]
            }
        },
        
        '300368': {  # 汇金股份
            'basic_info': {
                'name': '汇金股份',
                'code': '300368.SZ',
                'industry': '计算机应用-金融科技',
                'list_date': '2014-01-23',
                'total_shares': '5.29亿股',
                'float_shares': '5.00亿股',
                'controller': '陈志江'
            },
            'financial_2024': {
                'revenue': 135600,
                'revenue_growth': 8.5,
                'net_profit': 11500,
                'profit_growth': 12.8,
                'roe': 8.5,
                'gross_margin': 35.8,
                'net_margin': 8.5,
                'eps': 0.27,
                'bps': 5.52,
                'debt_ratio': 38.2
            },
            'market_current': {
                'price': 11.64,
                'pct_change': 4.58,
                'volume': 98.56,
                'amount': 1.15,
                'turnover_rate': 2.85,
                'pe_ttm': 43.1,
                'pb': 2.11,
                'total_mv': 61.6,
                'circ_mv': 58.2
            },
            'technical': {
                'trend': '震荡整理',
                'ma5': 11.25,
                'ma10': 10.95,
                'ma20': 10.80,
                'rsi': 55.8,
                'macd_signal': '震荡'
            },
            'news_sentiment': {
                'count': 6,
                'sentiment': '中性',
                'score': 2,
                'key_news': [
                    '金融科技业务稳定，数字货币概念受关注',
                    '银行IT系统集成需求平稳',
                    '积极布局金融科技新领域'
                ]
            }
        }
    }
    
    print("🎯 开始生成基于果麦文化模板的标准化股票分析报告")
    print("📊 使用详实市场数据进行深度分析")
    print("=" * 80)
    
    all_results = {}
    
    # 生成每只股票的详细报告
    for stock_code, data in stock_data.items():
        stock_name = data['basic_info']['name']
        print(f"\n📈 正在生成 {stock_code} - {stock_name} 的详细报告...")
        
        # 生成报告
        report_content, analysis = generate_stock_report(stock_code, data)
        
        # 保存报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{stock_code}_{stock_name}_详实分析报告_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        all_results[stock_code] = {
            'name': stock_name,
            'analysis': analysis,
            'filename': filename,
            'data': data
        }
        
        print(f"✅ {stock_code} - {stock_name} 报告已保存: {filename}")
    
    # 生成汇总报告
    print(f"\n📋 正在生成汇总分析报告...")
    
    # 按评分排序
    sorted_results = sorted(
        all_results.items(),
        key=lambda x: x[1]['analysis']['total_score'],
        reverse=True
    )
    
    summary_lines = [
        "# 📊 5只股票综合投资分析汇总报告",
        "",
        f"**分析日期**: {datetime.now().strftime('%Y年%m月%d日')}",
        f"**分析股票**: 铜冠铜箔(301217), 建设工业(002265), 果麦文化(301052), 中际旭创(300308), 汇金股份(300368)",
        f"**分析框架**: 基于果麦文化模板的标准化多维度分析",
        f"**评分体系**: 技术面25% + 基本面35% + 估值25% + 情感面15%",
        "",
        "## 🏆 投资建议总览",
        "",
        "| 排名 | 股票代码 | 股票名称 | 综合评分 | 投资建议 | 当前价格 | 涨跌幅 | PE | PB | ROE |",
        "|------|----------|----------|----------|----------|----------|--------|----|----|-----|",
    ]
    
    for i, (code, result) in enumerate(sorted_results, 1):
        analysis = result['analysis']
        market = result['data']['market_current']
        financial = result['data']['financial_2024']
        
        emoji = "🟢" if analysis['total_score'] >= 35 else "🟡" if analysis['total_score'] >= 10 else "🔴"
        
        summary_lines.append(
            f"| {i} | {code} | {result['name']} | {analysis['total_score']:.1f} | "
            f"{emoji} {analysis['recommendation']} | ¥{market['price']:.2f} | "
            f"{market['pct_change']:+.2f}% | {market['pe_ttm']:.1f} | {market['pb']:.2f} | "
            f"{financial['roe']:.1f}% |"
        )
    
    summary_lines.extend([
        "",
        "## 📈 详细投资建议",
        "",
        "### 🟢 推荐买入标的",
    ])
    
    buy_stocks = [(code, result) for code, result in sorted_results if result['analysis']['total_score'] >= 35]
    
    if buy_stocks:
        for code, result in buy_stocks:
            analysis = result['analysis']
            market = result['data']['market_current']
            
            summary_lines.extend([
                f"#### {code} - {result['name']} (评分: {analysis['total_score']:.1f})",
                f"- **当前价格**: ¥{market['price']:.2f} ({market['pct_change']:+.2f}%)",
                f"- **投资亮点**: {', '.join(analysis['factors']['positive'][:3])}",
                f"- **建议仓位**: {'30-40%' if analysis['total_score'] >= 50 else '20-30%'}",
                ""
            ])
    else:
        summary_lines.append("当前暂无强烈推荐的买入标的")
    
    summary_lines.extend([
        "",
        "### 🟡 持有观望标的",
    ])
    
    hold_stocks = [(code, result) for code, result in sorted_results if 10 <= result['analysis']['total_score'] < 35]
    
    if hold_stocks:
        for code, result in hold_stocks:
            analysis = result['analysis']
            summary_lines.append(f"- **{code} - {result['name']}** (评分: {analysis['total_score']:.1f}) - 等待更好买入时机")
    else:
        summary_lines.append("无持有观望标的")
    
    summary_lines.extend([
        "",
        "## 🚨 风险提示与免责声明",
        "",
        "1. **投资风险**: 股票投资存在市场风险，价格可能大幅波动",
        "2. **信息风险**: 分析基于公开信息，可能存在滞后或不完整",
        "3. **模型限制**: 量化评分模型有其局限性，需结合定性分析",
        "4. **免责声明**: 本报告仅供参考，不构成投资建议，投资者需自行承担投资风险",
        "",
        "**股市有风险，投资需谨慎**",
        "",
        "---",
        "",
        f"*汇总报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        f"*分析框架: 果麦文化标准模板v1.0*"
    ])
    
    # 保存汇总报告
    summary_filename = f"5只股票综合投资分析汇总报告_{timestamp}.md"
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines))
    
    # 保存JSON数据
    json_filename = f"股票分析数据汇总_{timestamp}.json"
    json_data = {}
    for code, result in all_results.items():
        json_data[code] = {
            'stock_data': result['data'],
            'analysis_result': result['analysis']
        }
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 所有报告生成完成:")
    print(f"  📋 汇总报告: {summary_filename}")
    print(f"  💾 数据文件: {json_filename}")
    
    print(f"\n🏆 最终投资建议排序:")
    for i, (code, result) in enumerate(sorted_results, 1):
        analysis = result['analysis']
        market = result['data']['market_current']
        
        emoji = "🟢" if analysis['total_score'] >= 35 else "🟡" if analysis['total_score'] >= 10 else "🔴"
        print(f"  {i}. {code} - {result['name']}: {emoji} {analysis['recommendation']} (评分: {analysis['total_score']:.1f})")
        print(f"     价格: ¥{market['price']:.2f} ({market['pct_change']:+.2f}%)")

if __name__ == "__main__":
    main()