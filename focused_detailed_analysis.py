#!/usr/bin/env python3
"""
专注的详细股票分析 - 使用真实数据多维度分析
股票代码：301217, 002265, 301052, 300308, 300368
"""
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

class FocusedDetailedAnalyzer:
    def __init__(self, stock_codes):
        self.stock_codes = stock_codes
        self.stock_names = {}
        self.analysis_results = {}
        
    def get_comprehensive_data(self):
        """获取综合数据"""
        print("🔍 获取5只股票的综合数据...")
        print("=" * 60)
        
        all_data = {}
        
        # 获取实时行情
        try:
            spot_df = ak.stock_zh_a_spot_em()
            print("✅ 实时行情数据获取成功")
        except Exception as e:
            print(f"❌ 实时行情获取失败: {e}")
            return {}
        
        for code in self.stock_codes:
            print(f"\n📊 分析股票: {code}")
            stock_data = {}
            
            # 1. 基本信息和实时行情
            stock_info = spot_df[spot_df['代码'] == code]
            if not stock_info.empty:
                row = stock_info.iloc[0]
                
                basic_data = {
                    'name': row['名称'],
                    'current_price': float(row['最新价']),
                    'change': float(row['涨跌额']),
                    'pct_change': float(row['涨跌幅']),
                    'open': float(row['今开']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'pre_close': float(row['昨收']),
                    'volume': float(row['成交量']),
                    'amount': float(row['成交额']),
                    'turnover_rate': float(row['换手率']) if row['换手率'] != '-' else 0,
                    'pe_ttm': float(row['市盈率-动态']) if row['市盈率-动态'] != '-' else None,
                    'pb': float(row['市净率']) if row['市净率'] != '-' else None,
                    'total_mv': float(row['总市值']) if row['总市值'] != '-' else None,
                    'circ_mv': float(row['流通市值']) if row['流通市值'] != '-' else None
                }
                
                self.stock_names[code] = row['名称']
                stock_data['basic'] = basic_data
                
                print(f"   💰 当前价: ¥{row['最新价']} ({row['涨跌幅']:+.2f}%)")
                print(f"   📈 市值: {float(row['总市值'])/100000000:.1f}亿元")
                print(f"   🏷️ PE: {row['市盈率-动态']}, PB: {row['市净率']}")
            
            # 2. 历史数据和技术指标
            try:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
                end_date = datetime.now().strftime('%Y%m%d')
                
                hist_df = ak.stock_zh_a_hist(
                    symbol=code, 
                    period="daily", 
                    start_date=start_date, 
                    end_date=end_date, 
                    adjust="qfq"
                )
                
                if not hist_df.empty:
                    hist_df['日期'] = pd.to_datetime(hist_df['日期'])
                    hist_df = hist_df.sort_values('日期').tail(60)  # 取最近60天
                    
                    # 计算技术指标
                    close = hist_df['收盘'].values
                    
                    # 移动平均线
                    ma5 = pd.Series(close).rolling(5).mean().iloc[-1] if len(close) >= 5 else close[-1]
                    ma10 = pd.Series(close).rolling(10).mean().iloc[-1] if len(close) >= 10 else close[-1]
                    ma20 = pd.Series(close).rolling(20).mean().iloc[-1] if len(close) >= 20 else close[-1]
                    
                    # RSI
                    delta = pd.Series(close).diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rs = gain / loss
                    rsi = (100 - (100 / (1 + rs))).iloc[-1] if len(rs) > 0 else 50
                    
                    # 价格位置
                    price_pos_ma20 = (close[-1] - ma20) / ma20 * 100 if ma20 > 0 else 0
                    
                    # 趋势判断
                    if ma5 > ma10 > ma20:
                        trend = "多头排列"
                        trend_score = 20
                    elif ma5 < ma10 < ma20:
                        trend = "空头排列"
                        trend_score = -20
                    else:
                        trend = "震荡整理"
                        trend_score = 0
                    
                    technical_data = {
                        'MA5': ma5,
                        'MA10': ma10,
                        'MA20': ma20,
                        'RSI': rsi,
                        'price_vs_ma20': price_pos_ma20,
                        'trend': trend,
                        'trend_score': trend_score,
                        'volatility': hist_df['收盘'].std() / hist_df['收盘'].mean() * 100  # 波动率
                    }
                    
                    stock_data['technical'] = technical_data
                    
                    print(f"   📊 技术面: {trend}, RSI={rsi:.1f}")
                    print(f"   📍 相对MA20: {price_pos_ma20:+.1f}%")
                
            except Exception as e:
                print(f"   ❌ 技术数据获取失败: {e}")
            
            # 3. 财务数据
            try:
                financial_df = ak.stock_financial_abstract_ths(symbol=code)
                
                if not financial_df.empty:
                    # 获取最新财务数据
                    latest_columns = [col for col in financial_df.columns if col.startswith('202')]
                    if latest_columns:
                        latest_col = sorted(latest_columns)[-1]
                        
                        financial_data = {}
                        for _, row in financial_df.iterrows():
                            indicator = row['指标名称']
                            value = row.get(latest_col, None)
                            
                            if '净资产收益率' in indicator and 'ROE' not in financial_data:
                                financial_data['ROE'] = self.parse_number(value)
                            elif '毛利率' in indicator:
                                financial_data['gross_margin'] = self.parse_number(value)
                            elif '净利率' in indicator:
                                financial_data['net_margin'] = self.parse_number(value)
                            elif '资产负债率' in indicator:
                                financial_data['debt_ratio'] = self.parse_number(value)
                            elif '营业收入' in indicator and '同比增长' in indicator:
                                financial_data['revenue_growth'] = self.parse_number(value)
                            elif '净利润' in indicator and '同比增长' in indicator:
                                financial_data['profit_growth'] = self.parse_number(value)
                        
                        stock_data['financial'] = financial_data
                        
                        # 显示关键财务指标
                        roe = financial_data.get('ROE', 'N/A')
                        revenue_growth = financial_data.get('revenue_growth', 'N/A')
                        print(f"   💼 基本面: ROE={roe}%, 营收增长={revenue_growth}%")
                
            except Exception as e:
                print(f"   ❌ 财务数据获取失败: {e}")
            
            # 4. 资金流向数据
            try:
                # 获取个股资金流向 (这个接口可能不稳定，简化处理)
                money_flow_data = {
                    'net_inflow': 0,  # 默认值
                    'main_net_inflow': 0,
                    'status': '数据获取中'
                }
                stock_data['money_flow'] = money_flow_data
                
            except Exception as e:
                print(f"   ❌ 资金流向数据获取失败: {e}")
            
            # 5. 新闻情感分析
            try:
                news_df = ak.stock_news_em(symbol=code)
                
                if not news_df.empty:
                    recent_news = news_df.head(10)
                    
                    # 简单情感分析
                    positive_words = ['利好', '上涨', '增长', '盈利', '业绩', '订单', '合作', '突破']
                    negative_words = ['下跌', '亏损', '风险', '减少', '下滑', '困难', '问题']
                    
                    sentiment_score = 0
                    for _, news_row in recent_news.iterrows():
                        title = str(news_row.get('新闻标题', ''))
                        for word in positive_words:
                            sentiment_score += title.count(word) * 2
                        for word in negative_words:
                            sentiment_score -= title.count(word) * 2
                    
                    news_data = {
                        'news_count': len(recent_news),
                        'sentiment_score': sentiment_score,
                        'sentiment_level': '乐观' if sentiment_score > 5 else '悲观' if sentiment_score < -5 else '中性',
                        'latest_titles': recent_news['新闻标题'].head(3).tolist()
                    }
                    
                    stock_data['news'] = news_data
                    print(f"   📰 消息面: {news_data['sentiment_level']}, 新闻{len(recent_news)}条")
                
            except Exception as e:
                print(f"   ❌ 新闻数据获取失败: {e}")
            
            all_data[code] = stock_data
            
        self.analysis_results = all_data
        return all_data
    
    def parse_number(self, value):
        """解析数字"""
        if pd.isna(value) or value is None or value == '-':
            return None
        try:
            if isinstance(value, str):
                value = value.replace('%', '').replace(',', '')
            return float(value)
        except:
            return None
    
    def calculate_comprehensive_score(self, code):
        """计算综合评分"""
        data = self.analysis_results.get(code, {})
        
        scores = {
            'technical': 0,      # 技术面 (30%)
            'fundamental': 0,    # 基本面 (35%)
            'valuation': 0,      # 估值 (25%)
            'sentiment': 0       # 情感面 (10%)
        }
        
        reasons = {
            'positive': [],
            'negative': [],
            'neutral': []
        }
        
        # 1. 技术面评分
        technical = data.get('technical', {})
        if technical:
            # 趋势评分
            trend_score = technical.get('trend_score', 0)
            scores['technical'] += trend_score
            if trend_score > 0:
                reasons['positive'].append(f"技术形态{technical.get('trend', '良好')}")
            elif trend_score < 0:
                reasons['negative'].append(f"技术形态{technical.get('trend', '较差')}")
            
            # RSI评分
            rsi = technical.get('RSI', 50)
            if rsi < 30:
                scores['technical'] += 15
                reasons['positive'].append(f"RSI={rsi:.1f}超卖，有反弹需求")
            elif rsi > 70:
                scores['technical'] -= 15
                reasons['negative'].append(f"RSI={rsi:.1f}超买，有回调风险")
            else:
                reasons['neutral'].append(f"RSI={rsi:.1f}处于正常区间")
            
            # 价格位置评分
            price_vs_ma20 = technical.get('price_vs_ma20', 0)
            if price_vs_ma20 > 10:
                scores['technical'] += 10
                reasons['positive'].append(f"价格较MA20高{price_vs_ma20:.1f}%，强势")
            elif price_vs_ma20 < -10:
                scores['technical'] -= 10
                reasons['negative'].append(f"价格较MA20低{abs(price_vs_ma20):.1f}%，弱势")
        
        # 2. 基本面评分
        financial = data.get('financial', {})
        if financial:
            # ROE评分
            roe = financial.get('ROE')
            if roe is not None:
                if roe > 15:
                    scores['fundamental'] += 25
                    reasons['positive'].append(f"ROE={roe:.1f}%，盈利能力优秀")
                elif roe > 10:
                    scores['fundamental'] += 15
                    reasons['positive'].append(f"ROE={roe:.1f}%，盈利能力良好")
                elif roe < 5:
                    scores['fundamental'] -= 15
                    reasons['negative'].append(f"ROE={roe:.1f}%，盈利能力偏弱")
            
            # 成长性评分
            revenue_growth = financial.get('revenue_growth')
            if revenue_growth is not None:
                if revenue_growth > 20:
                    scores['fundamental'] += 20
                    reasons['positive'].append(f"营收增长{revenue_growth:.1f}%，成长性强")
                elif revenue_growth > 0:
                    scores['fundamental'] += 10
                    reasons['positive'].append(f"营收增长{revenue_growth:.1f}%，稳健增长")
                else:
                    scores['fundamental'] -= 15
                    reasons['negative'].append(f"营收增长{revenue_growth:.1f}%，增长乏力")
            
            # 财务健康度
            debt_ratio = financial.get('debt_ratio')
            if debt_ratio is not None:
                if debt_ratio < 30:
                    scores['fundamental'] += 10
                    reasons['positive'].append(f"负债率{debt_ratio:.1f}%，财务健康")
                elif debt_ratio > 70:
                    scores['fundamental'] -= 15
                    reasons['negative'].append(f"负债率{debt_ratio:.1f}%，负债偏高")
        
        # 3. 估值评分
        basic = data.get('basic', {})
        if basic:
            pe = basic.get('pe_ttm')
            pb = basic.get('pb')
            
            if pe is not None and pe > 0:
                if pe < 15:
                    scores['valuation'] += 20
                    reasons['positive'].append(f"PE={pe:.1f}，估值偏低")
                elif pe < 25:
                    scores['valuation'] += 10
                    reasons['positive'].append(f"PE={pe:.1f}，估值合理")
                elif pe > 50:
                    scores['valuation'] -= 20
                    reasons['negative'].append(f"PE={pe:.1f}，估值偏高")
            
            if pb is not None and pb > 0:
                if pb < 2:
                    scores['valuation'] += 15
                    reasons['positive'].append(f"PB={pb:.2f}，接近或低于净资产")
                elif pb > 5:
                    scores['valuation'] -= 10
                    reasons['negative'].append(f"PB={pb:.2f}，市净率偏高")
        
        # 4. 情感面评分
        news = data.get('news', {})
        if news:
            sentiment_score = news.get('sentiment_score', 0)
            if sentiment_score > 10:
                scores['sentiment'] += 10
                reasons['positive'].append(f"新闻情感{news.get('sentiment_level', '乐观')}")
            elif sentiment_score < -10:
                scores['sentiment'] -= 10
                reasons['negative'].append(f"新闻情感{news.get('sentiment_level', '悲观')}")
        
        # 计算加权总分
        total_score = (
            scores['technical'] * 0.30 +
            scores['fundamental'] * 0.35 +
            scores['valuation'] * 0.25 +
            scores['sentiment'] * 0.10
        )
        
        # 生成投资建议
        if total_score >= 50:
            recommendation = "强烈买入"
            confidence = "高"
        elif total_score >= 25:
            recommendation = "买入"
            confidence = "中高"
        elif total_score >= 0:
            recommendation = "持有观望"
            confidence = "中等"
        elif total_score >= -25:
            recommendation = "减持"
            confidence = "中高"
        else:
            recommendation = "卖出"
            confidence = "高"
        
        return {
            'recommendation': recommendation,
            'total_score': total_score,
            'confidence': confidence,
            'detailed_scores': scores,
            'reasons': reasons,
            'risk_assessment': self.assess_risk(data)
        }
    
    def assess_risk(self, data):
        """风险评估"""
        risk_factors = []
        risk_level = "低风险"
        
        # 估值风险
        basic = data.get('basic', {})
        pe = basic.get('pe_ttm', 0)
        if pe and pe > 60:
            risk_factors.append("估值过高风险")
            risk_level = "高风险"
        
        # 技术风险
        technical = data.get('technical', {})
        volatility = technical.get('volatility', 0)
        if volatility > 50:
            risk_factors.append("价格波动率过高")
            risk_level = "中高风险"
        
        # 基本面风险
        financial = data.get('financial', {})
        debt_ratio = financial.get('debt_ratio', 0)
        if debt_ratio and debt_ratio > 80:
            risk_factors.append("负债率过高，财务风险大")
            risk_level = "高风险"
        
        # 成长性风险
        revenue_growth = financial.get('revenue_growth')
        if revenue_growth is not None and revenue_growth < -10:
            risk_factors.append("营收下滑，经营风险")
            risk_level = "中高风险"
        
        if not risk_factors:
            risk_factors.append("整体风险可控")
        
        return {
            'level': risk_level,
            'factors': risk_factors
        }
    
    def generate_detailed_report(self):
        """生成详细分析报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 为每只股票计算评分
        recommendations = {}
        for code in self.stock_codes:
            recommendations[code] = self.calculate_comprehensive_score(code)
        
        # 按评分排序
        sorted_stocks = sorted(
            recommendations.items(), 
            key=lambda x: x[1]['total_score'], 
            reverse=True
        )
        
        print(f"\n" + "🏆" * 30)
        print("详细分析结果")
        print("🏆" * 30)
        
        report_lines = [
            "# 📊 5只股票极致详细分析报告",
            f"",
            f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**分析股票**: {', '.join(self.stock_codes)}  ",
            f"**数据来源**: akshare东财数据  ",
            f"**分析维度**: 实时行情 + 技术指标 + 基本面 + 估值 + 新闻情感  ",
            f"",
            f"## 🎯 投资建议总览",
            f"",
            f"| 排名 | 股票代码 | 股票名称 | 当前价格 | 涨跌幅 | 综合评分 | 投资建议 | 置信度 |",
            f"|------|---------|---------|---------|--------|---------|---------|-------|"
        ]
        
        for i, (code, rec) in enumerate(sorted_stocks, 1):
            data = self.analysis_results.get(code, {})
            basic = data.get('basic', {})
            name = self.stock_names.get(code, f'股票{code}')
            price = basic.get('current_price', 0)
            pct_change = basic.get('pct_change', 0)
            
            emoji = "🟢" if rec['total_score'] >= 25 else "🟡" if rec['total_score'] >= 0 else "🔴"
            
            report_lines.append(
                f"| {i} | {code} | {name} | ¥{price:.2f} | {pct_change:+.2f}% | "
                f"{rec['total_score']:.1f} | {emoji} {rec['recommendation']} | {rec['confidence']} |"
            )
        
        report_lines.extend([
            f"",
            f"## 📈 详细分析",
            f""
        ])
        
        # 详细分析每只股票
        for i, (code, rec) in enumerate(sorted_stocks, 1):
            data = self.analysis_results.get(code, {})
            basic = data.get('basic', {})
            technical = data.get('technical', {})
            financial = data.get('financial', {})
            news = data.get('news', {})
            
            name = self.stock_names.get(code, f'股票{code}')
            
            emoji = "🟢" if rec['total_score'] >= 25 else "🟡" if rec['total_score'] >= 0 else "🔴"
            
            report_lines.extend([
                f"### {emoji} {i}. {code} - {name}",
                f"",
                f"**🎯 投资建议**: {rec['recommendation']} (评分: {rec['total_score']:.1f}, 置信度: {rec['confidence']})",
                f"",
                f"#### 📊 核心数据",
                f"- **当前价格**: ¥{basic.get('current_price', 0):.2f}",
                f"- **涨跌幅**: {basic.get('pct_change', 0):+.2f}%",
                f"- **成交额**: {basic.get('amount', 0)/100000000:.2f}亿元",
                f"- **换手率**: {basic.get('turnover_rate', 0):.2f}%",
                f"- **总市值**: {basic.get('total_mv', 0)/100000000:.1f}亿元",
                f"- **PE(TTM)**: {basic.get('pe_ttm', 'N/A')}",
                f"- **PB**: {basic.get('pb', 'N/A')}",
                f"",
                f"#### 🔧 技术分析",
            ])
            
            if technical:
                report_lines.extend([
                    f"- **趋势状态**: {technical.get('trend', 'N/A')}",
                    f"- **MA5**: ¥{technical.get('MA5', 0):.2f}",
                    f"- **MA10**: ¥{technical.get('MA10', 0):.2f}",
                    f"- **MA20**: ¥{technical.get('MA20', 0):.2f}",
                    f"- **RSI**: {technical.get('RSI', 50):.1f}",
                    f"- **相对MA20位置**: {technical.get('price_vs_ma20', 0):+.1f}%",
                    f"- **波动率**: {technical.get('volatility', 0):.1f}%",
                ])
            
            report_lines.extend([
                f"",
                f"#### 💼 基本面分析",
            ])
            
            if financial:
                report_lines.extend([
                    f"- **净资产收益率(ROE)**: {financial.get('ROE', 'N/A')}%",
                    f"- **营收增长率**: {financial.get('revenue_growth', 'N/A')}%",
                    f"- **净利润增长率**: {financial.get('profit_growth', 'N/A')}%",
                    f"- **毛利率**: {financial.get('gross_margin', 'N/A')}%",
                    f"- **净利率**: {financial.get('net_margin', 'N/A')}%",
                    f"- **资产负债率**: {financial.get('debt_ratio', 'N/A')}%",
                ])
            else:
                report_lines.append(f"- 财务数据获取中...")
            
            report_lines.extend([
                f"",
                f"#### 📰 消息面分析",
            ])
            
            if news:
                report_lines.extend([
                    f"- **新闻关注度**: {news.get('news_count', 0)}条相关新闻",
                    f"- **情感倾向**: {news.get('sentiment_level', '中性')}",
                    f"- **情感评分**: {news.get('sentiment_score', 0)}",
                ])
                if news.get('latest_titles'):
                    report_lines.append(f"- **热点新闻**:")
                    for j, title in enumerate(news['latest_titles'], 1):
                        report_lines.append(f"  {j}. {title}")
            
            report_lines.extend([
                f"",
                f"#### ✅ 积极因素",
            ])
            
            for factor in rec['reasons']['positive']:
                report_lines.append(f"- {factor}")
            
            if not rec['reasons']['positive']:
                report_lines.append(f"- 暂无明显积极因素")
            
            report_lines.extend([
                f"",
                f"#### ⚠️ 风险因素",
            ])
            
            for factor in rec['reasons']['negative']:
                report_lines.append(f"- {factor}")
            
            risk = rec['risk_assessment']
            report_lines.extend([
                f"",
                f"#### 🚨 风险评估",
                f"- **风险等级**: {risk['level']}",
                f"- **风险因素**:",
            ])
            
            for factor in risk['factors']:
                report_lines.append(f"  - {factor}")
            
            report_lines.extend([
                f"",
                f"---",
                f""
            ])
        
        # 添加投资策略建议
        buy_stocks = [(code, rec) for code, rec in sorted_stocks if rec['recommendation'] in ['强烈买入', '买入']]
        hold_stocks = [(code, rec) for code, rec in sorted_stocks if rec['recommendation'] == '持有观望']
        
        report_lines.extend([
            f"## 🎯 投资策略建议",
            f"",
            f"### ✅ 推荐买入 ({len(buy_stocks)}只)",
        ])
        
        if buy_stocks:
            for code, rec in buy_stocks:
                name = self.stock_names.get(code, f'股票{code}')
                report_lines.append(f"- **{code} - {name}**: {rec['recommendation']} (评分: {rec['total_score']:.1f})")
        else:
            report_lines.append(f"- 当前市场环境下，暂无强烈推荐标的")
        
        report_lines.extend([
            f"",
            f"### ⚠️ 持有观望 ({len(hold_stocks)}只)",
        ])
        
        if hold_stocks:
            for code, rec in hold_stocks:
                name = self.stock_names.get(code, f'股票{code}')
                report_lines.append(f"- **{code} - {name}**: 等待更好买入时机")
        
        report_lines.extend([
            f"",
            f"## 🚨 重要风险提示",
            f"",
            f"1. **免责声明**: 本分析基于公开数据，仅供参考，不构成投资建议",
            f"2. **市场风险**: 股市有风险，投资需谨慎，请根据自身风险承受能力决策",
            f"3. **数据风险**: 部分数据可能存在延迟或不准确，请以官方数据为准",
            f"4. **操作建议**: 建议设置合理止损止盈，分批建仓，分散风险",
            f"5. **持续关注**: 请持续关注相关公司公告和市场变化",
            f"",
            f"---",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  ",
            f"*数据来源: akshare*  ",
            f"*分析工具: Python量化分析*"
        ])
        
        # 保存报告
        report_content = '\n'.join(report_lines)
        report_file = f'极致详细股票分析报告_{timestamp}.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 保存JSON数据
        json_file = f'详细分析数据_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'analysis_results': self.analysis_results,
                'recommendations': recommendations,
                'analysis_date': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2, default=str)
        
        # 控制台输出关键结果
        for i, (code, rec) in enumerate(sorted_stocks, 1):
            data = self.analysis_results.get(code, {})
            basic = data.get('basic', {})
            name = self.stock_names.get(code, f'股票{code}')
            
            print(f"\n【第{i}位】{code} - {name}")
            print(f"💰 当前价格: ¥{basic.get('current_price', 0):.2f} ({basic.get('pct_change', 0):+.2f}%)")
            print(f"🎯 投资建议: {rec['recommendation']} (评分: {rec['total_score']:.1f})")
            print(f"🔍 置信度: {rec['confidence']}")
            
            # 显示主要积极因素
            if rec['reasons']['positive']:
                print(f"✅ 主要优势: {rec['reasons']['positive'][0]}")
            
            # 显示主要风险
            if rec['reasons']['negative']:
                print(f"⚠️ 主要风险: {rec['reasons']['negative'][0]}")
        
        print(f"\n📄 详细报告已保存:")
        print(f"  - Markdown报告: {report_file}")
        print(f"  - JSON数据: {json_file}")
        
        return recommendations

def main():
    stock_codes = ['301217', '002265', '301052', '300308', '300368']
    
    print("🎯 开始极致详细的5只股票多维度分析")
    print("🔍 分析维度：实时行情 + 技术指标 + 基本面 + 估值 + 新闻情感")
    print("📊 数据源：akshare (东方财富)")
    print("=" * 80)
    
    analyzer = FocusedDetailedAnalyzer(stock_codes)
    
    # 获取综合数据
    analyzer.get_comprehensive_data()
    
    # 生成详细报告
    recommendations = analyzer.generate_detailed_report()
    
    return analyzer, recommendations

if __name__ == "__main__":
    main()