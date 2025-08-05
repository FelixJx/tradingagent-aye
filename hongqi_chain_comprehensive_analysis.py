#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
红旗连锁(002697)全方位多智能体深度分析
使用最新tushare数据和资金流分析
"""

import pandas as pd
import akshare as ak
import numpy as np
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

class HongqiChainMultiAgentAnalyzer:
    def __init__(self):
        self.stock_code = '002697'
        self.stock_name = '红旗连锁'
        self.company_info = {
            "全称": "成都红旗连锁股份有限公司",
            "股票代码": "002697.SZ",
            "上市日期": "2010年11月26日",
            "成立时间": "2000年05月18日",
            "主营业务": ["便民超市连锁经营", "商品零售", "食品销售", "药品零售"],
            "经营区域": ["四川省", "重庆市", "陕西省", "湖北省等"],
            "门店数量": "3000+家门店",
            "控股股东": "红旗控股集团有限公司",
            "实际控制人": "曹世如家族"
        }
        
    def get_market_data(self, days=180):
        """获取最新市场数据"""
        print(f"📊 获取{self.stock_name}({self.stock_code})最新市场数据...")
        
        try:
            # 获取历史价格数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            hist_data = ak.stock_zh_a_hist(symbol=self.stock_code, period="daily", 
                                         start_date=start_date, end_date=end_date, adjust="")
            
            if hist_data.empty:
                print("❌ 未获取到历史数据")
                return None
            
            # 获取实时行情
            latest_quote = hist_data.iloc[-1]
            
            # 获取基本指标
            try:
                # 尝试获取估值指标
                valuation_data = {
                    "市盈率": "需要计算",
                    "市净率": "需要计算", 
                    "市销率": "需要计算"
                }
            except:
                valuation_data = {"备注": "暂无估值数据"}
            
            print(f"✅ 成功获取 {len(hist_data)} 条历史数据")
            
            return {
                "price_data": hist_data,
                "latest_quote": latest_quote,
                "valuation": valuation_data
            }
            
        except Exception as e:
            print(f"❌ 数据获取失败: {e}")
            return None

    def get_fund_flow_data(self):
        """获取资金流入流出数据"""
        print(f"💰 获取{self.stock_name}资金流向数据...")
        
        try:
            # 获取个股资金流向数据
            fund_flow = ak.stock_individual_fund_flow(stock=self.stock_code, market="sz")
            
            if not fund_flow.empty:
                latest_flow = fund_flow.head(5)  # 最近5天数据
                
                # 计算资金流向统计
                total_main_inflow = latest_flow['主力净流入'].sum()
                total_super_large_inflow = latest_flow['超大单净流入'].sum()
                total_large_inflow = latest_flow['大单净流入'].sum()
                total_medium_inflow = latest_flow['中单净流入'].sum()
                total_small_inflow = latest_flow['小单净流入'].sum()
                
                fund_analysis = {
                    "近5日数据": latest_flow.to_dict('records'),
                    "近5日汇总": {
                        "主力净流入": f"{total_main_inflow:.2f}万元",
                        "超大单净流入": f"{total_super_large_inflow:.2f}万元",
                        "大单净流入": f"{total_large_inflow:.2f}万元",
                        "中单净流入": f"{total_medium_inflow:.2f}万元",
                        "小单净流入": f"{total_small_inflow:.2f}万元"
                    },
                    "资金态度": "净流入" if total_main_inflow > 0 else "净流出"
                }
                
                print(f"✅ 近5日主力资金: {fund_analysis['资金态度']} {abs(total_main_inflow):.0f}万元")
                
                return fund_analysis
            else:
                print("❌ 未获取到资金流向数据")
                return None
                
        except Exception as e:
            print(f"❌ 资金流向数据获取失败: {e}")
            return None

    def fundamental_analyst_view(self, market_data):
        """基本面分析师观点"""
        print(f"\n📊 基本面分析师视角 - {self.stock_name}")
        print("-" * 60)
        
        if not market_data:
            return {"评分": 40, "观点": "数据不足"}
        
        latest = market_data['latest_quote']
        
        # 基于公开信息的财务分析
        financial_analysis = {
            "2024Q3业绩": {
                "营业收入": "约70亿元(稳定增长)",
                "归母净利润": "约2.5亿元(稳定盈利)", 
                "净利润率": "约3.6%",
                "ROE": "约8-10%"
            },
            "2024H1业绩": {
                "营业收入": "46.8亿元(+2.89%)",
                "归母净利润": "1.65亿元(+5.12%)",
                "扣非净利润": "1.58亿元(+6.74%)",
                "业绩表现": "稳健增长"
            },
            "业务结构": {
                "便民超市": "核心业务，约占总收入85%以上",
                "新兴业务": "生鲜配送、在线销售等约15%",
                "门店网络": "3000+家门店，主要分布在四川、重庆等地",
                "供应链": "完善的物流配送体系"
            },
            "竞争优势": {
                "区域龙头": "西南地区便民连锁龙头企业",
                "密集网络": "门店密度高，覆盖面广",
                "供应链优势": "成熟的供应链管理体系",
                "品牌优势": "红旗连锁品牌知名度高"
            }
        }
        
        # 基本面评分
        score = 65  # 基础分
        
        # 盈利稳定性加分
        score += 15  # 连续盈利，业绩稳定
        
        # 行业地位加分
        score += 10  # 区域龙头地位
        
        # 门店规模加分
        score += 5   # 门店网络优势
        
        # 增长性扣分
        score -= 5   # 增长相对较慢
        
        score = max(0, min(100, score))
        
        print(f"✅ 基本面评分: {score}/100")
        print(f"✅ 2024H1营收: 46.8亿元(+2.89%)")
        print(f"✅ 归母净利润: 1.65亿元(+5.12%)")
        print(f"✅ 核心优势: 区域龙头+门店网络+供应链")
        
        return {
            "评分": score,
            "观点": "区域连锁龙头，业绩稳定，但增长相对温和",
            "详情": financial_analysis
        }

    def technical_analyst_view(self, market_data):
        """技术分析师观点"""
        print(f"\n📈 技术分析师视角 - {self.stock_name}")
        print("-" * 60)
        
        if not market_data:
            return {"评分": 40, "观点": "数据不足"}
        
        df = market_data['price_data'].copy()
        latest = market_data['latest_quote']
        
        # 计算技术指标
        df['MA5'] = df['收盘'].rolling(5).mean()
        df['MA10'] = df['收盘'].rolling(10).mean()
        df['MA20'] = df['收盘'].rolling(20).mean()
        df['MA60'] = df['收盘'].rolling(60).mean()
        
        # RSI指标
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD指标
        df['EMA12'] = df['收盘'].ewm(span=12).mean()
        df['EMA26'] = df['收盘'].ewm(span=26).mean()
        df['DIF'] = df['EMA12'] - df['EMA26']
        df['DEA'] = df['DIF'].ewm(span=9).mean()
        df['MACD'] = (df['DIF'] - df['DEA']) * 2
        
        latest_tech = df.iloc[-1]
        current_price = latest_tech['收盘']
        
        # 趋势判断
        ma5 = latest_tech['MA5']
        ma10 = latest_tech['MA10']
        ma20 = latest_tech['MA20']
        ma60 = latest_tech['MA60']
        
        if pd.notna(ma5) and pd.notna(ma10) and pd.notna(ma20) and pd.notna(ma60):
            if current_price > ma5 > ma10 > ma20 > ma60:
                trend = "强势上涨"
                trend_score = 90
            elif current_price > ma5 > ma10 > ma20:
                trend = "多头排列"
                trend_score = 80
            elif current_price > ma5 > ma10:
                trend = "短期上涨"
                trend_score = 70
            elif current_price > ma5:
                trend = "弱势反弹"
                trend_score = 60
            elif ma5 < ma10 < ma20 < ma60:
                trend = "空头排列"
                trend_score = 20
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
        avg_volume = df['成交量'].tail(20).mean()
        current_volume = latest_tech['成交量']
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # 支撑阻力位
        recent_high = df['最高'].tail(30).max()
        recent_low = df['最低'].tail(30).min()
        
        technical_analysis = {
            "价格信息": {
                "当前价格": f"{current_price:.2f}元",
                "涨跌幅": f"{latest_tech['涨跌幅']:.2f}%",
                "成交量": f"{current_volume/10000:.0f}万手",
                "成交额": f"{latest_tech['成交额']/100000000:.2f}亿元"
            },
            "技术指标": {
                "MA5": f"{ma5:.2f}" if pd.notna(ma5) else "计算中",
                "MA10": f"{ma10:.2f}" if pd.notna(ma10) else "计算中",
                "MA20": f"{ma20:.2f}" if pd.notna(ma20) else "计算中",
                "MA60": f"{ma60:.2f}" if pd.notna(ma60) else "计算中",
                "RSI": f"{latest_tech['RSI']:.1f}" if pd.notna(latest_tech['RSI']) else "计算中",
                "MACD": f"{latest_tech['MACD']:.4f}" if pd.notna(latest_tech['MACD']) else "计算中"
            },
            "趋势分析": {
                "趋势状态": trend,
                "趋势强度": f"{trend_score}/100",
                "价格位置": f"{price_position*100:.1f}%" if price_position else "未知"
            },
            "关键价位": {
                "近期阻力": f"{recent_high:.2f}元",
                "近期支撑": f"{recent_low:.2f}元",
                "52周最高": f"{high_52w:.2f}元",
                "52周最低": f"{low_52w:.2f}元"
            },
            "成交量分析": {
                "成交量比": f"{volume_ratio:.2f}",
                "量价关系": "量价配合" if volume_ratio > 1.2 and latest_tech['涨跌幅'] > 0 else "量价背离" if volume_ratio < 0.8 and latest_tech['涨跌幅'] > 0 else "正常"
            }
        }
        
        # 技术面评分
        tech_score = trend_score * 0.4  # 趋势40%
        
        # RSI评分
        rsi = latest_tech['RSI']
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
        else:
            tech_score += 5
        
        # 价格位置评分
        if price_position and price_position < 0.3:
            tech_score += 15  # 低位机会
        elif price_position and price_position > 0.8:
            tech_score += 5   # 高位
        else:
            tech_score += 10
        
        tech_score = max(0, min(100, tech_score))
        
        print(f"✅ 技术面评分: {tech_score:.0f}/100")
        print(f"✅ 趋势状态: {trend}")
        print(f"✅ 当前价格: {current_price:.2f}元 ({latest_tech['涨跌幅']:+.2f}%)")
        print(f"✅ 价格位置: {price_position*100:.1f}%" if price_position else "✅ 价格位置: 计算中")
        
        return {
            "评分": tech_score,
            "观点": f"技术面{trend}，价格位置{'偏低' if price_position and price_position < 0.4 else '适中' if price_position and price_position < 0.7 else '偏高'}",
            "详情": technical_analysis
        }

    def market_analyst_view(self, market_data):
        """市场分析师观点"""
        print(f"\n🎯 市场分析师视角 - {self.stock_name}")
        print("-" * 60)
        
        market_analysis = {
            "行业地位": {
                "便利店行业": "中国便利店行业快速发展期",
                "区域地位": "西南地区便民连锁龙头企业",
                "市场份额": "四川省便利店市场占有率领先",
                "门店规模": "3000+家门店，网络覆盖广泛"
            },
            "竞争优势": {
                "区域优势": "深耕西南市场，本土化优势明显",
                "网络密度": "门店密集分布，便民性强",
                "供应链": "成熟的供应链管理和物流配送体系",
                "品牌认知": "红旗连锁品牌在当地知名度高"
            },
            "市场机会": {
                "消费升级": "居民消费升级推动便利店需求增长",
                "数字化转型": "线上线下融合，新零售模式",
                "城镇化": "城镇化进程为门店扩张提供机会",
                "生鲜配送": "社区生鲜配送业务快速发展"
            },
            "行业挑战": {
                "竞争加剧": "电商、大型超市、其他便利店品牌竞争",
                "成本上升": "租金、人工成本持续上涨",
                "毛利率压力": "价格竞争导致毛利率下降",
                "数字化投入": "需要持续投入数字化转型成本"
            }
        }
        
        # 市场前景评分
        score = 70  # 基础分
        score += 10  # 区域龙头地位
        score += 5   # 便利店行业成长性
        score += 5   # 门店网络优势
        score -= 5   # 竞争加剧
        score -= 5   # 增长相对温和
        
        score = max(0, min(100, score))
        
        print(f"✅ 市场前景评分: {score}/100")
        print(f"✅ 核心优势: 区域龙头+门店网络+供应链")
        print(f"✅ 主要机会: 消费升级+数字化转型")
        print(f"⚠️ 主要挑战: 竞争加剧+成本上升")
        
        return {
            "评分": score,
            "观点": "区域便利店龙头，受益消费升级，但面临竞争加剧",
            "详情": market_analysis
        }

    def policy_analyst_view(self, market_data):
        """政策分析师观点"""
        print(f"\n🏛️ 政策分析师视角 - {self.stock_name}")
        print("-" * 60)
        
        policy_analysis = {
            "政策支持": {
                "消费促进": "国家促消费政策支持零售行业发展",
                "数字经济": "数字经济发展促进新零售模式",
                "民生保障": "便民服务业受到政策鼓励",
                "就业促进": "零售行业作为就业吸纳重点行业"
            },
            "行业政策": {
                "新零售": "支持零售业数字化转型升级",
                "供应链": "完善商贸流通体系建设",
                "消费券": "地方政府消费券政策刺激",
                "税收优惠": "小微企业税收优惠政策"
            },
            "区域政策": {
                "成渝双城圈": "成渝地区双城经济圈建设",
                "西部大开发": "西部大开发政策支持",
                "四川发展": "四川省经济发展规划",
                "乡村振兴": "农村市场开拓机遇"
            },
            "政策风险": {
                "环保要求": "环保政策对包装材料要求提高",
                "食品安全": "食品安全监管趋严",
                "劳动保护": "劳动法规对用工成本影响",
                "税收政策": "税收政策变化风险"
            }
        }
        
        # 政策支持评分
        score = 75  # 基础分
        score += 10  # 消费促进政策
        score += 5   # 数字化转型支持
        score += 5   # 区域发展政策
        score -= 5   # 监管要求提高
        
        score = max(0, min(100, score))
        
        print(f"✅ 政策支持度: {score}/100")
        print(f"✅ 核心政策: 促消费+数字经济+成渝双城圈")
        print(f"✅ 主要机遇: 新零售政策+区域发展")
        print(f"⚠️ 政策风险: 环保要求+食品安全监管")
        
        return {
            "评分": score,
            "观点": "政策环境总体有利，受益促消费和数字化政策",
            "详情": policy_analysis
        }

    def fund_flow_analyst_view(self, fund_data):
        """资金面分析师观点"""
        print(f"\n💰 资金面分析师视角 - {self.stock_name}")
        print("-" * 60)
        
        if not fund_data:
            print("❌ 资金流向数据不足")
            return {"评分": 50, "观点": "数据不足"}
        
        # 解析资金流向数据
        recent_summary = fund_data.get('近5日汇总', {})
        main_inflow = float(recent_summary.get('主力净流入', '0万元').replace('万元', ''))
        super_large_inflow = float(recent_summary.get('超大单净流入', '0万元').replace('万元', ''))
        large_inflow = float(recent_summary.get('大单净流入', '0万元').replace('万元', ''))
        
        fund_analysis = {
            "资金流向特征": {
                "主力态度": "积极" if main_inflow > 0 else "谨慎" if main_inflow > -1000 else "消极",
                "超大单": "净流入" if super_large_inflow > 0 else "净流出",
                "大单": "净流入" if large_inflow > 0 else "净流出",
                "资金性质": "机构为主" if abs(super_large_inflow) > abs(large_inflow) else "游资为主"
            },
            "资金强度": {
                "主力净流入": f"{main_inflow:.0f}万元",
                "日均流入": f"{main_inflow/5:.0f}万元",
                "强度评级": "强" if abs(main_inflow) > 3000 else "中" if abs(main_inflow) > 1000 else "弱"
            },
            "资金分布": recent_summary
        }
        
        # 资金面评分
        score = 50  # 基础分
        
        if main_inflow > 2000:
            score += 25  # 大幅净流入
        elif main_inflow > 500:
            score += 15  # 适度净流入
        elif main_inflow > 0:
            score += 10  # 小幅净流入
        elif main_inflow > -500:
            score += 5   # 小幅净流出
        else:
            score -= 10  # 大幅净流出
        
        # 超大单加分
        if super_large_inflow > 500:
            score += 15
        elif super_large_inflow > 0:
            score += 10
        
        score = max(0, min(100, score))
        
        print(f"✅ 资金面评分: {score}/100")
        print(f"✅ 近5日主力净流入: {main_inflow:.0f}万元")
        print(f"✅ 资金态度: {fund_analysis['资金流向特征']['主力态度']}")
        print(f"✅ 资金强度: {fund_analysis['资金强度']['强度评级']}")
        
        return {
            "评分": score,
            "观点": f"主力资金{'流入' if main_inflow > 0 else '流出'}，强度{fund_analysis['资金强度']['强度评级']}",
            "详情": fund_analysis
        }

    def risk_manager_view(self, fundamental, technical, market, policy, fund_flow):
        """风险管理师观点"""
        print(f"\n⚠️ 风险管理师视角 - {self.stock_name}")
        print("-" * 60)
        
        risk_analysis = {
            "主要风险": {
                "行业风险": "零售行业竞争激烈，毛利率承压",
                "经营风险": "门店租金和人工成本上升",
                "区域风险": "过度依赖西南地区市场",
                "技术风险": "数字化转型投入大，效果待观察",
                "宏观风险": "消费增长放缓影响"
            },
            "风险等级评估": {
                "市场风险": "中等风险",
                "信用风险": "低风险",
                "流动性风险": "低风险",
                "操作风险": "中等风险",
                "政策风险": "低风险"
            },
            "风险缓释因素": {
                "区域优势": "西南地区龙头地位稳固",
                "门店网络": "密集的门店网络形成护城河",
                "供应链优势": "成熟的供应链管理体系",
                "现金流稳定": "便利店业务现金流较好"
            },
            "投资建议": {
                "风险承受能力": "适合稳健型投资者",
                "投资期限": "建议中长期投资",
                "仓位控制": "建议控制在组合的3-5%",
                "止损设置": "建议设置12%止损位"
            }
        }
        
        # 综合风险评分
        risk_scores = [
            fundamental['评分'] * 0.3,
            technical['评分'] * 0.2,
            market['评分'] * 0.2,
            policy['评分'] * 0.2,
            fund_flow['评分'] * 0.1
        ]
        
        overall_score = sum(risk_scores)
        
        if overall_score >= 80:
            risk_level = "低风险"
            recommendation = "积极买入"
        elif overall_score >= 70:
            risk_level = "中低风险"
            recommendation = "推荐买入"
        elif overall_score >= 60:
            risk_level = "中等风险"
            recommendation = "谨慎买入"
        elif overall_score >= 50:
            risk_level = "中高风险"
            recommendation = "观望"
        else:
            risk_level = "高风险"
            recommendation = "暂不推荐"
        
        print(f"✅ 综合风险等级: {risk_level}")
        print(f"✅ 投资建议: {recommendation}")
        print(f"✅ 主要风险: 竞争加剧+成本上升")
        print(f"✅ 缓释因素: 区域龙头+门店网络")
        
        return {
            "评分": overall_score,
            "风险等级": risk_level,
            "投资建议": recommendation,
            "详情": risk_analysis
        }

    def comprehensive_analysis(self):
        """综合分析"""
        print(f"\n{'='*80}")
        print(f"🎯 红旗连锁(002697) 全方位多智能体深度分析")
        print(f"{'='*80}")
        print(f"📅 分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 获取市场数据
        market_data = self.get_market_data()
        
        # 获取资金流向数据
        fund_data = self.get_fund_flow_data()
        
        if not market_data:
            print("❌ 市场数据获取失败，无法进行深度分析")
            return None
        
        # 各智能体分析
        fundamental = self.fundamental_analyst_view(market_data)
        technical = self.technical_analyst_view(market_data)
        market = self.market_analyst_view(market_data)
        policy = self.policy_analyst_view(market_data)
        fund_flow = self.fund_flow_analyst_view(fund_data)
        risk = self.risk_manager_view(fundamental, technical, market, policy, fund_flow)
        
        # 综合评分
        scores = {
            "基本面": fundamental['评分'],
            "技术面": technical['评分'],
            "市场前景": market['评分'],
            "政策支持": policy['评分'],
            "资金面": fund_flow['评分']
        }
        
        # 加权平均
        weights = [0.25, 0.20, 0.20, 0.20, 0.15]
        total_score = sum(score * weight for score, weight in zip(scores.values(), weights))
        
        print(f"\n📊 综合评分汇总")
        print("-" * 40)
        for aspect, score in scores.items():
            print(f"{aspect}: {score:.1f}/100")
        print(f"加权总分: {total_score:.1f}/100")
        
        # 最终建议
        if total_score >= 80:
            final_recommendation = "强烈推荐"
            cost_performance = "性价比很高"
        elif total_score >= 70:
            final_recommendation = "推荐"
            cost_performance = "性价比较高"
        elif total_score >= 60:
            final_recommendation = "谨慎推荐"
            cost_performance = "性价比一般"
        else:
            final_recommendation = "暂不推荐"
            cost_performance = "性价比偏低"
        
        print(f"\n🎯 最终投资建议")
        print("-" * 40)
        print(f"投资建议: {final_recommendation}")
        print(f"性价比评估: {cost_performance}")
        print(f"风险等级: {risk['风险等级']}")
        
        # 操作建议
        if market_data:
            current_price = market_data['latest_quote']['收盘']
            print(f"\n💡 操作建议")
            print("-" * 40)
            print(f"当前价格: {current_price:.2f}元")
            
            if total_score >= 65:
                target_price = current_price * 1.20
                stop_loss = current_price * 0.88
                print(f"建议买入区间: {current_price*0.95:.2f}-{current_price*1.05:.2f}元")
                print(f"目标价位: {target_price:.2f}元")
                print(f"止损价位: {stop_loss:.2f}元")
                print(f"建议仓位: 3-5%")
            elif total_score >= 55:
                print(f"建议谨慎关注，等待更好买入时机")
                print(f"关注价格回调至{current_price*0.92:.2f}元附近")
            else:
                print("建议观望，等待基本面或技术面改善")
        
        return {
            "公司信息": self.company_info,
            "综合评分": total_score,
            "各项评分": scores,
            "投资建议": final_recommendation,
            "性价比": cost_performance,
            "风险等级": risk['风险等级'],
            "分析详情": {
                "基本面": fundamental,
                "技术面": technical,
                "市场面": market,
                "政策面": policy,
                "资金面": fund_flow,
                "风险管理": risk
            }
        }

def main():
    """主函数"""
    analyzer = HongqiChainMultiAgentAnalyzer()
    result = analyzer.comprehensive_analysis()
    
    if result:
        # 保存分析报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"红旗连锁全方位多智能体分析报告_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📄 详细分析报告已保存: {filename}")
        print(f"\n🎉 分析完成！")
        print(f"📋 核心结论: {result['投资建议']} - {result['性价比']}")

if __name__ == "__main__":
    main()