#!/usr/bin/env python3
"""
使用tushare实时数据全面分析5只股票并给出买卖建议
股票代码：301217, 002265, 301052, 300308, 300368
"""
import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import warnings
warnings.filterwarnings('ignore')

# 设置tushare token
ts.set_token('YOUR_TUSHARE_TOKEN')  # 需要替换为实际的token
pro = ts.pro_api()

class StockAnalyzer:
    def __init__(self, stock_codes):
        self.stock_codes = stock_codes
        self.today = datetime.now().strftime('%Y%m%d')
        self.analysis_results = {}
        
    def get_realtime_quotes(self):
        """获取实时行情数据"""
        print("正在获取实时行情数据...")
        realtime_data = {}
        
        for code in self.stock_codes:
            try:
                # 获取实时行情
                df = ts.get_realtime_quotes(code)
                if not df.empty:
                    realtime_data[code] = {
                        'name': df['name'].iloc[0],
                        'price': float(df['price'].iloc[0]),
                        'pre_close': float(df['pre_close'].iloc[0]),
                        'open': float(df['open'].iloc[0]),
                        'high': float(df['high'].iloc[0]),
                        'low': float(df['low'].iloc[0]),
                        'volume': float(df['volume'].iloc[0]),
                        'amount': float(df['amount'].iloc[0]),
                        'change': float(df['price'].iloc[0]) - float(df['pre_close'].iloc[0]),
                        'pct_change': ((float(df['price'].iloc[0]) - float(df['pre_close'].iloc[0])) / float(df['pre_close'].iloc[0])) * 100
                    }
            except Exception as e:
                print(f"获取{code}实时行情失败: {e}")
                
        return realtime_data
    
    def get_daily_data(self, days=60):
        """获取日线数据"""
        print("正在获取历史日线数据...")
        daily_data = {}
        end_date = self.today
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        for code in self.stock_codes:
            try:
                # 转换股票代码格式
                ts_code = code + '.SZ' if code.startswith(('002', '300', '301')) else code + '.SH'
                
                # 获取日线数据
                df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
                if not df.empty:
                    df = df.sort_values('trade_date')
                    daily_data[code] = df
            except Exception as e:
                print(f"获取{code}日线数据失败: {e}")
                
        return daily_data
    
    def calculate_technical_indicators(self, daily_data):
        """计算技术指标"""
        print("正在计算技术指标...")
        tech_indicators = {}
        
        for code, df in daily_data.items():
            if df.empty:
                continue
                
            indicators = {}
            
            # 计算移动平均线
            df['MA5'] = df['close'].rolling(window=5).mean()
            df['MA10'] = df['close'].rolling(window=10).mean()
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['MA30'] = df['close'].rolling(window=30).mean()
            
            # 计算RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # 计算MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Histogram'] = df['MACD'] - df['Signal']
            
            # 计算布林带
            df['BB_Middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            
            # 获取最新值
            latest = df.iloc[-1]
            indicators['MA5'] = latest['MA5']
            indicators['MA10'] = latest['MA10']
            indicators['MA20'] = latest['MA20']
            indicators['MA30'] = latest['MA30']
            indicators['RSI'] = latest['RSI']
            indicators['MACD'] = latest['MACD']
            indicators['Signal'] = latest['Signal']
            indicators['MACD_Histogram'] = latest['MACD_Histogram']
            indicators['BB_Upper'] = latest['BB_Upper']
            indicators['BB_Middle'] = latest['BB_Middle']
            indicators['BB_Lower'] = latest['BB_Lower']
            
            # 趋势判断
            indicators['trend'] = self.judge_trend(df)
            
            tech_indicators[code] = indicators
            
        return tech_indicators
    
    def judge_trend(self, df):
        """判断趋势"""
        if len(df) < 20:
            return "数据不足"
            
        latest = df.iloc[-1]
        
        # 均线多头排列
        if latest['MA5'] > latest['MA10'] > latest['MA20']:
            ma_trend = "多头"
        elif latest['MA5'] < latest['MA10'] < latest['MA20']:
            ma_trend = "空头"
        else:
            ma_trend = "震荡"
            
        # MACD判断
        if latest['MACD'] > latest['Signal'] and latest['MACD_Histogram'] > 0:
            macd_trend = "多头"
        else:
            macd_trend = "空头"
            
        # RSI判断
        if latest['RSI'] > 70:
            rsi_status = "超买"
        elif latest['RSI'] < 30:
            rsi_status = "超卖"
        else:
            rsi_status = "正常"
            
        return {
            'ma_trend': ma_trend,
            'macd_trend': macd_trend,
            'rsi_status': rsi_status
        }
    
    def get_fundamental_data(self):
        """获取基本面数据"""
        print("正在获取基本面数据...")
        fundamental_data = {}
        
        for code in self.stock_codes:
            try:
                ts_code = code + '.SZ' if code.startswith(('002', '300', '301')) else code + '.SH'
                
                # 获取最新财务指标
                df_indicator = pro.fina_indicator(ts_code=ts_code, period='20240930')
                
                # 获取每日指标
                df_daily_basic = pro.daily_basic(ts_code=ts_code, trade_date=self.today)
                
                fundamental = {}
                
                if not df_indicator.empty:
                    latest_indicator = df_indicator.iloc[0]
                    fundamental['roe'] = latest_indicator.get('roe', None)
                    fundamental['gross_profit_margin'] = latest_indicator.get('grossprofit_margin', None)
                    fundamental['net_profit_margin'] = latest_indicator.get('netprofit_margin', None)
                    fundamental['current_ratio'] = latest_indicator.get('current_ratio', None)
                    fundamental['quick_ratio'] = latest_indicator.get('quick_ratio', None)
                    
                if not df_daily_basic.empty:
                    latest_basic = df_daily_basic.iloc[0]
                    fundamental['pe'] = latest_basic.get('pe', None)
                    fundamental['pb'] = latest_basic.get('pb', None)
                    fundamental['ps'] = latest_basic.get('ps', None)
                    fundamental['total_mv'] = latest_basic.get('total_mv', None)
                    fundamental['circ_mv'] = latest_basic.get('circ_mv', None)
                    
                fundamental_data[code] = fundamental
                
            except Exception as e:
                print(f"获取{code}基本面数据失败: {e}")
                
        return fundamental_data
    
    def get_money_flow(self):
        """获取资金流向数据"""
        print("正在获取资金流向数据...")
        money_flow = {}
        
        for code in self.stock_codes:
            try:
                ts_code = code + '.SZ' if code.startswith(('002', '300', '301')) else code + '.SH'
                
                # 获取资金流向数据
                df = pro.moneyflow(ts_code=ts_code, start_date=(datetime.now() - timedelta(days=5)).strftime('%Y%m%d'), 
                                  end_date=self.today)
                
                if not df.empty:
                    latest = df.iloc[0]
                    money_flow[code] = {
                        'buy_sm_vol': latest.get('buy_sm_vol', 0),  # 小单买入
                        'buy_md_vol': latest.get('buy_md_vol', 0),  # 中单买入
                        'buy_lg_vol': latest.get('buy_lg_vol', 0),  # 大单买入
                        'buy_elg_vol': latest.get('buy_elg_vol', 0),  # 特大单买入
                        'sell_sm_vol': latest.get('sell_sm_vol', 0),  # 小单卖出
                        'sell_md_vol': latest.get('sell_md_vol', 0),  # 中单卖出
                        'sell_lg_vol': latest.get('sell_lg_vol', 0),  # 大单卖出
                        'sell_elg_vol': latest.get('sell_elg_vol', 0),  # 特大单卖出
                        'net_mf_vol': latest.get('net_mf_vol', 0)  # 净流入
                    }
                    
            except Exception as e:
                print(f"获取{code}资金流向失败: {e}")
                
        return money_flow
    
    def generate_recommendation(self, code, realtime, technical, fundamental, money_flow):
        """生成买卖建议"""
        score = 0
        reasons = []
        
        # 技术面评分
        if technical and 'trend' in technical:
            trend = technical['trend']
            
            # 均线趋势
            if trend['ma_trend'] == '多头':
                score += 20
                reasons.append("均线呈多头排列")
            elif trend['ma_trend'] == '空头':
                score -= 20
                reasons.append("均线呈空头排列")
                
            # MACD趋势
            if trend['macd_trend'] == '多头':
                score += 15
                reasons.append("MACD金叉向上")
            else:
                score -= 15
                reasons.append("MACD死叉向下")
                
            # RSI状态
            if trend['rsi_status'] == '超卖':
                score += 10
                reasons.append("RSI超卖，有反弹需求")
            elif trend['rsi_status'] == '超买':
                score -= 10
                reasons.append("RSI超买，有回调风险")
                
        # 基本面评分
        if fundamental:
            # PE估值
            pe = fundamental.get('pe', None)
            if pe and pe > 0:
                if pe < 20:
                    score += 15
                    reasons.append(f"PE值{pe:.2f}，估值合理")
                elif pe > 50:
                    score -= 15
                    reasons.append(f"PE值{pe:.2f}，估值偏高")
                    
            # ROE盈利能力
            roe = fundamental.get('roe', None)
            if roe:
                if roe > 15:
                    score += 10
                    reasons.append(f"ROE为{roe:.2f}%，盈利能力强")
                elif roe < 5:
                    score -= 10
                    reasons.append(f"ROE为{roe:.2f}%，盈利能力弱")
                    
        # 资金流向评分
        if money_flow:
            net_flow = money_flow.get('net_mf_vol', 0)
            if net_flow > 0:
                score += 10
                reasons.append("资金净流入")
            else:
                score -= 10
                reasons.append("资金净流出")
                
        # 生成建议
        if score >= 30:
            recommendation = "强烈买入"
        elif score >= 15:
            recommendation = "买入"
        elif score >= -15:
            recommendation = "持有观望"
        elif score >= -30:
            recommendation = "卖出"
        else:
            recommendation = "强烈卖出"
            
        return {
            'recommendation': recommendation,
            'score': score,
            'reasons': reasons
        }
    
    def analyze_all(self):
        """执行全面分析"""
        # 获取各项数据
        realtime_data = self.get_realtime_quotes()
        daily_data = self.get_daily_data()
        technical_indicators = self.calculate_technical_indicators(daily_data)
        fundamental_data = self.get_fundamental_data()
        money_flow = self.get_money_flow()
        
        # 生成综合分析报告
        for code in self.stock_codes:
            print(f"\n正在分析股票 {code}...")
            
            analysis = {
                'code': code,
                'name': realtime_data.get(code, {}).get('name', '未知'),
                'realtime': realtime_data.get(code, {}),
                'technical': technical_indicators.get(code, {}),
                'fundamental': fundamental_data.get(code, {}),
                'money_flow': money_flow.get(code, {})
            }
            
            # 生成买卖建议
            recommendation = self.generate_recommendation(
                code, 
                analysis['realtime'],
                analysis['technical'],
                analysis['fundamental'],
                analysis['money_flow']
            )
            
            analysis['recommendation'] = recommendation
            self.analysis_results[code] = analysis
            
        return self.analysis_results
    
    def generate_report(self):
        """生成分析报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 生成详细报告
        report_lines = [
            f"# 5只股票全面分析报告",
            f"分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"分析股票：{', '.join(self.stock_codes)}",
            "",
            "## 一、综合评级与建议",
            ""
        ]
        
        # 汇总建议
        for code, analysis in self.analysis_results.items():
            rec = analysis['recommendation']
            report_lines.extend([
                f"### {code} - {analysis['name']}",
                f"- **综合建议**：{rec['recommendation']} (评分：{rec['score']})",
                f"- **当前价格**：{analysis['realtime'].get('price', 'N/A')}",
                f"- **今日涨跌**：{analysis['realtime'].get('pct_change', 0):.2f}%",
                f"- **主要理由**：",
                ""
            ])
            
            for reason in rec['reasons']:
                report_lines.append(f"  - {reason}")
            report_lines.append("")
        
        # 详细分析
        report_lines.extend([
            "",
            "## 二、详细分析数据",
            ""
        ])
        
        for code, analysis in self.analysis_results.items():
            report_lines.extend([
                f"### {code} - {analysis['name']}",
                "",
                "#### 1. 实时行情",
                f"- 当前价：{analysis['realtime'].get('price', 'N/A')}",
                f"- 开盘价：{analysis['realtime'].get('open', 'N/A')}",
                f"- 最高价：{analysis['realtime'].get('high', 'N/A')}",
                f"- 最低价：{analysis['realtime'].get('low', 'N/A')}",
                f"- 成交量：{analysis['realtime'].get('volume', 0)/10000:.2f}万手",
                f"- 成交额：{analysis['realtime'].get('amount', 0)/100000000:.2f}亿元",
                "",
                "#### 2. 技术指标",
            ])
            
            tech = analysis['technical']
            if tech:
                report_lines.extend([
                    f"- MA5：{tech.get('MA5', 'N/A'):.2f}" if tech.get('MA5') else "- MA5：N/A",
                    f"- MA10：{tech.get('MA10', 'N/A'):.2f}" if tech.get('MA10') else "- MA10：N/A",
                    f"- MA20：{tech.get('MA20', 'N/A'):.2f}" if tech.get('MA20') else "- MA20：N/A",
                    f"- RSI：{tech.get('RSI', 'N/A'):.2f}" if tech.get('RSI') else "- RSI：N/A",
                    f"- MACD：{tech.get('MACD', 'N/A'):.4f}" if tech.get('MACD') else "- MACD：N/A",
                ])
            
            report_lines.extend([
                "",
                "#### 3. 基本面指标",
            ])
            
            fund = analysis['fundamental']
            if fund:
                report_lines.extend([
                    f"- PE：{fund.get('pe', 'N/A'):.2f}" if fund.get('pe') else "- PE：N/A",
                    f"- PB：{fund.get('pb', 'N/A'):.2f}" if fund.get('pb') else "- PB：N/A",
                    f"- ROE：{fund.get('roe', 'N/A'):.2f}%" if fund.get('roe') else "- ROE：N/A",
                    f"- 总市值：{fund.get('total_mv', 0)/10000:.2f}亿元" if fund.get('total_mv') else "- 总市值：N/A",
                ])
            
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")
        
        # 保存报告
        report_content = '\n'.join(report_lines)
        
        # 保存Markdown报告
        with open(f'股票分析报告_{timestamp}.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        # 保存JSON数据
        with open(f'股票分析数据_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
            
        print(f"\n报告已生成：")
        print(f"- Markdown报告：股票分析报告_{timestamp}.md")
        print(f"- JSON数据：股票分析数据_{timestamp}.json")
        
        return report_content

def main():
    # 分析的股票代码
    stock_codes = ['301217', '002265', '301052', '300308', '300368']
    
    print("开始分析5只股票...")
    print(f"股票代码：{', '.join(stock_codes)}")
    print("-" * 50)
    
    # 创建分析器
    analyzer = StockAnalyzer(stock_codes)
    
    # 执行分析
    results = analyzer.analyze_all()
    
    # 生成报告
    report = analyzer.generate_report()
    
    # 打印简要结果
    print("\n" + "="*50)
    print("分析完成！买卖建议汇总：")
    print("="*50)
    
    for code, analysis in results.items():
        rec = analysis['recommendation']
        print(f"\n{code} - {analysis['name']}：")
        print(f"  建议：{rec['recommendation']} (评分：{rec['score']})")
        print(f"  当前价：{analysis['realtime'].get('price', 'N/A')}  涨跌幅：{analysis['realtime'].get('pct_change', 0):.2f}%")

if __name__ == "__main__":
    main()