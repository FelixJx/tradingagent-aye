#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版个股分析器 - Enhanced Stock Analyzer
集成消息面分析和雷区扫描，提供全方位风险评估
"""

import json
import sys
import os
from datetime import datetime

# 添加路径以导入自定义模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agents.analysts.news_sentiment_analyst import NewsSentimentAnalyst
    from agents.risk_scanner import ThunderboltRiskScanner
    from agents.analysts.fundamentals_analyst import FundamentalsAnalyst
    from agents.analysts.market_analyst import MarketAnalyst
except ImportError as e:
    print("导入模块失败: {}".format(str(e)))
    print("将使用简化版分析")

class EnhancedStockAnalyzer:
    """增强版个股分析器"""
    
    def __init__(self):
        self.analyzer_name = "增强版个股分析器"
        self.version = "2.0"
        
        # 初始化各个分析师
        try:
            self.news_analyst = NewsSentimentAnalyst()
            self.risk_scanner = ThunderboltRiskScanner()
            self.fundamentals_analyst = FundamentalsAnalyst()
            self.market_analyst = MarketAnalyst()
            self.has_all_analysts = True
        except:
            print("⚠️ 部分分析师初始化失败，使用基础分析模式")
            self.has_all_analysts = False
        
        # 分析权重配置
        self.analysis_weights = {
            "基本面": 0.25,
            "技术面": 0.20,
            "消息面": 0.25,
            "雷区风险": 0.30  # 最高权重给风险控制
        }
        
        # 投资决策阈值
        self.decision_thresholds = {
            "强烈买入": 85,
            "买入": 70,
            "谨慎买入": 55,
            "观望": 40,
            "回避": 25,
            "紧急回避": 0
        }
    
    def collect_stock_data(self, stock_code, stock_name):
        """收集股票数据"""
        print("📊 收集 {}({}) 的全方位数据...".format(stock_name, stock_code))
        
        # 模拟数据收集（实际应用中这里会调用各种数据API）
        stock_data = {
            "basic_info": {
                "code": stock_code,
                "name": stock_name,
                "industry": "医疗器械",
                "market": "创业板",
                "listing_date": "2021-12-27"
            },
            "financial": {
                "latest": {
                    "revenue": 835000000,
                    "revenue_growth": 50.73,
                    "net_profit": 18683000,
                    "net_profit_growth": 273.48,
                    "debt_ratio": 53.22,
                    "roe": 16.8,
                    "gross_margin": 31.51,
                    "operating_cash_flow": 19800000,
                    "receivables_to_revenue": 35.5
                },
                "gross_margin_trend": [42.8, 38.5, 35.2, 31.51],  # 连续下滑
                "revenue_trend": [554000000, 678000000, 745000000, 835000000]
            },
            "governance": {
                "top_shareholder_ratio": 44.23,
                "independent_director_ratio": 33.3,
                "related_transaction_ratio": 15.2,
                "executive_changes_12m": 1,
                "board_size": 9,
                "audit_opinion": "标准无保留意见"
            },
            "market": {
                "latest_price": 35.20,
                "price_change_30d": 27.26,
                "volatility_30d": 65.8,
                "volume_ratio_avg": 8.5,
                "avg_turnover_30d": 18.2,
                "limit_down_days_30d": 0,
                "limit_up_days_30d": 2,
                "market_cap": 3500000000
            },
            "news": [
                {
                    "title": "华康洁净：实控人减持华医转债996,710张",
                    "content": "华康洁净实际控制人谭平涛于2025年7月30日至31日期间，减持华医转债996,710张，占发行总量的13.29%。此次减持引发市场关注，可能对股价产生负面影响。",
                    "published_date": "2025-07-31",
                    "source": "证券时报",
                    "sentiment": "负面"
                },
                {
                    "title": "华康洁净发布异常波动公告",
                    "content": "华康洁净股价连续3个交易日累计涨幅超过30%，触发异常波动标准，公司发布公告提示投资风险。",
                    "published_date": "2025-07-31",
                    "source": "上交所",
                    "sentiment": "中性"
                },
                {
                    "title": "华康洁净2025年中报：营收增长50.73%",
                    "content": "华康洁净发布2025年半年报，实现营业收入8.35亿元，同比增长50.73%；归母净利润1868万元，同比增长273.48%。",
                    "published_date": "2025-07-29",
                    "source": "公司公告",
                    "sentiment": "正面"
                }
            ]
        }
        
        return stock_data
    
    def analyze_fundamentals(self, stock_data):
        """基本面分析"""
        print("\n💰 基本面分析")
        print("-" * 40)
        
        financial = stock_data.get('financial', {}).get('latest', {})
        
        # 基本面评分
        fundamental_score = 50  # 基础分
        
        # 成长性评分
        revenue_growth = financial.get('revenue_growth', 0)
        profit_growth = financial.get('net_profit_growth', 0)
        
        if revenue_growth > 30:
            fundamental_score += 15
        elif revenue_growth > 15:
            fundamental_score += 10
        elif revenue_growth > 0:
            fundamental_score += 5
        else:
            fundamental_score -= 10
        
        if profit_growth > 100:
            fundamental_score += 20
        elif profit_growth > 50:
            fundamental_score += 15
        elif profit_growth > 0:
            fundamental_score += 10
        else:
            fundamental_score -= 15
        
        # 盈利能力评分
        roe = financial.get('roe', 0)
        gross_margin = financial.get('gross_margin', 0)
        
        if roe > 15:
            fundamental_score += 10
        elif roe > 10:
            fundamental_score += 5
        
        if gross_margin > 40:
            fundamental_score += 10
        elif gross_margin > 30:
            fundamental_score += 5
        
        # 财务健康评分
        debt_ratio = financial.get('debt_ratio', 0)
        cash_flow = financial.get('operating_cash_flow', 0)
        
        if debt_ratio < 30:
            fundamental_score += 5
        elif debt_ratio > 70:
            fundamental_score -= 15
        elif debt_ratio > 60:
            fundamental_score -= 10
        
        if cash_flow > 0:
            fundamental_score += 5
        else:
            fundamental_score -= 10
        
        fundamental_score = max(0, min(100, fundamental_score))
        
        print("📈 营收增长: {:.2f}%".format(revenue_growth))
        print("💰 净利润增长: {:.2f}%".format(profit_growth))
        print("📊 ROE: {:.2f}%".format(roe))
        print("💎 毛利率: {:.2f}%".format(gross_margin))
        print("⚖️ 资产负债率: {:.2f}%".format(debt_ratio))
        print("🎯 基本面得分: {}/100".format(fundamental_score))
        
        return {
            "score": fundamental_score,
            "revenue_growth": revenue_growth,
            "profit_growth": profit_growth,
            "roe": roe,
            "gross_margin": gross_margin,
            "debt_ratio": debt_ratio,
            "assessment": "优秀" if fundamental_score >= 80 else "良好" if fundamental_score >= 60 else "一般" if fundamental_score >= 40 else "较差"
        }
    
    def analyze_technicals(self, stock_data):
        """技术面分析"""
        print("\n📊 技术面分析")
        print("-" * 40)
        
        market = stock_data.get('market', {})
        
        # 技术面评分
        technical_score = 50  # 基础分
        
        # 价格表现
        price_change_30d = market.get('price_change_30d', 0)
        volatility = market.get('volatility_30d', 0)
        
        if abs(price_change_30d) > 30:
            # 短期暴涨暴跌都是风险信号
            technical_score -= 20
        elif price_change_30d > 15:
            technical_score += 10
        elif price_change_30d > 5:
            technical_score += 5
        
        # 波动率评分
        if volatility > 60:
            technical_score -= 15  # 极高波动是风险
        elif volatility > 40:
            technical_score -= 5
        elif volatility < 20:
            technical_score += 5
        
        # 成交量评分
        volume_ratio = market.get('volume_ratio_avg', 1)
        if volume_ratio > 10:
            technical_score -= 10  # 成交量过度放大
        elif volume_ratio > 3:
            technical_score += 5
        elif volume_ratio < 0.5:
            technical_score -= 5
        
        # 流动性评分
        turnover = market.get('avg_turnover_30d', 0)
        if turnover > 10:
            technical_score += 5
        elif turnover < 1:
            technical_score -= 10
        
        # 异常交易评分
        limit_up_days = market.get('limit_up_days_30d', 0)
        limit_down_days = market.get('limit_down_days_30d', 0)
        
        if limit_up_days >= 3 or limit_down_days >= 3:
            technical_score -= 15  # 频繁涨跌停是风险信号
        
        technical_score = max(0, min(100, technical_score))
        
        print("📈 30日涨跌幅: {:.2f}%".format(price_change_30d))
        print("📊 波动率: {:.2f}%".format(volatility))
        print("🔄 成交量比率: {:.2f}".format(volume_ratio))
        print("💧 平均换手率: {:.2f}%".format(turnover))
        print("🎯 技术面得分: {}/100".format(technical_score))
        
        return {
            "score": technical_score,
            "price_change_30d": price_change_30d,
            "volatility": volatility,
            "volume_ratio": volume_ratio,
            "turnover": turnover,
            "assessment": "强势" if technical_score >= 80 else "健康" if technical_score >= 60 else "一般" if technical_score >= 40 else "弱势"
        }
    
    def comprehensive_analysis(self, stock_code, stock_name):
        """综合分析"""
        print("=" * 80)
        print("🎯 {} ({}) 增强版全方位分析".format(stock_name, stock_code))
        print("=" * 80)
        print("📅 分析时间: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        print("🔍 分析版本: {} v{}".format(self.analyzer_name, self.version))
        print("⚡ 新增功能: 消息面分析 + 雷区扫描")
        
        # 1. 收集数据
        stock_data = self.collect_stock_data(stock_code, stock_name)
        
        # 2. 基本面分析
        fundamental_analysis = self.analyze_fundamentals(stock_data)
        
        # 3. 技术面分析
        technical_analysis = self.analyze_technicals(stock_data)
        
        # 4. 消息面分析
        if self.has_all_analysts:
            news_analysis = self.news_analyst.analyze_news_sentiment(stock_data.get('news', []))
        else:
            news_analysis = self._simple_news_analysis(stock_data.get('news', []))
        
        # 5. 雷区扫描
        if self.has_all_analysts:
            risk_analysis = self.risk_scanner.comprehensive_risk_scan(stock_data)
        else:
            risk_analysis = self._simple_risk_analysis(stock_data)
        
        # 6. 综合评分计算
        scores = {
            "基本面": fundamental_analysis['score'],
            "技术面": technical_analysis['score'],
            "消息面": news_analysis.get('sentiment_score', 50),
            "雷区风险": max(0, 100 - risk_analysis.get('综合评估', {}).get('总分', 0))  # 风险分数越高，投资分数越低
        }
        
        # 加权平均
        weighted_score = sum(
            scores[dimension] * self.analysis_weights[dimension]
            for dimension in scores
        )
        
        # 生成投资建议
        investment_advice = self._generate_investment_advice(weighted_score, scores, risk_analysis)
        
        # 输出综合结果
        print("\n" + "=" * 80)
        print("📊 综合分析结果")
        print("=" * 80)
        
        for dimension, score in scores.items():
            weight = self.analysis_weights[dimension]
            print("📈 {}: {:.1f}/100 (权重: {:.0f}%)".format(dimension, score, weight*100))
        
        print("\n🎯 综合评分: {:.1f}/100".format(weighted_score))
        print("💡 投资建议: {}".format(investment_advice['建议']))
        print("💰 建议仓位: {}".format(investment_advice['仓位']))
        print("⏰ 持有周期: {}".format(investment_advice['周期']))
        
        # 重点风险提示
        risk_level = risk_analysis.get('综合评估', {}).get('风险等级', '未知')
        if risk_level in ['高风险', '极高风险']:
            print("\n🚨 重大风险警告:")
            print("❌ 检测到{}，强烈建议回避投资！".format(risk_level))
        
        # 生成完整报告
        comprehensive_report = {
            "股票信息": stock_data['basic_info'],
            "分析结果": {
                "基本面分析": fundamental_analysis,
                "技术面分析": technical_analysis,
                "消息面分析": news_analysis,
                "雷区扫描": risk_analysis
            },
            "综合评估": {
                "各维度得分": scores,
                "综合得分": round(weighted_score, 1),
                "投资建议": investment_advice
            },
            "分析配置": {
                "分析器": self.analyzer_name,
                "版本": self.version,
                "权重配置": self.analysis_weights
            },
            "分析时间": datetime.now().isoformat()
        }
        
        return comprehensive_report
    
    def _simple_news_analysis(self, news_list):
        """简化版新闻分析"""
        if not news_list:
            return {"sentiment_score": 50, "risk_level": "未知"}
        
        sentiment_score = 50
        risk_events = []
        
        for news in news_list:
            title = news.get('title', '')
            content = news.get('content', '')
            text = title + " " + content
            
            # 简单的情绪判断
            if any(word in text for word in ['减持', '违规', '处罚', '风险', '下滑']):
                sentiment_score -= 15
                risk_events.append(title)
            elif any(word in text for word in ['增长', '合作', '中标', '利好']):
                sentiment_score += 10
        
        return {
            "sentiment_score": max(0, min(100, sentiment_score)),
            "risk_level": "高风险" if len(risk_events) > 0 else "低风险",
            "risk_events": risk_events
        }
    
    def _simple_risk_analysis(self, stock_data):
        """简化版风险分析"""
        total_score = 0
        risks = []
        
        # 检查基本风险
        financial = stock_data.get('financial', {}).get('latest', {})
        market = stock_data.get('market', {})
        news = stock_data.get('news', [])
        
        # 财务风险
        if financial.get('debt_ratio', 0) > 70:
            total_score += 15
            risks.append("高负债风险")
        
        # 市场风险
        if market.get('volatility_30d', 0) > 60:
            total_score += 10
            risks.append("高波动风险")
        
        # 消息风险
        for news_item in news:
            if '减持' in news_item.get('title', ''):
                total_score += 20
                risks.append("实控人减持风险")
                break
        
        risk_level = "极高风险" if total_score >= 30 else "高风险" if total_score >= 15 else "中风险" if total_score >= 5 else "低风险"
        
        return {
            "综合评估": {
                "总分": total_score,
                "风险等级": risk_level,
                "主要风险": risks
            }
        }
    
    def _generate_investment_advice(self, weighted_score, scores, risk_analysis):
        """生成投资建议"""
        # 获取风险等级
        risk_level = risk_analysis.get('综合评估', {}).get('风险等级', '未知')
        
        # 如果存在极高或高风险，直接回避
        if risk_level in ['极高风险', '高风险']:
            return {
                "建议": "紧急回避",
                "仓位": "0%",
                "周期": "避免投资",
                "主要原因": "存在重大雷区风险",
                "风险提示": "检测到{}，投资风险极大".format(risk_level)
            }
        
        # 根据综合评分确定建议
        if weighted_score >= 85:
            advice = "强烈买入"
            position = "5-8%"
            period = "长期持有(12-24个月)"
        elif weighted_score >= 70:
            advice = "买入"
            position = "3-5%"
            period = "中长期持有(6-12个月)"
        elif weighted_score >= 55:
            advice = "谨慎买入"
            position = "2-3%"
            period = "中期关注(3-6个月)"
        elif weighted_score >= 40:
            advice = "观望"
            position = "0-1%"
            period = "等待机会"
        else:
            advice = "回避"
            position = "0%"
            period = "避免投资"
        
        # 特殊调整：如果消息面得分很低，降级处理
        if scores.get('消息面', 50) <= 30:
            if advice in ['强烈买入', '买入']:
                advice = "谨慎买入"
                position = "1-2%"
            elif advice == '谨慎买入':
                advice = "观望"
                position = "0-1%"
        
        return {
            "建议": advice,
            "仓位": position,
            "周期": period,
            "综合评分": weighted_score,
            "主要原因": "基于四维度综合分析结果"
        }

def main():
    """主函数"""
    print("🚀 启动增强版个股分析器")
    print("🔍 集成消息面分析和雷区扫描功能")
    
    analyzer = EnhancedStockAnalyzer()
    
    # 分析华康洁净
    report = analyzer.comprehensive_analysis("301235.SZ", "华康洁净")
    
    # 保存报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = "增强版股票分析报告_{}.json".format(timestamp)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n💾 增强版分析报告已保存: {}".format(filename))
    print("\n🎉 增强版分析完成！")
    print("✅ 新增功能：消息面情绪分析 + 雷区风险扫描")
    print("⚡ 提升效果：全方位风险识别，避免投资踩雷")

if __name__ == "__main__":
    main()