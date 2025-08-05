#!/usr/bin/env python3
"""
基于果麦文化模板的标准化股票分析
使用真实市场数据对301217, 002265, 301052, 300308, 300368进行详实分析
"""
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import warnings
import time
import requests
warnings.filterwarnings('ignore')

class StandardizedStockAnalyzer:
    def __init__(self, stock_codes):
        self.stock_codes = stock_codes
        self.stock_names = {}
        self.analysis_results = {}
        
    def get_real_basic_info(self, code):
        """获取真实的股票基本信息"""
        try:
            # 获取股票基本信息
            info_df = ak.stock_individual_info_em(symbol=code)
            basic_info = {}
            
            for _, row in info_df.iterrows():
                item = row['item']
                value = row['value']
                
                if '股票简称' in item:
                    basic_info['name'] = value
                elif '股票代码' in item:
                    basic_info['code'] = value
                elif '所属行业' in item:
                    basic_info['industry'] = value
                elif '上市时间' in item:
                    basic_info['list_date'] = value
                elif '总股本' in item:
                    basic_info['total_shares'] = value
                elif '流通股' in item:
                    basic_info['float_shares'] = value
                elif '总市值' in item:
                    basic_info['market_cap'] = value
                elif '流通市值' in item:
                    basic_info['float_market_cap'] = value
                elif '每股净资产' in item:
                    basic_info['bps'] = value
                elif '净资产收益率' in item:
                    basic_info['roe'] = value
                    
            return basic_info
        except Exception as e:
            print(f"获取{code}基本信息失败: {e}")
            return {}
    
    def get_real_financial_data(self, code):
        """获取真实的财务数据"""
        try:
            # 获取财务指标
            financial_data = {}
            
            # 获取主要财务指标
            indicator_df = ak.stock_financial_abstract_ths(symbol=code)
            
            if not indicator_df.empty:
                # 获取最新财务数据（通常是最近的季度或年度）
                latest_columns = [col for col in indicator_df.columns if col.startswith('202')]
                if latest_columns:
                    latest_col = sorted(latest_columns)[-1]  # 最新的时间列
                    
                    for _, row in indicator_df.iterrows():
                        indicator_name = row['指标名称']
                        value = row.get(latest_col, None)
                        
                        # 营收相关
                        if '营业收入' in indicator_name and '同比增长' not in indicator_name:
                            financial_data['revenue'] = self.parse_financial_number(value)
                        elif '营业收入' in indicator_name and '同比增长' in indicator_name:
                            financial_data['revenue_growth'] = self.parse_financial_number(value)
                        
                        # 利润相关
                        elif '净利润' in indicator_name and '同比增长' not in indicator_name and '扣非' not in indicator_name:
                            financial_data['net_profit'] = self.parse_financial_number(value)
                        elif '净利润' in indicator_name and '同比增长' in indicator_name:
                            financial_data['profit_growth'] = self.parse_financial_number(value)
                        
                        # 盈利能力
                        elif '净资产收益率' in indicator_name:
                            financial_data['roe'] = self.parse_financial_number(value)
                        elif '毛利率' in indicator_name:
                            financial_data['gross_margin'] = self.parse_financial_number(value)
                        elif '净利率' in indicator_name:
                            financial_data['net_margin'] = self.parse_financial_number(value)
                        
                        # 每股指标
                        elif '每股收益' in indicator_name:
                            financial_data['eps'] = self.parse_financial_number(value)
                        elif '每股净资产' in indicator_name:
                            financial_data['bps'] = self.parse_financial_number(value)
                        
                        # 财务结构
                        elif '资产负债率' in indicator_name:
                            financial_data['debt_ratio'] = self.parse_financial_number(value)
                        elif '流动比率' in indicator_name:
                            financial_data['current_ratio'] = self.parse_financial_number(value)
            
            return financial_data
            
        except Exception as e:
            print(f"获取{code}财务数据失败: {e}")
            return {}
    
    def get_real_market_data(self, code):
        """获取真实的市场行情数据"""
        try:
            # 获取实时行情
            spot_df = ak.stock_zh_a_spot_em()
            stock_data = spot_df[spot_df['代码'] == code]
            
            if stock_data.empty:
                return {}
            
            row = stock_data.iloc[0]
            
            market_data = {
                'current_price': self.safe_float(row['最新价']),
                'change': self.safe_float(row['涨跌额']),
                'pct_change': self.safe_float(row['涨跌幅']),
                'open': self.safe_float(row['今开']),
                'high': self.safe_float(row['最高']),
                'low': self.safe_float(row['最低']),
                'pre_close': self.safe_float(row['昨收']),
                'volume': self.safe_float(row['成交量']),
                'amount': self.safe_float(row['成交额']),
                'turnover_rate': self.safe_float(row['换手率']),
                'pe_ttm': self.safe_float(row['市盈率-动态']),
                'pb': self.safe_float(row['市净率']),
                'total_mv': self.safe_float(row['总市值']),
                'circ_mv': self.safe_float(row['流通市值'])
            }
            
            return market_data
            
        except Exception as e:
            print(f"获取{code}市场数据失败: {e}")
            return {}
    
    def get_real_historical_data(self, code, days=60):
        """获取真实的历史数据并计算技术指标"""
        try:
            # 获取历史数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')
            
            hist_df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            
            if hist_df.empty:
                return {}
            
            # 数据处理
            hist_df['日期'] = pd.to_datetime(hist_df['日期'])
            hist_df = hist_df.sort_values('日期').tail(days)
            
            if len(hist_df) < 20:
                return {}
            
            # 计算技术指标
            close_prices = hist_df['收盘'].values
            
            # 移动平均线
            ma5 = pd.Series(close_prices).rolling(5).mean().iloc[-1] if len(close_prices) >= 5 else None
            ma10 = pd.Series(close_prices).rolling(10).mean().iloc[-1] if len(close_prices) >= 10 else None
            ma20 = pd.Series(close_prices).rolling(20).mean().iloc[-1] if len(close_prices) >= 20 else None
            ma30 = pd.Series(close_prices).rolling(30).mean().iloc[-1] if len(close_prices) >= 30 else None
            
            # RSI
            delta = pd.Series(close_prices).diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = (100 - (100 / (1 + rs))).iloc[-1]
            
            # MACD
            exp1 = pd.Series(close_prices).ewm(span=12).mean()
            exp2 = pd.Series(close_prices).ewm(span=26).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9).mean()
            histogram = macd - signal
            
            # 布林带
            bb_middle = pd.Series(close_prices).rolling(20).mean()
            bb_std = pd.Series(close_prices).rolling(20).std()
            bb_upper = bb_middle + (bb_std * 2)
            bb_lower = bb_middle - (bb_std * 2)
            
            technical_data = {
                'ma5': ma5,
                'ma10': ma10,
                'ma20': ma20,
                'ma30': ma30,
                'rsi': rsi,
                'macd': macd.iloc[-1],
                'macd_signal': signal.iloc[-1],
                'macd_histogram': histogram.iloc[-1],
                'bb_upper': bb_upper.iloc[-1],
                'bb_middle': bb_middle.iloc[-1],
                'bb_lower': bb_lower.iloc[-1],
                'volatility': pd.Series(close_prices).std() / pd.Series(close_prices).mean() * 100,
                'trend_analysis': self.analyze_trend(ma5, ma10, ma20, ma30, close_prices[-1])
            }
            
            return technical_data
            
        except Exception as e:
            print(f"获取{code}历史数据失败: {e}")
            return {}
    
    def analyze_trend(self, ma5, ma10, ma20, ma30, current_price):
        """分析趋势"""
        if not all([ma5, ma10, ma20]):
            return "数据不足"
        
        if ma5 > ma10 > ma20:
            if ma30 and ma20 > ma30:
                return "强势多头"
            return "多头排列"
        elif ma5 < ma10 < ma20:
            if ma30 and ma20 < ma30:
                return "强势空头"
            return "空头排列"
        else:
            return "震荡整理"
    
    def get_real_news_data(self, code):
        """获取真实的新闻数据"""
        try:
            # 获取个股新闻
            news_df = ak.stock_news_em(symbol=code)
            
            if news_df.empty:
                return {}
            
            recent_news = news_df.head(15)
            
            # 情感分析关键词
            positive_keywords = [
                '利好', '上涨', '增长', '盈利', '业绩', '订单', '合作', '突破',
                '创新', '扩张', '收购', '中标', '签约', '涨停', '强势', '看好',
                '买入', '推荐', '目标价', '上调', '机会'
            ]
            
            negative_keywords = [
                '下跌', '亏损', '风险', '减少', '下滑', '困难', '问题', '调查',
                '处罚', '违规', '停牌', 'ST', '退市', '预警', '跌停', '卖出',
                '下调', '谨慎', '回调'
            ]
            
            sentiment_score = 0
            news_titles = []
            
            for _, news_row in recent_news.iterrows():
                title = str(news_row.get('新闻标题', ''))
                news_titles.append(title)
                
                # 计算情感分数
                for word in positive_keywords:
                    sentiment_score += title.count(word) * 2
                for word in negative_keywords:
                    sentiment_score -= title.count(word) * 2
            
            # 情感等级
            if sentiment_score >= 15:
                sentiment_level = "极度乐观"
            elif sentiment_score >= 8:
                sentiment_level = "乐观"
            elif sentiment_score >= 3:
                sentiment_level = "偏乐观"
            elif sentiment_score >= -3:
                sentiment_level = "中性"
            elif sentiment_score >= -8:
                sentiment_level = "偏悲观"
            elif sentiment_score >= -15:
                sentiment_level = "悲观"
            else:
                sentiment_level = "极度悲观"
            
            news_data = {
                'news_count': len(recent_news),
                'sentiment_score': sentiment_score,
                'sentiment_level': sentiment_level,
                'latest_news': news_titles[:10],
                'latest_date': recent_news.iloc[0].get('新闻时间', '') if len(recent_news) > 0 else ''
            }
            
            return news_data
            
        except Exception as e:
            print(f"获取{code}新闻数据失败: {e}")
            return {}
    
    def safe_float(self, value):
        """安全转换为浮点数"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        try:
            return float(value)
        except:
            return None
    
    def parse_financial_number(self, value):
        """解析财务数字"""
        if pd.isna(value) or value is None or value == '-' or value == '':
            return None
        try:
            if isinstance(value, str):
                # 处理百分比
                if '%' in value:
                    value = value.replace('%', '')
                # 处理单位
                value = value.replace(',', '').replace('万', '').replace('亿', '')
                if value.strip() == '' or value.strip() == '--':
                    return None
            return float(value)
        except:
            return None
    
    def calculate_investment_score(self, basic_info, financial_data, market_data, technical_data, news_data):
        """计算投资评分"""
        scores = {
            'technical': 0,      # 技术面 25%
            'fundamental': 0,    # 基本面 35%
            'valuation': 0,      # 估值 25%
            'sentiment': 0       # 情感面 15%
        }
        
        analysis_factors = {
            'positive': [],
            'negative': [],
            'neutral': []
        }
        
        # 1. 技术面评分
        if technical_data:
            # 趋势分析
            trend = technical_data.get('trend_analysis', '')
            if '强势多头' in trend:
                scores['technical'] += 25
                analysis_factors['positive'].append(f"技术形态{trend}")
            elif '多头排列' in trend:
                scores['technical'] += 20
                analysis_factors['positive'].append(f"技术形态{trend}")
            elif '空头排列' in trend:
                scores['technical'] -= 20
                analysis_factors['negative'].append(f"技术形态{trend}")
            elif '强势空头' in trend:
                scores['technical'] -= 25
                analysis_factors['negative'].append(f"技术形态{trend}")
            
            # RSI分析
            rsi = technical_data.get('rsi')
            if rsi:
                if rsi > 80:
                    scores['technical'] -= 15
                    analysis_factors['negative'].append(f"RSI={rsi:.1f}严重超买")
                elif rsi > 70:
                    scores['technical'] -= 8
                    analysis_factors['negative'].append(f"RSI={rsi:.1f}超买")
                elif rsi < 20:
                    scores['technical'] += 15
                    analysis_factors['positive'].append(f"RSI={rsi:.1f}严重超卖")
                elif rsi < 30:
                    scores['technical'] += 8
                    analysis_factors['positive'].append(f"RSI={rsi:.1f}超卖")
                else:
                    analysis_factors['neutral'].append(f"RSI={rsi:.1f}正常")
            
            # MACD分析
            macd = technical_data.get('macd')
            macd_signal = technical_data.get('macd_signal')
            if macd and macd_signal:
                if macd > macd_signal and macd > 0:
                    scores['technical'] += 10
                    analysis_factors['positive'].append("MACD金叉向上")
                elif macd < macd_signal and macd < 0:
                    scores['technical'] -= 10
                    analysis_factors['negative'].append("MACD死叉向下")
        
        # 2. 基本面评分
        if financial_data:
            # ROE评分
            roe = financial_data.get('roe')
            if roe:
                if roe > 20:
                    scores['fundamental'] += 30
                    analysis_factors['positive'].append(f"ROE={roe:.1f}%卓越")
                elif roe > 15:
                    scores['fundamental'] += 25
                    analysis_factors['positive'].append(f"ROE={roe:.1f}%优秀")
                elif roe > 10:
                    scores['fundamental'] += 15
                    analysis_factors['positive'].append(f"ROE={roe:.1f}%良好")
                elif roe < 5:
                    scores['fundamental'] -= 15
                    analysis_factors['negative'].append(f"ROE={roe:.1f}%偏低")
            
            # 成长性评分
            revenue_growth = financial_data.get('revenue_growth')
            profit_growth = financial_data.get('profit_growth')
            
            if revenue_growth:
                if revenue_growth > 30:
                    scores['fundamental'] += 20
                    analysis_factors['positive'].append(f"营收增长{revenue_growth:.1f}%强劲")
                elif revenue_growth > 15:
                    scores['fundamental'] += 15
                    analysis_factors['positive'].append(f"营收增长{revenue_growth:.1f}%良好")
                elif revenue_growth < 0:
                    scores['fundamental'] -= 20
                    analysis_factors['negative'].append(f"营收下滑{revenue_growth:.1f}%")
            
            if profit_growth:
                if profit_growth > 40:
                    scores['fundamental'] += 25
                    analysis_factors['positive'].append(f"利润增长{profit_growth:.1f}%强劲")
                elif profit_growth > 20:
                    scores['fundamental'] += 20
                    analysis_factors['positive'].append(f"利润增长{profit_growth:.1f}%良好")
                elif profit_growth < 0:
                    scores['fundamental'] -= 25
                    analysis_factors['negative'].append(f"利润下滑{profit_growth:.1f}%")
            
            # 盈利质量
            net_margin = financial_data.get('net_margin')
            if net_margin:
                if net_margin > 15:
                    scores['fundamental'] += 15
                    analysis_factors['positive'].append(f"净利率{net_margin:.1f}%优秀")
                elif net_margin > 8:
                    scores['fundamental'] += 10
                    analysis_factors['positive'].append(f"净利率{net_margin:.1f}%良好")
                elif net_margin < 3:
                    scores['fundamental'] -= 10
                    analysis_factors['negative'].append(f"净利率{net_margin:.1f}%偏低")
            
            # 财务健康
            debt_ratio = financial_data.get('debt_ratio')
            if debt_ratio:
                if debt_ratio < 30:
                    scores['fundamental'] += 10
                    analysis_factors['positive'].append(f"负债率{debt_ratio:.1f}%健康")
                elif debt_ratio > 70:
                    scores['fundamental'] -= 15
                    analysis_factors['negative'].append(f"负债率{debt_ratio:.1f}%偏高")
        
        # 3. 估值评分
        if market_data:
            pe_ttm = market_data.get('pe_ttm')
            pb = market_data.get('pb')
            
            if pe_ttm and pe_ttm > 0:
                if pe_ttm < 15:
                    scores['valuation'] += 25
                    analysis_factors['positive'].append(f"PE={pe_ttm:.1f}低估值")
                elif pe_ttm < 25:
                    scores['valuation'] += 15
                    analysis_factors['positive'].append(f"PE={pe_ttm:.1f}合理估值")
                elif pe_ttm > 50:
                    scores['valuation'] -= 20
                    analysis_factors['negative'].append(f"PE={pe_ttm:.1f}高估值")
            
            if pb and pb > 0:
                if pb < 2:
                    scores['valuation'] += 20
                    analysis_factors['positive'].append(f"PB={pb:.2f}低估值")
                elif pb < 3:
                    scores['valuation'] += 10
                    analysis_factors['positive'].append(f"PB={pb:.2f}合理估值")
                elif pb > 6:
                    scores['valuation'] -= 15
                    analysis_factors['negative'].append(f"PB={pb:.2f}高估值")
        
        # 4. 情感面评分
        if news_data:
            sentiment_score = news_data.get('sentiment_score', 0)
            sentiment_level = news_data.get('sentiment_level', '中性')
            
            if sentiment_score > 15:
                scores['sentiment'] += 15
                analysis_factors['positive'].append(f"新闻情感{sentiment_level}")
            elif sentiment_score > 8:
                scores['sentiment'] += 10
                analysis_factors['positive'].append(f"新闻情感{sentiment_level}")
            elif sentiment_score < -15:
                scores['sentiment'] -= 15
                analysis_factors['negative'].append(f"新闻情感{sentiment_level}")
            elif sentiment_score < -8:
                scores['sentiment'] -= 10
                analysis_factors['negative'].append(f"新闻情感{sentiment_level}")
        
        # 计算加权总分
        total_score = (
            scores['technical'] * 0.25 +
            scores['fundamental'] * 0.35 +
            scores['valuation'] * 0.25 +
            scores['sentiment'] * 0.15
        )
        
        # 生成投资建议
        if total_score >= 60:
            recommendation = "强烈买入"
            confidence = "高"
        elif total_score >= 35:
            recommendation = "买入"
            confidence = "中高"
        elif total_score >= 10:
            recommendation = "持有观望"
            confidence = "中等"
        elif total_score >= -20:
            recommendation = "减持"
            confidence = "中高"
        else:
            recommendation = "卖出"
            confidence = "高"
        
        return {
            'total_score': total_score,
            'detailed_scores': scores,
            'recommendation': recommendation,
            'confidence': confidence,
            'analysis_factors': analysis_factors
        }
    
    def generate_standardized_report(self, code):
        """生成标准化分析报告"""
        print(f"\n🔍 开始分析 {code}...")
        
        # 获取各项真实数据
        basic_info = self.get_real_basic_info(code)
        financial_data = self.get_real_financial_data(code)
        market_data = self.get_real_market_data(code)
        technical_data = self.get_real_historical_data(code)
        news_data = self.get_real_news_data(code)
        
        # 计算投资评分
        investment_analysis = self.calculate_investment_score(
            basic_info, financial_data, market_data, technical_data, news_data
        )
        
        # 股票名称
        stock_name = basic_info.get('name', market_data.get('name', f'股票{code}'))
        self.stock_names[code] = stock_name
        
        # 生成报告内容
        report_lines = [
            f"# {stock_name}({code})详实数据研究报告",
            "",
            f"> **报告日期**: {datetime.now().strftime('%Y年%m月%d日')}  ",
            f"> **研究机构**: AI量化分析系统  ",
            f"> **报告类型**: 深度数据驱动分析",
            "",
            "---",
            "",
            "## 📊 公司基本信息与财务数据",
            "",
            "### 基础信息",
            "| 项目 | 数据 | 备注 |",
            "|------|------|------|",
            f"| **股票代码** | {code} | {'深交所创业板' if code.startswith('30') else '深交所主板' if code.startswith('00') else '上交所主板'} |",
            f"| **公司全称** | {stock_name} | |",
            f"| **所属行业** | {basic_info.get('industry', 'N/A')} | |",
            f"| **上市时间** | {basic_info.get('list_date', 'N/A')} | |",
            f"| **总股本** | {basic_info.get('total_shares', 'N/A')} | |",
            f"| **流通股本** | {basic_info.get('float_shares', 'N/A')} | |",
            "",
            "### 最新财务数据 (最近报告期)",
            "| 财务指标 | 数值 | 同比变化 |",
            "|----------|------|----------|",
            f"| **营业收入** | {financial_data.get('revenue', 'N/A')}万元 | {financial_data.get('revenue_growth', 'N/A')}% |",
            f"| **净利润** | {financial_data.get('net_profit', 'N/A')}万元 | {financial_data.get('profit_growth', 'N/A')}% |",
            f"| **净资产收益率(ROE)** | {financial_data.get('roe', 'N/A')}% | - |",
            f"| **毛利率** | {financial_data.get('gross_margin', 'N/A')}% | - |",
            f"| **净利率** | {financial_data.get('net_margin', 'N/A')}% | - |",
            f"| **每股收益(EPS)** | {financial_data.get('eps', 'N/A')}元 | - |",
            f"| **每股净资产(BPS)** | {financial_data.get('bps', 'N/A')}元 | - |",
            f"| **资产负债率** | {financial_data.get('debt_ratio', 'N/A')}% | - |",
            "",
            "## 📈 市场表现与估值分析",
            "",
            "### 股价表现",
            "| 指标 | 数值 | 备注 |",
            "|------|------|------|",
            f"| **最新价** | ¥{market_data.get('current_price', 'N/A')} | {market_data.get('pct_change', 0):+.2f}% |",
            f"| **今日区间** | ¥{market_data.get('low', 'N/A')} - ¥{market_data.get('high', 'N/A')} | |",
            f"| **成交量** | {market_data.get('volume', 0)/10000:.0f}万手 | |",
            f"| **成交额** | {market_data.get('amount', 0)/100000000:.2f}亿元 | |",
            f"| **换手率** | {market_data.get('turnover_rate', 'N/A')}% | |",
            f"| **总市值** | {market_data.get('total_mv', 0)/100000000:.1f}亿元 | |",
            f"| **流通市值** | {market_data.get('circ_mv', 0)/100000000:.1f}亿元 | |",
            "",
            "### 估值指标",
            "| 估值指标 | 当前值 | 评估 |",
            "|----------|--------|------|",
            f"| **市盈率(PE-TTM)** | {market_data.get('pe_ttm', 'N/A')} | {'合理' if market_data.get('pe_ttm', 100) < 30 else '偏高' if market_data.get('pe_ttm', 100) < 50 else '过高'} |",
            f"| **市净率(PB)** | {market_data.get('pb', 'N/A')} | {'低估' if market_data.get('pb', 10) < 2 else '合理' if market_data.get('pb', 10) < 4 else '偏高'} |",
            "",
            "## 🔧 技术分析",
            "",
            "### 技术指标",
            "| 技术指标 | 数值 | 信号 |",
            "|----------|------|------|",
        ]
        
        if technical_data:
            ma5 = technical_data.get('ma5')
            ma10 = technical_data.get('ma10')
            ma20 = technical_data.get('ma20')
            rsi = technical_data.get('rsi')
            current_price = market_data.get('current_price')
            
            report_lines.extend([
                f"| **MA5** | ¥{ma5:.2f if ma5 else 'N/A'} | {'支撑' if current_price and ma5 and current_price > ma5 else '压力'} |",
                f"| **MA10** | ¥{ma10:.2f if ma10 else 'N/A'} | {'支撑' if current_price and ma10 and current_price > ma10 else '压力'} |",
                f"| **MA20** | ¥{ma20:.2f if ma20 else 'N/A'} | {'支撑' if current_price and ma20 and current_price > ma20 else '压力'} |",
                f"| **RSI(14)** | {rsi:.1f if rsi else 'N/A'} | {'超买' if rsi and rsi > 70 else '超卖' if rsi and rsi < 30 else '正常'} |",
                f"| **趋势状态** | {technical_data.get('trend_analysis', 'N/A')} | - |",
                f"| **波动率** | {technical_data.get('volatility', 0):.1f}% | {'高波动' if technical_data.get('volatility', 0) > 40 else '正常'} |",
            ])
        
        report_lines.extend([
            "",
            "## 📰 市场情绪与新闻分析",
            "",
            "### 新闻热度",
            f"- **相关新闻数量**: {news_data.get('news_count', 0)}条 (近期)",
            f"- **市场情绪**: {news_data.get('sentiment_level', '中性')}",
            f"- **情绪评分**: {news_data.get('sentiment_score', 0)}分",
            "",
            "### 重点新闻",
        ])
        
        if news_data.get('latest_news'):
            for i, news in enumerate(news_data['latest_news'][:5], 1):
                report_lines.append(f"{i}. {news}")
        else:
            report_lines.append("暂无重点新闻")
        
        report_lines.extend([
            "",
            "## 🎯 投资建议与评级",
            "",
            f"### 综合评分: {investment_analysis['total_score']:.1f}分",
            "",
            "| 评分维度 | 得分 | 权重 | 说明 |",
            "|----------|------|------|------|",
            f"| **技术面** | {investment_analysis['detailed_scores']['technical']:.1f} | 25% | 趋势与技术指标分析 |",
            f"| **基本面** | {investment_analysis['detailed_scores']['fundamental']:.1f} | 35% | 财务质量与成长性 |",
            f"| **估值面** | {investment_analysis['detailed_scores']['valuation']:.1f} | 25% | 估值水平评估 |",
            f"| **情感面** | {investment_analysis['detailed_scores']['sentiment']:.1f} | 15% | 市场情绪与新闻面 |",
            "",
            f"### 🎯 投资建议: {investment_analysis['recommendation']}",
            f"**置信度**: {investment_analysis['confidence']}",
            "",
            "### ✅ 积极因素",
        ])
        
        for factor in investment_analysis['analysis_factors']['positive']:
            report_lines.append(f"- {factor}")
        
        if not investment_analysis['analysis_factors']['positive']:
            report_lines.append("- 暂无明显积极因素")
        
        report_lines.extend([
            "",
            "### ⚠️ 风险因素",
        ])
        
        for factor in investment_analysis['analysis_factors']['negative']:
            report_lines.append(f"- {factor}")
        
        if not investment_analysis['analysis_factors']['negative']:
            report_lines.append("- 暂无明显风险因素")
        
        report_lines.extend([
            "",
            "### 📋 中性因素",
        ])
        
        for factor in investment_analysis['analysis_factors']['neutral']:
            report_lines.append(f"- {factor}")
        
        if not investment_analysis['analysis_factors']['neutral']:
            report_lines.append("- 无")
        
        report_lines.extend([
            "",
            "## 🚨 风险提示",
            "",
            "1. **市场风险**: 股票价格受多种因素影响，存在波动风险",
            "2. **行业风险**: 所属行业政策变化或竞争加剧的风险",
            "3. **公司风险**: 经营管理、财务状况变化的风险",
            "4. **流动性风险**: 成交量不足可能影响买卖操作",
            "5. **信息风险**: 分析基于公开信息，可能存在滞后或不完整",
            "",
            "---",
            "",
            f"*本报告基于公开数据分析，仅供参考，不构成投资建议*  ",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  ",
            f"*数据来源: akshare & 东方财富*"
        ])
        
        # 保存分析结果
        self.analysis_results[code] = {
            'basic_info': basic_info,
            'financial_data': financial_data,
            'market_data': market_data,
            'technical_data': technical_data,
            'news_data': news_data,
            'investment_analysis': investment_analysis,
            'stock_name': stock_name
        }
        
        return '\n'.join(report_lines)
    
    def analyze_all_stocks(self):
        """分析所有股票"""
        print("🎯 开始使用真实数据分析5只股票")
        print("📊 分析标准：基于果麦文化模板的标准化分析")
        print("=" * 80)
        
        all_reports = {}
        
        for code in self.stock_codes:
            try:
                print(f"\n📈 正在分析 {code}...")
                report = self.generate_standardized_report(code)
                
                # 保存个股报告
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{code}_{self.stock_names.get(code, 'Unknown')}_详实分析报告_{timestamp}.md"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                all_reports[code] = {
                    'report': report,
                    'filename': filename
                }
                
                print(f"✅ {code} 分析完成，报告已保存: {filename}")
                
                # 添加延迟避免请求过于频繁
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ {code} 分析失败: {e}")
                continue
        
        # 生成汇总报告
        self.generate_summary_report()
        
        return all_reports
    
    def generate_summary_report(self):
        """生成汇总分析报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 按投资评分排序
        sorted_stocks = sorted(
            self.analysis_results.items(),
            key=lambda x: x[1]['investment_analysis']['total_score'],
            reverse=True
        )
        
        summary_lines = [
            "# 📊 5只股票综合投资分析汇总报告",
            "",
            f"**分析日期**: {datetime.now().strftime('%Y年%m月%d日')}  ",
            f"**分析股票**: {', '.join(self.stock_codes)}  ",
            f"**分析方法**: 基于果麦文化模板的标准化多维度分析  ",
            "",
            "## 🏆 投资建议排序",
            "",
            "| 排名 | 股票代码 | 股票名称 | 综合评分 | 投资建议 | 当前价格 | 涨跌幅 | PE | 主要亮点 |",
            "|------|----------|----------|----------|----------|----------|--------|----|---------| ",
        ]
        
        for i, (code, data) in enumerate(sorted_stocks, 1):
            analysis = data['investment_analysis']
            market = data['market_data']
            name = data['stock_name']
            
            # 获取主要积极因素
            positive_factors = analysis['analysis_factors']['positive']
            main_highlight = positive_factors[0] if positive_factors else "基本面稳定"
            
            summary_lines.append(
                f"| {i} | {code} | {name} | {analysis['total_score']:.1f} | "
                f"{'🟢' if analysis['total_score'] >= 35 else '🟡' if analysis['total_score'] >= 10 else '🔴'} {analysis['recommendation']} | "
                f"¥{market.get('current_price', 0):.2f} | {market.get('pct_change', 0):+.2f}% | "
                f"{market.get('pe_ttm', 'N/A')} | {main_highlight[:20]}... |"
            )
        
        summary_lines.extend([
            "",
            "## 📈 详细投资建议",
            ""
        ])
        
        # 分类投资建议
        strong_buy = [(code, data) for code, data in sorted_stocks if data['investment_analysis']['total_score'] >= 60]
        buy = [(code, data) for code, data in sorted_stocks if 35 <= data['investment_analysis']['total_score'] < 60]
        hold = [(code, data) for code, data in sorted_stocks if 10 <= data['investment_analysis']['total_score'] < 35]
        sell = [(code, data) for code, data in sorted_stocks if data['investment_analysis']['total_score'] < 10]
        
        summary_lines.extend([
            f"### 🟢 强烈推荐 ({len(strong_buy)}只)",
            ""
        ])
        
        if strong_buy:
            for code, data in strong_buy:
                analysis = data['investment_analysis']
                market = data['market_data']
                summary_lines.extend([
                    f"**{code} - {data['stock_name']}** (评分: {analysis['total_score']:.1f})",
                    f"- 当前价: ¥{market.get('current_price', 0):.2f}",
                    f"- 主要优势: {', '.join(analysis['analysis_factors']['positive'][:3])}",
                    ""
                ])
        else:
            summary_lines.append("暂无强烈推荐标的")
        
        summary_lines.extend([
            f"### 🟢 推荐买入 ({len(buy)}只)",
            ""
        ])
        
        if buy:
            for code, data in buy:
                analysis = data['investment_analysis']
                market = data['market_data']
                summary_lines.extend([
                    f"**{code} - {data['stock_name']}** (评分: {analysis['total_score']:.1f})",
                    f"- 当前价: ¥{market.get('current_price', 0):.2f}",
                    f"- 主要优势: {', '.join(analysis['analysis_factors']['positive'][:2])}",
                    ""
                ])
        else:
            summary_lines.append("暂无推荐买入标的")
        
        summary_lines.extend([
            f"### 🟡 持有观望 ({len(hold)}只)",
            ""
        ])
        
        if hold:
            for code, data in hold:
                analysis = data['investment_analysis']
                summary_lines.append(f"**{code} - {data['stock_name']}** (评分: {analysis['total_score']:.1f}) - 等待更好时机")
        else:
            summary_lines.append("无持有观望标的")
        
        if sell:
            summary_lines.extend([
                f"### 🔴 建议减持 ({len(sell)}只)",
                ""
            ])
            for code, data in sell:
                analysis = data['investment_analysis']
                summary_lines.append(f"**{code} - {data['stock_name']}** (评分: {analysis['total_score']:.1f}) - 风险较大")
        
        summary_lines.extend([
            "",
            "## 🎯 投资策略建议",
            "",
            "### 核心配置建议",
            f"1. **核心持仓**: 评分60分以上股票，建议配置40-60%",
            f"2. **配置持仓**: 评分35-60分股票，建议配置20-40%", 
            f"3. **观察持仓**: 评分10-35分股票，建议配置0-20%",
            f"4. **规避持仓**: 评分10分以下股票，建议回避",
            "",
            "### 风险控制",
            "- 单只股票持仓不超过30%",
            "- 设置止损位，建议10-15%",
            "- 定期检视，根据基本面变化调整",
            "- 关注市场整体环境变化",
            "",
            "---",
            f"*本汇总报告基于标准化分析模板生成*  ",
            f"*各股票详细报告请查看对应的单独文件*  ",
            f"*报告仅供参考，投资需谨慎*"
        ])
        
        # 保存汇总报告
        summary_filename = f"5只股票综合分析汇总报告_{timestamp}.md"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_lines))
        
        # 保存JSON数据
        json_filename = f"股票分析数据_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📄 汇总报告已生成:")
        print(f"  - 汇总报告: {summary_filename}")
        print(f"  - 数据文件: {json_filename}")
        
        # 打印简要结果
        print(f"\n🏆 投资建议汇总:")
        for i, (code, data) in enumerate(sorted_stocks, 1):
            analysis = data['investment_analysis']
            market = data['market_data']
            name = data['stock_name']
            
            emoji = "🟢" if analysis['total_score'] >= 35 else "🟡" if analysis['total_score'] >= 10 else "🔴"
            print(f"  {i}. {code} - {name}: {emoji} {analysis['recommendation']} (评分: {analysis['total_score']:.1f})")

def main():
    stock_codes = ['301217', '002265', '301052', '300308', '300368']
    
    analyzer = StandardizedStockAnalyzer(stock_codes)
    
    # 分析所有股票
    results = analyzer.analyze_all_stocks()
    
    return analyzer, results

if __name__ == "__main__":
    main()