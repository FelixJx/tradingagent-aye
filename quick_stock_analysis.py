#!/usr/bin/env python3
"""
快速分析5只股票并给出买卖建议
股票代码：301217, 002265, 301052, 300308, 300368
"""
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

class QuickStockAnalyzer:
    def __init__(self, stock_codes):
        self.stock_codes = stock_codes
        self.analysis_results = {}
        
    def get_realtime_quotes(self):
        """获取实时行情"""
        print("获取实时行情数据...")
        try:
            # 获取实时行情
            df = ak.stock_zh_a_spot_em()
            realtime_data = {}
            
            for code in self.stock_codes:
                stock_data = df[df['代码'] == code]
                if not stock_data.empty:
                    row = stock_data.iloc[0]
                    realtime_data[code] = {
                        'name': row['名称'],
                        'price': row['最新价'],
                        'pct_change': row['涨跌幅'],
                        'change': row['涨跌额'],
                        'volume': row['成交量'],
                        'amount': row['成交额'],
                        'turnover_rate': row['换手率'],
                        'pe_ratio': row['市盈率-动态'],
                        'pb_ratio': row['市净率'],
                        'high': row['最高'],
                        'low': row['最低'],
                        'open': row['今开'],
                        'pre_close': row['昨收']
                    }
            return realtime_data
        except Exception as e:
            print(f"获取实时行情失败: {e}")
            return {}
    
    def get_historical_data_simple(self):
        """获取简化的历史数据"""
        print("获取历史数据...")
        historical_data = {}
        
        for code in self.stock_codes:
            try:
                # 获取最近30天数据
                df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20240601", end_date="20241231", adjust="qfq")
                if not df.empty:
                    df['日期'] = pd.to_datetime(df['日期'])
                    df = df.sort_values('日期').tail(30)  # 只取最近30天
                    historical_data[code] = df
            except Exception as e:
                print(f"获取{code}历史数据失败: {e}")
                
        return historical_data
    
    def calculate_simple_indicators(self, historical_data):
        """计算简化技术指标"""
        print("计算技术指标...")
        indicators = {}
        
        for code, df in historical_data.items():
            if df.empty or len(df) < 20:
                continue
                
            # 计算移动平均线
            df['MA5'] = df['收盘'].rolling(window=5).mean()
            df['MA10'] = df['收盘'].rolling(window=10).mean()
            df['MA20'] = df['收盘'].rolling(window=20).mean()
            
            # 计算RSI
            delta = df['收盘'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            latest = df.iloc[-1]
            indicators[code] = {
                'MA5': latest['MA5'],
                'MA10': latest['MA10'],
                'MA20': latest['MA20'],
                'RSI': latest['RSI'],
                'price_vs_ma5': (latest['收盘'] - latest['MA5']) / latest['MA5'] * 100,
                'price_vs_ma20': (latest['收盘'] - latest['MA20']) / latest['MA20'] * 100,
                'ma_trend': self.judge_ma_trend(latest)
            }
            
        return indicators
    
    def judge_ma_trend(self, latest):
        """判断均线趋势"""
        if latest['MA5'] > latest['MA10'] > latest['MA20']:
            return "多头排列"
        elif latest['MA5'] < latest['MA10'] < latest['MA20']:
            return "空头排列"
        else:
            return "震荡"
    
    def generate_quick_recommendation(self, code, realtime, technical):
        """快速生成买卖建议"""
        score = 0
        reasons = []
        
        # 技术面评分
        if technical:
            # 均线趋势
            if technical['ma_trend'] == '多头排列':
                score += 25
                reasons.append("均线多头排列")
            elif technical['ma_trend'] == '空头排列':
                score -= 25
                reasons.append("均线空头排列")
            
            # 价格相对位置
            if technical['price_vs_ma5'] > 5:
                score += 10
                reasons.append("突破MA5")
            elif technical['price_vs_ma5'] < -5:
                score -= 10
                reasons.append("跌破MA5")
                
            # RSI状态
            rsi = technical.get('RSI', 50)
            if rsi > 70:
                score -= 15
                reasons.append(f"RSI超买({rsi:.1f})")
            elif rsi < 30:
                score += 15
                reasons.append(f"RSI超卖({rsi:.1f})")
        
        # 估值评分
        if realtime:
            pe = realtime.get('pe_ratio', 0)
            if pe and pe > 0:
                if pe < 20:
                    score += 15
                    reasons.append(f"PE低估值({pe:.1f})")
                elif pe > 60:
                    score -= 15
                    reasons.append(f"PE高估值({pe:.1f})")
            
            # 涨跌幅
            pct_change = realtime.get('pct_change', 0)
            if pct_change > 5:
                score += 5
                reasons.append("今日强势")
            elif pct_change < -5:
                score -= 5
                reasons.append("今日弱势")
        
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
        """执行分析"""
        # 获取数据
        realtime_data = self.get_realtime_quotes()
        historical_data = self.get_historical_data_simple()
        technical_indicators = self.calculate_simple_indicators(historical_data)
        
        # 分析每只股票
        for code in self.stock_codes:
            realtime = realtime_data.get(code, {})
            technical = technical_indicators.get(code, {})
            
            recommendation = self.generate_quick_recommendation(code, realtime, technical)
            
            self.analysis_results[code] = {
                'name': realtime.get('name', f'股票{code}'),
                'realtime': realtime,
                'technical': technical,
                'recommendation': recommendation
            }
        
        return self.analysis_results
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*60)
        print("📊 5只股票买卖建议分析结果")
        print("="*60)
        
        # 按评分排序
        sorted_results = sorted(self.analysis_results.items(), 
                              key=lambda x: x[1]['recommendation']['score'], 
                              reverse=True)
        
        for i, (code, analysis) in enumerate(sorted_results, 1):
            rec = analysis['recommendation']
            realtime = analysis['realtime']
            technical = analysis['technical']
            
            print(f"\n【{i}】{code} - {analysis['name']}")
            print(f"💰 当前价格: ¥{realtime.get('price', 'N/A')}")
            print(f"📈 今日涨跌: {realtime.get('pct_change', 0):.2f}%")
            print(f"🎯 投资建议: {rec['recommendation']} (评分: {rec['score']})")
            
            if technical:
                print(f"📊 技术状态: {technical.get('ma_trend', 'N/A')} | RSI: {technical.get('RSI', 0):.1f}")
                print(f"📍 相对MA5: {technical.get('price_vs_ma5', 0):+.1f}% | 相对MA20: {technical.get('price_vs_ma20', 0):+.1f}%")
            
            print(f"📋 分析依据: {', '.join(rec['reasons'])}")
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 生成简要报告
        report_lines = [
            f"# 5只股票快速分析报告",
            f"分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"## 投资建议排序",
            f""
        ]
        
        for i, (code, analysis) in enumerate(sorted_results, 1):
            rec = analysis['recommendation']
            realtime = analysis['realtime']
            
            report_lines.extend([
                f"### {i}. {code} - {analysis['name']}",
                f"- **投资建议**: {rec['recommendation']} (评分: {rec['score']})",
                f"- **当前价格**: ¥{realtime.get('price', 'N/A')}",
                f"- **今日涨跌**: {realtime.get('pct_change', 0):.2f}%",
                f"- **分析依据**: {', '.join(rec['reasons'])}",
                f""
            ])
        
        # 保存报告
        with open(f'快速股票分析_{timestamp}.md', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        with open(f'股票分析数据_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📄 分析报告已保存: 快速股票分析_{timestamp}.md")

def main():
    stock_codes = ['301217', '002265', '301052', '300308', '300368']
    
    print("🚀 开始快速分析5只股票...")
    print(f"📊 股票代码: {', '.join(stock_codes)}")
    
    analyzer = QuickStockAnalyzer(stock_codes)
    analyzer.analyze_all()
    analyzer.print_results()

if __name__ == "__main__":
    main()