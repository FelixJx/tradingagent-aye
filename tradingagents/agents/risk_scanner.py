#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雷区扫描器 - Thunderbolt Risk Scanner
专门识别个股的重大风险点，防范投资雷区
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any

class ThunderboltRiskScanner:
    """雷区扫描器"""
    
    def __init__(self):
        self.scanner_name = "雷区扫描器"
        
        # 定义各类雷区风险权重和关键词
        self.risk_categories = {
            "实控人风险": {
                "weight": 10,  # 最高权重
                "keywords": [
                    "实控人减持", "控股股东减持", "大股东减持", "董事长减持",
                    "实控人质押", "控股股东质押", "实控人变更", "控股权转让",
                    "实控人违规", "控股股东违规", "实控人被调查", "实控人失联"
                ]
            },
            "财务雷区": {
                "weight": 9,
                "keywords": [
                    "财务造假", "虚增收入", "虚构利润", "财务舞弊",
                    "审计意见", "无法表示意见", "否定意见", "保留意见",
                    "会计师事务所", "更换审计机构", "审计费用异常",
                    "关联交易", "资金占用", "违规担保"
                ]
            },
            "债务风险": {
                "weight": 8,
                "keywords": [
                    "债务违约", "逾期债务", "资金链断裂", "流动性危机",
                    "银行抽贷", "担保纠纷", "债权人", "破产重整",
                    "资产冻结", "账户冻结", "诉讼保全"
                ]
            },
            "合规风险": {
                "weight": 8,
                "keywords": [
                    "证监会处罚", "立案调查", "行政处罚", "刑事调查",
                    "内幕交易", "市场操纵", "信息披露违规", "虚假陈述",
                    "退市风险", "ST", "*ST", "暂停上市"
                ]
            },
            "经营风险": {
                "weight": 6,
                "keywords": [
                    "主营业务下滑", "核心客户流失", "重要合同终止",
                    "生产停滞", "工厂关闭", "产能过剩", "行业衰退",
                    "技术落后", "产品滞销", "库存积压"
                ]
            },
            "人事风险": {
                "weight": 5,
                "keywords": [
                    "董事长辞职", "总经理离职", "财务总监离职", "核心高管离职",
                    "董事会改组", "管理层变动", "创始人退出", "核心技术人员离职"
                ]
            },
            "外部风险": {
                "weight": 4,
                "keywords": [
                    "政策打压", "行业整顿", "环保处罚", "安全事故",
                    "产品召回", "质量问题", "诉讼败诉", "专利纠纷",
                    "商誉减值", "资产减值", "投资损失"
                ]
            }
        }
        
        # 雷区严重程度阈值
        self.risk_thresholds = {
            "安全": (0, 10),
            "低风险": (11, 25),
            "中风险": (26, 50),
            "高风险": (51, 80),
            "极高风险": (81, 100)
        }
    
    def scan_financial_risks(self, financial_data: Dict) -> Dict:
        """扫描财务雷区"""
        print("💰 财务雷区扫描")
        print("-" * 40)
        
        risks = []
        risk_score = 0
        
        if not financial_data:
            return {"risks": [], "score": 0, "level": "数据不足"}
        
        # 检查关键财务指标
        latest_data = financial_data.get('latest', {})
        
        # 1. 资产负债率过高
        debt_ratio = latest_data.get('debt_ratio', 0)
        if debt_ratio > 80:
            risks.append({
                "类型": "高负债风险",
                "描述": "资产负债率{:.2f}%，严重超标".format(debt_ratio),
                "严重程度": "高",
                "分数": 15
            })
            risk_score += 15
        elif debt_ratio > 60:
            risks.append({
                "类型": "负债风险",
                "描述": "资产负债率{:.2f}%，偏高".format(debt_ratio),
                "严重程度": "中",
                "分数": 8
            })
            risk_score += 8
        
        # 2. 现金流为负
        cash_flow = latest_data.get('operating_cash_flow', 0)
        if cash_flow < 0:
            risks.append({
                "类型": "现金流风险",
                "描述": "经营现金流为负，存在资金压力",
                "严重程度": "高",
                "分数": 12
            })
            risk_score += 12
        
        # 3. 应收账款占比过高
        receivables_ratio = latest_data.get('receivables_to_revenue', 0)
        if receivables_ratio > 50:
            risks.append({
                "类型": "应收账款风险",
                "描述": "应收账款占营收{:.1f}%，回款风险大".format(receivables_ratio),
                "严重程度": "中",
                "分数": 10
            })
            risk_score += 10
        
        # 4. 毛利率持续下滑
        gross_margins = financial_data.get('gross_margin_trend', [])
        if len(gross_margins) >= 3:
            if all(gross_margins[i] > gross_margins[i+1] for i in range(len(gross_margins)-1)):
                risks.append({
                    "类型": "盈利能力下滑",
                    "描述": "毛利率连续下滑，竞争力下降",
                    "严重程度": "中",
                    "分数": 8
                })
                risk_score += 8
        
        risk_level = self._determine_risk_level(risk_score)
        
        print("📊 发现财务风险: {}个".format(len(risks)))
        print("🎯 财务风险评分: {}/100".format(risk_score))
        print("⚠️ 风险等级: {}".format(risk_level))
        
        for risk in risks:
            print("  - {}: {} ({}分)".format(
                risk["类型"], risk["描述"], risk["分数"]
            ))
        
        return {
            "risks": risks,
            "score": risk_score,
            "level": risk_level
        }
    
    def scan_governance_risks(self, governance_data: Dict) -> Dict:
        """扫描公司治理雷区"""
        print("\n🏛️ 公司治理雷区扫描")
        print("-" * 40)
        
        risks = []
        risk_score = 0
        
        if not governance_data:
            return {"risks": [], "score": 0, "level": "数据不足"}
        
        # 1. 股权集中度过高
        top_shareholder_ratio = governance_data.get('top_shareholder_ratio', 0)
        if top_shareholder_ratio > 70:
            risks.append({
                "类型": "股权过度集中",
                "描述": "第一大股东持股{:.1f}%，治理风险高".format(top_shareholder_ratio),
                "严重程度": "中",
                "分数": 8
            })
            risk_score += 8
        
        # 2. 独立董事比例不足
        independent_director_ratio = governance_data.get('independent_director_ratio', 0)
        if independent_director_ratio < 30:
            risks.append({
                "类型": "独董比例不足",
                "描述": "独立董事比例{:.1f}%，低于监管要求".format(independent_director_ratio),
                "严重程度": "低",
                "分数": 3
            })
            risk_score += 3
        
        # 3. 关联交易过多
        related_transaction_ratio = governance_data.get('related_transaction_ratio', 0)
        if related_transaction_ratio > 30:
            risks.append({
                "类型": "关联交易风险",
                "描述": "关联交易占比{:.1f}%，存在利益输送风险".format(related_transaction_ratio),
                "严重程度": "高",
                "分数": 12
            })
            risk_score += 12
        
        # 4. 高管频繁变动
        executive_changes = governance_data.get('executive_changes_12m', 0)
        if executive_changes >= 3:
            risks.append({
                "类型": "高管变动频繁",
                "描述": "12个月内高管变动{}次，管理不稳定".format(executive_changes),
                "严重程度": "中",
                "分数": 6
            })
            risk_score += 6
        
        risk_level = self._determine_risk_level(risk_score)
        
        print("📊 发现治理风险: {}个".format(len(risks)))
        print("🎯 治理风险评分: {}/100".format(risk_score))
        print("⚠️ 风险等级: {}".format(risk_level))
        
        return {
            "risks": risks,
            "score": risk_score,
            "level": risk_level
        }
    
    def scan_market_risks(self, market_data: Dict) -> Dict:
        """扫描市场交易雷区"""
        print("\n📊 市场交易雷区扫描")
        print("-" * 40)
        
        risks = []
        risk_score = 0
        
        if not market_data:
            return {"risks": [], "score": 0, "level": "数据不足"}
        
        # 1. 股价暴涨暴跌
        price_volatility = market_data.get('volatility_30d', 0)
        if price_volatility > 80:
            risks.append({
                "类型": "极高波动",
                "描述": "30日波动率{:.1f}%，存在操纵嫌疑".format(price_volatility),
                "严重程度": "高",
                "分数": 15
            })
            risk_score += 15
        elif price_volatility > 50:
            risks.append({
                "类型": "高波动",
                "描述": "30日波动率{:.1f}%，投机性强".format(price_volatility),
                "严重程度": "中",
                "分数": 8
            })
            risk_score += 8
        
        # 2. 成交量异常
        volume_ratio = market_data.get('volume_ratio_avg', 1)
        if volume_ratio > 5:
            risks.append({
                "类型": "成交量异常",
                "描述": "成交量是均值的{:.1f}倍，存在异常交易".format(volume_ratio),
                "严重程度": "中",
                "分数": 6
            })
            risk_score += 6
        
        # 3. 流动性风险
        avg_turnover = market_data.get('avg_turnover_30d', 0)
        if avg_turnover < 0.5:
            risks.append({
                "类型": "流动性不足",
                "描述": "30日平均换手率{:.2f}%，流动性差".format(avg_turnover),
                "严重程度": "中",
                "分数": 5
            })
            risk_score += 5
        
        # 4. 跌停次数过多
        limit_down_days = market_data.get('limit_down_days_30d', 0)
        if limit_down_days >= 5:
            risks.append({
                "类型": "频繁跌停",
                "描述": "30日内跌停{}次，市场信心缺失".format(limit_down_days),
                "严重程度": "高",
                "分数": 12
            })
            risk_score += 12
        elif limit_down_days >= 3:
            risks.append({
                "类型": "多次跌停",
                "描述": "30日内跌停{}次，需要关注".format(limit_down_days),
                "严重程度": "中",
                "分数": 6
            })
            risk_score += 6
        
        risk_level = self._determine_risk_level(risk_score)
        
        print("📊 发现市场风险: {}个".format(len(risks)))
        print("🎯 市场风险评分: {}/100".format(risk_score))
        print("⚠️ 风险等级: {}".format(risk_level))
        
        return {
            "risks": risks,
            "score": risk_score,
            "level": risk_level
        }
    
    def scan_news_risks(self, news_data: List[Dict]) -> Dict:
        """扫描新闻消息雷区"""
        print("\n📰 新闻消息雷区扫描")
        print("-" * 40)
        
        risks = []
        risk_score = 0
        
        if not news_data:
            return {"risks": [], "score": 0, "level": "数据不足"}
        
        # 分析每条新闻
        for news in news_data:
            title = news.get('title', '')
            content = news.get('content', '')
            text = (title + " " + content).lower()
            
            # 按风险类别扫描
            for risk_category, risk_info in self.risk_categories.items():
                weight = risk_info['weight']
                keywords = risk_info['keywords']
                
                for keyword in keywords:
                    if keyword in text:
                        severity_score = weight
                        
                        # 根据关键词调整严重程度
                        if any(severe_word in keyword for severe_word in ['实控人', '造假', '违约', '处罚']):
                            severity_score = min(weight + 5, 15)
                        
                        risks.append({
                            "类型": risk_category,
                            "描述": "发现关键词: {}".format(keyword),
                            "新闻标题": title,
                            "日期": news.get('published_date', ''),
                            "严重程度": self._get_severity_level(severity_score),
                            "分数": severity_score
                        })
                        
                        risk_score += severity_score
                        break  # 避免重复计分
        
        # 去重和合并同类风险
        unique_risks = self._merge_similar_risks(risks)
        total_score = sum(risk['分数'] for risk in unique_risks)
        
        risk_level = self._determine_risk_level(total_score)
        
        print("📊 发现新闻风险: {}个".format(len(unique_risks)))
        print("🎯 新闻风险评分: {}/100".format(total_score))
        print("⚠️ 风险等级: {}".format(risk_level))
        
        for risk in unique_risks[:5]:  # 只显示前5个最重要的风险
            print("  - {}: {} ({}分)".format(
                risk["类型"], risk["描述"], risk["分数"]
            ))
        
        return {
            "risks": unique_risks,
            "score": total_score,
            "level": risk_level
        }
    
    def comprehensive_risk_scan(self, stock_data: Dict) -> Dict:
        """综合雷区扫描"""
        print("=" * 60)
        print("⚡ {} ({}) 综合雷区扫描".format(
            stock_data.get('name', ''), stock_data.get('code', '')
        ))
        print("=" * 60)
        
        # 分别扫描各个维度
        financial_risks = self.scan_financial_risks(stock_data.get('financial', {}))
        governance_risks = self.scan_governance_risks(stock_data.get('governance', {}))
        market_risks = self.scan_market_risks(stock_data.get('market', {}))
        news_risks = self.scan_news_risks(stock_data.get('news', []))
        
        # 计算综合风险评分
        total_score = (
            financial_risks['score'] +
            governance_risks['score'] +
            market_risks['score'] +
            news_risks['score']
        )
        
        overall_risk_level = self._determine_risk_level(total_score)
        
        # 生成投资建议
        investment_advice = self._generate_risk_based_advice(
            total_score, overall_risk_level, [
                financial_risks, governance_risks, market_risks, news_risks
            ]
        )
        
        print("\n" + "=" * 60)
        print("📊 综合雷区扫描结果")
        print("=" * 60)
        print("🎯 综合风险评分: {}/400".format(total_score))
        print("⚠️ 综合风险等级: {}".format(overall_risk_level))
        print("💡 投资建议: {}".format(investment_advice['建议']))
        
        comprehensive_report = {
            "股票信息": {
                "代码": stock_data.get('code', ''),
                "名称": stock_data.get('name', '')
            },
            "风险扫描结果": {
                "财务风险": financial_risks,
                "治理风险": governance_risks,
                "市场风险": market_risks,
                "新闻风险": news_risks
            },
            "综合评估": {
                "总分": total_score,
                "风险等级": overall_risk_level,
                "投资建议": investment_advice
            },
            "扫描时间": datetime.now().isoformat(),
            "扫描器": self.scanner_name
        }
        
        return comprehensive_report
    
    def _determine_risk_level(self, score: float) -> str:
        """根据分数确定风险等级"""
        for level, (min_score, max_score) in self.risk_thresholds.items():
            if min_score <= score <= max_score:
                return level
        return "极高风险"
    
    def _get_severity_level(self, score: float) -> str:
        """获取严重程度等级"""
        if score >= 12:
            return "极高"
        elif score >= 8:
            return "高"
        elif score >= 5:
            return "中"
        else:
            return "低"
    
    def _merge_similar_risks(self, risks: List[Dict]) -> List[Dict]:
        """合并相似风险"""
        risk_groups = {}
        
        for risk in risks:
            risk_type = risk['类型']
            if risk_type not in risk_groups:
                risk_groups[risk_type] = []
            risk_groups[risk_type].append(risk)
        
        merged_risks = []
        for risk_type, group_risks in risk_groups.items():
            if len(group_risks) == 1:
                merged_risks.append(group_risks[0])
            else:
                # 合并同类风险
                total_score = sum(risk['分数'] for risk in group_risks)
                merged_risk = {
                    "类型": risk_type,
                    "描述": "发现{}个相关风险点".format(len(group_risks)),
                    "严重程度": self._get_severity_level(total_score),
                    "分数": min(total_score, 20),  # 限制最高分数
                    "详细风险": [risk['描述'] for risk in group_risks]
                }
                merged_risks.append(merged_risk)
        
        # 按分数排序
        return sorted(merged_risks, key=lambda x: x['分数'], reverse=True)
    
    def _generate_risk_based_advice(self, total_score: float, risk_level: str, 
                                   risk_analyses: List[Dict]) -> Dict:
        """基于风险扫描生成投资建议"""
        if risk_level == "极高风险" or total_score >= 80:
            advice = "立即回避"
            position = "0%"
            reason = "存在重大雷区风险，投资极度危险"
        elif risk_level == "高风险" or total_score >= 50:
            advice = "紧急回避"
            position = "0%"
            reason = "多项高风险指标，不适合投资"
        elif risk_level == "中风险" or total_score >= 25:
            advice = "谨慎观望"
            position = "0-1%"
            reason = "存在一定风险，建议等待改善"
        elif risk_level == "低风险":
            advice = "审慎关注"
            position = "1-3%"
            reason = "风险相对可控，可小仓位关注"
        else:
            advice = "正常关注"
            position = "2-5%"
            reason = "未发现重大风险"
        
        return {
            "建议": advice,
            "仓位": position,
            "原因": reason,
            "风险评分": total_score,
            "风险等级": risk_level
        }

