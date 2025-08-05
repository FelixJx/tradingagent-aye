#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息面分析师 - News Sentiment Analyst
专门负责消息面和市场情绪分析，识别重大利空利好
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class NewsSentimentAnalyst:
    """消息面分析师"""
    
    def __init__(self):
        self.analyst_name = "消息面分析师"
        self.tavily_api_key = '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'
        
        # 雷区关键词库
        self.thunderbolt_keywords = {
            "高危": [
                "实控人减持", "控股股东减持", "大股东减持", "董事长减持",
                "违法违规", "证监会处罚", "立案调查", "财务造假",
                "债务违约", "资金链断裂", "经营困难", "停产停业",
                "退市风险", "ST", "*ST", "暂停上市"
            ],
            "中危": [
                "业绩预亏", "业绩下滑", "营收下降", "利润下滑",
                "高管离职", "核心人员离职", "董事变更", "监事变更",
                "诉讼纠纷", "仲裁", "担保纠纷", "合同纠纷",
                "产品召回", "安全事故", "环保处罚", "质量问题"
            ],
            "低危": [
                "股权质押", "股权转让", "增发", "配股",
                "业绩预告", "业绩修正", "会计政策变更", "会计估计变更",
                "关联交易", "对外投资", "资产重组", "并购重组"
            ]
        }
        
        # 利好关键词库
        self.positive_keywords = {
            "重大利好": [
                "重大合同", "战略合作", "技术突破", "专利获得",
                "政策支持", "补贴获得", "税收优惠", "资质获得",
                "中标", "订单增长", "产能扩张", "新产品发布"
            ],
            "一般利好": [
                "业绩增长", "营收增长", "利润增长", "分红",
                "股份回购", "员工持股", "股权激励", "增持"
            ]
        }
    
    def search_stock_news(self, stock_code: str, stock_name: str, days: int = 30) -> List[Dict]:
        """搜索股票相关新闻"""
        print("🔍 搜索 {}({}) 近{}日新闻...".format(stock_name, stock_code, days))
        
        try:
            # 构建搜索查询
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = "{} {} 公告 减持 业绩 利空 利好 风险".format(stock_name, stock_code)
            
            # 使用WebSearch API
            search_data = {
                'query': query,
                'max_results': 20,
                'include_domains': [
                    'cninfo.com.cn', 'sse.com.cn', 'szse.cn',
                    'eastmoney.com', 'sina.com.cn', 'stcn.com',
                    'cs.com.cn', 'cnstock.com', 'stockstar.com'
                ]
            }
            
            # 这里应该调用实际的搜索API，暂时返回模拟数据
            mock_news = [
                {
                    "title": "华康洁净：实控人减持华医转债996,710张",
                    "content": "华康洁净实际控制人谭平涛于2025年7月30日至31日期间，减持华医转债996,710张，占发行总量的13.29%。此次减持引发市场关注。",
                    "published_date": "2025-07-31",
                    "source": "证券时报",
                    "url": "https://example.com/news1",
                    "sentiment": "负面"
                },
                {
                    "title": "华康洁净发布异常波动公告",
                    "content": "华康洁净股价连续3个交易日累计涨幅超过30%，公司发布异常波动公告，提示投资风险。",
                    "published_date": "2025-07-31",
                    "source": "上交所",
                    "url": "https://example.com/news2",
                    "sentiment": "中性"
                }
            ]
            
            return mock_news
            
        except Exception as e:
            print("❌ 新闻搜索失败: {}".format(str(e)))
            return []
    
    def analyze_news_sentiment(self, news_list: List[Dict]) -> Dict:
        """分析新闻情绪"""
        if not news_list:
            return {"sentiment_score": 50, "risk_level": "中性", "key_events": []}
        
        print("\n📰 新闻情绪分析")
        print("-" * 40)
        
        sentiment_scores = []
        risk_events = []
        positive_events = []
        
        for news in news_list:
            title = news.get('title', '')
            content = news.get('content', '')
            text = title + " " + content
            
            # 计算情绪分数
            score = self._calculate_sentiment_score(text)
            sentiment_scores.append(score)
            
            # 识别风险事件
            risk_level = self._identify_risk_level(text)
            if risk_level != "无风险":
                risk_events.append({
                    "title": title,
                    "risk_level": risk_level,
                    "date": news.get('published_date', '')
                })
            
            # 识别利好事件
            positive_level = self._identify_positive_level(text)
            if positive_level != "无利好":
                positive_events.append({
                    "title": title,
                    "positive_level": positive_level,
                    "date": news.get('published_date', '')
                })
        
        # 计算综合情绪分数
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 50
        
        # 确定整体风险等级
        overall_risk = self._determine_overall_risk(risk_events)
        
        print("📊 新闻总数: {}".format(len(news_list)))
        print("📈 情绪得分: {:.1f}/100".format(avg_sentiment))
        print("⚠️ 风险等级: {}".format(overall_risk))
        print("🚨 风险事件: {}个".format(len(risk_events)))
        print("✅ 利好事件: {}个".format(len(positive_events)))
        
        return {
            "sentiment_score": round(avg_sentiment, 1),
            "risk_level": overall_risk,
            "risk_events": risk_events,
            "positive_events": positive_events,
            "news_count": len(news_list),
            "analysis_date": datetime.now().isoformat()
        }
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """计算单条新闻的情绪分数"""
        score = 50  # 中性分数
        
        # 检查负面关键词
        for risk_level, keywords in self.thunderbolt_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    if risk_level == "高危":
                        score -= 30
                    elif risk_level == "中危":
                        score -= 15
                    elif risk_level == "低危":
                        score -= 5
        
        # 检查正面关键词
        for positive_level, keywords in self.positive_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    if positive_level == "重大利好":
                        score += 20
                    elif positive_level == "一般利好":
                        score += 10
        
        return max(0, min(100, score))
    
    def _identify_risk_level(self, text: str) -> str:
        """识别风险等级"""
        for risk_level, keywords in self.thunderbolt_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return risk_level
        return "无风险"
    
    def _identify_positive_level(self, text: str) -> str:
        """识别利好等级"""
        for positive_level, keywords in self.positive_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return positive_level
        return "无利好"
    
    def _determine_overall_risk(self, risk_events: List[Dict]) -> str:
        """确定整体风险等级"""
        if not risk_events:
            return "低风险"
        
        high_risk_count = sum(1 for event in risk_events if event['risk_level'] == '高危')
        medium_risk_count = sum(1 for event in risk_events if event['risk_level'] == '中危')
        
        if high_risk_count > 0:
            return "高风险"
        elif medium_risk_count >= 2:
            return "中高风险"
        elif medium_risk_count >= 1:
            return "中风险"
        else:
            return "低风险"
    
    def identify_thunderbolt_risks(self, stock_code: str, stock_name: str) -> Dict:
        """识别重大雷区风险"""
        print("\n⚡ 雷区风险识别")
        print("=" * 50)
        
        # 搜索最近60天的新闻
        news_list = self.search_stock_news(stock_code, stock_name, days=60)
        
        # 重点关注的雷区类型
        thunderbolt_risks = {
            "实控人风险": [],
            "财务风险": [],
            "经营风险": [],
            "合规风险": [],
            "其他风险": []
        }
        
        # 分析每条新闻
        for news in news_list:
            title = news.get('title', '')
            content = news.get('content', '')
            text = title + " " + content
            
            # 实控人风险
            controller_risks = ["实控人减持", "控股股东减持", "大股东减持", "董事长减持"]
            if any(risk in text for risk in controller_risks):
                thunderbolt_risks["实控人风险"].append({
                    "事件": title,
                    "日期": news.get('published_date', ''),
                    "严重程度": "极高"
                })
            
            # 财务风险
            financial_risks = ["财务造假", "业绩预亏", "债务违约", "资金链断裂"]
            if any(risk in text for risk in financial_risks):
                thunderbolt_risks["财务风险"].append({
                    "事件": title,
                    "日期": news.get('published_date', ''),
                    "严重程度": "高"
                })
            
            # 合规风险
            compliance_risks = ["证监会处罚", "立案调查", "违法违规"]
            if any(risk in text for risk in compliance_risks):
                thunderbolt_risks["合规风险"].append({
                    "事件": title,
                    "日期": news.get('published_date', ''),
                    "严重程度": "极高"
                })
        
        # 输出风险分析结果
        total_risks = sum(len(risks) for risks in thunderbolt_risks.values())
        
        print("🔍 雷区扫描结果:")
        print("-" * 30)
        
        for risk_type, risks in thunderbolt_risks.items():
            if risks:
                print("⚠️ {}: {}个风险点".format(risk_type, len(risks)))
                for risk in risks:
                    print("   - {} ({})".format(risk["事件"], risk["严重程度"]))
            else:
                print("✅ {}: 无风险".format(risk_type))
        
        print("\n📊 雷区风险总评:")
        print("-" * 30)
        
        if total_risks == 0:
            risk_rating = "安全"
            risk_color = "🟢"
        elif total_risks <= 2:
            risk_rating = "低风险"
            risk_color = "🟡"
        elif total_risks <= 5:
            risk_rating = "中风险"
            risk_color = "🟠"
        else:
            risk_rating = "高风险"
            risk_color = "🔴"
        
        print("{} 雷区风险等级: {}".format(risk_color, risk_rating))
        print("📊 发现风险点: {}个".format(total_risks))
        
        return {
            "risk_rating": risk_rating,
            "total_risks": total_risks,
            "detailed_risks": thunderbolt_risks,
            "scan_date": datetime.now().isoformat()
        }
    
    def generate_news_analysis_report(self, stock_code: str, stock_name: str) -> Dict:
        """生成消息面分析报告"""
        print("=" * 60)
        print("📰 {} ({}) 消息面分析报告".format(stock_name, stock_code))
        print("=" * 60)
        
        # 搜索新闻
        news_list = self.search_stock_news(stock_code, stock_name)
        
        # 情绪分析
        sentiment_analysis = self.analyze_news_sentiment(news_list)
        
        # 雷区识别
        thunderbolt_analysis = self.identify_thunderbolt_risks(stock_code, stock_name)
        
        # 生成投资建议
        investment_advice = self._generate_news_based_advice(
            sentiment_analysis, thunderbolt_analysis
        )
        
        comprehensive_report = {
            "股票信息": {
                "代码": stock_code,
                "名称": stock_name
            },
            "新闻分析": sentiment_analysis,
            "雷区识别": thunderbolt_analysis,
            "消息面建议": investment_advice,
            "分析师": self.analyst_name,
            "分析时间": datetime.now().isoformat()
        }
        
        return comprehensive_report
    
    def _generate_news_based_advice(self, sentiment_analysis: Dict, thunderbolt_analysis: Dict) -> Dict:
        """基于消息面生成投资建议"""
        sentiment_score = sentiment_analysis.get('sentiment_score', 50)
        risk_rating = thunderbolt_analysis.get('risk_rating', '安全')
        total_risks = thunderbolt_analysis.get('total_risks', 0)
        
        print("\n💡 消息面投资建议")
        print("-" * 40)
        
        # 基于雷区风险调整建议
        if risk_rating == "高风险" or total_risks >= 5:
            advice_rating = "紧急回避"
            position = "0%"
            reason = "存在重大雷区风险，建议立即回避"
        elif risk_rating == "中风险":
            advice_rating = "谨慎观望"
            position = "0-1%"
            reason = "存在一定风险，建议观望等待"
        elif sentiment_score <= 30:
            advice_rating = "暂时回避"
            position = "0-2%"
            reason = "消息面偏负面，建议等待改善"
        elif sentiment_score >= 70:
            advice_rating = "积极关注"
            position = "3-5%"
            reason = "消息面偏正面，可适度关注"
        else:
            advice_rating = "中性观望"
            position = "1-3%"
            reason = "消息面中性，保持观望"
        
        print("🎯 消息面评级: {}".format(advice_rating))
        print("💰 建议仓位: {}".format(position))
        print("📝 主要原因: {}".format(reason))
        
        return {
            "评级": advice_rating,
            "建议仓位": position,
            "主要原因": reason,
            "情绪得分": sentiment_score,
            "风险等级": risk_rating
        }

def main():
    """测试消息面分析师"""
    print("🚀 启动消息面分析师测试")
    
    analyst = NewsSentimentAnalyst()
    
    # 测试华康洁净
    report = analyst.generate_news_analysis_report("301235.SZ", "华康洁净")
    
    # 保存报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = "消息面分析报告_{}.json".format(timestamp)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n💾 消息面分析报告已保存: {}".format(filename))

if __name__ == "__main__":
    main()