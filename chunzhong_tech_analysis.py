#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淳中科技(603516.SH)实时数据分析系统
包含实时行情、新闻分析、技术指标和基本面评估
"""

import json
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

class ChunzhongTechAnalyzer:
    """淳中科技专业分析器"""
    
    def __init__(self):
        self.stock_code = "603516"
        self.stock_name = "淳中科技"
        self.market = "SH"
        self.full_code = "sh603516"
        self.analysis_time = datetime.now()
        
    def get_realtime_data(self):
        """获取实时股票数据"""
        print("\n" + "="*60)
        print(f"📊 {self.stock_name}({self.stock_code}) 实时数据分析")
        print(f"⏰ 分析时间: {self.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
        try:
            # 获取实时行情
            stock_zh_a_spot_df = ak.stock_zh_a_spot_em()
            stock_info = stock_zh_a_spot_df[stock_zh_a_spot_df['代码'] == self.stock_code]
            
            if not stock_info.empty:
                info = stock_info.iloc[0]
                realtime_data = {
                    "最新价": float(info['最新价']),
                    "涨跌幅": float(info['涨跌幅']),
                    "涨跌额": float(info['涨跌额']),
                    "成交量": float(info['成交量']),
                    "成交额": float(info['成交额']),
                    "振幅": float(info['振幅']),
                    "最高": float(info['最高']),
                    "最低": float(info['最低']),
                    "今开": float(info['今开']),
                    "昨收": float(info['昨收']),
                    "量比": float(info['量比']) if '量比' in info else 0,
                    "换手率": float(info['换手率']),
                    "市盈率-动态": float(info['市盈率-动态']) if info['市盈率-动态'] != '-' else 0,
                    "市净率": float(info['市净率']) if info['市净率'] != '-' else 0,
                }
                
                print("📈 实时行情数据:")
                print(f"   最新价: {realtime_data['最新价']} 元")
                print(f"   涨跌幅: {realtime_data['涨跌幅']}%")
                print(f"   成交额: {realtime_data['成交额']/100000000:.2f} 亿元")
                print(f"   换手率: {realtime_data['换手率']}%")
                print(f"   市盈率: {realtime_data['市盈率-动态']}")
                
                return realtime_data
            else:
                print("⚠️ 未找到实时行情数据")
                return None
                
        except Exception as e:
            print(f"❌ 获取实时数据失败: {str(e)}")
            return None
            
    def get_company_info(self):
        """获取公司基本信息"""
        try:
            # 获取公司简介
            print("\n📋 公司基本信息:")
            
            # 获取个股信息
            stock_individual_info_em_df = ak.stock_individual_info_em(symbol=self.stock_code)
            
            company_info = {
                "公司名称": "北京淳中科技股份有限公司",
                "所属行业": "计算机、通信和其他电子设备制造业",
                "主营业务": "显示控制产品及解决方案的研发、生产和销售",
                "产品类型": "图像处理器、矩阵切换器、多屏处理器等",
                "上市日期": stock_individual_info_em_df[stock_individual_info_em_df['item'] == '上市时间']['value'].values[0] if '上市时间' in stock_individual_info_em_df['item'].values else "2017-12-22",
                "总股本": stock_individual_info_em_df[stock_individual_info_em_df['item'] == '总股本']['value'].values[0] if '总股本' in stock_individual_info_em_df['item'].values else "-",
                "流通股本": stock_individual_info_em_df[stock_individual_info_em_df['item'] == '流通股本']['value'].values[0] if '流通股本' in stock_individual_info_em_df['item'].values else "-",
            }
            
            print(f"   公司名称: {company_info['公司名称']}")
            print(f"   所属行业: {company_info['所属行业']}")
            print(f"   主营业务: {company_info['主营业务']}")
            print(f"   上市日期: {company_info['上市日期']}")
            
            return company_info
            
        except Exception as e:
            print(f"❌ 获取公司信息失败: {str(e)}")
            return None
            
    def get_financial_indicators(self):
        """获取财务指标"""
        try:
            print("\n💰 财务指标分析:")
            
            # 获取财务指标
            stock_financial_analysis_indicator_df = ak.stock_financial_analysis_indicator(
                symbol=self.stock_code, 
                start_year="2024"
            )
            
            if not stock_financial_analysis_indicator_df.empty:
                latest_finance = stock_financial_analysis_indicator_df.iloc[0]
                
                financial_data = {
                    "净资产收益率": latest_finance.get('净资产收益率(%)', 0),
                    "销售毛利率": latest_finance.get('销售毛利率(%)', 0),
                    "资产负债率": latest_finance.get('资产负债率(%)', 0),
                    "流动比率": latest_finance.get('流动比率', 0),
                    "总资产周转率": latest_finance.get('总资产周转率(次)', 0),
                }
                
                print(f"   净资产收益率: {financial_data['净资产收益率']}%")
                print(f"   销售毛利率: {financial_data['销售毛利率']}%")
                print(f"   资产负债率: {financial_data['资产负债率']}%")
                
                return financial_data
            else:
                print("   暂无最新财务数据")
                return None
                
        except Exception as e:
            print(f"❌ 获取财务指标失败: {str(e)}")
            return None
            
    def get_technical_indicators(self):
        """计算技术指标"""
        try:
            print("\n📊 技术指标分析:")
            
            # 获取历史数据
            stock_zh_a_hist_df = ak.stock_zh_a_hist(
                symbol=self.stock_code,
                period="daily",
                start_date=(datetime.now() - timedelta(days=100)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d"),
                adjust="qfq"
            )
            
            if not stock_zh_a_hist_df.empty:
                # 计算移动平均线
                stock_zh_a_hist_df['MA5'] = stock_zh_a_hist_df['收盘'].rolling(window=5).mean()
                stock_zh_a_hist_df['MA10'] = stock_zh_a_hist_df['收盘'].rolling(window=10).mean()
                stock_zh_a_hist_df['MA20'] = stock_zh_a_hist_df['收盘'].rolling(window=20).mean()
                stock_zh_a_hist_df['MA60'] = stock_zh_a_hist_df['收盘'].rolling(window=60).mean()
                
                # 计算RSI
                delta = stock_zh_a_hist_df['收盘'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                stock_zh_a_hist_df['RSI'] = 100 - (100 / (1 + rs))
                
                # 获取最新值
                latest = stock_zh_a_hist_df.iloc[-1]
                
                technical_data = {
                    "MA5": round(latest['MA5'], 2),
                    "MA10": round(latest['MA10'], 2),
                    "MA20": round(latest['MA20'], 2),
                    "MA60": round(latest['MA60'], 2) if not pd.isna(latest['MA60']) else 0,
                    "RSI": round(latest['RSI'], 2),
                    "收盘价": latest['收盘'],
                    "成交量": latest['成交量'],
                }
                
                print(f"   MA5: {technical_data['MA5']}")
                print(f"   MA20: {technical_data['MA20']}")
                print(f"   RSI(14): {technical_data['RSI']}")
                
                # 趋势判断
                if technical_data['收盘价'] > technical_data['MA5'] > technical_data['MA20']:
                    print("   📈 技术面: 上升趋势")
                elif technical_data['收盘价'] < technical_data['MA5'] < technical_data['MA20']:
                    print("   📉 技术面: 下降趋势")
                else:
                    print("   ➡️ 技术面: 震荡整理")
                    
                return technical_data
            else:
                print("   暂无历史数据")
                return None
                
        except Exception as e:
            print(f"❌ 获取技术指标失败: {str(e)}")
            return None
            
    def get_latest_news(self):
        """获取最新新闻和公告"""
        try:
            print("\n📰 最新资讯分析:")
            
            # 获取个股新闻
            stock_news_em_df = ak.stock_news_em(symbol=self.stock_code)
            
            if not stock_news_em_df.empty:
                # 显示最新5条新闻
                news_list = []
                for idx, row in stock_news_em_df.head(5).iterrows():
                    news_item = {
                        "标题": row['新闻标题'],
                        "时间": row['发布时间'],
                        "来源": row['新闻来源'],
                    }
                    news_list.append(news_item)
                    print(f"   [{idx+1}] {news_item['标题'][:40]}...")
                    print(f"       时间: {news_item['时间']} | 来源: {news_item['来源']}")
                    
                return news_list
            else:
                print("   暂无最新新闻")
                return []
                
        except Exception as e:
            print(f"❌ 获取新闻失败: {str(e)}")
            return []
            
    def analyze_investment_value(self):
        """综合投资价值分析"""
        print("\n🎯 投资价值综合评估:")
        
        # 获取各项数据
        realtime_data = self.get_realtime_data()
        company_info = self.get_company_info()
        financial_data = self.get_financial_indicators()
        technical_data = self.get_technical_indicators()
        news_list = self.get_latest_news()
        
        # 综合评分
        score = 50  # 基础分
        
        if realtime_data:
            # 估值评分
            if realtime_data['市盈率-动态'] > 0 and realtime_data['市盈率-动态'] < 30:
                score += 10
            elif realtime_data['市盈率-动态'] > 50:
                score -= 10
                
            # 成交活跃度
            if realtime_data['换手率'] > 3:
                score += 5
                
            # 涨跌幅
            if realtime_data['涨跌幅'] > 0:
                score += 5
            elif realtime_data['涨跌幅'] < -3:
                score -= 10
                
        if technical_data:
            # 技术面评分
            if technical_data['收盘价'] > technical_data['MA20']:
                score += 10
            if technical_data['RSI'] > 30 and technical_data['RSI'] < 70:
                score += 5
                
        if financial_data:
            # 财务面评分
            if financial_data['净资产收益率'] > 10:
                score += 10
            if financial_data['资产负债率'] < 60:
                score += 5
                
        # 输出综合评估
        print(f"\n   综合评分: {score}/100")
        
        if score >= 80:
            rating = "强烈推荐"
            suggestion = "该股票具有较高投资价值，建议积极关注"
        elif score >= 60:
            rating = "谨慎推荐"
            suggestion = "该股票具有一定投资价值，但需注意风险"
        elif score >= 40:
            rating = "中性观望"
            suggestion = "该股票表现一般，建议继续观察"
        else:
            rating = "暂不推荐"
            suggestion = "该股票存在一定风险，建议谨慎对待"
            
        print(f"   投资评级: {rating}")
        print(f"   投资建议: {suggestion}")
        
        # 风险提示
        print("\n⚠️ 风险提示:")
        print("   1. 科技股波动较大，需注意市场风险")
        print("   2. 关注公司订单和业绩兑现情况")
        print("   3. 留意行业政策变化和技术迭代风险")
        
        # 生成分析报告
        report = {
            "股票代码": self.stock_code,
            "股票名称": self.stock_name,
            "分析时间": self.analysis_time.strftime('%Y-%m-%d %H:%M:%S'),
            "实时数据": realtime_data,
            "公司信息": company_info,
            "财务指标": financial_data,
            "技术指标": technical_data,
            "最新资讯": news_list[:3] if news_list else [],
            "综合评分": score,
            "投资评级": rating,
            "投资建议": suggestion,
        }
        
        # 保存报告
        report_filename = f"{self.stock_name}_实时分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        print(f"\n📄 分析报告已保存: {report_filename}")
        
        return report

def main():
    """主函数"""
    analyzer = ChunzhongTechAnalyzer()
    report = analyzer.analyze_investment_value()
    
    print("\n" + "="*60)
    print("分析完成！")
    print("="*60)

if __name__ == "__main__":
    main()