#!/usr/bin/env python3
"""
使用多种数据源全面分析5只股票并给出买卖建议
股票代码：301217, 002265, 301052, 300308, 300368
"""
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import warnings
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class ComprehensiveStockAnalyzer:
    def __init__(self, stock_codes):
        self.stock_codes = stock_codes
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.analysis_results = {}
        self.stock_names = {}
        
    def get_stock_info(self):
        """获取股票基本信息"""
        print("正在获取股票基本信息...")
        for code in self.stock_codes:
            try:
                # 获取股票信息
                info = ak.stock_individual_info_em(symbol=code)
                if not info.empty:
                    name_row = info[info['item'] == '股票简称']
                    if not name_row.empty:
                        self.stock_names[code] = name_row['value'].iloc[0]
                    else:
                        self.stock_names[code] = f"股票{code}"
                else:
                    self.stock_names[code] = f"股票{code}"
            except Exception as e:
                print(f"获取{code}基本信息失败: {e}")
                self.stock_names[code] = f"股票{code}"
    
    def get_realtime_data(self):
        """获取实时行情数据"""
        print("正在获取实时行情数据...")
        realtime_data = {}
        
        for code in self.stock_codes:
            try:
                # 获取实时行情
                df = ak.stock_zh_a_spot_em()
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
                        'high': row['最高'],
                        'low': row['最低'],
                        'open': row['今开'],
                        'pre_close': row['昨收'],
                        'turnover_rate': row['换手率'],
                        'pe_ratio': row['市盈率-动态'],
                        'pb_ratio': row['市净率']
                    }
                    self.stock_names[code] = row['名称']
                    
            except Exception as e:
                print(f"获取{code}实时行情失败: {e}")
                
        return realtime_data
    
    def get_historical_data(self, period="daily", adjust="qfq"):
        """获取历史行情数据"""
        print("正在获取历史行情数据...")
        historical_data = {}
        
        for code in self.stock_codes:
            try:
                # 获取历史数据
                df = ak.stock_zh_a_hist(symbol=code, period=period, adjust=adjust)
                if not df.empty:
                    df['日期'] = pd.to_datetime(df['日期'])
                    df = df.sort_values('日期')
                    historical_data[code] = df
                    
            except Exception as e:
                print(f"获取{code}历史数据失败: {e}")
                
        return historical_data
    
    def calculate_technical_indicators(self, historical_data):
        """计算技术指标"""
        print("正在计算技术指标...")
        tech_indicators = {}
        
        for code, df in historical_data.items():
            if df.empty:
                continue
                
            indicators = {}
            
            # 确保数据足够
            if len(df) < 30:
                print(f"{code}历史数据不足，跳过技术指标计算")
                continue
            
            # 计算移动平均线
            df['MA5'] = df['收盘'].rolling(window=5).mean()
            df['MA10'] = df['收盘'].rolling(window=10).mean()
            df['MA20'] = df['收盘'].rolling(window=20).mean()
            df['MA30'] = df['收盘'].rolling(window=30).mean()
            
            # 计算RSI
            delta = df['收盘'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # 计算MACD
            exp1 = df['收盘'].ewm(span=12, adjust=False).mean()
            exp2 = df['收盘'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Histogram'] = df['MACD'] - df['Signal']
            
            # 计算布林带
            df['BB_Middle'] = df['收盘'].rolling(window=20).mean()
            bb_std = df['收盘'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            
            # 计算KDJ
            low_min = df['最低'].rolling(window=9).min()
            high_max = df['最高'].rolling(window=9).max()
            rsv = (df['收盘'] - low_min) / (high_max - low_min) * 100
            df['K'] = rsv.ewm(alpha=1/3).mean()
            df['D'] = df['K'].ewm(alpha=1/3).mean()
            df['J'] = 3 * df['K'] - 2 * df['D']
            
            # 获取最新值
            latest = df.iloc[-1]
            indicators['price'] = latest['收盘']
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
            indicators['K'] = latest['K']
            indicators['D'] = latest['D']
            indicators['J'] = latest['J']
            
            # 趋势判断
            indicators['trend_analysis'] = self.analyze_trend(df)
            
            tech_indicators[code] = indicators
            
        return tech_indicators
    
    def analyze_trend(self, df):
        """分析趋势"""
        latest = df.iloc[-1]
        prev_5 = df.iloc[-6:-1] if len(df) >= 6 else df.iloc[:-1]
        
        analysis = {}
        
        # 均线趋势
        if latest['MA5'] > latest['MA10'] > latest['MA20']:
            analysis['ma_trend'] = "多头排列"
            analysis['ma_score'] = 20
        elif latest['MA5'] < latest['MA10'] < latest['MA20']:
            analysis['ma_trend'] = "空头排列"
            analysis['ma_score'] = -20
        else:
            analysis['ma_trend'] = "震荡整理"
            analysis['ma_score'] = 0
            
        # MACD趋势
        if latest['MACD'] > latest['Signal'] and latest['MACD_Histogram'] > 0:
            analysis['macd_trend'] = "金叉向上"
            analysis['macd_score'] = 15
        elif latest['MACD'] < latest['Signal'] and latest['MACD_Histogram'] < 0:
            analysis['macd_trend'] = "死叉向下"
            analysis['macd_score'] = -15
        else:
            analysis['macd_trend'] = "震荡"
            analysis['macd_score'] = 0
            
        # RSI判断
        if latest['RSI'] > 80:
            analysis['rsi_status'] = "严重超买"
            analysis['rsi_score'] = -15
        elif latest['RSI'] > 70:
            analysis['rsi_status'] = "超买"
            analysis['rsi_score'] = -10
        elif latest['RSI'] < 20:
            analysis['rsi_status'] = "严重超卖"
            analysis['rsi_score'] = 15
        elif latest['RSI'] < 30:
            analysis['rsi_status'] = "超卖"
            analysis['rsi_score'] = 10
        else:
            analysis['rsi_status'] = "正常区间"
            analysis['rsi_score'] = 0
            
        # KDJ判断
        if latest['K'] > 80 and latest['D'] > 80:
            analysis['kdj_status'] = "超买区域"
            analysis['kdj_score'] = -10
        elif latest['K'] < 20 and latest['D'] < 20:
            analysis['kdj_status'] = "超卖区域"
            analysis['kdj_score'] = 10
        else:
            analysis['kdj_status'] = "正常区域"
            analysis['kdj_score'] = 0
            
        # 布林带位置
        bb_position = (latest['收盘'] - latest['BB_Lower']) / (latest['BB_Upper'] - latest['BB_Lower'])
        if bb_position > 0.8:
            analysis['bb_position'] = "接近上轨"
            analysis['bb_score'] = -5
        elif bb_position < 0.2:
            analysis['bb_position'] = "接近下轨"
            analysis['bb_score'] = 5
        else:
            analysis['bb_position'] = "中轨附近"
            analysis['bb_score'] = 0
            
        # 成交量分析
        vol_ma5 = prev_5['成交量'].mean() if len(prev_5) > 0 else latest['成交量']
        if latest['成交量'] > vol_ma5 * 1.5:
            analysis['volume_status'] = "放量"
            analysis['volume_score'] = 5
        elif latest['成交量'] < vol_ma5 * 0.5:
            analysis['volume_status'] = "缩量"
            analysis['volume_score'] = -5
        else:
            analysis['volume_status'] = "正常"
            analysis['volume_score'] = 0
            
        return analysis
    
    def get_financial_data(self):
        """获取财务数据"""
        print("正在获取财务数据...")
        financial_data = {}
        
        for code in self.stock_codes:
            try:
                # 获取主要财务指标
                df_indicator = ak.stock_financial_abstract_ths(symbol=code)
                
                if not df_indicator.empty:
                    financial_data[code] = {}
                    
                    # 提取关键财务指标
                    for index, row in df_indicator.iterrows():
                        item = row['指标名称']
                        value = row.get('2024-09-30', row.get('2024-06-30', row.get('2023-12-31', None)))
                        
                        if '净资产收益率' in item:
                            financial_data[code]['roe'] = self.parse_number(value)
                        elif '毛利率' in item:
                            financial_data[code]['gross_margin'] = self.parse_number(value)
                        elif '净利率' in item:
                            financial_data[code]['net_margin'] = self.parse_number(value)
                        elif '资产负债率' in item:
                            financial_data[code]['debt_ratio'] = self.parse_number(value)
                        elif '流动比率' in item:
                            financial_data[code]['current_ratio'] = self.parse_number(value)
                            
            except Exception as e:
                print(f"获取{code}财务数据失败: {e}")
                
        return financial_data
    
    def parse_number(self, value):
        """解析数字字符串"""
        if pd.isna(value) or value is None:
            return None
        try:
            # 移除百分号并转换为数字
            if isinstance(value, str):
                value = value.replace('%', '').replace(',', '')
            return float(value)
        except:
            return None
    
    def get_news_sentiment(self):
        """获取新闻情感分析"""
        print("正在获取新闻数据...")
        news_data = {}
        
        for code in self.stock_codes:
            try:
                # 获取个股新闻
                news_df = ak.stock_news_em(symbol=code)
                
                if not news_df.empty:
                    recent_news = news_df.head(10)  # 取最近10条新闻
                    
                    # 简单的情感分析（基于关键词）
                    positive_keywords = ['上涨', '利好', '突破', '增长', '盈利', '合作', '订单', '业绩', '创新']
                    negative_keywords = ['下跌', '利空', '亏损', '风险', '下滑', '减少', '困难', '问题']
                    
                    sentiment_score = 0
                    for _, news in recent_news.iterrows():
                        title = str(news['新闻标题'])
                        for word in positive_keywords:
                            sentiment_score += title.count(word) * 1
                        for word in negative_keywords:
                            sentiment_score -= title.count(word) * 1
                    
                    news_data[code] = {
                        'news_count': len(recent_news),
                        'sentiment_score': sentiment_score,
                        'latest_news': recent_news['新闻标题'].tolist()[:3]
                    }
                    
            except Exception as e:
                print(f"获取{code}新闻数据失败: {e}")
                
        return news_data
    
    def generate_comprehensive_recommendation(self, code, realtime, technical, financial, news):
        """生成综合买卖建议"""
        total_score = 0
        detailed_analysis = []
        
        # 技术面分析
        if technical and 'trend_analysis' in technical:
            trend = technical['trend_analysis']
            tech_score = (trend.get('ma_score', 0) + 
                         trend.get('macd_score', 0) + 
                         trend.get('rsi_score', 0) + 
                         trend.get('kdj_score', 0) + 
                         trend.get('bb_score', 0) + 
                         trend.get('volume_score', 0))
            
            total_score += tech_score
            detailed_analysis.append(f"技术面评分：{tech_score} ({trend.get('ma_trend', '')}, {trend.get('macd_trend', '')}, RSI:{trend.get('rsi_status', '')})")
            
        # 基本面分析
        if financial:
            fund_score = 0
            fund_reasons = []
            
            roe = financial.get('roe')
            if roe:
                if roe > 15:
                    fund_score += 15
                    fund_reasons.append(f"ROE {roe:.2f}% 优秀")
                elif roe > 10:
                    fund_score += 10
                    fund_reasons.append(f"ROE {roe:.2f}% 良好")
                elif roe < 5:
                    fund_score -= 10
                    fund_reasons.append(f"ROE {roe:.2f}% 偏低")
                    
            debt_ratio = financial.get('debt_ratio')
            if debt_ratio:
                if debt_ratio < 30:
                    fund_score += 5
                    fund_reasons.append("负债率低")
                elif debt_ratio > 70:
                    fund_score -= 10
                    fund_reasons.append("负债率偏高")
                    
            total_score += fund_score
            detailed_analysis.append(f"基本面评分：{fund_score} ({', '.join(fund_reasons)})")
        
        # 估值分析
        if realtime:
            valuation_score = 0
            pe = realtime.get('pe_ratio')
            pb = realtime.get('pb_ratio')
            
            if pe and pe > 0:
                if pe < 15:
                    valuation_score += 10
                    detailed_analysis.append(f"PE {pe:.2f} 估值合理")
                elif pe > 50:
                    valuation_score -= 15
                    detailed_analysis.append(f"PE {pe:.2f} 估值偏高")
                    
            total_score += valuation_score
        
        # 消息面分析
        if news:
            news_score = min(max(news.get('sentiment_score', 0), -10), 10)
            total_score += news_score
            if news_score != 0:
                detailed_analysis.append(f"消息面评分：{news_score}")
        
        # 生成建议
        if total_score >= 40:
            recommendation = "强烈买入"
            color_code = "🟢"
        elif total_score >= 20:
            recommendation = "买入"
            color_code = "🟢"
        elif total_score >= -10:
            recommendation = "持有观望"
            color_code = "🟡"
        elif total_score >= -30:
            recommendation = "卖出"
            color_code = "🔴"
        else:
            recommendation = "强烈卖出"
            color_code = "🔴"
            
        return {
            'recommendation': recommendation,
            'total_score': total_score,
            'color_code': color_code,
            'detailed_analysis': detailed_analysis,
            'risk_level': self.assess_risk_level(total_score, technical, realtime)
        }
    
    def assess_risk_level(self, score, technical, realtime):
        """评估风险等级"""
        risk_factors = []
        
        # 技术风险
        if technical and 'trend_analysis' in technical:
            trend = technical['trend_analysis']
            if trend.get('rsi_status') in ['严重超买', '超买']:
                risk_factors.append("技术指标超买")
                
        # 估值风险
        if realtime:
            pe = realtime.get('pe_ratio', 0)
            if pe > 100:
                risk_factors.append("估值过高")
                
        # 综合风险等级
        if len(risk_factors) >= 3 or score < -30:
            return {"level": "高风险", "factors": risk_factors}
        elif len(risk_factors) >= 1 or score < 0:
            return {"level": "中等风险", "factors": risk_factors}
        else:
            return {"level": "低风险", "factors": risk_factors}
    
    def create_visualization(self):
        """创建可视化图表"""
        print("正在生成可视化图表...")
        
        # 创建图表
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('5只股票综合分析Dashboard', fontsize=16, fontweight='bold')
        
        # 收集数据用于可视化
        codes = []
        names = []
        scores = []
        recommendations = []
        prices = []
        changes = []
        
        for code, analysis in self.analysis_results.items():
            codes.append(code)
            names.append(analysis.get('name', f'股票{code}'))
            scores.append(analysis['recommendation']['total_score'])
            recommendations.append(analysis['recommendation']['recommendation'])
            
            realtime = analysis.get('realtime', {})
            prices.append(realtime.get('price', 0))
            changes.append(realtime.get('pct_change', 0))
        
        # 1. 综合评分柱状图
        colors = ['green' if s >= 0 else 'red' for s in scores]
        axes[0,0].bar(codes, scores, color=colors, alpha=0.7)
        axes[0,0].set_title('综合评分对比')
        axes[0,0].set_ylabel('评分')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # 2. 涨跌幅对比
        change_colors = ['green' if c >= 0 else 'red' for c in changes]
        axes[0,1].bar(codes, changes, color=change_colors, alpha=0.7)
        axes[0,1].set_title('今日涨跌幅(%)')
        axes[0,1].set_ylabel('涨跌幅(%)')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # 3. 价格对比
        axes[0,2].bar(codes, prices, color='blue', alpha=0.7)
        axes[0,2].set_title('当前价格(元)')
        axes[0,2].set_ylabel('价格(元)')
        axes[0,2].tick_params(axis='x', rotation=45)
        
        # 4. 买卖建议分布饼图
        rec_counts = {}
        for rec in recommendations:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1
        
        axes[1,0].pie(rec_counts.values(), labels=rec_counts.keys(), autopct='%1.1f%%')
        axes[1,0].set_title('买卖建议分布')
        
        # 5. 风险等级评估
        risk_levels = []
        for code, analysis in self.analysis_results.items():
            risk_level = analysis['recommendation']['risk_level']['level']
            risk_levels.append(risk_level)
            
        risk_counts = {}
        for risk in risk_levels:
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
            
        axes[1,1].pie(risk_counts.values(), labels=risk_counts.keys(), autopct='%1.1f%%',
                      colors=['green', 'orange', 'red'])
        axes[1,1].set_title('风险等级分布')
        
        # 6. 评分vs涨跌幅散点图
        axes[1,2].scatter(scores, changes, s=100, alpha=0.7)
        for i, code in enumerate(codes):
            axes[1,2].annotate(code, (scores[i], changes[i]), xytext=(5,5), 
                              textcoords='offset points')
        axes[1,2].set_xlabel('综合评分')
        axes[1,2].set_ylabel('涨跌幅(%)')
        axes[1,2].set_title('评分与涨跌幅关系')
        axes[1,2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图表
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        chart_file = f'股票分析图表_{timestamp}.png'
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_file
    
    def analyze_all_stocks(self):
        """执行全面分析"""
        print("开始全面分析...")
        
        # 获取股票基本信息
        self.get_stock_info()
        
        # 获取各类数据
        realtime_data = self.get_realtime_data()
        historical_data = self.get_historical_data()
        technical_indicators = self.calculate_technical_indicators(historical_data)
        financial_data = self.get_financial_data()
        news_data = self.get_news_sentiment()
        
        # 综合分析每只股票
        for code in self.stock_codes:
            print(f"\n正在综合分析 {code} - {self.stock_names.get(code, '')}...")
            
            analysis = {
                'code': code,
                'name': self.stock_names.get(code, f'股票{code}'),
                'realtime': realtime_data.get(code, {}),
                'technical': technical_indicators.get(code, {}),
                'financial': financial_data.get(code, {}),
                'news': news_data.get(code, {})
            }
            
            # 生成综合建议
            recommendation = self.generate_comprehensive_recommendation(
                code,
                analysis['realtime'],
                analysis['technical'],
                analysis['financial'],
                analysis['news']
            )
            
            analysis['recommendation'] = recommendation
            self.analysis_results[code] = analysis
        
        return self.analysis_results
    
    def generate_comprehensive_report(self):
        """生成综合分析报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 创建可视化图表
        chart_file = self.create_visualization()
        
        # 生成报告内容
        report_lines = [
            "# 🏆 5只股票全面投资分析报告",
            f"",
            f"**分析时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**分析股票**：{', '.join(self.stock_codes)}  ",
            f"**数据来源**：akshare, 东方财富  ",
            f"**分析维度**：实时行情、技术指标、基本面、消息面、风险评估  ",
            "",
            "---",
            "",
            "## 📊 投资建议一览表",
            "",
            "| 股票代码 | 股票名称 | 当前价格 | 涨跌幅 | 综合评分 | 投资建议 | 风险等级 |",
            "|---------|---------|---------|--------|---------|---------|---------|"
        ]
        
        # 按评分排序
        sorted_results = sorted(self.analysis_results.items(), 
                              key=lambda x: x[1]['recommendation']['total_score'], 
                              reverse=True)
        
        for code, analysis in sorted_results:
            rec = analysis['recommendation']
            realtime = analysis['realtime']
            
            report_lines.append(
                f"| {code} | {analysis['name']} | "
                f"{realtime.get('price', 'N/A')} | "
                f"{realtime.get('pct_change', 0):.2f}% | "
                f"{rec['total_score']} | "
                f"{rec['color_code']} **{rec['recommendation']}** | "
                f"{rec['risk_level']['level']} |"
            )
        
        report_lines.extend([
            "",
            "---",
            "",
            "## 📈 详细分析报告",
            ""
        ])
        
        # 详细分析每只股票
        for code, analysis in sorted_results:
            rec = analysis['recommendation']
            realtime = analysis['realtime']
            technical = analysis['technical']
            financial = analysis['financial']
            news = analysis['news']
            
            report_lines.extend([
                f"### {rec['color_code']} {code} - {analysis['name']}",
                "",
                f"**🎯 投资建议**：{rec['recommendation']} (综合评分：{rec['total_score']})",
                "",
                "#### 📊 实时行情",
                f"- **当前价格**：¥{realtime.get('price', 'N/A')}",
                f"- **涨跌幅**：{realtime.get('pct_change', 0):.2f}%",
                f"- **今日区间**：¥{realtime.get('low', 'N/A')} - ¥{realtime.get('high', 'N/A')}",
                f"- **成交量**：{realtime.get('volume', 0)/10000:.1f}万手",
                f"- **换手率**：{realtime.get('turnover_rate', 'N/A')}%",
                f"- **市盈率**：{realtime.get('pe_ratio', 'N/A')}",
                "",
                "#### 🔧 技术分析",
            ])
            
            if technical and 'trend_analysis' in technical:
                trend = technical['trend_analysis']
                report_lines.extend([
                    f"- **均线趋势**：{trend.get('ma_trend', 'N/A')}",
                    f"- **MACD**：{trend.get('macd_trend', 'N/A')}",
                    f"- **RSI状态**：{trend.get('rsi_status', 'N/A')} ({technical.get('RSI', 0):.1f})",
                    f"- **KDJ**：{trend.get('kdj_status', 'N/A')} (K:{technical.get('K', 0):.1f})",
                    f"- **布林带**：{trend.get('bb_position', 'N/A')}",
                    f"- **成交量**：{trend.get('volume_status', 'N/A')}",
                ])
            
            report_lines.extend([
                "",
                "#### 💰 基本面分析",
            ])
            
            if financial:
                roe = financial.get('roe')
                debt_ratio = financial.get('debt_ratio')
                report_lines.extend([
                    f"- **净资产收益率(ROE)**：{roe:.2f}%" if roe else "- **净资产收益率(ROE)**：N/A",
                    f"- **资产负债率**：{debt_ratio:.2f}%" if debt_ratio else "- **资产负债率**：N/A",
                    f"- **毛利率**：{financial.get('gross_margin', 'N/A')}%",
                    f"- **净利率**：{financial.get('net_margin', 'N/A')}%",
                ])
            else:
                report_lines.append("- 基本面数据获取中...")
            
            report_lines.extend([
                "",
                "#### 📰 消息面分析",
            ])
            
            if news:
                report_lines.extend([
                    f"- **新闻关注度**：最近{news.get('news_count', 0)}条相关新闻",
                    f"- **情感倾向**：{news.get('sentiment_score', 0)} (正数偏好，负数偏空)",
                ])
                
                if news.get('latest_news'):
                    report_lines.append("- **热点新闻**：")
                    for i, title in enumerate(news['latest_news'][:3], 1):
                        report_lines.append(f"  {i}. {title}")
            
            report_lines.extend([
                "",
                "#### ⚠️ 风险提示",
                f"- **风险等级**：{rec['risk_level']['level']}",
            ])
            
            if rec['risk_level']['factors']:
                report_lines.append("- **风险因素**：")
                for factor in rec['risk_level']['factors']:
                    report_lines.append(f"  - {factor}")
            
            report_lines.extend([
                "",
                "#### 📋 具体分析依据",
            ])
            
            for detail in rec['detailed_analysis']:
                report_lines.append(f"- {detail}")
            
            report_lines.extend([
                "",
                "---",
                ""
            ])
        
        # 添加总结
        report_lines.extend([
            "## 🎯 投资策略总结",
            "",
            "### 推荐买入",
        ])
        
        buy_stocks = [(code, analysis) for code, analysis in sorted_results 
                     if analysis['recommendation']['recommendation'] in ['强烈买入', '买入']]
        
        if buy_stocks:
            for code, analysis in buy_stocks:
                report_lines.append(f"- **{code} - {analysis['name']}**：{analysis['recommendation']['recommendation']}")
        else:
            report_lines.append("- 暂无推荐买入股票")
        
        report_lines.extend([
            "",
            "### 风险提示",
            "- 本分析仅供参考，不构成投资建议",
            "- 股市有风险，投资需谨慎",
            "- 请根据自身风险承受能力做出投资决策",
            "- 建议设置合理的止损止盈点位",
            "",
            f"### 图表分析",
            f"- 详细图表请查看：{chart_file}",
            "",
            "---",
            f"*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        # 保存报告
        report_content = '\n'.join(report_lines)
        report_file = f'股票综合分析报告_{timestamp}.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 保存JSON数据
        json_file = f'股票分析数据_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📄 分析报告已生成：")
        print(f"  - Markdown报告：{report_file}")
        print(f"  - JSON数据：{json_file}")
        print(f"  - 可视化图表：{chart_file}")
        
        return report_content, chart_file

def main():
    # 分析的股票代码
    stock_codes = ['301217', '002265', '301052', '300308', '300368']
    
    print("🚀 开始全面分析5只股票...")
    print(f"📊 股票代码：{', '.join(stock_codes)}")
    print("🔍 分析维度：实时行情 + 技术指标 + 基本面 + 消息面 + 风险评估")
    print("=" * 60)
    
    # 创建分析器
    analyzer = ComprehensiveStockAnalyzer(stock_codes)
    
    # 执行全面分析
    results = analyzer.analyze_all_stocks()
    
    # 生成综合报告
    report, chart_file = analyzer.generate_comprehensive_report()
    
    # 显示简要结果
    print("\n" + "🎯" * 20)
    print("投资建议汇总")
    print("🎯" * 20)
    
    # 按评分排序显示
    sorted_results = sorted(results.items(), 
                          key=lambda x: x[1]['recommendation']['total_score'], 
                          reverse=True)
    
    for code, analysis in sorted_results:
        rec = analysis['recommendation']
        realtime = analysis['realtime']
        
        print(f"\n{rec['color_code']} {code} - {analysis['name']}")
        print(f"   💡 建议：{rec['recommendation']} (评分：{rec['total_score']})")
        print(f"   💰 价格：¥{realtime.get('price', 'N/A')}  📈 涨跌：{realtime.get('pct_change', 0):.2f}%")
        print(f"   ⚠️  风险：{rec['risk_level']['level']}")

if __name__ == "__main__":
    main()