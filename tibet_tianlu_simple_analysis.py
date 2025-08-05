#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
西藏天路(600326)多智能体深度分析 (简化版)
"""

import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

class TibetTianluAnalyzer:
    def __init__(self):
        self.stock_code = '600326'
        self.stock_name = '西藏天路'
        
    def get_stock_data(self):
        """获取股票数据"""
        print(f"📊 获取{self.stock_name}({self.stock_code})数据...")
        
        try:
            # 获取最近60天数据
            hist_data = ak.stock_zh_a_hist(symbol=self.stock_code, period="daily", 
                                         start_date="20250601", end_date="20250730", adjust="")
            
            if hist_data.empty:
                print("❌ 未获取到数据")
                return None
            
            print(f"✅ 成功获取 {len(hist_data)} 条数据")
            print(f"数据列名: {list(hist_data.columns)}")
            
            return hist_data
            
        except Exception as e:
            print(f"❌ 数据获取失败: {e}")
            return None

    def fundamental_analyst_view(self, data):
        """基本面分析师观点"""
        print(f"\n📊 基本面分析师视角 - {self.stock_name}")
        print("-" * 50)
        
        if data is None or data.empty:
            return {"评分": 40, "观点": "数据不足"}
        
        latest = data.iloc[-1]
        current_price = latest['收盘']
        change_pct = latest['涨跌幅']
        
        # 基本面分析
        analysis = {
            "当前价格": f"{current_price:.2f}元",
            "涨跌幅": f"{change_pct:.2f}%",
            "财务状况": {
                "2025Q1营收": "3.386亿元(+10.76%)",
                "2025Q1净利": "-1.24亿元(-68.73%)",
                "上半年预告": "亏损7700万-1.15亿元",
                "主要问题": "盈利能力下降，现金流紧张"
            },
            "竞争优势": {
                "地位": "西藏建筑行业龙头",
                "经验": "承建170+重点工程项目",
                "资质": "国家级高新技术企业",
                "品牌": "天路品牌西藏著名商标"
            },
            "主要挑战": {
                "盈利": "短期面临亏损压力",
                "竞争": "市场竞争加剧",
                "回款": "应收账款回收周期长",
                "成本": "原材料和人工成本上升"
            }
        }
        
        # 评分逻辑
        score = 50  # 基础分
        score -= 15  # 亏损扣分
        score += 10  # 行业龙头加分
        score += 5   # 政策受益加分
        
        if change_pct > 5:
            score += 5
        elif change_pct < -5:
            score -= 5
        
        score = max(0, min(100, score))
        
        print(f"✅ 基本面评分: {score}/100")
        print(f"✅ 当前价格: {current_price:.2f}元 ({change_pct:+.2f}%)")
        print(f"✅ 核心优势: 西藏建筑龙头企业")
        print(f"⚠️ 主要风险: 短期盈利压力")
        
        return {
            "评分": score,
            "观点": "西藏建筑龙头，政策受益，但短期盈利承压",
            "详情": analysis
        }

    def technical_analyst_view(self, data):
        """技术分析师观点"""
        print(f"\n📈 技术分析师视角 - {self.stock_name}")
        print("-" * 50)
        
        if data is None or data.empty:
            return {"评分": 40, "观点": "数据不足"}
        
        df = data.copy()
        
        # 计算均线
        df['MA5'] = df['收盘'].rolling(5).mean()
        df['MA10'] = df['收盘'].rolling(10).mean()
        df['MA20'] = df['收盘'].rolling(20).mean()
        
        latest = df.iloc[-1]
        current_price = latest['收盘']
        ma5 = latest['MA5']
        ma10 = latest['MA10']
        ma20 = latest['MA20']
        
        # 趋势判断
        if pd.notna(ma5) and pd.notna(ma10) and pd.notna(ma20):
            if current_price > ma5 > ma10 > ma20:
                trend = "强势上涨"
                trend_score = 85
            elif current_price > ma5 > ma10:
                trend = "短期上涨"
                trend_score = 75
            elif current_price > ma5:
                trend = "弱势反弹"
                trend_score = 60
            elif ma5 < ma10 < ma20:
                trend = "下跌趋势"
                trend_score = 30
            else:
                trend = "震荡整理"
                trend_score = 50
        else:
            trend = "数据不足"
            trend_score = 50
        
        # 价格位置分析
        high_52w = df['最高'].max()
        low_52w = df['最低'].min()
        price_position = (current_price - low_52w) / (high_52w - low_52w) if high_52w > low_52w else 0.5
        
        # 成交量分析
        avg_volume = df['成交量'].mean()
        current_volume = latest['成交量']
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        analysis = {
            "价格": f"{current_price:.2f}元",
            "涨跌幅": f"{latest['涨跌幅']:.2f}%",
            "趋势": trend,
            "均线": {
                "MA5": f"{ma5:.2f}" if pd.notna(ma5) else "计算中",
                "MA10": f"{ma10:.2f}" if pd.notna(ma10) else "计算中", 
                "MA20": f"{ma20:.2f}" if pd.notna(ma20) else "计算中"
            },
            "价格位置": f"{price_position*100:.1f}%" if price_position else "未知",
            "成交量比": f"{volume_ratio:.2f}",
            "支撑阻力": {
                "52周最高": f"{high_52w:.2f}元",
                "52周最低": f"{low_52w:.2f}元"
            }
        }
        
        # 技术面评分
        tech_score = trend_score * 0.5  # 趋势50%
        
        # 价格位置评分
        if price_position < 0.3:
            tech_score += 20  # 低位
        elif price_position > 0.8:
            tech_score += 5   # 高位
        else:
            tech_score += 15  # 中位
        
        # 成交量评分
        if volume_ratio > 1.5:
            tech_score += 15
        elif volume_ratio > 1.0:
            tech_score += 10
        else:
            tech_score += 5
        
        tech_score = max(0, min(100, tech_score))
        
        print(f"✅ 技术面评分: {tech_score:.0f}/100")
        print(f"✅ 趋势状态: {trend}")
        print(f"✅ 价格位置: {price_position*100:.1f}%" if price_position else "✅ 价格位置: 计算中")
        print(f"✅ 成交量: {'放量' if volume_ratio > 1.2 else '缩量' if volume_ratio < 0.8 else '正常'}")
        
        return {
            "评分": tech_score,
            "观点": f"技术面{trend}，当前位置{'偏低' if price_position and price_position < 0.4 else '适中'}",
            "详情": analysis
        }

    def market_analyst_view(self, data):
        """市场分析师观点"""
        print(f"\n🎯 市场分析师视角 - {self.stock_name}")
        print("-" * 50)
        
        analysis = {
            "行业地位": "西藏建筑行业龙头，市占率高",
            "竞争优势": "地域垄断+技术实力+政府关系",
            "市场机会": "川藏铁路+西藏基建+一带一路",
            "主要风险": "竞争加剧+成本上升+回款风险"
        }
        
        score = 65  # 基础分
        
        print(f"✅ 市场前景评分: {score}/100")
        print(f"✅ 核心机会: 川藏铁路建设")
        print(f"✅ 竞争优势: 地域垄断+技术实力")
        print(f"⚠️ 主要挑战: 行业竞争加剧")
        
        return {
            "评分": score,
            "观点": "西藏建筑龙头，受益基建投资，但面临竞争压力",
            "详情": analysis
        }

    def policy_analyst_view(self, data):
        """政策分析师观点"""
        print(f"\n🏛️ 政策分析师视角 - {self.stock_name}")
        print("-" * 50)
        
        analysis = {
            "政策支持": "西藏发展+川藏铁路+一带一路",
            "投资规划": "十四五西藏基础设施建设",
            "政策机遇": "国家对西藏建设支持力度大",
            "政策风险": "环保要求+债务管控"
        }
        
        score = 78  # 基础分
        
        print(f"✅ 政策支持度: {score}/100")
        print(f"✅ 核心政策: 西藏发展战略")
        print(f"✅ 重大机遇: 川藏铁路建设")
        print(f"⚠️ 政策约束: 环保要求提高")
        
        return {
            "评分": score,
            "观点": "西藏战略地位重要，政策长期利好",
            "详情": analysis
        }

    def risk_manager_view(self, fundamental, technical, market, policy):
        """风险管理师观点"""
        print(f"\n⚠️ 风险管理师视角 - {self.stock_name}")
        print("-" * 50)
        
        analysis = {
            "主要风险": [
                "财务风险：短期亏损压力",
                "经营风险：业务集中西藏地区",
                "市场风险：建筑行业竞争激烈",
                "流动性风险：股票流动性一般"
            ],
            "缓释因素": [
                "国企背景：抗风险能力强",
                "地域优势：西藏市场垄断地位",
                "政策支持：国家战略重点支持",
                "技术壁垒：高原施工技术门槛"
            ]
        }
        
        # 综合风险评分
        risk_score = (fundamental['评分'] * 0.3 + technical['评分'] * 0.2 + 
                     market['评分'] * 0.2 + policy['评分'] * 0.3)
        
        if risk_score >= 70:
            risk_level = "中等风险"
            recommendation = "可以买入"
        elif risk_score >= 55:
            risk_level = "中等偏高风险"
            recommendation = "谨慎买入"
        else:
            risk_level = "较高风险"
            recommendation = "暂缓买入"
        
        print(f"✅ 风险等级: {risk_level}")
        print(f"✅ 投资建议: {recommendation}")
        print(f"✅ 主要缓释: 国企背景+政策支持")
        
        return {
            "评分": risk_score,
            "风险等级": risk_level,
            "投资建议": recommendation,
            "详情": analysis
        }

    def comprehensive_analysis(self):
        """综合分析"""
        print(f"\n{'='*60}")
        print(f"🎯 西藏天路(600326) 多智能体综合分析")
        print(f"{'='*60}")
        print(f"📅 分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 获取数据
        data = self.get_stock_data()
        
        # 各智能体分析
        fundamental = self.fundamental_analyst_view(data)
        technical = self.technical_analyst_view(data)
        market = self.market_analyst_view(data)
        policy = self.policy_analyst_view(data)
        risk = self.risk_manager_view(fundamental, technical, market, policy)
        
        # 综合评分
        scores = {
            "基本面": fundamental['评分'],
            "技术面": technical['评分'],
            "市场前景": market['评分'],
            "政策支持": policy['评分']
        }
        
        # 加权总分
        total_score = (scores["基本面"] * 0.3 + scores["技术面"] * 0.2 + 
                      scores["市场前景"] * 0.2 + scores["政策支持"] * 0.3)
        
        print(f"\n📊 综合评分汇总")
        print("-" * 30)
        for aspect, score in scores.items():
            print(f"{aspect}: {score:.0f}/100")
        print(f"加权总分: {total_score:.1f}/100")
        
        # 最终建议
        if total_score >= 75:
            final_recommendation = "强烈推荐买入"
            cost_performance = "性价比很高"
        elif total_score >= 65:
            final_recommendation = "推荐买入"
            cost_performance = "性价比较高"
        elif total_score >= 55:
            final_recommendation = "谨慎买入"
            cost_performance = "性价比一般"
        else:
            final_recommendation = "暂缓买入"
            cost_performance = "性价比偏低"
        
        print(f"\n🎯 最终投资建议")
        print("-" * 30)
        print(f"投资建议: {final_recommendation}")
        print(f"性价比评估: {cost_performance}")
        print(f"风险等级: {risk['风险等级']}")
        
        # 操作建议
        if data is not None and not data.empty:
            current_price = data.iloc[-1]['收盘']
            print(f"\n💡 操作建议")
            print("-" * 30)
            print(f"当前价格: {current_price:.2f}元")
            
            if total_score >= 60:
                print(f"建议买入区间: {current_price*0.95:.2f}-{current_price*1.05:.2f}元")
                print(f"目标价位: {current_price*1.2:.2f}元 (+20%)")
                print(f"止损价位: {current_price*0.85:.2f}元 (-15%)")
            else:
                print("建议等待更好时机")
        
        return {
            "总分": total_score,
            "建议": final_recommendation,
            "性价比": cost_performance,
            "风险": risk['风险等级']
        }

def main():
    analyzer = TibetTianluAnalyzer()
    result = analyzer.comprehensive_analysis()
    
    print(f"\n🎉 分析完成！")
    if result:
        print(f"📋 结论: {result['建议']} - {result['性价比']}")

if __name__ == "__main__":
    main()