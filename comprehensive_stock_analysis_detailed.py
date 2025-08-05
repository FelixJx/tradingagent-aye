#!/usr/bin/env python3
"""
使用真实数据对5只股票进行极致详细的多维度分析
股票代码：301217, 002265, 301052, 300308, 300368
"""
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import requests
from bs4 import BeautifulSoup
import time
import math

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class DetailedStockAnalyzer:
    def __init__(self, stock_codes):
        self.stock_codes = stock_codes
        self.stock_names = {}
        self.analysis_results = {}
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        
    def get_stock_basic_info(self):
        """获取股票基本信息"""
        print("=" * 60)
        print("🔍 第一步：获取股票基本信息")
        print("=" * 60)
        
        basic_info = {}
        
        for code in self.stock_codes:
            print(f"\n📊 正在获取 {code} 的基本信息...")
            try:
                # 获取股票基本信息
                info_df = ak.stock_individual_info_em(symbol=code)
                
                basic_data = {}
                for _, row in info_df.iterrows():
                    item = row['item']
                    value = row['value']
                    
                    if '股票简称' in item:
                        basic_data['name'] = value
                        self.stock_names[code] = value
                    elif '所属行业' in item:
                        basic_data['industry'] = value
                    elif '上市时间' in item:
                        basic_data['list_date'] = value
                    elif '总股本' in item:
                        basic_data['total_shares'] = value
                    elif '流通股' in item:
                        basic_data['float_shares'] = value
                    elif '总市值' in item:
                        basic_data['market_cap'] = value
                    elif '流通市值' in item:
                        basic_data['float_market_cap'] = value
                        
                basic_info[code] = basic_data
                print(f"✅ {code} - {basic_data.get('name', 'Unknown')}")
                print(f"   行业: {basic_data.get('industry', 'N/A')}")
                print(f"   上市时间: {basic_data.get('list_date', 'N/A')}")
                print(f"   总市值: {basic_data.get('market_cap', 'N/A')}")
                
            except Exception as e:
                print(f"❌ 获取 {code} 基本信息失败: {e}")
                basic_info[code] = {'name': f'股票{code}'}
                self.stock_names[code] = f'股票{code}'
                
        return basic_info
    
    def get_realtime_data(self):
        """获取实时行情数据"""
        print(f"\n🕒 正在获取实时行情数据...")
        realtime_data = {}
        
        try:
            # 获取A股实时行情
            df = ak.stock_zh_a_spot_em()
            
            for code in self.stock_codes:
                stock_data = df[df['代码'] == code]
                if not stock_data.empty:
                    row = stock_data.iloc[0]
                    
                    realtime_data[code] = {
                        'current_price': float(row['最新价']),
                        'change': float(row['涨跌额']),
                        'pct_change': float(row['涨跌幅']),
                        'open': float(row['今开']),
                        'high': float(row['最高']),
                        'low': float(row['最低']),
                        'pre_close': float(row['昨收']),
                        'volume': float(row['成交量']),
                        'amount': float(row['成交额']),
                        'turnover_rate': float(row['换手率']) if row['换手率'] != '-' else 0,
                        'pe_ttm': float(row['市盈率-动态']) if row['市盈率-动态'] != '-' else None,
                        'pb': float(row['市净率']) if row['市净率'] != '-' else None,
                        'total_mv': float(row['总市值']) if row['总市值'] != '-' else None,
                        'circ_mv': float(row['流通市值']) if row['流通市值'] != '-' else None
                    }
                    
                    print(f"✅ {code}: ¥{row['最新价']} ({row['涨跌幅']:+.2f}%)")
                else:
                    print(f"❌ 未找到 {code} 的实时数据")
                    
        except Exception as e:
            print(f"❌ 获取实时数据失败: {e}")
            
        return realtime_data
    
    def get_historical_data(self, period_days=252):
        """获取历史价格数据"""
        print(f"\n📈 正在获取历史价格数据（{period_days}天）...")
        historical_data = {}
        
        start_date = (datetime.now() - timedelta(days=period_days*2)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')
        
        for code in self.stock_codes:
            try:
                print(f"   正在获取 {code} 历史数据...")
                
                # 获取日线数据
                df = ak.stock_zh_a_hist(
                    symbol=code, 
                    period="daily", 
                    start_date=start_date, 
                    end_date=end_date, 
                    adjust="qfq"
                )
                
                if not df.empty:
                    df['日期'] = pd.to_datetime(df['日期'])
                    df = df.sort_values('日期').tail(period_days)
                    df.reset_index(drop=True, inplace=True)
                    
                    # 重命名列以便后续计算
                    df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'pct_change', 'change', 'turnover']
                    
                    historical_data[code] = df
                    print(f"   ✅ {code}: 获取到 {len(df)} 天数据")
                else:
                    print(f"   ❌ {code}: 未获取到数据")
                    
            except Exception as e:
                print(f"   ❌ {code}: {e}")
                
        return historical_data
    
    def calculate_sma(self, data, period):
        """计算简单移动平均线"""
        return pd.Series(data).rolling(window=period).mean().values
    
    def calculate_ema(self, data, period):
        """计算指数移动平均线"""
        return pd.Series(data).ewm(span=period, adjust=False).mean().values
    
    def calculate_rsi(self, data, period=14):
        """计算RSI指标"""
        delta = pd.Series(data).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return (100 - (100 / (1 + rs))).values
    
    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        """计算MACD指标"""
        exp1 = pd.Series(data).ewm(span=fast, adjust=False).mean()
        exp2 = pd.Series(data).ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd.values, signal_line.values, histogram.values
    
    def calculate_bollinger_bands(self, data, period=20, std_dev=2):
        """计算布林带"""
        sma = pd.Series(data).rolling(window=period).mean()
        std = pd.Series(data).rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper.values, sma.values, lower.values
    
    def calculate_kdj(self, high, low, close, period=9):
        """计算KDJ指标"""
        high_series = pd.Series(high)
        low_series = pd.Series(low)
        close_series = pd.Series(close)
        
        lowest_low = low_series.rolling(window=period).min()
        highest_high = high_series.rolling(window=period).max()
        
        rsv = (close_series - lowest_low) / (highest_high - lowest_low) * 100
        k = rsv.ewm(alpha=1/3, adjust=False).mean()
        d = k.ewm(alpha=1/3, adjust=False).mean()
        j = 3 * k - 2 * d
        
        return k.values, d.values, j.values
    
    def calculate_atr(self, high, low, close, period=14):
        """计算ATR指标"""
        high_series = pd.Series(high)
        low_series = pd.Series(low)
        close_series = pd.Series(close)
        
        tr1 = high_series - low_series
        tr2 = abs(high_series - close_series.shift())
        tr3 = abs(low_series - close_series.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr.values

    def calculate_technical_indicators(self, historical_data):
        """计算全面的技术指标"""
        print(f"\n🔧 正在计算技术指标...")
        technical_data = {}
        
        for code, df in historical_data.items():
            if df.empty or len(df) < 50:
                print(f"   ❌ {code}: 数据不足，跳过技术指标计算")
                continue
                
            print(f"   📊 计算 {code} 的技术指标...")
            
            # 准备价格数据
            close = df['close'].values
            high = df['high'].values
            low = df['low'].values
            volume = df['volume'].values
            
            indicators = {}
            
            try:
                # 1. 移动平均线系列
                indicators['MA5'] = self.calculate_sma(close, 5)
                indicators['MA10'] = self.calculate_sma(close, 10)
                indicators['MA20'] = self.calculate_sma(close, 20)
                indicators['MA30'] = self.calculate_sma(close, 30)
                indicators['MA60'] = self.calculate_sma(close, 60)
                
                # 2. 指数移动平均线
                indicators['EMA12'] = self.calculate_ema(close, 12)
                indicators['EMA26'] = self.calculate_ema(close, 26)
                
                # 3. MACD指标
                macd, macdsignal, macdhist = self.calculate_macd(close)
                indicators['MACD'] = macd
                indicators['MACD_Signal'] = macdsignal
                indicators['MACD_Hist'] = macdhist
                
                # 4. RSI指标
                indicators['RSI6'] = self.calculate_rsi(close, 6)
                indicators['RSI14'] = self.calculate_rsi(close, 14)
                indicators['RSI24'] = self.calculate_rsi(close, 24)
                
                # 5. KDJ指标
                k, d, j = self.calculate_kdj(high, low, close)
                indicators['K'] = k
                indicators['D'] = d
                indicators['J'] = j
                
                # 6. 布林带
                bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(close)
                indicators['BB_Upper'] = bb_upper
                indicators['BB_Middle'] = bb_middle
                indicators['BB_Lower'] = bb_lower
                indicators['BB_Width'] = (bb_upper - bb_lower) / bb_middle * 100
                
                # 7. 威廉指标 (简化版)
                highest_high = pd.Series(high).rolling(window=10).max().values
                lowest_low = pd.Series(low).rolling(window=10).min().values
                indicators['WR10'] = -100 * (highest_high - close) / (highest_high - lowest_low)
                
                # 8. ATR波动率
                indicators['ATR14'] = self.calculate_atr(high, low, close, 14)
                indicators['ATR20'] = self.calculate_atr(high, low, close, 20)
                
                # 9. 成交量指标 (简化OBV)
                price_change = pd.Series(close).diff()
                obv = []
                obv_value = 0
                for i, change in enumerate(price_change):
                    if pd.isna(change):
                        obv.append(obv_value)
                    elif change > 0:
                        obv_value += volume[i]
                        obv.append(obv_value)
                    elif change < 0:
                        obv_value -= volume[i]
                        obv.append(obv_value)
                    else:
                        obv.append(obv_value)
                indicators['OBV'] = np.array(obv)
                
                # 10. 动量指标
                indicators['MOM10'] = pd.Series(close).diff(10).values
                indicators['ROC10'] = pd.Series(close).pct_change(10).values * 100
                
                # 11. 价格通道
                indicators['UPPER_CHANNEL'] = pd.Series(high).rolling(window=20).max().values
                indicators['LOWER_CHANNEL'] = pd.Series(low).rolling(window=20).min().values
                
                # 13. 自定义指标计算
                # 价格相对位置
                latest_price = close[-1]
                indicators['price_position_MA20'] = (latest_price - indicators['MA20'][-1]) / indicators['MA20'][-1] * 100
                indicators['price_position_MA60'] = (latest_price - indicators['MA60'][-1]) / indicators['MA60'][-1] * 100
                
                # 均线排列状态
                ma5_current = indicators['MA5'][-1]
                ma10_current = indicators['MA10'][-1]
                ma20_current = indicators['MA20'][-1]
                ma30_current = indicators['MA30'][-1]
                
                if ma5_current > ma10_current > ma20_current > ma30_current:
                    indicators['ma_alignment'] = "完美多头"
                    indicators['ma_score'] = 100
                elif ma5_current > ma10_current > ma20_current:
                    indicators['ma_alignment'] = "多头排列"
                    indicators['ma_score'] = 80
                elif ma5_current < ma10_current < ma20_current < ma30_current:
                    indicators['ma_alignment'] = "完美空头"
                    indicators['ma_score'] = 0
                elif ma5_current < ma10_current < ma20_current:
                    indicators['ma_alignment'] = "空头排列"
                    indicators['ma_score'] = 20
                else:
                    indicators['ma_alignment'] = "震荡整理"
                    indicators['ma_score'] = 50
                
                # 成交量趋势
                vol_ma5 = np.mean(volume[-5:])
                vol_ma20 = np.mean(volume[-20:])
                indicators['volume_trend'] = vol_ma5 / vol_ma20
                
                technical_data[code] = indicators
                print(f"   ✅ {code}: 计算完成，共{len(indicators)}个指标")
                
            except Exception as e:
                print(f"   ❌ {code}: 技术指标计算失败 - {e}")
                
        return technical_data
    
    def get_financial_data(self):
        """获取财务数据"""
        print(f"\n💰 正在获取财务数据...")
        financial_data = {}
        
        for code in self.stock_codes:
            print(f"   📋 获取 {code} 财务数据...")
            financial_info = {}
            
            try:
                # 获取财务指标
                df_indicator = ak.stock_financial_abstract_ths(symbol=code)
                
                if not df_indicator.empty:
                    # 获取最新的财务数据
                    latest_columns = [col for col in df_indicator.columns if col.startswith('202')]
                    if latest_columns:
                        latest_col = sorted(latest_columns)[-1]
                        
                        for _, row in df_indicator.iterrows():
                            indicator_name = row['指标名称']
                            value = row.get(latest_col, None)
                            
                            # 解析各种财务指标
                            if '净资产收益率' in indicator_name and 'ROE' not in financial_info:
                                financial_info['ROE'] = self.parse_financial_number(value)
                            elif '总资产收益率' in indicator_name:
                                financial_info['ROA'] = self.parse_financial_number(value)
                            elif '毛利率' in indicator_name:
                                financial_info['gross_margin'] = self.parse_financial_number(value)
                            elif '净利率' in indicator_name:
                                financial_info['net_margin'] = self.parse_financial_number(value)
                            elif '资产负债率' in indicator_name:
                                financial_info['debt_ratio'] = self.parse_financial_number(value)
                            elif '流动比率' in indicator_name:
                                financial_info['current_ratio'] = self.parse_financial_number(value)
                            elif '速动比率' in indicator_name:
                                financial_info['quick_ratio'] = self.parse_financial_number(value)
                            elif '营业收入' in indicator_name and '同比增长' in indicator_name:
                                financial_info['revenue_growth'] = self.parse_financial_number(value)
                            elif '净利润' in indicator_name and '同比增长' in indicator_name:
                                financial_info['profit_growth'] = self.parse_financial_number(value)
                            elif '每股收益' in indicator_name:
                                financial_info['EPS'] = self.parse_financial_number(value)
                            elif '每股净资产' in indicator_name:
                                financial_info['BPS'] = self.parse_financial_number(value)
                
                # 获取现金流数据
                try:
                    cashflow_df = ak.stock_cash_flow_sheet_by_yearly_em(symbol=code)
                    if not cashflow_df.empty:
                        latest_cashflow = cashflow_df.iloc[0]
                        financial_info['operating_cashflow'] = self.parse_financial_number(latest_cashflow.get('经营活动产生的现金流量净额', None))
                        financial_info['free_cashflow'] = self.parse_financial_number(latest_cashflow.get('企业自由现金流量', None))
                except:
                    pass
                
                financial_data[code] = financial_info
                print(f"   ✅ {code}: 获取到 {len(financial_info)} 个财务指标")
                
            except Exception as e:
                print(f"   ❌ {code}: 财务数据获取失败 - {e}")
                financial_data[code] = {}
                
        return financial_data
    
    def parse_financial_number(self, value):
        """解析财务数字"""
        if pd.isna(value) or value is None or value == '-':
            return None
        try:
            if isinstance(value, str):
                # 移除百分号和其他符号
                value = value.replace('%', '').replace(',', '').replace('万', '').replace('亿', '')
                if value.strip() == '' or value.strip() == '--':
                    return None
            return float(value)
        except:
            return None
    
    def get_money_flow_data(self):
        """获取资金流向数据"""
        print(f"\n💸 正在获取资金流向数据...")
        money_flow_data = {}
        
        for code in self.stock_codes:
            print(f"   💰 获取 {code} 资金流向...")
            
            try:
                # 获取个股资金流向
                df = ak.stock_individual_fund_flow_rank(symbol="资金流入")
                stock_flow = df[df['代码'] == code]
                
                if not stock_flow.empty:
                    row = stock_flow.iloc[0]
                    money_flow_data[code] = {
                        'net_inflow': float(row.get('净流入-净额', 0)),
                        'main_net_inflow': float(row.get('主力净流入-净额', 0)),
                        'main_net_inflow_rate': float(row.get('主力净流入-净占比', 0)),
                        'super_large_inflow': float(row.get('超大单净流入-净额', 0)),
                        'large_inflow': float(row.get('大单净流入-净额', 0)),
                        'medium_inflow': float(row.get('中单净流入-净额', 0)),
                        'small_inflow': float(row.get('小单净流入-净额', 0))
                    }
                    print(f"   ✅ {code}: 主力净流入 {row.get('主力净流入-净额', 0)} 万元")
                else:
                    print(f"   ⚠️ {code}: 未找到资金流向数据")
                    money_flow_data[code] = {}
                    
            except Exception as e:
                print(f"   ❌ {code}: 资金流向数据获取失败 - {e}")
                money_flow_data[code] = {}
                
        return money_flow_data
    
    def get_news_and_announcements(self):
        """获取新闻和公告"""
        print(f"\n📰 正在获取新闻和公告...")
        news_data = {}
        
        for code in self.stock_codes:
            print(f"   📄 获取 {code} 相关信息...")
            
            try:
                # 获取个股新闻
                news_df = ak.stock_news_em(symbol=code)
                
                if not news_df.empty:
                    recent_news = news_df.head(20)
                    
                    # 简单情感分析
                    positive_keywords = [
                        '利好', '上涨', '增长', '盈利', '业绩', '订单', '合作', '突破', 
                        '创新', '扩张', '收购', '中标', '签约', '涨停', '强势'
                    ]
                    negative_keywords = [
                        '下跌', '亏损', '风险', '减少', '下滑', '困难', '问题', '调查',
                        '处罚', '违规', '停牌', 'ST', '退市', '预警', '跌停'
                    ]
                    
                    sentiment_score = 0
                    news_titles = []
                    
                    for _, news in recent_news.iterrows():
                        title = str(news.get('新闻标题', ''))
                        news_titles.append(title)
                        
                        # 情感评分
                        for word in positive_keywords:
                            sentiment_score += title.count(word) * 2
                        for word in negative_keywords:
                            sentiment_score -= title.count(word) * 2
                    
                    news_data[code] = {
                        'news_count': len(recent_news),
                        'sentiment_score': sentiment_score,
                        'sentiment_level': self.get_sentiment_level(sentiment_score),
                        'recent_news': news_titles[:10],
                        'latest_news_date': recent_news.iloc[0].get('新闻时间', '') if len(recent_news) > 0 else ''
                    }
                    
                    print(f"   ✅ {code}: 获取到 {len(recent_news)} 条新闻，情感评分: {sentiment_score}")
                else:
                    print(f"   ⚠️ {code}: 未找到新闻数据")
                    news_data[code] = {'news_count': 0, 'sentiment_score': 0}
                    
            except Exception as e:
                print(f"   ❌ {code}: 新闻数据获取失败 - {e}")
                news_data[code] = {'news_count': 0, 'sentiment_score': 0}
                
        return news_data
    
    def get_sentiment_level(self, score):
        """获取情感等级"""
        if score >= 10:
            return "非常乐观"
        elif score >= 5:
            return "乐观"
        elif score >= -5:
            return "中性"
        elif score >= -10:
            return "悲观"
        else:
            return "非常悲观"
    
    def calculate_valuation_metrics(self, realtime_data, financial_data):
        """计算估值指标"""
        print(f"\n📊 正在计算估值指标...")
        valuation_data = {}
        
        for code in self.stock_codes:
            print(f"   📈 计算 {code} 估值指标...")
            
            realtime = realtime_data.get(code, {})
            financial = financial_data.get(code, {})
            
            valuation = {}
            
            # 基础估值指标
            if realtime:
                valuation['current_price'] = realtime.get('current_price', 0)
                valuation['market_cap'] = realtime.get('total_mv', 0)  # 亿元
                valuation['pe_ttm'] = realtime.get('pe_ttm', None)
                valuation['pb'] = realtime.get('pb', None)
                
            # 计算其他估值指标
            if financial and realtime:
                eps = financial.get('EPS', None)
                bps = financial.get('BPS', None)
                price = realtime.get('current_price', 0)
                
                # PEG比率
                if eps and financial.get('profit_growth'):
                    pe = price / eps if eps > 0 else None
                    peg = pe / financial.get('profit_growth') if pe and financial.get('profit_growth', 0) > 0 else None
                    valuation['PEG'] = peg
                
                # 股息率（如果有分红数据）
                # 这里需要额外获取分红数据，暂时跳过
                
                # 估值评级
                valuation['valuation_rating'] = self.get_valuation_rating(
                    valuation.get('pe_ttm'), 
                    valuation.get('pb'), 
                    valuation.get('PEG')
                )
            
            valuation_data[code] = valuation
            print(f"   ✅ {code}: PE={valuation.get('pe_ttm', 'N/A')}, PB={valuation.get('pb', 'N/A')}")
            
        return valuation_data
    
    def get_valuation_rating(self, pe, pb, peg):
        """获取估值评级"""
        score = 0
        
        # PE评分
        if pe:
            if pe < 15:
                score += 30
            elif pe < 25:
                score += 20
            elif pe < 35:
                score += 10
            elif pe > 50:
                score -= 20
        
        # PB评分
        if pb:
            if pb < 1.5:
                score += 20
            elif pb < 3:
                score += 10
            elif pb > 5:
                score -= 10
        
        # PEG评分
        if peg:
            if peg < 1:
                score += 20
            elif peg < 1.5:
                score += 10
            elif peg > 2:
                score -= 10
        
        if score >= 50:
            return "严重低估"
        elif score >= 30:
            return "低估"
        elif score >= 10:
            return "合理"
        elif score >= -10:
            return "略高估"
        else:
            return "高估"
    
    def perform_comprehensive_analysis(self):
        """执行综合分析"""
        print("🚀 开始执行极致详细的股票分析...")
        print(f"📅 分析日期: {self.current_date}")
        print(f"🎯 分析标的: {', '.join(self.stock_codes)}")
        
        # 第一步：获取基础数据
        basic_info = self.get_stock_basic_info()
        
        # 更新todo状态
        print(f"\n✅ 第1步完成：基本信息获取")
        
        # 第二步：获取实时行情
        realtime_data = self.get_realtime_data()
        print(f"✅ 第2步完成：实时行情获取")
        
        # 第三步：获取历史数据
        historical_data = self.get_historical_data()
        print(f"✅ 第3步完成：历史数据获取")
        
        # 第四步：计算技术指标
        technical_data = self.calculate_technical_indicators(historical_data)
        print(f"✅ 第4步完成：技术指标计算")
        
        # 第五步：获取财务数据
        financial_data = self.get_financial_data()
        print(f"✅ 第5步完成：财务数据获取")
        
        # 第六步：获取资金流向
        money_flow_data = self.get_money_flow_data()
        print(f"✅ 第6步完成：资金流向获取")
        
        # 第七步：获取新闻数据
        news_data = self.get_news_and_announcements()
        print(f"✅ 第7步完成：新闻数据获取")
        
        # 第八步：计算估值指标
        valuation_data = self.calculate_valuation_metrics(realtime_data, financial_data)
        print(f"✅ 第8步完成：估值指标计算")
        
        # 综合分析结果
        for code in self.stock_codes:
            self.analysis_results[code] = {
                'basic_info': basic_info.get(code, {}),
                'realtime': realtime_data.get(code, {}),
                'historical': historical_data.get(code, pd.DataFrame()),
                'technical': technical_data.get(code, {}),
                'financial': financial_data.get(code, {}),
                'money_flow': money_flow_data.get(code, {}),
                'news': news_data.get(code, {}),
                'valuation': valuation_data.get(code, {})
            }
        
        return self.analysis_results
    
    def generate_detailed_recommendation(self, code):
        """生成详细的投资建议"""
        analysis = self.analysis_results.get(code, {})
        
        # 初始化评分系统
        scores = {
            'technical': 0,
            'fundamental': 0,
            'valuation': 0,
            'momentum': 0,
            'risk': 0,
            'sentiment': 0
        }
        
        detailed_reasons = {
            'positive': [],
            'negative': [],
            'neutral': []
        }
        
        # 技术面评分 (权重25%)
        technical = analysis.get('technical', {})
        if technical:
            # 均线系统
            ma_score = technical.get('ma_score', 50)
            if ma_score >= 80:
                scores['technical'] += 20
                detailed_reasons['positive'].append(f"均线呈{technical.get('ma_alignment', '多头')}，技术形态良好")
            elif ma_score <= 20:
                scores['technical'] -= 20
                detailed_reasons['negative'].append(f"均线呈{technical.get('ma_alignment', '空头')}，技术形态较差")
            
            # RSI指标
            rsi14 = technical.get('RSI14')
            if rsi14 is not None and len(rsi14) > 0:
                current_rsi = rsi14[-1]
                if current_rsi < 30:
                    scores['technical'] += 15
                    detailed_reasons['positive'].append(f"RSI={current_rsi:.1f}，处于超卖区域，有反弹需求")
                elif current_rsi > 70:
                    scores['technical'] -= 15
                    detailed_reasons['negative'].append(f"RSI={current_rsi:.1f}，处于超买区域，有回调风险")
                else:
                    detailed_reasons['neutral'].append(f"RSI={current_rsi:.1f}，处于正常区间")
            
            # MACD
            macd = technical.get('MACD')
            macd_signal = technical.get('MACD_Signal')
            if macd is not None and macd_signal is not None and len(macd) > 0:
                if macd[-1] > macd_signal[-1]:
                    scores['technical'] += 10
                    detailed_reasons['positive'].append("MACD金叉向上，短期趋势向好")
                else:
                    scores['technical'] -= 10
                    detailed_reasons['negative'].append("MACD死叉向下，短期趋势转弱")
        
        # 基本面评分 (权重30%)
        financial = analysis.get('financial', {})
        if financial:
            # ROE
            roe = financial.get('ROE')
            if roe is not None:
                if roe > 15:
                    scores['fundamental'] += 25
                    detailed_reasons['positive'].append(f"ROE={roe:.2f}%，盈利能力优秀")
                elif roe > 10:
                    scores['fundamental'] += 15
                    detailed_reasons['positive'].append(f"ROE={roe:.2f}%，盈利能力良好")
                elif roe < 5:
                    scores['fundamental'] -= 15
                    detailed_reasons['negative'].append(f"ROE={roe:.2f}%，盈利能力偏弱")
            
            # 成长性
            revenue_growth = financial.get('revenue_growth')
            profit_growth = financial.get('profit_growth')
            
            if revenue_growth is not None and revenue_growth > 20:
                scores['fundamental'] += 15
                detailed_reasons['positive'].append(f"营收增长率{revenue_growth:.1f}%，成长性良好")
            elif revenue_growth is not None and revenue_growth < 0:
                scores['fundamental'] -= 15
                detailed_reasons['negative'].append(f"营收增长率{revenue_growth:.1f}%，增长乏力")
            
            if profit_growth is not None and profit_growth > 30:
                scores['fundamental'] += 20
                detailed_reasons['positive'].append(f"净利润增长率{profit_growth:.1f}%，盈利增长强劲")
            elif profit_growth is not None and profit_growth < 0:
                scores['fundamental'] -= 20
                detailed_reasons['negative'].append(f"净利润增长率{profit_growth:.1f}%，盈利下滑")
            
            # 财务健康度
            debt_ratio = financial.get('debt_ratio')
            if debt_ratio is not None:
                if debt_ratio < 30:
                    scores['fundamental'] += 10
                    detailed_reasons['positive'].append(f"资产负债率{debt_ratio:.1f}%，财务结构健康")
                elif debt_ratio > 70:
                    scores['fundamental'] -= 15
                    detailed_reasons['negative'].append(f"资产负债率{debt_ratio:.1f}%，负债率偏高")
        
        # 估值评分 (权重20%)
        valuation = analysis.get('valuation', {})
        if valuation:
            pe_ttm = valuation.get('pe_ttm')
            pb = valuation.get('pb')
            
            if pe_ttm is not None:
                if pe_ttm < 15:
                    scores['valuation'] += 20
                    detailed_reasons['positive'].append(f"PE={pe_ttm:.1f}，估值偏低")
                elif pe_ttm < 25:
                    scores['valuation'] += 10
                    detailed_reasons['positive'].append(f"PE={pe_ttm:.1f}，估值合理")
                elif pe_ttm > 50:
                    scores['valuation'] -= 20
                    detailed_reasons['negative'].append(f"PE={pe_ttm:.1f}，估值偏高")
            
            if pb is not None:
                if pb < 1.5:
                    scores['valuation'] += 15
                    detailed_reasons['positive'].append(f"PB={pb:.2f}，破净或接近净资产")
                elif pb > 5:
                    scores['valuation'] -= 10
                    detailed_reasons['negative'].append(f"PB={pb:.2f}，市净率偏高")
        
        # 资金面评分 (权重15%)
        money_flow = analysis.get('money_flow', {})
        if money_flow:
            main_inflow = money_flow.get('main_net_inflow', 0)
            if main_inflow > 0:
                scores['momentum'] += 15
                detailed_reasons['positive'].append(f"主力资金净流入{main_inflow:.0f}万元")
            elif main_inflow < -10000:  # 超过1亿流出
                scores['momentum'] -= 15
                detailed_reasons['negative'].append(f"主力资金大幅流出{abs(main_inflow):.0f}万元")
        
        # 情感面评分 (权重10%)
        news = analysis.get('news', {})
        if news:
            sentiment_score = news.get('sentiment_score', 0)
            if sentiment_score > 10:
                scores['sentiment'] += 10
                detailed_reasons['positive'].append(f"新闻情感{news.get('sentiment_level', '乐观')}，市场关注度高")
            elif sentiment_score < -10:
                scores['sentiment'] -= 10
                detailed_reasons['negative'].append(f"新闻情感{news.get('sentiment_level', '悲观')}，负面消息较多")
        
        # 计算总分
        total_score = (
            scores['technical'] * 0.25 +
            scores['fundamental'] * 0.30 +
            scores['valuation'] * 0.20 +
            scores['momentum'] * 0.15 +
            scores['sentiment'] * 0.10
        )
        
        # 风险评估
        risk_factors = []
        realtime = analysis.get('realtime', {})
        
        if realtime.get('pct_change', 0) > 5:
            risk_factors.append("短期涨幅较大，注意回调风险")
        
        if valuation.get('pe_ttm', 0) > 60:
            risk_factors.append("估值偏高，存在泡沫风险")
        
        if financial.get('debt_ratio', 0) > 80:
            risk_factors.append("负债率过高，财务风险较大")
        
        # 生成投资建议
        if total_score >= 60:
            recommendation = "强烈买入"
            confidence = "高"
        elif total_score >= 30:
            recommendation = "买入"
            confidence = "中高"
        elif total_score >= 0:
            recommendation = "持有观望"
            confidence = "中等"
        elif total_score >= -30:
            recommendation = "减持"
            confidence = "中高"
        else:
            recommendation = "卖出"
            confidence = "高"
        
        return {
            'recommendation': recommendation,
            'total_score': total_score,
            'confidence': confidence,
            'detailed_scores': scores,
            'positive_factors': detailed_reasons['positive'],
            'negative_factors': detailed_reasons['negative'],
            'neutral_factors': detailed_reasons['neutral'],
            'risk_factors': risk_factors,
            'target_price': self.calculate_target_price(analysis),
            'stop_loss': self.calculate_stop_loss(analysis)
        }
    
    def calculate_target_price(self, analysis):
        """计算目标价格"""
        try:
            realtime = analysis.get('realtime', {})
            current_price = realtime.get('current_price', 0)
            
            if current_price == 0:
                return None
            
            # 基于技术分析的目标价
            technical = analysis.get('technical', {})
            if technical and 'BB_Upper' in technical:
                bb_upper = technical['BB_Upper']
                if bb_upper is not None and len(bb_upper) > 0:
                    technical_target = bb_upper[-1]
                else:
                    technical_target = current_price * 1.15
            else:
                technical_target = current_price * 1.15
            
            # 基于估值的目标价
            financial = analysis.get('financial', {})
            if financial.get('EPS') and financial.get('profit_growth'):
                # 使用PEG模型
                eps = financial['EPS']
                growth = financial['profit_growth']
                reasonable_pe = min(growth * 1.2, 30)  # 合理PE不超过30
                fundamental_target = eps * reasonable_pe
            else:
                fundamental_target = current_price * 1.20
            
            # 综合目标价
            target_price = (technical_target + fundamental_target) / 2
            
            # 限制目标价涨幅在50%以内
            max_target = current_price * 1.5
            return min(target_price, max_target)
            
        except:
            return None
    
    def calculate_stop_loss(self, analysis):
        """计算止损价格"""
        try:
            realtime = analysis.get('realtime', {})
            current_price = realtime.get('current_price', 0)
            
            if current_price == 0:
                return None
            
            # 基于ATR的止损
            technical = analysis.get('technical', {})
            if technical and 'ATR14' in technical:
                atr = technical['ATR14']
                if atr is not None and len(atr) > 0:
                    stop_loss = current_price - (atr[-1] * 2)
                else:
                    stop_loss = current_price * 0.90
            else:
                stop_loss = current_price * 0.90
            
            # 基于支撑位的止损
            if technical and 'MA20' in technical:
                ma20 = technical['MA20']
                if ma20 is not None and len(ma20) > 0:
                    ma20_support = ma20[-1] * 0.95
                    stop_loss = max(stop_loss, ma20_support)
            
            return max(stop_loss, current_price * 0.85)  # 最大止损15%
            
        except:
            return None

def main():
    stock_codes = ['301217', '002265', '301052', '300308', '300368']
    
    print("🎯 开始极致详细的5只股票分析")
    print("=" * 80)
    
    analyzer = DetailedStockAnalyzer(stock_codes)
    
    # 执行综合分析
    results = analyzer.perform_comprehensive_analysis()
    
    print(f"\n" + "🏆" * 30)
    print("综合分析结果")
    print("🏆" * 30)
    
    # 生成每只股票的详细建议
    recommendations = {}
    for code in stock_codes:
        print(f"\n{'='*60}")
        print(f"📊 {code} - {analyzer.stock_names.get(code, 'Unknown')} 详细分析")
        print(f"{'='*60}")
        
        recommendation = analyzer.generate_detailed_recommendation(code)
        recommendations[code] = recommendation
        
        # 输出详细分析结果
        print(f"🎯 投资建议: {recommendation['recommendation']}")
        print(f"📊 综合评分: {recommendation['total_score']:.1f}")
        print(f"🔍 置信度: {recommendation['confidence']}")
        
        if recommendation.get('target_price'):
            print(f"🎯 目标价格: ¥{recommendation['target_price']:.2f}")
        if recommendation.get('stop_loss'):
            print(f"🛑 止损价格: ¥{recommendation['stop_loss']:.2f}")
        
        print(f"\n✅ 积极因素:")
        for factor in recommendation['positive_factors']:
            print(f"   • {factor}")
        
        print(f"\n⚠️ 消极因素:")
        for factor in recommendation['negative_factors']:
            print(f"   • {factor}")
        
        if recommendation['risk_factors']:
            print(f"\n🚨 风险提示:")
            for risk in recommendation['risk_factors']:
                print(f"   • {risk}")
    
    # 按评分排序并输出投资建议
    sorted_recommendations = sorted(
        recommendations.items(), 
        key=lambda x: x[1]['total_score'], 
        reverse=True
    )
    
    print(f"\n" + "🏅" * 30)
    print("最终投资排序建议")
    print("🏅" * 30)
    
    for i, (code, rec) in enumerate(sorted_recommendations, 1):
        name = analyzer.stock_names.get(code, 'Unknown')
        realtime = results.get(code, {}).get('realtime', {})
        price = realtime.get('current_price', 0)
        change = realtime.get('pct_change', 0)
        
        print(f"\n【第{i}位】{code} - {name}")
        print(f"💰 当前价格: ¥{price:.2f} ({change:+.2f}%)")
        print(f"🎯 投资建议: {rec['recommendation']} (评分: {rec['total_score']:.1f})")
        
        if rec.get('target_price'):
            upside = (rec['target_price'] - price) / price * 100
            print(f"📈 上涨空间: {upside:.1f}%")
    
    # 保存详细报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 保存分析结果
    with open(f'详细股票分析_{timestamp}.json', 'w', encoding='utf-8') as f:
        # 转换DataFrame为dict以便JSON序列化
        results_for_json = {}
        for code, data in results.items():
            results_for_json[code] = {}
            for key, value in data.items():
                if isinstance(value, pd.DataFrame):
                    results_for_json[code][key] = value.to_dict('records') if not value.empty else []
                elif isinstance(value, np.ndarray):
                    results_for_json[code][key] = value.tolist()
                else:
                    results_for_json[code][key] = value
        
        json.dump({
            'analysis_results': results_for_json,
            'recommendations': recommendations,
            'analysis_date': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n📄 详细分析报告已保存: 详细股票分析_{timestamp}.json")
    
    return results, recommendations

if __name__ == "__main__":
    main()