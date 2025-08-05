#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
西藏天路(600326)多智能体深度分析 (修复版)
使用tushare和akshare真实交易数据进行全面分析
"""

import pandas as pd
import akshare as ak
import numpy as np
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

class TibetTianluAnalyzer:
    def __init__(self):
        self.stock_code = '600326'
        self.stock_name = '西藏天路'
        self.company_info = {
            "全称": "西藏天路股份有限公司",
            "成立时间": "1999-03-29",
            "上市时间": "2001-01-16", 
            "主营业务": "工程承包、水泥及水泥制品生产销售、沥青制品、矿产品加工",
            "所属行业": "制造业-非金属矿物制品业",
            "公司性质": "西藏自治区国有企业"
        }
        
    def get_stock_data(self, days=180):
        """使用akshare获取真实交易数据"""
        print(f"📊 获取{self.stock_name}({self.stock_code})近{days}天交易数据...")
        
        try:
            # 获取历史数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            # 使用akshare获取历史数据
            hist_data = ak.stock_zh_a_hist(symbol=self.stock_code, period="daily", 
                                         start_date=start_date, end_date=end_date, adjust="")
            
            if hist_data.empty:
                print("❌ 未获取到历史数据")
                return None
            
            # 重命名列名以便统一处理
            hist_data.columns = ['日期', 'open', 'close', 'high', 'low', 'volume', 'turnover', 'amplitude', 'pct_chg', 'change', 'turnover_rate']
            
            # 确保数据类型正确
            numeric_cols = ['open', 'close', 'high', 'low', 'volume', 'turnover', 'amplitude', 'pct_chg', 'change', 'turnover_rate']
            for col in numeric_cols:
                if col in hist_data.columns:
                    hist_data[col] = pd.to_numeric(hist_data[col], errors='coerce')
            
            hist_data = hist_data.sort_values('日期').reset_index(drop=True)
            
            print(f"✅ 成功获取 {len(hist_data)} 条交易数据")
            
            return hist_data
            
        except Exception as e:
            print(f"❌ 数据获取失败: {e}")
            return None

    def fundamental_analyst_view(self, data):
        """基本面分析师观点"""
        print(f"\n📊 基本面分析师视角 - {self.stock_name}")
        print("-" * 50)
        
        if data is None or data.empty:
            print("❌ 缺乏足够数据进行基本面分析")
            return {"评分": 40, "观点": "数据不足", "详情": {}}
        
        latest_data = data.iloc[-1]
        
        analysis = {
            "基本情况": {
                "当前价格": f"{latest_data['close']:.2f}元",
                "涨跌幅": f"{latest_data['pct_chg']:.2f}%",
                "成交量": f"{latest_data['volume']/10000:.1f}万手",
                "换手率": f"{latest_data.get('turnover_rate', 0):.2f}%"
            },
            "财务表现": {
                "营业收入": "2025Q1: 3.386亿元(+10.76%)",
                "净利润": "2025Q1: -1.24亿元(-68.73%)",
                "上半年预告": "亏损7700万-1.15亿元",
                "经营状况": "短期面临盈利压力"
            },
            "业务优势": {
                "核心业务": "工程承包+建材生产双轮驱动",
                "项目经验": "承建青藏公路、川藏公路等170多个重点工程",
                "地域优势": "深耕西藏市场，拓展全国及海外",
                "资质优势": "国家级高新技术企业，西藏国企标杆"
            },
            "业务挑战": {
                "竞争加剧": "西藏建筑市场竞争激烈",
                "项目周期": "存量项目完工，新项目收入确认滞后",
                "盈利压力": "成本上升，毛利率承压",
                "资金压力": "工程垫资较多，现金流紧张"
            }
        }
        
        # 基本面评分
        score = 50  # 基础分
        
        # 近期表现扣分
        if latest_data['pct_chg'] < -5:
            score -= 10
        elif latest_data['pct_chg'] > 5:
            score += 10
        
        # 亏损情况扣分
        score -= 15  # 近期亏损
        
        # 行业地位加分
        score += 10  # 西藏建筑龙头
        
        # 政策受益加分
        score += 5   # 西藏建设政策
        
        score = max(0, min(100, score))
        
        print(f"✅ 基本面评分: {score}/100")
        print(f"✅ 当前价格: {analysis['基本情况']['当前价格']}")
        print(f"✅ 核心优势: {analysis['业务优势']['核心业务']}")
        print(f"⚠️ 主要挑战: {analysis['业务挑战']['盈利压力']}")
        
        return {
            "评分": score,
            "观点": "西藏建筑龙头，但短期面临盈利挑战",
            "详情": analysis
        }

    def technical_analyst_view(self, data):
        """技术分析师观点"""
        print(f"\n📈 技术分析师视角 - {self.stock_name}")
        print("-" * 50)
        
        if data is None or data.empty:
            print("❌ 缺乏技术分析数据")
            return {"评分": 40, "观点": "数据不足", "详情": {}}
        
        df = data.copy()
        
        # 计算技术指标
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()
        
        # RSI指标
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        latest = df.iloc[-1]
        
        # 趋势分析
        current_price = latest['close']
        ma5 = latest['ma5']
        ma10 = latest['ma10'] 
        ma20 = latest['ma20']
        ma60 = latest['ma60']
        
        if pd.isna(ma5) or pd.isna(ma10) or pd.isna(ma20):
            trend = "数据不足"
            trend_score = 50
        elif current_price > ma5 > ma10 > ma20 > ma60:
            trend = "强势上涨"
            trend_score = 90
        elif current_price > ma5 > ma10 > ma20:
            trend = "多头排列"
            trend_score = 80
        elif current_price > ma5 > ma10:
            trend = "短期向好"
            trend_score = 70
        elif current_price > ma5:
            trend = "弱势反弹"
            trend_score = 60
        elif ma5 < ma10 < ma20:
            trend = "空头排列"
            trend_score = 20
        else:
            trend = "震荡整理"
            trend_score = 50
        
        # 成交量分析
        avg_volume = df['volume'].tail(20).mean()
        current_volume = latest['volume']
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # 支撑阻力分析
        recent_high = df['high'].tail(30).max()
        recent_low = df['low'].tail(30).min()
        high_52w = df['high'].max()
        low_52w = df['low'].min()
        
        analysis = {
            "价格信息": {
                "当前价格": f"{current_price:.2f}元",
                "涨跌幅": f"{latest['pct_chg']:.2f}%",
                "成交量": f"{current_volume/10000:.1f}万手",
                "成交额": f"{latest['turnover']/10000:.1f}万元"
            },
            "技术指标": {
                "MA5": f"{ma5:.2f}" if pd.notna(ma5) else "计算中",
                "MA10": f"{ma10:.2f}" if pd.notna(ma10) else "计算中",
                "MA20": f"{ma20:.2f}" if pd.notna(ma20) else "计算中",
                "MA60": f"{ma60:.2f}" if pd.notna(ma60) else "计算中",
                "RSI": f"{latest['rsi']:.1f}" if pd.notna(latest['rsi']) else "计算中"
            },
            "趋势分析": {
                "趋势状态": trend,
                "趋势强度": f"{trend_score}/100",
                "均线系统": "多头排列" if current_price > ma5 > ma10 > ma20 else "空头排列" if ma5 < ma10 < ma20 else "混乱状态"
            },
            "关键价位": {
                "近期阻力": f"{recent_high:.2f}元",
                "近期支撑": f"{recent_low:.2f}元", 
                "52周最高": f"{high_52w:.2f}元",
                "52周最低": f"{low_52w:.2f}元"
            },
            "成交量分析": {
                "成交量比": f"{volume_ratio:.2f}",
                "量价关系": "量价配合" if volume_ratio > 1.2 and latest['pct_chg'] > 0 else "量价背离" if volume_ratio < 0.8 and latest['pct_chg'] > 0 else "正常"
            }
        }
        
        # 技术面综合评分
        tech_score = trend_score * 0.4  # 趋势占40%
        
        # RSI评分
        rsi = latest['rsi']
        if pd.notna(rsi):
            if 30 <= rsi <= 70:
                tech_score += 20
            elif rsi < 30:
                tech_score += 25  # 超卖机会
            elif rsi > 70:
                tech_score += 10  # 超买风险
        else:
            tech_score += 15
        
        # 成交量评分
        if volume_ratio > 1.5:
            tech_score += 15
        elif volume_ratio > 1.2:
            tech_score += 10
        elif volume_ratio > 0.8:
            tech_score += 5
        
        # 价格位置评分
        price_position = (current_price - low_52w) / (high_52w - low_52w) if high_52w > low_52w else 0.5
        if price_position < 0.3:
            tech_score += 10  # 低位机会
        elif price_position > 0.8:
            tech_score -= 5   # 高位风险
        
        tech_score = max(0, min(100, tech_score))
        
        print(f"✅ 技术面评分: {tech_score:.0f}/100")
        print(f"✅ 趋势状态: {trend}")
        print(f"✅ 当前价格: {current_price:.2f}元 ({latest['pct_chg']:+.2f}%)")
        print(f"✅ RSI指标: {latest['rsi']:.1f}" if pd.notna(latest['rsi']) else "✅ RSI: 计算中")
        
        return {
            "评分": tech_score,
            "观点": f"技术面{trend}，关注{recent_high:.2f}元阻力位",
            "详情": analysis
        }

    def market_analyst_view(self, data):
        """市场分析师观点"""
        print(f"\n🎯 市场分析师视角 - {self.stock_name}")
        print("-" * 50)
        
        analysis = {
            "行业地位": {
                "市场地位": "西藏建筑行业龙头企业",
                "品牌优势": "天路品牌为西藏著名商标",
                "资质实力": "国家级高新技术企业",
                "项目经验": "承建170+国家级、自治区级重点工程"
            },
            "竞争优势": {
                "地域垄断": "在西藏地区具有较强的地域优势",
                "技术实力": "掌握高原地区特殊施工技术",
                "政府关系": "国有企业背景，政府项目获取能力强",
                "产业链整合": "工程承包+建材生产一体化"
            },
            "市场机会": {
                "西藏建设": "十四五西藏基础设施建设规划",
                "川藏铁路": "川藏铁路建设带来巨大机遇",
                "一带一路": "参与尼泊尔等海外项目", 
                "新基建": "数字西藏、绿色能源基础设施"
            },
            "行业挑战": {
                "竞争加剧": "央企、民企进入西藏市场",
                "成本上升": "原材料价格上涨，人工成本增加",
                "季节性": "高原气候导致施工季节性明显",
                "回款风险": "政府项目回款周期较长"
            }
        }
        
        # 市场前景评分
        score = 60  # 基础分
        score += 15  # 西藏建筑龙头
        score += 10  # 川藏铁路等大项目
        score -= 5   # 竞争加剧
        score -= 10  # 近期亏损
        
        score = max(0, min(100, score))
        
        print(f"✅ 市场前景评分: {score}/100")
        print(f"✅ 核心优势: 西藏建筑龙头+技术实力")
        print(f"✅ 主要机会: 川藏铁路+西藏基建")
        print(f"⚠️ 主要挑战: 竞争加剧+成本压力")
        
        return {
            "评分": score,
            "观点": "西藏建筑龙头，受益基建政策，但面临竞争压力",
            "详情": analysis
        }

    def policy_analyst_view(self, data):
        """政策分析师观点"""
        print(f"\n🏛️ 政策分析师视角 - {self.stock_name}")
        print("-" * 50)
        
        analysis = {
            "核心政策支持": {
                "西藏发展": "新时代党的治藏方略，西藏长治久安和高质量发展",
                "川藏铁路": "川藏铁路等重大基础设施建设项目",
                "一带一路": "西藏面向南亚开放重要通道建设",
                "乡村振兴": "西藏乡村振兴和边境小康村建设"
            },
            "具体政策机遇": {
                "十四五规划": "西藏十四五综合交通运输发展规划",
                "基础设施": "适度超前开展基础设施投资",
                "生态保护": "生态保护和高质量发展并重",
                "对口援藏": "全国对口援藏项目持续推进"
            },
            "政策风险": {
                "环保要求": "生态红线约束，环保要求趋严",
                "债务管控": "地方政府债务管控影响项目推进",
                "竞争政策": "建筑市场开放，竞争更加充分",
                "价格管控": "工程造价管控，利润空间压缩"
            }
        }
        
        # 政策支持度评分
        score = 70  # 基础分
        score += 15  # 国家战略重点地区
        score += 10  # 重大项目机遇
        score -= 5   # 环保要求提高
        score -= 5   # 市场更加开放
        
        score = max(0, min(100, score))
        
        print(f"✅ 政策支持度: {score}/100")
        print(f"✅ 核心政策: 西藏发展+川藏铁路")
        print(f"✅ 主要机遇: 基础设施建设+对口援藏")
        print(f"⚠️ 政策风险: 环保约束+债务管控")
        
        return {
            "评分": score,
            "观点": "西藏战略地位重要，政策支持力度大，长期利好确定",
            "详情": analysis
        }

    def risk_manager_view(self, data, fundamental, technical, market, policy):
        """风险管理师观点"""
        print(f"\n⚠️ 风险管理师视角 - {self.stock_name}")
        print("-" * 50)
        
        analysis = {
            "主要风险": {
                "财务风险": "短期亏损，现金流紧张，应收账款较高",
                "经营风险": "项目集中在西藏，地域风险较大",
                "市场风险": "建筑行业竞争激烈，毛利率下降",
                "政策风险": "依赖政府投资，政策变化影响大",
                "流动性风险": "股票流动性一般，大额交易可能冲击价格"
            },
            "风险等级评估": {
                "财务风险": "高风险" if fundamental['评分'] < 50 else "中等风险",
                "技术风险": "低风险" if technical['评分'] > 70 else "中等风险",
                "市场风险": "中等风险",
                "政策风险": "低风险" if policy['评分'] > 80 else "中等风险",
                "流动性风险": "中等风险"
            },
            "风险缓释因素": {
                "国企背景": "国有企业，抗风险能力相对较强",
                "地域垄断": "在西藏地区竞争优势明显",
                "政策支持": "西藏建设政策支持力度大",
                "技术实力": "高原施工技术门槛较高"
            }
        }
        
        # 风险评分（分数越高风险越低）
        risk_scores = [
            fundamental['评分'] * 0.3,  # 基本面30%
            technical['评分'] * 0.2,    # 技术面20%
            market['评分'] * 0.2,       # 市场面20%
            policy['评分'] * 0.3        # 政策面30%
        ]
        
        overall_score = sum(risk_scores)
        
        if overall_score >= 80:
            risk_level = "低风险"
            recommendation = "可以买入"
        elif overall_score >= 60:
            risk_level = "中等风险"
            recommendation = "谨慎买入"
        elif overall_score >= 40:
            risk_level = "较高风险"
            recommendation = "暂缓买入"
        else:
            risk_level = "高风险"
            recommendation = "不建议买入"
        
        print(f"✅ 综合风险等级: {risk_level}")
        print(f"✅ 投资建议: {recommendation}")
        print(f"✅ 主要风险: 财务风险+经营风险")
        print(f"✅ 缓释因素: 国企背景+政策支持")
        
        return {
            "评分": overall_score,
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
        
        if data is None:
            print("❌ 数据获取失败，无法进行分析")
            return None
        
        # 各智能体分析
        fundamental = self.fundamental_analyst_view(data)
        technical = self.technical_analyst_view(data)
        market = self.market_analyst_view(data)
        policy = self.policy_analyst_view(data)
        risk = self.risk_manager_view(data, fundamental, technical, market, policy)
        
        # 综合评分
        scores = {
            "基本面": fundamental['评分'],
            "技术面": technical['评分'],
            "市场前景": market['评分'],
            "政策支持": policy['评分'],
            "风险控制": risk['评分']
        }
        
        # 加权平均（基本面30%，技术面20%，市场20%，政策20%，风险10%）
        weights = [0.3, 0.2, 0.2, 0.2, 0.1]
        total_score = sum(score * weight for score, weight in zip(scores.values(), weights))
        
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
        elif total_score >= 45:
            final_recommendation = "暂缓买入"
            cost_performance = "性价比偏低"
        else:
            final_recommendation = "不建议买入"
            cost_performance = "性价比低"
        
        print(f"\n🎯 最终投资建议")
        print("-" * 30)
        print(f"投资建议: {final_recommendation}")
        print(f"性价比评估: {cost_performance}")
        print(f"风险等级: {risk['风险等级']}")
        
        # 操作建议
        if data is not None and not data.empty:
            current_price = data.iloc[-1]['close']
            print(f"\n💡 操作建议")
            print("-" * 30)
            print(f"当前价格: {current_price:.2f}元")
            
            if total_score >= 60:
                target_price = current_price * 1.2
                stop_loss = current_price * 0.85
                print(f"建议买入区间: {current_price*0.95:.2f}-{current_price*1.05:.2f}元")
                print(f"目标价位: {target_price:.2f}元")
                print(f"止损价位: {stop_loss:.2f}元")
                print(f"建议仓位: 3-5%")
            else:
                print("建议等待更好的买入时机")
                print("关注基本面改善和技术面突破")
        
        return {
            "company_info": self.company_info,
            "scores": scores,
            "total_score": total_score,
            "recommendation": final_recommendation,
            "cost_performance": cost_performance,
            "risk_level": risk['风险等级'],
            "analysis_details": {
                "fundamental": fundamental,
                "technical": technical,
                "market": market,
                "policy": policy,
                "risk": risk
            }
        }

def main():
    """主函数"""
    analyzer = TibetTianluAnalyzer()
    result = analyzer.comprehensive_analysis()
    
    if result:
        # 保存分析报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"西藏天路多智能体分析报告_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📄 详细分析报告已保存: {filename}")
        print(f"\n🎉 分析完成！")
        print(f"📋 核心结论: {result['recommendation']} - {result['cost_performance']}")

if __name__ == "__main__":
    main()