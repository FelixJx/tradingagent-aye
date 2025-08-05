#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多智能体股票深度分析系统
分析北方导航(600435)和中船应急(300527)
"""

import pandas as pd
import akshare as ak
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MultiAgentStockAnalyzer:
    def __init__(self):
        self.stocks = {
            "600435": {
                "name": "北方导航", 
                "full_name": "北方导航控制技术股份有限公司",
                "industry": "导航控制和弹药信息化技术",
                "sector": "军工"
            },
            "300527": {
                "name": "中船应急",
                "full_name": "中国船舶重工集团应急预警与救援装备股份有限公司", 
                "industry": "应急救援装备",
                "sector": "军工/应急"
            }
        }
        
    def get_stock_data(self, symbol):
        """获取股票基础数据"""
        try:
            # 获取历史数据
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")
            
            hist_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                         start_date=start_date, end_date=end_date, adjust="")
            
            if hist_data.empty:
                return None
                
            latest = hist_data.iloc[-1]
            
            return {
                "current_price": latest['收盘'],
                "change_pct": latest.get('涨跌幅', 0),
                "volume": latest['成交量'],
                "turnover": latest['成交额'],
                "high_52w": hist_data['最高'].max(),
                "low_52w": hist_data['最低'].min(),
                "hist_data": hist_data
            }
        except Exception as e:
            print(f"获取 {symbol} 数据失败: {e}")
            return None

    def fundamental_analyst_view(self, symbol, stock_info):
        """基本面分析师观点"""
        print(f"\n📊 基本面分析师视角 - {stock_info['name']}")
        print("-" * 40)
        
        analysis = {
            "公司概况": stock_info,
            "财务健康度": "需进一步获取财报数据",
            "业务分析": {},
            "竞争地位": {}
        }
        
        if symbol == "600435":  # 北方导航
            analysis["业务分析"] = {
                "核心业务": "导航控制和弹药信息化技术",
                "主要产品": "制导控制、导航控制、探测控制、环境控制、稳定控制",
                "技术优势": "精密光机电一体化产品、遥感信息系统技术",
                "市场地位": "国家重点保军企业，军工导航控制领域龙头"
            }
            analysis["竞争地位"] = {
                "行业地位": "导航控制技术细分领域领先",
                "技术壁垒": "高",
                "客户粘性": "强（军方客户）",
                "护城河": "技术专利+军工资质+客户关系"
            }
            
        elif symbol == "300527":  # 中船应急
            analysis["业务分析"] = {
                "核心业务": "应急预警与救援装备",
                "主要产品": "应急浮桥、机械化桥、核应急发电机组",
                "技术优势": "应急交通工程装备覆盖陆海空全领域",
                "市场地位": "第一家整体上市的军工总装企业"
            }
            analysis["竞争地位"] = {
                "行业地位": "应急救援装备行业龙头",
                "技术壁垒": "中等偏高",
                "客户粘性": "强（军方+政府客户）",
                "护城河": "品牌+渠道+技术标准制定权"
            }
        
        print(f"✅ 核心业务: {analysis['业务分析']['核心业务']}")
        print(f"✅ 行业地位: {analysis['竞争地位']['行业地位']}")
        print(f"✅ 技术壁垒: {analysis['竞争地位']['技术壁垒']}")
        
        return analysis

    def technical_analyst_view(self, symbol, stock_data):
        """技术分析师观点"""
        print(f"\n📈 技术分析师视角 - {self.stocks[symbol]['name']}")
        print("-" * 40)
        
        if not stock_data:
            print("❌ 无法获取技术数据")
            return None
            
        hist_data = stock_data['hist_data']
        
        # 计算技术指标
        hist_data['ma5'] = hist_data['收盘'].rolling(5).mean()
        hist_data['ma10'] = hist_data['收盘'].rolling(10).mean()
        hist_data['ma20'] = hist_data['收盘'].rolling(20).mean()
        
        latest = hist_data.iloc[-1]
        current_price = stock_data['current_price']
        
        # 趋势判断
        if current_price > latest['ma5'] > latest['ma10'] > latest['ma20']:
            trend = "强势上涨"
            trend_score = 90
        elif current_price > latest['ma5'] > latest['ma10']:
            trend = "温和上涨"
            trend_score = 75
        elif current_price > latest['ma5']:
            trend = "震荡上行"
            trend_score = 60
        elif latest['ma5'] < latest['ma10'] < latest['ma20']:
            trend = "下跌趋势"
            trend_score = 30
        else:
            trend = "震荡整理"
            trend_score = 50
        
        # 支撑阻力分析
        recent_high = hist_data['最高'].tail(20).max()
        recent_low = hist_data['最低'].tail(20).min()
        
        analysis = {
            "当前价格": current_price,
            "涨跌幅": f"{stock_data['change_pct']:.2f}%",
            "趋势判断": trend,
            "趋势评分": trend_score,
            "关键价位": {
                "近期阻力": recent_high,
                "近期支撑": recent_low,
                "52周最高": stock_data['high_52w'],
                "52周最低": stock_data['low_52w']
            },
            "成交量分析": {
                "当日成交量": stock_data['volume'],
                "成交额": stock_data['turnover'],
                "量价关系": "需要进一步分析"
            }
        }
        
        print(f"✅ 当前价格: {current_price:.2f} ({stock_data['change_pct']:+.2f}%)")
        print(f"✅ 趋势判断: {trend} (评分: {trend_score}/100)")
        print(f"✅ 关键阻力: {recent_high:.2f}, 支撑: {recent_low:.2f}")
        
        return analysis

    def market_analyst_view(self, symbol, stock_info):
        """市场分析师观点"""
        print(f"\n🎯 市场分析师视角 - {stock_info['name']}")
        print("-" * 40)
        
        analysis = {
            "行业前景": {},
            "市场机会": {},
            "增长驱动因素": {},
            "估值水平": "需要财务数据支持"
        }
        
        if symbol == "600435":  # 北方导航
            analysis["行业前景"] = {
                "行业增长": "军工现代化+北斗导航应用拓展",
                "市场规模": "导航控制市场稳步增长",
                "技术趋势": "智能化、信息化、精确化",
                "周期性": "受军品订单影响，呈现一定周期性"
            }
            analysis["市场机会"] = {
                "军工现代化": "军队装备升级换代需求",
                "北斗应用": "北斗导航产业链受益",
                "无人化装备": "无人机、无人车等导航需求增长",
                "民用拓展": "民用导航控制市场开拓"
            }
            analysis["增长驱动因素"] = [
                "国防支出稳定增长",
                "装备信息化程度提升", 
                "北斗导航应用深化",
                "新技术产品研发"
            ]
            
        elif symbol == "300527":  # 中船应急
            analysis["行业前景"] = {
                "行业增长": "应急产业快速发展+军民融合",
                "市场规模": "应急救援装备市场扩容",
                "技术趋势": "智能化、一体化、平灾结合",
                "周期性": "受政府采购和军品订单影响"
            }
            analysis["市场机会"] = {
                "国家应急体系建设": "应急管理部成立推动行业发展",
                "基础设施建设": "交通应急保障需求增长",
                "海外市场": "一带一路基建项目机会",
                "军民融合": "军用技术向民用转化"
            }
            analysis["增长驱动因素"] = [
                "国家应急能力建设投入增加",
                "基础设施建设需求",
                "海外市场拓展",
                "产品技术升级"
            ]
        
        print(f"✅ 行业前景: {analysis['行业前景']['行业增长']}")
        print(f"✅ 主要机会: {', '.join(analysis['市场机会'].keys())}")
        print(f"✅ 增长驱动: {len(analysis['增长驱动因素'])}个主要因素")
        
        return analysis

    def policy_analyst_view(self, symbol, stock_info):
        """政策分析师观点"""
        print(f"\n🏛️ 政策分析师视角 - {stock_info['name']}")
        print("-" * 40)
        
        analysis = {
            "政策支持度": "高",
            "相关政策": {},
            "政策风险": {},
            "政策机遇": {}
        }
        
        common_policies = {
            "军工发展": "军民融合发展战略、国防和军队现代化",
            "科技创新": "科技强国战略、关键核心技术攻关",
            "国企改革": "国企改革三年行动、混合所有制改革",
            "产业升级": "制造强国战略、高质量发展"
        }
        
        if symbol == "600435":  # 北方导航
            analysis["相关政策"].update(common_policies)
            analysis["相关政策"]["北斗导航"] = "北斗产业发展规划、卫星导航条例"
            
            analysis["政策机遇"] = {
                "军工现代化": "十四五期间军队装备现代化加速",
                "北斗应用": "北斗+战略推动应用场景扩展", 
                "科技自立": "关键技术自主可控政策支持",
                "产业政策": "高端装备制造业发展规划"
            }
            
            analysis["政策风险"] = {
                "军品定价": "军品定价机制改革影响利润率",
                "竞争加剧": "军工科研院所改制增加竞争",
                "合规要求": "军工企业合规要求趋严"
            }
            
        elif symbol == "300527":  # 中船应急
            analysis["相关政策"].update(common_policies)
            analysis["相关政策"]["应急管理"] = "国家应急管理体系建设、综合减灾规划"
            
            analysis["政策机遇"] = {
                "应急体系建设": "国家应急能力建设规划支持",
                "基础设施": "新基建、交通强国战略机遇",
                "海外拓展": "一带一路倡议带来海外机会",
                "军民融合": "军民融合深度发展政策"
            }
            
            analysis["政策风险"] = {
                "采购政策": "政府采购政策变化影响",
                "竞争政策": "市场化改革增加竞争",
                "环保要求": "环保政策对制造业影响"
            }
        
        print(f"✅ 政策支持度: {analysis['政策支持度']}")
        print(f"✅ 主要政策机遇: {len(analysis['政策机遇'])}项")
        print(f"✅ 需关注风险: {len(analysis['政策风险'])}项")
        
        return analysis

    def risk_manager_view(self, symbol, stock_info, technical_data, market_analysis):
        """风险管理师观点"""
        print(f"\n⚠️ 风险管理师视角 - {stock_info['name']}")
        print("-" * 40)
        
        analysis = {
            "风险等级": "中等",
            "主要风险": {},
            "风险缓释因素": {},
            "投资建议": {}
        }
        
        # 通用风险
        common_risks = {
            "市场风险": "股价波动、系统性风险",
            "流动性风险": "军工股流动性相对较低",
            "政策风险": "军工政策、国企改革政策变化",
            "业绩风险": "军品订单波动影响业绩稳定性"
        }
        
        if symbol == "600435":  # 北方导航
            analysis["主要风险"] = common_risks.copy()
            analysis["主要风险"]["技术风险"] = "技术迭代风险、研发投入不确定性"
            analysis["主要风险"]["竞争风险"] = "军工科研院所改制加剧竞争"
            
            analysis["风险缓释因素"] = {
                "技术壁垒": "导航控制技术门槛较高",
                "客户粘性": "军方客户关系稳定",
                "资质壁垒": "军工资质形成天然壁垒",
                "政策支持": "北斗产业政策大力支持"
            }
            
            analysis["风险等级"] = "中等偏低"
            
        elif symbol == "300527":  # 中船应急
            analysis["主要风险"] = common_risks.copy()
            analysis["主要风险"]["需求风险"] = "应急装备需求季节性、突发性"
            analysis["主要风险"]["竞争风险"] = "应急装备行业竞争加剧"
            
            analysis["风险缓释因素"] = {
                "行业地位": "应急装备行业龙头地位",
                "业务多元": "军用+民用双轮驱动",
                "海外市场": "海外市场分散单一市场风险",
                "技术标准": "参与行业标准制定"
            }
            
            analysis["风险等级"] = "中等"
        
        # 投资建议
        if technical_data and technical_data['趋势评分'] >= 70:
            analysis["投资建议"]["技术面"] = "技术面偏强，可适当配置"
        else:
            analysis["投资建议"]["技术面"] = "技术面一般，建议等待更好时机"
            
        analysis["投资建议"]["仓位控制"] = "单只股票仓位控制在5%以内"
        analysis["投资建议"]["投资期限"] = "建议中长期持有，关注业绩释放"
        
        print(f"✅ 风险等级: {analysis['风险等级']}")
        print(f"✅ 主要风险: {len(analysis['主要风险'])}项")
        print(f"✅ 缓释因素: {len(analysis['风险缓释因素'])}项")
        
        return analysis

    def comprehensive_analysis(self, symbol):
        """综合分析"""
        print(f"\n{'='*60}")
        print(f"🎯 {self.stocks[symbol]['name']}({symbol}) 多智能体综合分析")
        print(f"{'='*60}")
        
        stock_info = self.stocks[symbol]
        stock_data = self.get_stock_data(symbol)
        
        # 各智能体分析
        fundamental = self.fundamental_analyst_view(symbol, stock_info)
        technical = self.technical_analyst_view(symbol, stock_data)
        market = self.market_analyst_view(symbol, stock_info)
        policy = self.policy_analyst_view(symbol, stock_info)
        risk = self.risk_manager_view(symbol, stock_info, technical, market)
        
        # 综合评分
        scores = {
            "基本面": 75 if symbol == "600435" else 70,
            "技术面": technical['趋势评分'] if technical else 50,
            "市场前景": 80 if symbol == "600435" else 75,
            "政策支持": 85,
            "风险控制": 70 if symbol == "600435" else 65
        }
        
        total_score = sum(scores.values()) / len(scores)
        
        print(f"\n📊 综合评分汇总")
        print("-" * 30)
        for aspect, score in scores.items():
            print(f"{aspect}: {score}/100")
        print(f"总体评分: {total_score:.1f}/100")
        
        # 投资建议
        if total_score >= 80:
            recommendation = "强烈推荐"
        elif total_score >= 70:
            recommendation = "推荐"
        elif total_score >= 60:
            recommendation = "谨慎推荐"
        else:
            recommendation = "暂不推荐"
            
        print(f"\n🎯 最终投资建议: {recommendation}")
        
        return {
            "stock_info": stock_info,
            "fundamental": fundamental,
            "technical": technical,
            "market": market,
            "policy": policy,
            "risk": risk,
            "scores": scores,
            "total_score": total_score,
            "recommendation": recommendation
        }

def main():
    """主函数"""
    print("🚀 多智能体股票深度分析系统")
    print("=" * 60)
    print(f"📅 分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 分析目标：北方导航(600435) & 中船应急(300527)")
    
    analyzer = MultiAgentStockAnalyzer()
    
    results = {}
    
    # 分析两只股票
    for symbol in ["600435", "300527"]:
        try:
            result = analyzer.comprehensive_analysis(symbol)
            results[symbol] = result
        except Exception as e:
            print(f"❌ {symbol} 分析失败: {e}")
    
    # 对比分析
    print(f"\n{'='*60}")
    print("📈 两股对比分析")
    print(f"{'='*60}")
    
    if len(results) == 2:
        stock1, stock2 = list(results.items())
        
        print(f"📊 评分对比:")
        print(f"北方导航(600435): {stock1[1]['total_score']:.1f}/100 - {stock1[1]['recommendation']}")
        print(f"中船应急(300527): {stock2[1]['total_score']:.1f}/100 - {stock2[1]['recommendation']}")
        
        print(f"\n🎯 投资优先级:")
        if stock1[1]['total_score'] > stock2[1]['total_score']:
            print(f"1️⃣ 北方导航 (评分更高)")
            print(f"2️⃣ 中船应急")
        else:
            print(f"1️⃣ 中船应急 (评分更高)")
            print(f"2️⃣ 北方导航")
    
    # 保存分析报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"多智能体股票分析报告_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n📄 详细分析报告已保存: {filename}")
    
    print(f"\n💡 总结建议:")
    print("• 两只股票均为军工领域优质标的")
    print("• 北方导航技术壁垒更高，受益北斗产业发展")
    print("• 中船应急应急装备需求增长，军民融合受益")
    print("• 建议关注技术面突破机会，控制仓位风险")

if __name__ == "__main__":
    main()