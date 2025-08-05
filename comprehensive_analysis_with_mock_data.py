#!/usr/bin/env python3
"""
使用模拟真实数据进行极致详细的股票分析示例
展示完整的多维度分析逻辑和过程
股票代码：301217, 002265, 301052, 300308, 300368
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ComprehensiveStockAnalyzer:
    def __init__(self):
        self.stock_codes = ['301217', '002265', '301052', '300308', '300368']
        self.stock_names = {
            '301217': '铜冠铜箔',
            '002265': '建设工业', 
            '301052': '果麦文化',
            '300308': '中际旭创',
            '300368': '汇金股份'
        }
        self.analysis_results = {}
        
    def create_mock_data(self):
        """创建模拟的真实数据用于分析演示"""
        print("🔍 构建模拟真实市场数据...")
        print("=" * 60)
        
        # 基于真实市场情况的模拟数据
        mock_data = {
            '301217': {  # 铜冠铜箔
                'basic': {
                    'name': '铜冠铜箔',
                    'current_price': 25.08,
                    'change': 2.89,
                    'pct_change': 13.02,
                    'open': 24.50,
                    'high': 26.30,
                    'low': 24.20,
                    'pre_close': 22.19,
                    'volume': 2845600,
                    'amount': 72358000,
                    'turnover_rate': 8.42,
                    'pe_ttm': 18.6,
                    'pb': 2.3,
                    'total_mv': 207.9,  # 亿元
                    'circ_mv': 180.2
                },
                'technical': {
                    'MA5': 23.45,
                    'MA10': 22.80,
                    'MA20': 21.90,
                    'MA30': 21.20,
                    'RSI': 78.5,
                    'MACD': 0.45,
                    'MACD_Signal': 0.32,
                    'K': 85.2,
                    'D': 78.9,
                    'J': 97.8,
                    'BB_Upper': 26.80,
                    'BB_Middle': 22.50,
                    'BB_Lower': 18.20,
                    'price_vs_ma20': 14.5,
                    'trend': '多头排列',
                    'trend_score': 20,
                    'volatility': 42.5
                },
                'financial': {
                    'ROE': 12.8,
                    'gross_margin': 18.5,
                    'net_margin': 8.2,
                    'debt_ratio': 45.2,
                    'revenue_growth': 28.5,
                    'profit_growth': 35.8,
                    'EPS': 1.35,
                    'BPS': 10.92,
                    'current_ratio': 1.8,
                    'quick_ratio': 1.4
                },
                'news': {
                    'news_count': 15,
                    'sentiment_score': 12,
                    'sentiment_level': '乐观',
                    'latest_titles': [
                        '铜冠铜箔：受益新能源车需求爆发，订单饱满',
                        '铜箔行业景气度持续，龙头企业优势明显',
                        '新能源汽车带动铜箔需求，相关公司业绩亮眼'
                    ]
                },
                'industry': {
                    'industry_name': '有色金属-铜加工',
                    'industry_pe': 22.5,
                    'industry_growth': 25.3,
                    'market_position': '细分龙头'
                }
            },
            
            '002265': {  # 建设工业
                'basic': {
                    'name': '建设工业',
                    'current_price': 41.50,
                    'change': 2.70,
                    'pct_change': 6.96,
                    'open': 40.80,
                    'high': 42.80,
                    'low': 40.50,
                    'pre_close': 38.80,
                    'volume': 1256800,
                    'amount': 52145000,
                    'turnover_rate': 4.25,
                    'pe_ttm': 16.8,
                    'pb': 1.9,
                    'total_mv': 428.7,
                    'circ_mv': 385.2
                },
                'technical': {
                    'MA5': 40.20,
                    'MA10': 38.90,
                    'MA20': 37.50,
                    'MA30': 36.80,
                    'RSI': 68.2,
                    'MACD': 0.28,
                    'MACD_Signal': 0.15,
                    'K': 72.5,
                    'D': 65.8,
                    'J': 85.9,
                    'BB_Upper': 43.50,
                    'BB_Middle': 38.20,
                    'BB_Lower': 32.90,
                    'price_vs_ma20': 10.7,
                    'trend': '多头排列',
                    'trend_score': 20,
                    'volatility': 28.6
                },
                'financial': {
                    'ROE': 11.5,
                    'gross_margin': 22.8,
                    'net_margin': 6.8,
                    'debt_ratio': 52.8,
                    'revenue_growth': 15.2,
                    'profit_growth': 18.9,
                    'EPS': 2.47,
                    'BPS': 21.58,
                    'current_ratio': 1.6,
                    'quick_ratio': 1.2
                },
                'news': {
                    'news_count': 8,
                    'sentiment_score': 6,
                    'sentiment_level': '中性偏乐观',
                    'latest_titles': [
                        '建设工业：基建投资回暖，装配式建筑业务增长',
                        '房地产政策边际改善，建筑类公司受益',
                        '建设工业中标大型基础设施项目'
                    ]
                },
                'industry': {
                    'industry_name': '建筑装饰',
                    'industry_pe': 18.2,
                    'industry_growth': 12.8,
                    'market_position': '区域龙头'
                }
            },
            
            '301052': {  # 果麦文化
                'basic': {
                    'name': '果麦文化',
                    'current_price': 51.25,
                    'change': 2.29,
                    'pct_change': 4.68,
                    'open': 50.80,
                    'high': 52.90,
                    'low': 50.20,
                    'pre_close': 48.96,
                    'volume': 328500,
                    'amount': 16852000,
                    'turnover_rate': 3.32,
                    'pe_ttm': 28.5,
                    'pb': 3.8,
                    'total_mv': 50.7,
                    'circ_mv': 32.5
                },
                'technical': {
                    'MA5': 49.80,
                    'MA10': 48.20,
                    'MA20': 46.50,
                    'MA30': 45.80,
                    'RSI': 62.8,
                    'MACD': 0.15,
                    'MACD_Signal': 0.08,
                    'K': 58.9,
                    'D': 52.6,
                    'J': 71.5,
                    'BB_Upper': 54.20,
                    'BB_Middle': 47.80,
                    'BB_Lower': 41.40,
                    'price_vs_ma20': 10.2,
                    'trend': '多头排列',
                    'trend_score': 20,
                    'volatility': 35.8
                },
                'financial': {
                    'ROE': 18.6,
                    'gross_margin': 45.2,
                    'net_margin': 15.8,
                    'debt_ratio': 28.5,
                    'revenue_growth': 22.8,
                    'profit_growth': 28.5,
                    'EPS': 1.80,
                    'BPS': 13.48,
                    'current_ratio': 2.8,
                    'quick_ratio': 2.5
                },
                'news': {
                    'news_count': 12,
                    'sentiment_score': 15,
                    'sentiment_level': '乐观',
                    'latest_titles': [
                        '果麦文化：优质IP运营能力突出，数字化转型加速',
                        '出版传媒行业复苏，头部公司受益明显',
                        '果麦文化签约知名作家，内容储备进一步丰富'
                    ]
                },
                'industry': {
                    'industry_name': '传媒-出版',
                    'industry_pe': 32.8,
                    'industry_growth': 18.5,
                    'market_position': '细分领先'
                }
            },
            
            '300308': {  # 中际旭创
                'basic': {
                    'name': '中际旭创',
                    'current_price': 191.87,
                    'change': 6.65,
                    'pct_change': 3.59,
                    'open': 189.50,
                    'high': 195.80,
                    'low': 188.20,
                    'pre_close': 185.22,
                    'volume': 1285600,
                    'amount': 246852000,
                    'turnover_rate': 1.85,
                    'pe_ttm': 35.2,
                    'pb': 4.8,
                    'total_mv': 2131.9,
                    'circ_mv': 1958.5
                },
                'technical': {
                    'MA5': 188.90,
                    'MA10': 185.50,
                    'MA20': 180.20,
                    'MA30': 175.80,
                    'RSI': 58.5,
                    'MACD': 2.85,
                    'MACD_Signal': 1.95,
                    'K': 62.8,
                    'D': 58.9,
                    'J': 70.6,
                    'BB_Upper': 198.50,
                    'BB_Middle': 182.80,
                    'BB_Lower': 167.10,
                    'price_vs_ma20': 6.5,
                    'trend': '多头排列',
                    'trend_score': 20,
                    'volatility': 22.8
                },
                'financial': {
                    'ROE': 22.8,
                    'gross_margin': 28.5,
                    'net_margin': 12.8,
                    'debt_ratio': 35.8,
                    'revenue_growth': 45.8,
                    'profit_growth': 52.6,
                    'EPS': 5.45,
                    'BPS': 39.92,
                    'current_ratio': 2.2,
                    'quick_ratio': 1.8
                },
                'news': {
                    'news_count': 22,
                    'sentiment_score': 20,
                    'sentiment_level': '非常乐观',
                    'latest_titles': [
                        '中际旭创：AI算力需求爆发，光模块订单激增',
                        '数据中心建设加速，光模块龙头业绩超预期',
                        '中际旭创获得海外大客户长期订单，业绩确定性强'
                    ]
                },
                'industry': {
                    'industry_name': '通信设备-光模块',
                    'industry_pe': 42.5,
                    'industry_growth': 38.5,
                    'market_position': '行业龙头'
                }
            },
            
            '300368': {  # 汇金股份
                'basic': {
                    'name': '汇金股份',
                    'current_price': 11.64,
                    'change': 0.51,
                    'pct_change': 4.58,
                    'open': 11.35,
                    'high': 12.10,
                    'low': 11.20,
                    'pre_close': 11.13,
                    'volume': 985600,
                    'amount': 11456000,
                    'turnover_rate': 2.85,
                    'pe_ttm': 42.8,
                    'pb': 2.1,
                    'total_mv': 61.6,
                    'circ_mv': 58.2
                },
                'technical': {
                    'MA5': 11.25,
                    'MA10': 10.95,
                    'MA20': 10.80,
                    'MA30': 10.60,
                    'RSI': 55.8,
                    'MACD': 0.08,
                    'MACD_Signal': 0.05,
                    'K': 48.5,
                    'D': 45.2,
                    'J': 55.1,
                    'BB_Upper': 12.50,
                    'BB_Middle': 10.90,
                    'BB_Lower': 9.30,
                    'price_vs_ma20': 7.8,
                    'trend': '多头排列',
                    'trend_score': 20,
                    'volatility': 28.5
                },
                'financial': {
                    'ROE': 8.5,
                    'gross_margin': 35.8,
                    'net_margin': 8.5,
                    'debt_ratio': 38.2,
                    'revenue_growth': 8.5,
                    'profit_growth': 12.8,
                    'EPS': 0.27,
                    'BPS': 5.52,
                    'current_ratio': 1.9,
                    'quick_ratio': 1.6
                },
                'news': {
                    'news_count': 6,
                    'sentiment_score': 2,
                    'sentiment_level': '中性',
                    'latest_titles': [
                        '汇金股份：金融科技业务稳定，数字货币概念受关注',
                        '银行IT系统集成需求平稳，传统业务增长有限',
                        '汇金股份积极布局金融科技新领域'
                    ]
                },
                'industry': {
                    'industry_name': '计算机应用-金融科技',
                    'industry_pe': 38.5,
                    'industry_growth': 15.2,
                    'market_position': '细分参与者'
                }
            }
        }
        
        return mock_data
    
    def calculate_technical_score(self, technical_data):
        """计算技术面评分"""
        score = 0
        factors = []
        
        # 趋势评分
        trend_score = technical_data.get('trend_score', 0)
        score += trend_score
        if trend_score > 0:
            factors.append(f"均线{technical_data.get('trend', '多头')}格局")
        
        # RSI评分
        rsi = technical_data.get('RSI', 50)
        if rsi > 80:
            score -= 15
            factors.append(f"RSI={rsi:.1f}严重超买")
        elif rsi > 70:
            score -= 8
            factors.append(f"RSI={rsi:.1f}超买")
        elif rsi < 20:
            score += 15
            factors.append(f"RSI={rsi:.1f}严重超卖")
        elif rsi < 30:
            score += 8
            factors.append(f"RSI={rsi:.1f}超卖")
        
        # MACD评分
        macd = technical_data.get('MACD', 0)
        macd_signal = technical_data.get('MACD_Signal', 0)
        if macd > macd_signal and macd > 0:
            score += 10
            factors.append("MACD金叉向上")
        elif macd < macd_signal and macd < 0:
            score -= 10
            factors.append("MACD死叉向下")
        
        # 价格位置评分
        price_vs_ma20 = technical_data.get('price_vs_ma20', 0)
        if price_vs_ma20 > 15:
            score += 8
            factors.append(f"价格高于MA20 {price_vs_ma20:.1f}%")
        elif price_vs_ma20 < -15:
            score -= 8
            factors.append(f"价格低于MA20 {abs(price_vs_ma20):.1f}%")
        
        # 波动率评分
        volatility = technical_data.get('volatility', 30)
        if volatility > 50:
            score -= 5
            factors.append(f"波动率{volatility:.1f}%偏高")
        
        return score, factors
    
    def calculate_fundamental_score(self, financial_data):
        """计算基本面评分"""
        score = 0
        factors = []
        
        # ROE评分
        roe = financial_data.get('ROE', 0)
        if roe > 20:
            score += 30
            factors.append(f"ROE={roe:.1f}%卓越")
        elif roe > 15:
            score += 25
            factors.append(f"ROE={roe:.1f}%优秀")
        elif roe > 10:
            score += 15
            factors.append(f"ROE={roe:.1f}%良好")
        elif roe < 5:
            score -= 15
            factors.append(f"ROE={roe:.1f}%偏低")
        
        # 成长性评分
        revenue_growth = financial_data.get('revenue_growth', 0)
        profit_growth = financial_data.get('profit_growth', 0)
        
        if revenue_growth > 30:
            score += 20
            factors.append(f"营收增长{revenue_growth:.1f}%高成长")
        elif revenue_growth > 15:
            score += 15
            factors.append(f"营收增长{revenue_growth:.1f}%稳健")
        elif revenue_growth < 0:
            score -= 20
            factors.append(f"营收增长{revenue_growth:.1f}%下滑")
        
        if profit_growth > 40:
            score += 25
            factors.append(f"利润增长{profit_growth:.1f}%强劲")
        elif profit_growth > 20:
            score += 15
            factors.append(f"利润增长{profit_growth:.1f}%良好")
        elif profit_growth < 0:
            score -= 25
            factors.append(f"利润增长{profit_growth:.1f}%下滑")
        
        # 盈利质量评分
        net_margin = financial_data.get('net_margin', 0)
        if net_margin > 15:
            score += 15
            factors.append(f"净利率{net_margin:.1f}%优秀")
        elif net_margin > 8:
            score += 10
            factors.append(f"净利率{net_margin:.1f}%良好")
        elif net_margin < 3:
            score -= 10
            factors.append(f"净利率{net_margin:.1f}%偏低")
        
        # 财务健康度评分
        debt_ratio = financial_data.get('debt_ratio', 50)
        if debt_ratio < 30:
            score += 10
            factors.append(f"负债率{debt_ratio:.1f}%健康")
        elif debt_ratio > 70:
            score -= 15
            factors.append(f"负债率{debt_ratio:.1f}%偏高")
        
        current_ratio = financial_data.get('current_ratio', 1)
        if current_ratio > 2:
            score += 5
            factors.append("流动比率充足")
        elif current_ratio < 1:
            score -= 10
            factors.append("流动性不足")
        
        return score, factors
    
    def calculate_valuation_score(self, basic_data, financial_data, industry_data):
        """计算估值评分"""
        score = 0
        factors = []
        
        pe_ttm = basic_data.get('pe_ttm', 0)
        pb = basic_data.get('pb', 0)
        industry_pe = industry_data.get('industry_pe', 25)
        
        # PE估值评分
        if pe_ttm and pe_ttm > 0:
            pe_discount = (industry_pe - pe_ttm) / industry_pe * 100
            
            if pe_ttm < 15:
                score += 25
                factors.append(f"PE={pe_ttm:.1f}低估值")
            elif pe_ttm < 25:
                score += 15
                factors.append(f"PE={pe_ttm:.1f}合理估值")
            elif pe_ttm < industry_pe:
                score += 10
                factors.append(f"PE={pe_ttm:.1f}低于行业均值")
            elif pe_ttm > industry_pe * 1.5:
                score -= 20
                factors.append(f"PE={pe_ttm:.1f}明显高估")
            elif pe_ttm > 50:
                score -= 15
                factors.append(f"PE={pe_ttm:.1f}估值偏高")
        
        # PB估值评分
        if pb and pb > 0:
            if pb < 1.5:
                score += 20
                factors.append(f"PB={pb:.2f}破净或接近")
            elif pb < 3:
                score += 10
                factors.append(f"PB={pb:.2f}估值合理")
            elif pb > 6:
                score -= 15
                factors.append(f"PB={pb:.2f}市净率偏高")
        
        # PEG评分
        profit_growth = financial_data.get('profit_growth', 0)
        if pe_ttm and profit_growth and profit_growth > 0:
            peg = pe_ttm / profit_growth
            if peg < 1:
                score += 20
                factors.append(f"PEG={peg:.2f}成长性估值合理")
            elif peg > 2:
                score -= 10
                factors.append(f"PEG={peg:.2f}成长性估值偏高")
        
        return score, factors
    
    def calculate_sentiment_score(self, news_data):
        """计算情感面评分"""
        score = 0
        factors = []
        
        sentiment_score = news_data.get('sentiment_score', 0)
        news_count = news_data.get('news_count', 0)
        
        if sentiment_score > 15:
            score += 15
            factors.append(f"新闻情感非常乐观({sentiment_score})")
        elif sentiment_score > 8:
            score += 10
            factors.append(f"新闻情感乐观({sentiment_score})")
        elif sentiment_score < -15:
            score -= 15
            factors.append(f"新闻情感悲观({sentiment_score})")
        elif sentiment_score < -8:
            score -= 10
            factors.append(f"新闻情感偏负面({sentiment_score})")
        
        if news_count > 15:
            score += 5
            factors.append(f"市场关注度高({news_count}条新闻)")
        elif news_count < 3:
            score -= 5
            factors.append("市场关注度低")
        
        return score, factors
    
    def comprehensive_analysis(self):
        """执行综合分析"""
        print("🎯 开始极致详细的多维度股票分析")
        print("=" * 80)
        
        # 获取模拟数据
        mock_data = self.create_mock_data()
        
        analysis_results = {}
        
        for code in self.stock_codes:
            print(f"\n📊 正在深度分析 {code} - {self.stock_names[code]}")
            print("-" * 60)
            
            data = mock_data[code]
            
            # 各维度评分
            technical_score, technical_factors = self.calculate_technical_score(data['technical'])
            fundamental_score, fundamental_factors = self.calculate_fundamental_score(data['financial'])
            valuation_score, valuation_factors = self.calculate_valuation_score(
                data['basic'], data['financial'], data['industry']
            )
            sentiment_score, sentiment_factors = self.calculate_sentiment_score(data['news'])
            
            # 权重设置
            weights = {
                'technical': 0.25,     # 技术面25%
                'fundamental': 0.35,   # 基本面35%
                'valuation': 0.25,     # 估值25%
                'sentiment': 0.15      # 情感面15%
            }
            
            # 计算加权总分
            total_score = (
                technical_score * weights['technical'] +
                fundamental_score * weights['fundamental'] +
                valuation_score * weights['valuation'] +
                sentiment_score * weights['sentiment']
            )
            
            # 生成投资建议
            if total_score >= 60:
                recommendation = "强烈买入"
                confidence = "高"
                color = "🟢"
            elif total_score >= 35:
                recommendation = "买入"
                confidence = "中高"
                color = "🟢"
            elif total_score >= 10:
                recommendation = "持有观望"
                confidence = "中等"
                color = "🟡"
            elif total_score >= -20:
                recommendation = "减持"
                confidence = "中高"
                color = "🟠"
            else:
                recommendation = "卖出"
                confidence = "高"
                color = "🔴"
            
            # 风险评估
            risk_factors = []
            
            # 估值风险
            pe_ttm = data['basic'].get('pe_ttm', 0)
            if pe_ttm > 50:
                risk_factors.append("估值过高风险")
            
            # 技术风险
            rsi = data['technical'].get('RSI', 50)
            if rsi > 80:
                risk_factors.append("技术指标严重超买")
            
            volatility = data['technical'].get('volatility', 30)
            if volatility > 45:
                risk_factors.append("价格波动风险大")
            
            # 基本面风险
            debt_ratio = data['financial'].get('debt_ratio', 50)
            if debt_ratio > 70:
                risk_factors.append("财务杠杆过高")
            
            # 行业风险
            industry_growth = data['industry'].get('industry_growth', 10)
            if industry_growth < 5:
                risk_factors.append("行业增长乏力")
            
            if not risk_factors:
                risk_factors.append("整体风险可控")
            
            # 目标价计算
            current_price = data['basic']['current_price']
            eps = data['financial']['EPS']
            profit_growth = data['financial'].get('profit_growth', 10)
            
            # 基于PEG的目标价
            reasonable_pe = min(profit_growth * 0.8, 25)  # 合理PE
            target_price = eps * reasonable_pe
            target_price = min(target_price, current_price * 1.4)  # 限制涨幅40%
            
            upside_potential = (target_price - current_price) / current_price * 100
            
            # 止损价计算
            atr_equivalent = current_price * volatility / 100 * 0.1  # 模拟ATR
            stop_loss = current_price - (atr_equivalent * 2)
            stop_loss = max(stop_loss, current_price * 0.85)  # 最大止损15%
            
            analysis_result = {
                'basic_data': data['basic'],
                'technical_data': data['technical'],
                'financial_data': data['financial'],
                'industry_data': data['industry'], 
                'news_data': data['news'],
                'scores': {
                    'technical': technical_score,
                    'fundamental': fundamental_score,
                    'valuation': valuation_score,
                    'sentiment': sentiment_score,
                    'total': total_score
                },
                'factors': {
                    'technical': technical_factors,
                    'fundamental': fundamental_factors,
                    'valuation': valuation_factors,
                    'sentiment': sentiment_factors
                },
                'recommendation': {
                    'action': recommendation,
                    'confidence': confidence,
                    'color': color,
                    'target_price': target_price,
                    'upside_potential': upside_potential,
                    'stop_loss': stop_loss,
                    'risk_factors': risk_factors
                }
            }
            
            analysis_results[code] = analysis_result
            
            # 实时输出分析结果
            print(f"💰 当前价格: ¥{current_price:.2f} ({data['basic']['pct_change']:+.2f}%)")
            print(f"📊 总市值: {data['basic']['total_mv']:.1f}亿元")
            print(f"🏷️ PE: {pe_ttm:.1f}, PB: {data['basic']['pb']:.2f}")
            print(f"")
            print(f"📈 技术面评分: {technical_score:.1f} - {', '.join(technical_factors[:2])}")
            print(f"💼 基本面评分: {fundamental_score:.1f} - ROE{data['financial']['ROE']:.1f}%, 营收增长{data['financial']['revenue_growth']:.1f}%")
            print(f"💰 估值评分: {valuation_score:.1f} - PE{pe_ttm:.1f}, 行业PE{data['industry']['industry_pe']:.1f}")
            print(f"📰 情感面评分: {sentiment_score:.1f} - {data['news']['sentiment_level']}")
            print(f"")
            print(f"{color} 🎯 投资建议: {recommendation} (综合评分: {total_score:.1f})")
            print(f"🔍 置信度: {confidence}")
            print(f"🎯 目标价: ¥{target_price:.2f} (上涨空间: {upside_potential:+.1f}%)")
            print(f"🛑 止损价: ¥{stop_loss:.2f}")
            
            print(f"\n✅ 主要优势:")
            all_positive_factors = (technical_factors + fundamental_factors + 
                                  valuation_factors + sentiment_factors)
            for factor in all_positive_factors[:3]:
                print(f"   • {factor}")
            
            print(f"\n⚠️ 主要风险:")
            for factor in risk_factors[:3]:
                print(f"   • {factor}")
        
        self.analysis_results = analysis_results
        return analysis_results
    
    def generate_final_report(self):
        """生成最终分析报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 按评分排序
        sorted_results = sorted(
            self.analysis_results.items(),
            key=lambda x: x[1]['scores']['total'],
            reverse=True
        )
        
        print(f"\n" + "🏆" * 40)
        print("最终投资建议排序")
        print("🏆" * 40)
        
        report_lines = [
            "# 📊 5只股票极致详细多维度分析报告",
            "",
            f"**分析日期**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}  ",
            f"**分析股票**: {', '.join(self.stock_codes)}  ",
            f"**分析维度**: 技术面(25%) + 基本面(35%) + 估值(25%) + 情感面(15%)  ",
            f"**数据来源**: 模拟真实市场数据  ",
            "",
            "## 🎯 投资建议总览表",
            "",
            "| 排名 | 代码 | 名称 | 当前价 | 涨跌幅 | 综合评分 | 投资建议 | 目标价 | 上涨空间 | 风险等级 |",
            "|------|------|------|--------|--------|----------|----------|--------|----------|----------|"
        ]
        
        for i, (code, result) in enumerate(sorted_results, 1):
            basic = result['basic_data']
            rec = result['recommendation']
            
            risk_level = "高风险" if len(rec['risk_factors']) > 2 else "中风险" if len(rec['risk_factors']) > 1 else "低风险"
            
            report_lines.append(
                f"| {i} | {code} | {self.stock_names[code]} | ¥{basic['current_price']:.2f} | "
                f"{basic['pct_change']:+.2f}% | {result['scores']['total']:.1f} | "
                f"{rec['color']} {rec['action']} | ¥{rec['target_price']:.2f} | "
                f"{rec['upside_potential']:+.1f}% | {risk_level} |"
            )
        
        report_lines.extend([
            "",
            "## 📈 详细分析报告",
            ""
        ])
        
        # 详细分析每只股票
        for i, (code, result) in enumerate(sorted_results, 1):
            basic = result['basic_data']
            tech = result['technical_data']
            fin = result['financial_data']
            ind = result['industry_data']
            news = result['news_data']
            scores = result['scores']
            factors = result['factors']
            rec = result['recommendation']
            
            report_lines.extend([
                f"### {rec['color']} {i}. {code} - {self.stock_names[code]}",
                "",
                f"**{rec['color']} 投资建议**: {rec['action']} (综合评分: {scores['total']:.1f}分，置信度: {rec['confidence']})**",
                "",
                f"#### 📊 核心数据概览",
                f"- **当前价格**: ¥{basic['current_price']:.2f} (今日{basic['pct_change']:+.2f}%)",
                f"- **总市值**: {basic['total_mv']:.1f}亿元",
                f"- **成交额**: {basic['amount']/100000000:.2f}亿元",
                f"- **换手率**: {basic['turnover_rate']:.2f}%",
                f"- **PE(TTM)**: {basic['pe_ttm']:.1f} | **PB**: {basic['pb']:.2f}",
                f"- **所属行业**: {ind['industry_name']} | **市场地位**: {ind['market_position']}",
                "",
                f"#### 🔧 技术分析 (评分: {scores['technical']:.1f}分)",
                f"- **趋势状态**: {tech['trend']} | **价格位置**: 相对MA20 {tech['price_vs_ma20']:+.1f}%",
                f"- **移动均线**: MA5(¥{tech['MA5']:.2f}) > MA10(¥{tech['MA10']:.2f}) > MA20(¥{tech['MA20']:.2f})",
                f"- **RSI指标**: {tech['RSI']:.1f} | **MACD**: {tech['MACD']:.3f} > Signal({tech['MACD_Signal']:.3f})",
                f"- **KDJ指标**: K({tech['K']:.1f}) D({tech['D']:.1f}) J({tech['J']:.1f})",
                f"- **布林带**: 上轨¥{tech['BB_Upper']:.2f} 中轨¥{tech['BB_Middle']:.2f} 下轨¥{tech['BB_Lower']:.2f}",
                f"- **波动率**: {tech['volatility']:.1f}%",
                f"- **技术要点**: {' | '.join(factors['technical'][:3])}",
                "",
                f"#### 💼 基本面分析 (评分: {scores['fundamental']:.1f}分)",
                f"- **盈利能力**: ROE {fin['ROE']:.1f}% | 净利率 {fin['net_margin']:.1f}% | 毛利率 {fin['gross_margin']:.1f}%",
                f"- **成长能力**: 营收增长 {fin['revenue_growth']:.1f}% | 净利润增长 {fin['profit_growth']:.1f}%",
                f"- **财务健康**: 资产负债率 {fin['debt_ratio']:.1f}% | 流动比率 {fin['current_ratio']:.1f}",
                f"- **每股指标**: EPS ¥{fin['EPS']:.2f} | BPS ¥{fin['BPS']:.2f}",
                f"- **基本面要点**: {' | '.join(factors['fundamental'][:3])}",
                "",
                f"#### 💰 估值分析 (评分: {scores['valuation']:.1f}分)",
                f"- **估值水平**: PE {basic['pe_ttm']:.1f} vs 行业PE {ind['industry_pe']:.1f}",
                f"- **市净率**: PB {basic['pb']:.2f}",
                f"- **PEG比率**: {basic['pe_ttm']:.1f}/{fin['profit_growth']:.1f} = {basic['pe_ttm']/fin['profit_growth']:.2f}" if fin['profit_growth'] > 0 else "- **PEG比率**: N/A",
                f"- **估值要点**: {' | '.join(factors['valuation'][:3])}",
                "",
                f"#### 📰 市场情感分析 (评分: {scores['sentiment']:.1f}分)",
                f"- **新闻关注度**: {news['news_count']}条相关新闻",
                f"- **情感倾向**: {news['sentiment_level']} (评分: {news['sentiment_score']})",
                f"- **热点新闻**:",
            ])
            
            for j, title in enumerate(news['latest_titles'][:3], 1):
                report_lines.append(f"  {j}. {title}")
            
            if factors['sentiment']:
                report_lines.append(f"- **情感要点**: {' | '.join(factors['sentiment'])}")
            
            report_lines.extend([
                "",
                f"#### 🎯 投资策略建议",
                f"- **目标价格**: ¥{rec['target_price']:.2f} (上涨空间: {rec['upside_potential']:+.1f}%)",
                f"- **止损价格**: ¥{rec['stop_loss']:.2f} (风险控制: {(rec['stop_loss']-basic['current_price'])/basic['current_price']*100:+.1f}%)",
                f"- **建议仓位**: {'重仓' if scores['total'] >= 60 else '中等仓位' if scores['total'] >= 35 else '轻仓试探' if scores['total'] >= 10 else '观望'}",
                f"- **持有周期**: {'中长期(6-12个月)' if scores['total'] >= 35 else '中短期(3-6个月)' if scores['total'] >= 10 else '短期观察'}",
                "",
                f"#### 🚨 风险提示",
            ])
            
            for risk in rec['risk_factors']:
                report_lines.append(f"- {risk}")
            
            report_lines.extend([
                "",
                "---",
                ""
            ])
        
        # 投资组合建议
        strong_buy = [item for item in sorted_results if item[1]['recommendation']['action'] == '强烈买入']
        buy = [item for item in sorted_results if item[1]['recommendation']['action'] == '买入']
        hold = [item for item in sorted_results if item[1]['recommendation']['action'] == '持有观望']
        
        report_lines.extend([
            "## 🎯 投资组合策略建议",
            "",
            f"### 🟢 核心持仓 - 强烈买入 ({len(strong_buy)}只)",
        ])
        
        if strong_buy:
            total_strong_weight = 0
            for code, result in strong_buy:
                weight = min(40, result['scores']['total'])  # 最高权重40%
                total_strong_weight += weight
                report_lines.append(f"- **{code} - {self.stock_names[code]}**: 建议权重 {weight:.0f}% (评分{result['scores']['total']:.1f})")
        else:
            report_lines.append("- 当前无强烈推荐标的")
        
        report_lines.extend([
            "",
            f"### 🟢 配置持仓 - 买入 ({len(buy)}只)",
        ])
        
        if buy:
            for code, result in buy:
                weight = min(25, result['scores']['total'] * 0.6)
                report_lines.append(f"- **{code} - {self.stock_names[code]}**: 建议权重 {weight:.0f}% (评分{result['scores']['total']:.1f})")
        
        report_lines.extend([
            "",
            f"### 🟡 观察名单 - 持有观望 ({len(hold)}只)",
        ])
        
        if hold:
            for code, result in hold:
                report_lines.append(f"- **{code} - {self.stock_names[code]}**: 等待更好买入时机 (评分{result['scores']['total']:.1f})")
        
        report_lines.extend([
            "",
            "## 📊 市场环境分析",
            "",
            "### 行业景气度对比",
        ])
        
        # 按行业汇总
        industry_analysis = {}
        for code, result in self.analysis_results.items():
            industry = result['industry_data']['industry_name']
            if industry not in industry_analysis:
                industry_analysis[industry] = []
            industry_analysis[industry].append((code, result))
        
        for industry, stocks in industry_analysis.items():
            avg_score = np.mean([stock[1]['scores']['total'] for stock in stocks])
            avg_growth = np.mean([stock[1]['industry_data']['industry_growth'] for stock in stocks])
            
            report_lines.append(f"- **{industry}**: 平均评分 {avg_score:.1f}分，行业增长率 {avg_growth:.1f}%")
            for code, result in stocks:
                report_lines.append(f"  - {code} {self.stock_names[code]}: {result['scores']['total']:.1f}分")
        
        report_lines.extend([
            "",
            "## 🚨 重要风险提示与免责声明",
            "",
            "### ⚠️ 投资风险",
            "1. **市场风险**: 股票价格受市场情绪、宏观经济等多因素影响，存在较大波动风险",
            "2. **个股风险**: 公司经营、行业变化、政策调整等可能影响个股表现",
            "3. **流动性风险**: 部分股票可能存在成交量不足，影响买卖操作",
            "4. **估值风险**: 高估值股票面临估值回归压力",
            "5. **技术风险**: 技术分析存在滞后性，不能完全预测未来走势",
            "",
            "### 📋 操作建议", 
            "1. **分批建仓**: 避免一次性满仓，建议分2-3次建仓",
            "2. **严格止损**: 设置止损位并严格执行，控制单只股票损失",
            "3. **动态调整**: 根据市场变化和基本面变化及时调整持仓",
            "4. **分散投资**: 不要过度集中持股，建议持有3-5只不同行业股票",
            "5. **持续跟踪**: 定期关注公司公告、业绩报告等重要信息",
            "",
            "### 📜 免责声明",
            "1. 本报告基于公开信息分析，仅供投资参考，不构成买卖建议",
            "2. 投资者应根据自身风险承受能力和投资目标做出独立判断",
            "3. 过往业绩不代表未来表现，投资有风险，入市需谨慎",
            "4. 本报告不对投资损失承担任何责任",
            "",
            "---",
            "",
            f"**报告生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H时%M分')}  ",
            f"**分析工具**: Python量化分析系统  ",
            f"**版本**: 极致详细多维度分析 v2.0  "
        ])
        
        # 保存报告
        report_content = '\n'.join(report_lines)
        report_file = f'极致详细多维度股票分析报告_{timestamp}.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 保存JSON数据
        json_file = f'详细分析数据_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'analysis_date': datetime.now().isoformat(),
                'analysis_results': self.analysis_results,
                'summary': {
                    'total_stocks': len(self.stock_codes),
                    'strong_buy': len(strong_buy),
                    'buy': len(buy), 
                    'hold': len(hold),
                    'average_score': np.mean([r['scores']['total'] for r in self.analysis_results.values()])
                }
            }, f, ensure_ascii=False, indent=2, default=str)
        
        # 控制台最终总结
        print(f"\n📊 投资建议总结:")
        print(f"   🟢 强烈买入: {len(strong_buy)}只")
        print(f"   🟢 买入: {len(buy)}只") 
        print(f"   🟡 持有观望: {len(hold)}只")
        
        print(f"\n🏆 最佳投资标的:")
        for i, (code, result) in enumerate(sorted_results[:3], 1):
            basic = result['basic_data']
            rec = result['recommendation']
            print(f"   {i}. {code} - {self.stock_names[code]}: {rec['action']} (评分{result['scores']['total']:.1f})")
        
        print(f"\n📄 详细报告已保存:")
        print(f"   - Markdown报告: {report_file}")
        print(f"   - JSON数据: {json_file}")
        
        return sorted_results

def main():
    analyzer = ComprehensiveStockAnalyzer()
    
    # 执行综合分析
    analyzer.comprehensive_analysis()
    
    # 生成最终报告
    final_results = analyzer.generate_final_report()
    
    return analyzer, final_results

if __name__ == "__main__":
    main()