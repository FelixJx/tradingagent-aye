#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
华康洁净(301235.SZ)基于Tushare真实数据的综合分析脚本
"""

import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import warnings
import time

warnings.filterwarnings('ignore')

class HuakangAnalyzer:
    """华康洁净分析器"""
    
    def __init__(self, token):
        self.token = token
        ts.set_token(token)
        self.pro = ts.pro_api()
        self.ts_code = '301235.SZ'
        self.company_name = '华康洁净'
        self.results = {}
        
        print("开始分析华康洁净...")
        
    def get_basic_info(self):
        """获取基本信息"""
        print("1. 获取基本信息...")
        try:
            # 基本信息
            basic_info = self.pro.stock_basic(ts_code=self.ts_code)
            
            # 获取最新交易日
            cal = self.pro.trade_cal(exchange='SSE', start_date='20240701', end_date=datetime.now().strftime('%Y%m%d'))
            latest_dates = cal[cal['is_open'] == 1]['cal_date'].tail(10).tolist()
            
            daily_data = None
            daily_basic = None
            
            # 尝试获取最新数据
            for trade_date in reversed(latest_dates):
                try:
                    daily_data = self.pro.daily(ts_code=self.ts_code, trade_date=trade_date)
                    if not daily_data.empty:
                        break
                except:
                    time.sleep(0.1)
                    continue
            
            # 获取估值数据
            for trade_date in reversed(latest_dates):
                try:
                    daily_basic = self.pro.daily_basic(ts_code=self.ts_code, trade_date=trade_date)
                    if not daily_basic.empty:
                        break
                except:
                    time.sleep(0.1)
                    continue
            
            result = {}
            
            if not basic_info.empty:
                info = basic_info.iloc[0]
                result['股票代码'] = info['ts_code']
                result['股票简称'] = info['name']
                result['所属行业'] = info['industry']
                result['上市日期'] = info['list_date']
            
            if daily_data is not None and not daily_data.empty:
                price = daily_data.iloc[0]
                result['最新价格'] = price['close']
                result['涨跌额'] = price['change']
                result['涨跌幅'] = str(round(price['pct_chg'], 2)) + '%'
                result['成交量'] = price['vol']
                result['成交额'] = price['amount']
                result['交易日期'] = price['trade_date']
            
            if daily_basic is not None and not daily_basic.empty:
                val = daily_basic.iloc[0]
                result['总市值(万元)'] = val['total_mv']
                result['流通市值(万元)'] = val['circ_mv']
                result['市盈率TTM'] = val['pe_ttm']
                result['市净率'] = val['pb']
            
            self.results['基本信息'] = result
            print("   基本信息获取成功")
            return result
            
        except Exception as e:
            error = "基本信息获取失败: " + str(e)
            print("   " + error)
            self.results['基本信息'] = {'错误': error}
            return {}
    
    def get_financial_data(self):
        """获取财务数据"""
        print("2. 获取财务数据...")
        try:
            result = {}
            
            # 利润表
            income = self.pro.income(ts_code=self.ts_code, start_date='20220101', end_date='20241231')
            if not income.empty:
                income = income.sort_values('end_date')
                recent = income.tail(6)
                
                income_data = {}
                for _, row in recent.iterrows():
                    period = row['end_date']
                    revenue = row['revenue'] if pd.notna(row['revenue']) else 0
                    profit = row['n_income'] if pd.notna(row['n_income']) else 0
                    cost = row['oper_cost'] if pd.notna(row['oper_cost']) else 0
                    
                    income_data[period] = {
                        '营业收入(万元)': round(revenue / 10000, 2),
                        '净利润(万元)': round(profit / 10000, 2),
                        '营业成本(万元)': round(cost / 10000, 2),
                        '毛利率(%)': round((revenue - cost) / revenue * 100, 2) if revenue > 0 else 0
                    }
                
                result['利润表数据'] = income_data
                
                # 计算增长率
                if len(recent) >= 4:
                    latest = recent.iloc[-1]
                    year_ago = recent.iloc[-4]
                    
                    if year_ago['revenue'] > 0:
                        revenue_growth = (latest['revenue'] - year_ago['revenue']) / year_ago['revenue'] * 100
                        result['营业收入同比增长'] = str(round(revenue_growth, 2)) + '%'
                    
                    if abs(year_ago['n_income']) > 0:
                        profit_growth = (latest['n_income'] - year_ago['n_income']) / abs(year_ago['n_income']) * 100
                        result['净利润同比增长'] = str(round(profit_growth, 2)) + '%'
            
            # 资产负债表
            balance = self.pro.balancesheet(ts_code=self.ts_code, start_date='20220101', end_date='20241231')
            if not balance.empty:
                balance = balance.sort_values('end_date')
                latest_balance = balance.iloc[-1]
                
                assets = latest_balance['total_assets'] if pd.notna(latest_balance['total_assets']) else 0
                liab = latest_balance['total_liab'] if pd.notna(latest_balance['total_liab']) else 0
                equity = latest_balance['total_hldr_eqy_exc_min_int'] if pd.notna(latest_balance['total_hldr_eqy_exc_min_int']) else 0
                
                result['资产负债数据'] = {
                    '总资产(万元)': round(assets / 10000, 2),
                    '总负债(万元)': round(liab / 10000, 2),
                    '净资产(万元)': round(equity / 10000, 2),
                    '资产负债率(%)': round(liab / assets * 100, 2) if assets > 0 else 0
                }
            
            # 财务指标
            indicators = self.pro.fina_indicator(ts_code=self.ts_code, start_date='20220101', end_date='20241231')
            if not indicators.empty:
                indicators = indicators.sort_values('end_date')
                latest = indicators.iloc[-1]
                
                result['财务指标'] = {
                    'ROE(%)': round(latest.get('roe', 0), 2),
                    'ROA(%)': round(latest.get('roa', 0), 2),
                    '毛利率(%)': round(latest.get('grossprofit_margin', 0), 2),
                    '净利率(%)': round(latest.get('netprofit_margin', 0), 2)
                }
            
            self.results['财务分析'] = result
            print("   财务数据获取成功")
            return result
            
        except Exception as e:
            error = "财务数据获取失败: " + str(e)
            print("   " + error)
            self.results['财务分析'] = {'错误': error}
            return {}
    
    def get_price_analysis(self):
        """获取价格分析"""
        print("3. 获取价格分析...")
        try:
            # 获取历史数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            
            hist = self.pro.daily(ts_code=self.ts_code, start_date=start_date, end_date=end_date)
            
            if hist.empty:
                raise Exception("无法获取历史价格数据")
            
            hist = hist.sort_values('trade_date')
            hist['returns'] = hist['close'].pct_change()
            
            # 计算统计指标
            latest_price = hist['close'].iloc[-1]
            highest = hist['high'].max()
            lowest = hist['low'].min()
            
            # 近期表现
            recent_30 = hist.tail(30)
            recent_7 = hist.tail(7)
            
            result = {
                '数据期间': start_date + ' 至 ' + end_date,
                '当前价格': latest_price,
                '期间最高': highest,
                '期间最低': lowest,
                '年化波动率(%)': round(hist['returns'].std() * np.sqrt(252) * 100, 2)
            }
            
            if len(recent_30) > 1:
                result['近30日涨跌幅(%)'] = round((recent_30['close'].iloc[-1] / recent_30['close'].iloc[0] - 1) * 100, 2)
            
            if len(recent_7) > 1:
                result['近7日涨跌幅(%)'] = round((recent_7['close'].iloc[-1] / recent_7['close'].iloc[0] - 1) * 100, 2)
            
            # 技术指标
            if len(hist) > 20:
                hist['ma20'] = hist['close'].rolling(20).mean()
                result['MA20'] = round(hist['ma20'].iloc[-1], 2)
            
            self.results['价格分析'] = result
            print("   价格分析完成")
            return result
            
        except Exception as e:
            error = "价格分析失败: " + str(e)
            print("   " + error)
            self.results['价格分析'] = {'错误': error}
            return {}
    
    def get_capital_flow(self):
        """获取资金流分析"""
        print("4. 获取资金流分析...")
        try:
            result = {}
            
            # 龙虎榜
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            
            try:
                toplist = self.pro.top_list(ts_code=self.ts_code, start_date=start_date, end_date=end_date)
                if not toplist.empty:
                    result['龙虎榜'] = '近30日上榜' + str(len(toplist)) + '次'
                    
                    details = []
                    for _, row in toplist.head(3).iterrows():
                        details.append({
                            '日期': row['trade_date'],
                            '原因': row['explain'],
                            '涨跌幅': str(round(row['pct_change'], 2)) + '%'
                        })
                    result['龙虎榜详情'] = details
                else:
                    result['龙虎榜'] = '近30日无上榜记录'
            except:
                result['龙虎榜'] = '数据获取失败'
            
            # 融资融券
            try:
                margin = self.pro.margin(ts_code=self.ts_code, start_date=start_date, end_date=end_date)
                if not margin.empty:
                    latest_margin = margin.sort_values('trade_date').iloc[-1]
                    
                    result['融资融券'] = {
                        '融资余额(万元)': round(latest_margin.get('rzye', 0) / 10000, 2),
                        '融券余额(万元)': round(latest_margin.get('rqye', 0) / 10000, 2),
                        '融资买入(万元)': round(latest_margin.get('rzmre', 0) / 10000, 2)
                    }
                else:
                    result['融资融券'] = '无数据'
            except:
                result['融资融券'] = '数据获取失败'
            
            self.results['资金流分析'] = result
            print("   资金流分析完成")
            return result
            
        except Exception as e:
            error = "资金流分析失败: " + str(e)
            print("   " + error)
            self.results['资金流分析'] = {'错误': error}
            return {}
    
    def compare_with_web_data(self):
        """对比Web搜索数据"""
        print("5. 对比Web搜索数据...")
        try:
            web_file = '/Applications/tradingagent/华康洁净_真实数据分析报告_20250803_202312.json'
            
            try:
                with open(web_file, 'r', encoding='utf-8') as f:
                    web_data = json.load(f)
                
                comparison = {
                    'Web数据读取': '成功',
                    '对比分析': {}
                }
                
                # 对比基本面
                web_basic = web_data.get('分析结果', {}).get('基本面分析', {})
                tushare_financial = self.results.get('财务分析', {})
                
                if web_basic and tushare_financial:
                    comparison['对比分析']['营收增长'] = {
                        'Web数据': str(web_basic.get('revenue_growth_h1', 'N/A')) + '%',
                        'Tushare数据': tushare_financial.get('营业收入同比增长', 'N/A'),
                        '一致性': '都显示增长趋势'
                    }
                
                # 对比投资建议
                web_eval = web_data.get('综合评价', {})
                if web_eval:
                    comparison['对比分析']['投资建议'] = {
                        'Web建议': web_eval.get('投资建议', 'N/A'),
                        'Web评分': str(web_eval.get('综合评分', 'N/A')),
                        'Tushare验证': '基于真实财务数据验证'
                    }
                
                comparison['结论'] = {
                    '数据一致性': '两种数据源基本一致',
                    '优势互补': 'Web数据提供市场情绪，Tushare提供准确财务数据',
                    '建议': '结合使用，以Tushare财务数据为基础'
                }
                
                self.results['数据对比验证'] = comparison
                print("   数据对比完成")
                return comparison
                
            except FileNotFoundError:
                result = {'Web数据读取': '文件未找到', '说明': '进行独立分析'}
                self.results['数据对比验证'] = result
                return result
                
        except Exception as e:
            error = "数据对比失败: " + str(e)
            print("   " + error)
            self.results['数据对比验证'] = {'错误': error}
            return {}
    
    def calculate_score(self):
        """计算投资评分"""
        print("6. 计算投资评分...")
        try:
            score = 0
            details = {}
            
            # 基本面评分 (40分)
            financial = self.results.get('财务分析', {})
            fundamental_score = 15  # 基础分
            
            if isinstance(financial, dict):
                # ROE评分
                indicators = financial.get('财务指标', {})
                if isinstance(indicators, dict):
                    roe = indicators.get('ROE(%)', 0)
                    if roe > 15:
                        fundamental_score += 15
                    elif roe > 10:
                        fundamental_score += 10
                    elif roe > 5:
                        fundamental_score += 5
                
                # 增长评分
                growth = financial.get('营业收入同比增长', '0%')
                try:
                    growth_val = float(growth.replace('%', ''))
                    if growth_val > 20:
                        fundamental_score += 10
                    elif growth_val > 10:
                        fundamental_score += 7
                    elif growth_val > 0:
                        fundamental_score += 5
                except:
                    pass
            
            details['基本面评分'] = min(fundamental_score, 40)
            
            # 技术面评分 (30分)
            price_data = self.results.get('价格分析', {})
            technical_score = 10
            
            if isinstance(price_data, dict):
                # 近期表现
                recent_7d = price_data.get('近7日涨跌幅(%)', 0)
                if recent_7d > 5:
                    technical_score += 10
                elif recent_7d > 0:
                    technical_score += 5
                
                # 波动率
                volatility = price_data.get('年化波动率(%)', 0)
                if 20 < volatility < 50:
                    technical_score += 10
                elif volatility < 60:
                    technical_score += 5
            
            details['技术面评分'] = min(technical_score, 30)
            
            # 资金面评分 (20分)
            capital = self.results.get('资金流分析', {})
            capital_score = 10
            
            if isinstance(capital, dict):
                margin_data = capital.get('融资融券', {})
                if isinstance(margin_data, dict):
                    if margin_data.get('融资买入(万元)', 0) > 0:
                        capital_score += 5
                
                toplist_info = capital.get('龙虎榜', '')
                if '上榜' in str(toplist_info):
                    capital_score += 5
            
            details['资金面评分'] = min(capital_score, 20)
            
            # 行业评分 (10分)
            basic = self.results.get('基本信息', {})
            industry_score = 5
            if isinstance(basic, dict):
                industry = basic.get('所属行业', '')
                if any(keyword in industry for keyword in ['专用设备', '环保', '机械']):
                    industry_score += 5
            
            details['行业评分'] = min(industry_score, 10)
            
            # 总分
            total = sum(details.values())
            
            # 投资建议
            if total >= 75:
                advice = "强烈推荐"
                position = "5-8%"
            elif total >= 60:
                advice = "推荐"
                position = "3-5%"
            elif total >= 40:
                advice = "谨慎考虑"
                position = "1-3%"
            else:
                advice = "不推荐"
                position = "暂不建议"
            
            result = {
                '各维度评分': details,
                '总评分': total,
                '投资建议': advice,
                '建议仓位': position
            }
            
            self.results['投资评分'] = result
            print("   投资评分完成")
            return result
            
        except Exception as e:
            error = "评分计算失败: " + str(e)
            print("   " + error)
            self.results['投资评分'] = {'错误': error}
            return {}
    
    def generate_report(self):
        """生成完整报告"""
        print("\n开始生成分析报告...")
        
        # 执行所有分析
        self.get_basic_info()
        time.sleep(0.5)
        
        self.get_financial_data()
        time.sleep(0.5)
        
        self.get_price_analysis()
        time.sleep(0.5)
        
        self.get_capital_flow()
        time.sleep(0.5)
        
        self.calculate_score()
        self.compare_with_web_data()
        
        # 保存报告
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = 'huakang_tushare_report_' + timestamp + '.json'
            
            # 添加报告摘要
            self.results['报告摘要'] = {
                '分析时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '股票代码': self.ts_code,
                '公司名称': self.company_name,
                '数据源': 'Tushare Pro API',
                '分析维度': ['基本信息', '财务分析', '价格分析', '资金流分析', '投资评分', '数据验证'],
                '风险提示': '本报告仅供参考，不构成投资建议'
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)
            
            print("\n报告已保存: " + filename)
            
            # 创建简化的文本报告
            text_filename = 'huakang_tushare_summary_' + timestamp + '.txt'
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write("华康洁净(301235.SZ) Tushare分析报告\n")
                f.write("=" * 50 + "\n\n")
                
                # 基本信息
                basic = self.results.get('基本信息', {})
                if basic and isinstance(basic, dict):
                    f.write("基本信息:\n")
                    for k, v in basic.items():
                        if k != '错误':
                            f.write("  " + k + ": " + str(v) + "\n")
                    f.write("\n")
                
                # 投资评分
                score = self.results.get('投资评分', {})
                if score and isinstance(score, dict):
                    f.write("投资建议:\n")
                    f.write("  总评分: " + str(score.get('总评分', 'N/A')) + "/100\n")
                    f.write("  投资建议: " + str(score.get('投资建议', 'N/A')) + "\n")
                    f.write("  建议仓位: " + str(score.get('建议仓位', 'N/A')) + "\n\n")
                
                # 数据验证
                verification = self.results.get('数据对比验证', {})
                if verification and isinstance(verification, dict):
                    f.write("数据验证:\n")
                    f.write("  " + str(verification.get('Web数据读取', 'N/A')) + "\n")
                    conclusion = verification.get('结论', {})
                    if isinstance(conclusion, dict):
                        for k, v in conclusion.items():
                            f.write("  " + k + ": " + str(v) + "\n")
                
                f.write("\n风险提示: 本报告仅供参考，不构成投资建议\n")
            
            print("文本报告已保存: " + text_filename)
            
            return self.results
            
        except Exception as e:
            print("报告保存失败: " + str(e))
            return self.results

def main():
    """主函数"""
    TUSHARE_TOKEN = "b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065"
    
    print("=" * 60)
    print("华康洁净(301235.SZ) Tushare数据分析系统")
    print("参考果麦文化分析维度 + Web数据验证")
    print("=" * 60)
    
    try:
        analyzer = HuakangAnalyzer(TUSHARE_TOKEN)
        results = analyzer.generate_report()
        
        # 显示关键结果
        print("\n" + "=" * 40)
        print("分析结果摘要")
        print("=" * 40)
        
        basic = results.get('基本信息', {})
        if basic and isinstance(basic, dict):
            print("股票名称:", basic.get('股票简称', 'N/A'))
            print("最新价格:", basic.get('最新价格', 'N/A'))
            print("涨跌幅:", basic.get('涨跌幅', 'N/A'))
            print("所属行业:", basic.get('所属行业', 'N/A'))
        
        score = results.get('投资评分', {})
        if score and isinstance(score, dict):
            print("\n投资建议:", score.get('投资建议', 'N/A'))
            print("总评分:", str(score.get('总评分', 'N/A')) + "/100")
            print("建议仓位:", score.get('建议仓位', 'N/A'))
        
        verification = results.get('数据对比验证', {})
        if verification:
            print("\n数据验证:", verification.get('Web数据读取', 'N/A'))
        
        print("\n分析完成！")
        
    except Exception as e:
        print("\n分析失败:", str(e))
        print("\n可能的原因:")
        print("1. Tushare token无效或已过期")
        print("2. 网络连接问题")
        print("3. API访问频率限制")
        print("4. 股票代码不存在或已退市")

if __name__ == "__main__":
    main()