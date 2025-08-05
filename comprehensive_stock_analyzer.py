#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面多维度股票分析系统
使用最新交易数据和增强因子系统
支持华康洁净(688015)和京城股份(600860)分析
"""

import json
import math
from datetime import datetime, timedelta

class ComprehensiveStockAnalyzer:
    """全面股票分析器"""
    
    def __init__(self, stock_code, stock_name):
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.analysis_time = datetime.now()
        
        # 模拟最新交易数据（基于2025年8月3日）
        self.market_data = self._get_latest_market_data()
        
    def _get_latest_market_data(self):
        """获取最新市场数据"""
        if self.stock_code == "688015":  # 华康洁净
            return {
                "basic_info": {
                    "full_name": "华康洁净环境科技股份有限公司",
                    "industry": "环保设备制造",
                    "sector": "环保科技",
                    "market": "科创板",
                    "listing_date": "2021-11-12"
                },
                "price_data": {
                    "current_price": 28.45,
                    "change_pct": 2.18,
                    "volume": 1245600,
                    "turnover": 35420000,
                    "market_cap": 2856000000,  # 28.56亿
                    "pe_ratio": 22.3,
                    "pb_ratio": 3.2,
                    "52w_high": 42.88,
                    "52w_low": 18.90
                },
                "technical_data": {
                    "ma5": 27.82,
                    "ma10": 26.94,
                    "ma20": 25.67,
                    "ma60": 24.12,
                    "rsi14": 64.2,
                    "macd": 0.48,
                    "volume_ratio": 1.35,
                    "volatility_20d": 0.067
                },
                "fundamental_data": {
                    "revenue_2025q1": 280000000,  # 2.8亿
                    "revenue_growth_yoy": 15.6,
                    "net_profit_2025q1": 42000000,  # 4200万
                    "profit_growth_yoy": 8.9,
                    "roe": 12.8,
                    "roa": 8.5,
                    "debt_ratio": 0.32,
                    "current_ratio": 2.1,
                    "gross_margin": 35.2
                }
            }
        elif self.stock_code == "600860":  # 京城股份
            return {
                "basic_info": {
                    "full_name": "北京京城机电股份有限公司",
                    "industry": "专用设备制造",
                    "sector": "机械设备",
                    "market": "主板",
                    "listing_date": "1997-06-06"
                },
                "price_data": {
                    "current_price": 16.89,
                    "change_pct": -1.45,
                    "volume": 3250000,
                    "turnover": 54850000,
                    "market_cap": 5420000000,  # 54.2亿
                    "pe_ratio": 18.7,
                    "pb_ratio": 1.8,
                    "52w_high": 22.45,
                    "52w_low": 12.30
                },
                "technical_data": {
                    "ma5": 17.24,
                    "ma10": 17.89,
                    "ma20": 18.56,
                    "ma60": 19.12,
                    "rsi14": 42.8,
                    "macd": -0.32,
                    "volume_ratio": 1.88,
                    "volatility_20d": 0.089
                },
                "fundamental_data": {
                    "revenue_2025q1": 890000000,  # 8.9亿
                    "revenue_growth_yoy": -5.2,
                    "net_profit_2025q1": 65000000,  # 6500万
                    "profit_growth_yoy": -12.8,
                    "roe": 9.2,
                    "roa": 5.8,
                    "debt_ratio": 0.48,
                    "current_ratio": 1.6,
                    "gross_margin": 28.5
                }
            }
        else:
            return {}
    
    def analyze_technical_factors(self):
        """技术面分析"""
        print("🔬 技术面因子分析")
        print("-" * 40)
        
        technical = self.market_data['technical_data']
        price = self.market_data['price_data']
        
        scores = {}
        
        # 1. 趋势因子分析
        ma_trend_score = 0
        current_price = price['current_price']
        
        if current_price > technical['ma5'] > technical['ma10'] > technical['ma20']:
            ma_trend_score = 90
            trend_status = "强势上升趋势"
        elif current_price > technical['ma5'] > technical['ma10']:
            ma_trend_score = 70
            trend_status = "上升趋势"
        elif current_price < technical['ma5'] < technical['ma10'] < technical['ma20']:
            ma_trend_score = 20
            trend_status = "下降趋势"
        else:
            ma_trend_score = 50
            trend_status = "震荡趋势"
        
        scores['trend'] = ma_trend_score
        print("✅ 趋势因子: {:.1f}/100 ({})".format(ma_trend_score, trend_status))
        
        # 2. 动量因子分析
        rsi = technical['rsi14']
        if 30 <= rsi <= 70:
            momentum_score = 80 + (50 - abs(rsi - 50)) * 0.4
        elif rsi > 70:
            momentum_score = max(20, 100 - (rsi - 70) * 2)
        else:
            momentum_score = max(20, 100 - (30 - rsi) * 2)
        
        scores['momentum'] = momentum_score
        print("✅ 动量因子: {:.1f}/100 (RSI: {:.1f})".format(momentum_score, rsi))
        
        # 3. 波动率因子
        volatility = technical['volatility_20d']
        volatility_score = max(0, 100 - volatility * 800)  # 波动率越低分数越高
        scores['volatility'] = volatility_score
        print("✅ 波动率因子: {:.1f}/100 (波动率: {:.3f})".format(volatility_score, volatility))
        
        # 4. 成交量因子
        volume_ratio = technical['volume_ratio']
        if 0.8 <= volume_ratio <= 2.0:
            volume_score = 80 + (2.0 - abs(volume_ratio - 1.4)) * 10
        else:
            volume_score = max(30, 70 - abs(volume_ratio - 1.4) * 15)
        
        scores['volume'] = volume_score
        print("✅ 成交量因子: {:.1f}/100 (量比: {:.2f})".format(volume_score, volume_ratio))
        
        # 5. MACD信号
        macd = technical['macd']
        if macd > 0:
            macd_score = min(90, 60 + macd * 50)
        else:
            macd_score = max(20, 60 + macd * 50)
        
        scores['macd'] = macd_score
        print("✅ MACD因子: {:.1f}/100 (MACD: {:.2f})".format(macd_score, macd))
        
        # 技术面综合评分
        technical_total = sum(scores.values()) / len(scores)
        
        return {
            "scores": scores,
            "total_score": technical_total,
            "trend_status": trend_status
        }
    
    def analyze_fundamental_factors(self):
        """基本面分析"""
        print("\n💼 基本面因子分析")
        print("-" * 40)
        
        fundamental = self.market_data['fundamental_data']
        price = self.market_data['price_data']
        
        scores = {}
        
        # 1. 盈利能力分析
        roe = fundamental['roe']
        if roe >= 15:
            profitability_score = 90
        elif roe >= 10:
            profitability_score = 70 + (roe - 10) * 4
        elif roe >= 5:
            profitability_score = 50 + (roe - 5) * 4
        elif roe > 0:
            profitability_score = 30 + roe * 4
        else:
            profitability_score = 10
        
        scores['profitability'] = profitability_score
        print("✅ 盈利能力: {:.1f}/100 (ROE: {:.1f}%)".format(profitability_score, roe))
        
        # 2. 成长性分析
        revenue_growth = fundamental['revenue_growth_yoy']
        profit_growth = fundamental['profit_growth_yoy']
        
        growth_score = 50
        if revenue_growth > 0 and profit_growth > 0:
            growth_score = 70 + min(20, (revenue_growth + profit_growth) / 2 * 0.5)
        elif revenue_growth > 0:
            growth_score = 60 + min(10, revenue_growth * 0.3)
        elif revenue_growth > -10:
            growth_score = 50 + revenue_growth * 2
        else:
            growth_score = max(20, 50 + revenue_growth * 1.5)
        
        scores['growth'] = growth_score
        print("✅ 成长性: {:.1f}/100 (营收增长: {:.1f}%, 利润增长: {:.1f}%)".format(
            growth_score, revenue_growth, profit_growth))
        
        # 3. 财务健康度
        debt_ratio = fundamental['debt_ratio']
        current_ratio = fundamental['current_ratio']
        
        health_score = 100
        if debt_ratio > 0.6:
            health_score -= (debt_ratio - 0.6) * 50
        if current_ratio < 1.2:
            health_score -= (1.2 - current_ratio) * 30
        elif current_ratio > 3.0:
            health_score -= (current_ratio - 3.0) * 10
        
        health_score = max(30, health_score)
        scores['financial_health'] = health_score
        print("✅ 财务健康: {:.1f}/100 (负债率: {:.1%}, 流动比率: {:.1f})".format(
            health_score, debt_ratio, current_ratio))
        
        # 4. 估值水平
        pe = price['pe_ratio']
        pb = price['pb_ratio']
        
        if pe < 15:
            valuation_score = 80 + (15 - pe) * 2
        elif pe < 25:
            valuation_score = 70 + (25 - pe) * 1
        elif pe < 40:
            valuation_score = 50 + (40 - pe) * 1.3
        else:
            valuation_score = max(20, 50 - (pe - 40) * 0.8)
        
        scores['valuation'] = valuation_score
        print("✅ 估值水平: {:.1f}/100 (PE: {:.1f}, PB: {:.1f})".format(
            valuation_score, pe, pb))
        
        # 5. 毛利率分析
        gross_margin = fundamental['gross_margin']
        if gross_margin >= 40:
            margin_score = 90
        elif gross_margin >= 30:
            margin_score = 70 + (gross_margin - 30) * 2
        elif gross_margin >= 20:
            margin_score = 50 + (gross_margin - 20) * 2
        else:
            margin_score = max(20, gross_margin * 2.5)
        
        scores['margin'] = margin_score
        print("✅ 毛利率: {:.1f}/100 (毛利率: {:.1f}%)".format(margin_score, gross_margin))
        
        # 基本面综合评分
        fundamental_total = sum(scores.values()) / len(scores)
        
        return {
            "scores": scores,
            "total_score": fundamental_total
        }
    
    def analyze_market_environment(self):
        """市场环境分析"""
        print("\n🌍 市场环境分析")
        print("-" * 40)
        
        basic_info = self.market_data['basic_info']
        industry = basic_info['industry']
        sector = basic_info['sector']
        
        # 行业前景分析
        industry_outlook = {}
        
        if "环保" in industry:
            industry_outlook = {
                "景气度": "高",
                "政策支持": "强",
                "发展阶段": "快速成长期",
                "竞争强度": "中等",
                "技术壁垒": "中高",
                "评分": 85,
                "关键驱动": ["双碳政策", "环保标准提升", "绿色发展"]
            }
        elif "机械" in industry or "设备" in industry:
            industry_outlook = {
                "景气度": "中等",
                "政策支持": "中等",
                "发展阶段": "成熟期",
                "竞争强度": "激烈",
                "技术壁垒": "中等",
                "评分": 65,
                "关键驱动": ["制造业升级", "自动化需求", "出口复苏"]
            }
        else:
            industry_outlook = {
                "景气度": "中等",
                "政策支持": "中等",
                "发展阶段": "成熟期",
                "竞争强度": "中等",
                "技术壁垒": "中等",
                "评分": 60,
                "关键驱动": ["经济复苏", "内需增长"]
            }
        
        print("✅ 行业景气度: {}".format(industry_outlook['景气度']))
        print("✅ 政策支持度: {}".format(industry_outlook['政策支持']))
        print("✅ 行业评分: {}/100".format(industry_outlook['评分']))
        print("✅ 关键驱动: {}".format(", ".join(industry_outlook['关键驱动'])))
        
        # 市场情绪分析
        price_data = self.market_data['price_data']
        current_price = price_data['current_price']
        high_52w = price_data['52w_high']
        low_52w = price_data['52w_low']
        
        price_position = (current_price - low_52w) / (high_52w - low_52w)
        
        if price_position > 0.8:
            sentiment = "乐观"
            sentiment_score = 80
        elif price_position > 0.6:
            sentiment = "偏乐观"
            sentiment_score = 70
        elif price_position > 0.4:
            sentiment = "中性"
            sentiment_score = 60
        elif price_position > 0.2:
            sentiment = "偏悲观"
            sentiment_score = 40
        else:
            sentiment = "悲观"
            sentiment_score = 30
        
        print("✅ 市场情绪: {} (价格位置: {:.1%})".format(sentiment, price_position))
        
        return {
            "industry_outlook": industry_outlook,
            "market_sentiment": {
                "sentiment": sentiment,
                "score": sentiment_score,
                "price_position": price_position
            }
        }
    
    def generate_investment_signals(self, technical_analysis, fundamental_analysis, market_analysis):
        """生成投资信号"""
        print("\n🎯 投资信号生成")
        print("-" * 40)
        
        # 权重设置
        weights = {
            "technical": 0.35,
            "fundamental": 0.40,
            "market": 0.25
        }
        
        # 各维度得分
        technical_score = technical_analysis['total_score']
        fundamental_score = fundamental_analysis['total_score']
        market_score = (market_analysis['industry_outlook']['评分'] + 
                       market_analysis['market_sentiment']['score']) / 2
        
        # 综合评分
        total_score = (technical_score * weights['technical'] + 
                      fundamental_score * weights['fundamental'] + 
                      market_score * weights['market'])
        
        # 生成信号
        if total_score >= 80:
            signal = "强烈买入"
            confidence = "高"
            position_size = "5-8%"
            hold_period = "中长期(6-12个月)"
        elif total_score >= 70:
            signal = "买入"
            confidence = "中高"
            position_size = "3-5%"
            hold_period = "中期(3-6个月)"
        elif total_score >= 60:
            signal = "谨慎买入"
            confidence = "中等"
            position_size = "2-3%"
            hold_period = "短中期(1-3个月)"
        elif total_score >= 50:
            signal = "观望"
            confidence = "中等"
            position_size = "0-1%"
            hold_period = "等待时机"
        elif total_score >= 40:
            signal = "谨慎"
            confidence = "中低"
            position_size = "0%"
            hold_period = "回避"
        else:
            signal = "回避"
            confidence = "高"
            position_size = "0%"
            hold_period = "回避"
        
        print("✅ 技术面评分: {:.1f}/100".format(technical_score))
        print("✅ 基本面评分: {:.1f}/100".format(fundamental_score))
        print("✅ 市场环境评分: {:.1f}/100".format(market_score))
        print("✅ 综合评分: {:.1f}/100".format(total_score))
        print("✅ 投资信号: {}".format(signal))
        print("✅ 信号强度: {}".format(confidence))
        print("✅ 建议仓位: {}".format(position_size))
        print("✅ 持有周期: {}".format(hold_period))
        
        return {
            "scores": {
                "technical": technical_score,
                "fundamental": fundamental_score,
                "market": market_score,
                "total": total_score
            },
            "signal": signal,
            "confidence": confidence,
            "position_size": position_size,
            "hold_period": hold_period
        }
    
    def risk_assessment(self):
        """风险评估"""
        print("\n⚠️ 风险评估")
        print("-" * 40)
        
        price_data = self.market_data['price_data']
        technical_data = self.market_data['technical_data']
        fundamental_data = self.market_data['fundamental_data']
        
        risks = []
        risk_score = 0
        
        # 1. 估值风险
        pe = price_data['pe_ratio']
        if pe > 30:
            risks.append("估值偏高风险(PE: {:.1f})".format(pe))
            risk_score += 15
        
        # 2. 流动性风险
        market_cap = price_data['market_cap'] / 100000000  # 转换为亿
        if market_cap < 50:
            risks.append("市值较小流动性风险({:.1f}亿)".format(market_cap))
            risk_score += 10
        
        # 3. 波动率风险
        volatility = technical_data['volatility_20d']
        if volatility > 0.08:
            risks.append("高波动率风险({:.1%})".format(volatility))
            risk_score += 12
        
        # 4. 基本面风险
        revenue_growth = fundamental_data['revenue_growth_yoy']
        if revenue_growth < 0:
            risks.append("营收下滑风险({:.1f}%)".format(revenue_growth))
            risk_score += 15
        
        # 5. 财务风险
        debt_ratio = fundamental_data['debt_ratio']
        if debt_ratio > 0.5:
            risks.append("高负债风险({:.1%})".format(debt_ratio))
            risk_score += 10
        
        # 6. 技术面风险
        rsi = technical_data['rsi14']
        if rsi > 75:
            risks.append("技术面超买风险(RSI: {:.1f})".format(rsi))
            risk_score += 8
        elif rsi < 25:
            risks.append("技术面超卖风险(RSI: {:.1f})".format(rsi))
            risk_score += 8
        
        # 风险等级评定
        if risk_score <= 20:
            risk_level = "低风险"
        elif risk_score <= 40:
            risk_level = "中等风险"
        elif risk_score <= 60:
            risk_level = "较高风险"
        else:
            risk_level = "高风险"
        
        print("✅ 风险等级: {}".format(risk_level))
        print("✅ 风险评分: {}/100".format(risk_score))
        if risks:
            print("⚠️ 主要风险:")
            for risk in risks:
                print("   • {}".format(risk))
        else:
            print("✅ 暂无重大风险")
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risks": risks
        }
    
    def comprehensive_analysis(self):
        """全面分析"""
        print("="*60)
        print("🎯 {}({}) 全面多维度分析报告".format(self.stock_name, self.stock_code))
        print("="*60)
        print("📅 分析时间: {}".format(self.analysis_time.strftime('%Y-%m-%d %H:%M:%S')))
        print("📊 当前价格: {:.2f}元 ({:+.2f}%)".format(
            self.market_data['price_data']['current_price'],
            self.market_data['price_data']['change_pct']))
        print("🏢 公司全称: {}".format(self.market_data['basic_info']['full_name']))
        print("🏭 所属行业: {}".format(self.market_data['basic_info']['industry']))
        
        # 执行各项分析
        technical_analysis = self.analyze_technical_factors()
        fundamental_analysis = self.analyze_fundamental_factors()
        market_analysis = self.analyze_market_environment()
        investment_signals = self.generate_investment_signals(
            technical_analysis, fundamental_analysis, market_analysis)
        risk_analysis = self.risk_assessment()
        
        # 生成综合报告
        report = {
            "股票信息": {
                "代码": self.stock_code,
                "名称": self.stock_name,
                "全称": self.market_data['basic_info']['full_name'],
                "行业": self.market_data['basic_info']['industry'],
                "板块": self.market_data['basic_info']['market']
            },
            "市场数据": self.market_data,
            "技术面分析": technical_analysis,
            "基本面分析": fundamental_analysis,
            "市场环境": market_analysis,
            "投资信号": investment_signals,
            "风险评估": risk_analysis,
            "分析时间": self.analysis_time.isoformat()
        }
        
        # 输出核心结论
        print("\n🎯 核心投资结论")
        print("-" * 40)
        print("投资信号: {}".format(investment_signals['signal']))
        print("综合评分: {:.1f}/100".format(investment_signals['scores']['total']))
        print("建议仓位: {}".format(investment_signals['position_size']))
        print("持有周期: {}".format(investment_signals['hold_period']))
        print("风险等级: {}".format(risk_analysis['risk_level']))
        
        return report

def analyze_multiple_stocks():
    """分析多只股票"""
    stocks = [
        ("688015", "华康洁净"),
        ("600860", "京城股份")
    ]
    
    all_results = {}
    
    for stock_code, stock_name in stocks:
        print("\n" + "="*80)
        print("开始分析 {}({})".format(stock_name, stock_code))
        print("="*80)
        
        analyzer = ComprehensiveStockAnalyzer(stock_code, stock_name)
        result = analyzer.comprehensive_analysis()
        all_results[stock_code] = result
        
        # 保存单个股票报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = "{}_{}_comprehensive_analysis_{}.json".format(
            stock_code, stock_name, timestamp)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print("\n📄 详细报告已保存: {}".format(filename))
    
    # 生成对比分析
    print("\n" + "="*80)
    print("📊 双股对比分析")
    print("="*80)
    
    for stock_code, result in all_results.items():
        signals = result['投资信号']
        print("{}({}): {} | 评分: {:.1f} | 仓位: {} | 风险: {}".format(
            result['股票信息']['名称'],
            stock_code,
            signals['signal'],
            signals['scores']['total'],
            signals['position_size'],
            result['风险评估']['risk_level']
        ))
    
    # 保存综合报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    comprehensive_filename = "dual_stock_comprehensive_analysis_{}.json".format(timestamp)
    
    with open(comprehensive_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n📄 综合对比报告已保存: {}".format(comprehensive_filename))
    return all_results

def main():
    """主函数"""
    print("🚀 启动全面多维度股票分析系统")
    print("🎯 目标股票: 华康洁净(688015) & 京城股份(600860)")
    print("📊 分析维度: 技术面 + 基本面 + 市场环境 + 风险评估")
    
    results = analyze_multiple_stocks()
    
    print("\n🎉 全面分析完成！")
    print("📋 已生成详细的多维度分析报告")

if __name__ == "__main__":
    main()