def main():
    """测试雷区扫描器"""
    print("🚀 启动雷区扫描器测试")
    
    scanner = ThunderboltRiskScanner()
    
    # 模拟华康洁净数据
    test_data = {
        "code": "301235.SZ",
        "name": "华康洁净",
        "financial": {
            "latest": {
                "debt_ratio": 53.22,
                "operating_cash_flow": 19800000,
                "receivables_to_revenue": 35.5
            }
        },
        "governance": {
            "top_shareholder_ratio": 44.23,
            "independent_director_ratio": 33.3,
            "related_transaction_ratio": 15.2,
            "executive_changes_12m": 1
        },
        "market": {
            "volatility_30d": 65.8,
            "volume_ratio_avg": 8.5,
            "avg_turnover_30d": 18.2,
            "limit_down_days_30d": 0
        },
        "news": [
            {
                "title": "华康洁净：实控人减持华医转债996,710张",
                "content": "华康洁净实际控制人谭平涛减持可转债，占发行总量13.29%",
                "published_date": "2025-07-31"
            }
        ]
    }
    
    # 执行综合扫描
    report = scanner.comprehensive_risk_scan(test_data)
    
    # 保存报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = "雷区扫描报告_{}.json".format(timestamp)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n💾 雷区扫描报告已保存: {}".format(filename))

if __name__ == "__main__":
    main()