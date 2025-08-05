# -*- coding: utf-8 -*-
"""
简化版回测测试
"""

import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime

def test_agent_backtest():
    """测试Agent回测"""
    # 设置token
    ts.set_token('b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065')
    pro = ts.pro_api()
    
    print("开始获取股票数据...")
    
    # 获取平安银行2年数据
    df = pro.daily(ts_code='000001.SZ', start_date='20220101', end_date='20240131')
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    
    print("获取数据成功，共{}个交易日".format(len(df)))
    print("数据时间范围: {} 到 {}".format(df['trade_date'].min(), df['trade_date'].max()))
    
    # 计算基础技术指标
    print("计算技术指标...")
    
    # 移动平均线
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['close'].ewm(span=12).mean()
    exp2 = df['close'].ewm(span=26).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    
    # 成交量指标
    df['vol_ma5'] = df['vol'].rolling(5).mean()
    df['vol_ratio'] = df['vol'] / df['vol_ma5']
    
    print("开始模拟Agent预测...")
    
    # 模拟市场分析师预测
    predictions = []
    
    for i in range(60, len(df)):  # 需要足够历史数据
        row = df.iloc[i]
        
        # 简单的技术分析逻辑
        signals = []
        
        # MACD信号
        if row['macd'] > row['macd_signal'] and df.iloc[i-1]['macd'] <= df.iloc[i-1]['macd_signal']:
            signals.append('MACD_GOLDEN')
        elif row['macd'] < row['macd_signal'] and df.iloc[i-1]['macd'] >= df.iloc[i-1]['macd_signal']:
            signals.append('MACD_DEATH')
        
        # 均线信号
        if row['close'] > row['ma20'] and row['ma5'] > row['ma10']:
            signals.append('MA_BULLISH')
        elif row['close'] < row['ma20'] and row['ma5'] < row['ma10']:
            signals.append('MA_BEARISH')
        
        # RSI信号
        if row['rsi'] < 30:
            signals.append('RSI_OVERSOLD')
        elif row['rsi'] > 70:
            signals.append('RSI_OVERBOUGHT')
        
        # 成交量信号
        if row['vol_ratio'] > 1.5:
            signals.append('VOL_SURGE')
        
        # 生成预测
        bullish_signals = ['MACD_GOLDEN', 'MA_BULLISH', 'RSI_OVERSOLD', 'VOL_SURGE']
        bearish_signals = ['MACD_DEATH', 'MA_BEARISH', 'RSI_OVERBOUGHT']
        
        bull_count = sum(1 for s in signals if s in bullish_signals)
        bear_count = sum(1 for s in signals if s in bearish_signals)
        
        if bull_count > bear_count and bull_count >= 2:
            prediction = 'BUY'
        elif bear_count > bull_count and bear_count >= 2:
            prediction = 'SELL'
        else:
            prediction = 'HOLD'
        
        predictions.append({
            'index': i,
            'date': row['trade_date'],
            'prediction': prediction,
            'signals': signals,
            'close': row['close'],
            'rsi': row['rsi'],
            'macd': row['macd']
        })
    
    print("生成{}个预测".format(len(predictions)))
    
    # 计算预测准确性
    print("计算预测准确性...")
    
    correct_predictions = 0
    returns_1d = []
    returns_5d = []
    returns_20d = []
    
    for pred in predictions:
        idx = pred['index']
        prediction_type = pred['prediction']
        
        # 计算未来收益率
        if idx + 1 < len(df):
            ret_1d = (df.iloc[idx + 1]['close'] - df.iloc[idx]['close']) / df.iloc[idx]['close']
            returns_1d.append(ret_1d)
            
            # 简单的准确性判断
            if prediction_type == 'BUY' and ret_1d > 0.01:  # 1%阈值
                correct_predictions += 1
            elif prediction_type == 'SELL' and ret_1d < -0.01:
                correct_predictions += 1
            elif prediction_type == 'HOLD' and abs(ret_1d) <= 0.01:
                correct_predictions += 1
        
        if idx + 5 < len(df):
            ret_5d = (df.iloc[idx + 5]['close'] - df.iloc[idx]['close']) / df.iloc[idx]['close']
            returns_5d.append(ret_5d)
        
        if idx + 20 < len(df):
            ret_20d = (df.iloc[idx + 20]['close'] - df.iloc[idx]['close']) / df.iloc[idx]['close']
            returns_20d.append(ret_20d)
    
    # 计算结果
    accuracy = correct_predictions / len(predictions) if predictions else 0
    avg_return_1d = np.mean(returns_1d) if returns_1d else 0
    avg_return_5d = np.mean(returns_5d) if returns_5d else 0
    avg_return_20d = np.mean(returns_20d) if returns_20d else 0
    
    # 输出结果
    print("\n" + "="*50)
    print("回测结果 - 000001.SZ 平安银行 (2022-2024)")
    print("="*50)
    print("总预测次数: {}".format(len(predictions)))
    print("正确预测次数: {}".format(correct_predictions))
    print("预测准确率: {:.2%}".format(accuracy))
    print("1日平均收益率: {:.2%}".format(avg_return_1d))
    print("5日平均收益率: {:.2%}".format(avg_return_5d))
    print("20日平均收益率: {:.2%}".format(avg_return_20d))
    
    # 分析预测分布
    buy_count = sum(1 for p in predictions if p['prediction'] == 'BUY')
    sell_count = sum(1 for p in predictions if p['prediction'] == 'SELL')
    hold_count = sum(1 for p in predictions if p['prediction'] == 'HOLD')
    
    print("\n预测分布:")
    print("BUY: {} ({:.1%})".format(buy_count, buy_count/len(predictions)))
    print("SELL: {} ({:.1%})".format(sell_count, sell_count/len(predictions)))
    print("HOLD: {} ({:.1%})".format(hold_count, hold_count/len(predictions)))
    
    # 显示一些具体预测示例
    print("\n最近10个预测示例:")
    for pred in predictions[-10:]:
        print("{}: {} (信号: {}) 收盘价: {:.2f}".format(
            pred['date'].strftime('%Y-%m-%d'), 
            pred['prediction'],
            pred['signals'], 
            pred['close']
        ))
    
    return {
        'total_predictions': len(predictions),
        'accuracy': accuracy,
        'avg_return_1d': avg_return_1d,
        'avg_return_5d': avg_return_5d,
        'avg_return_20d': avg_return_20d,
        'predictions': predictions
    }

if __name__ == "__main__":
    result = test_agent_backtest()