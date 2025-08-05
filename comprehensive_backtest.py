# -*- coding: utf-8 -*-
"""
综合回测分析 - 测试多只股票和多种Agent策略
"""

import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime
import json

def initialize_tushare():
    """初始化tushare"""
    ts.set_token('b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065')
    return ts.pro_api()

def calculate_technical_indicators(df):
    """计算技术指标"""
    # 移动平均线
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    df['ma60'] = df['close'].rolling(60).mean()
    
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
    df['vol_ma20'] = df['vol'].rolling(20).mean()
    df['vol_ratio'] = df['vol'] / df['vol_ma20']
    
    # 布林带
    df['bb_middle'] = df['close'].rolling(20).mean()
    bb_std = df['close'].rolling(20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    
    return df

def market_analyst_strategy(df, i):
    """市场分析师策略 - 基于技术指标"""
    row = df.iloc[i]
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
    if row['vol_ratio'] > 1.8:
        signals.append('VOL_SURGE')
    
    # 布林带信号
    if row['close'] < row['bb_lower']:
        signals.append('BB_OVERSOLD')
    elif row['close'] > row['bb_upper']:
        signals.append('BB_OVERBOUGHT')
    
    # 生成预测
    bullish_signals = ['MACD_GOLDEN', 'MA_BULLISH', 'RSI_OVERSOLD', 'VOL_SURGE', 'BB_OVERSOLD']
    bearish_signals = ['MACD_DEATH', 'MA_BEARISH', 'RSI_OVERBOUGHT', 'BB_OVERBOUGHT']
    
    bull_count = sum(1 for s in signals if s in bullish_signals)
    bear_count = sum(1 for s in signals if s in bearish_signals)
    
    if bull_count >= 2 and bull_count > bear_count:
        return 'BUY', signals
    elif bear_count >= 2 and bear_count > bull_count:
        return 'SELL', signals
    else:
        return 'HOLD', signals

def fundamental_analyst_strategy(df, i):
    """基本面分析师策略 - 简化版"""
    row = df.iloc[i]
    
    # 基于价格相对位置和成交量的简化基本面分析
    signals = []
    
    # 价格趋势
    if row['close'] > row['ma60']:
        signals.append('LONG_TERM_UPTREND')
    elif row['close'] < row['ma60']:
        signals.append('LONG_TERM_DOWNTREND')
    
    # 成交量确认
    if row['vol_ratio'] > 1.2:
        signals.append('VOLUME_CONFIRM')
    
    # 相对强度
    recent_high = df['close'].iloc[max(0, i-20):i+1].max()
    recent_low = df['close'].iloc[max(0, i-20):i+1].min()
    position = (row['close'] - recent_low) / (recent_high - recent_low) if recent_high != recent_low else 0.5
    
    if position > 0.8:
        signals.append('NEAR_HIGH')
    elif position < 0.2:
        signals.append('NEAR_LOW')
    
    # 决策逻辑
    if 'LONG_TERM_UPTREND' in signals and 'VOLUME_CONFIRM' in signals and 'NEAR_LOW' in signals:
        return 'BUY', signals
    elif 'LONG_TERM_DOWNTREND' in signals and 'NEAR_HIGH' in signals:
        return 'SELL', signals
    else:
        return 'HOLD', signals

def bull_researcher_strategy(df, i):
    """多头研究员策略 - 偏向看涨"""
    row = df.iloc[i]
    signals = []
    
    # 多头偏向逻辑
    if row['ma5'] > row['ma10'] > row['ma20']:
        signals.append('TRIPLE_MA_BULLISH')
    
    if row['close'] > row['ma20'] * 1.02:  # 突破2%
        signals.append('BREAKOUT')
    
    if row['vol_ratio'] > 1.5:
        signals.append('HIGH_VOLUME')
    
    if row['rsi'] < 50 and row['close'] > row['ma5']:  # RSI不过热但价格强势
        signals.append('RSI_HEALTHY')
    
    # 多头研究员更倾向于买入
    if len(signals) >= 2:
        return 'BUY', signals
    elif len(signals) == 1:
        return 'BUY', signals  # 更激进
    else:
        return 'HOLD', signals

def bear_researcher_strategy(df, i):
    """空头研究员策略 - 偏向看跌"""
    row = df.iloc[i]
    signals = []
    
    # 空头偏向逻辑
    if row['ma5'] < row['ma10'] < row['ma20']:
        signals.append('TRIPLE_MA_BEARISH')
    
    if row['close'] < row['ma20'] * 0.98:  # 跌破2%
        signals.append('BREAKDOWN')
    
    if row['rsi'] > 70:
        signals.append('RSI_OVERBOUGHT')
    
    if row['vol_ratio'] > 1.5 and row['close'] < row['open']:  # 放量下跌
        signals.append('VOLUME_SELL_OFF')
    
    # 空头研究员更倾向于卖出
    if len(signals) >= 2:
        return 'SELL', signals
    elif len(signals) == 1:
        return 'SELL', signals  # 更激进
    else:
        return 'HOLD', signals

def backtest_stock(pro, stock_code, stock_name, start_date, end_date):
    """回测单只股票"""
    print("正在回测 {} - {}".format(stock_code, stock_name))
    
    try:
        # 获取数据
        df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values('trade_date').reset_index(drop=True)
        
        if len(df) < 100:  # 数据不足
            print("数据不足，跳过")
            return None
        
        # 计算技术指标
        df = calculate_technical_indicators(df)
        
        # 定义Agent策略
        strategies = {
            'market_analyst': market_analyst_strategy,
            'fundamental_analyst': fundamental_analyst_strategy,
            'bull_researcher': bull_researcher_strategy,
            'bear_researcher': bear_researcher_strategy
        }
        
        results = {}
        
        # 对每种策略进行回测
        for strategy_name, strategy_func in strategies.items():
            predictions = []
            
            # 生成预测
            for i in range(60, len(df)):  # 需要足够历史数据
                try:
                    prediction, signals = strategy_func(df, i)
                    predictions.append({
                        'index': i,
                        'date': df.iloc[i]['trade_date'],
                        'prediction': prediction,
                        'signals': signals,
                        'close': df.iloc[i]['close']
                    })
                except:
                    continue
            
            if not predictions:
                continue
            
            # 计算准确性和收益
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
                    
                    # 判断预测准确性
                    if prediction_type == 'BUY' and ret_1d > 0.015:  # 1.5%阈值
                        correct_predictions += 1
                    elif prediction_type == 'SELL' and ret_1d < -0.015:
                        correct_predictions += 1
                    elif prediction_type == 'HOLD' and abs(ret_1d) <= 0.015:
                        correct_predictions += 1
                
                if idx + 5 < len(df):
                    ret_5d = (df.iloc[idx + 5]['close'] - df.iloc[idx]['close']) / df.iloc[idx]['close']
                    returns_5d.append(ret_5d)
                
                if idx + 20 < len(df):
                    ret_20d = (df.iloc[idx + 20]['close'] - df.iloc[idx]['close']) / df.iloc[idx]['close']
                    returns_20d.append(ret_20d)
            
            # 统计结果
            accuracy = correct_predictions / len(predictions) if predictions else 0
            avg_return_1d = np.mean(returns_1d) if returns_1d else 0
            avg_return_5d = np.mean(returns_5d) if returns_5d else 0
            avg_return_20d = np.mean(returns_20d) if returns_20d else 0
            
            # 预测分布
            buy_count = sum(1 for p in predictions if p['prediction'] == 'BUY')
            sell_count = sum(1 for p in predictions if p['prediction'] == 'SELL')
            hold_count = sum(1 for p in predictions if p['prediction'] == 'HOLD')
            
            results[strategy_name] = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'total_predictions': len(predictions),
                'correct_predictions': correct_predictions,
                'accuracy': accuracy,
                'avg_return_1d': avg_return_1d,
                'avg_return_5d': avg_return_5d,
                'avg_return_20d': avg_return_20d,
                'buy_ratio': buy_count / len(predictions),
                'sell_ratio': sell_count / len(predictions),
                'hold_ratio': hold_count / len(predictions)
            }
        
        return results
        
    except Exception as e:
        print("回测失败: {}".format(e))
        return None

def run_comprehensive_backtest():
    """运行综合回测"""
    print("开始综合Agent回测分析...")
    
    # 初始化
    pro = initialize_tushare()
    
    # 测试股票列表 (代表性股票)
    test_stocks = [
        ('000001.SZ', '平安银行'),
        ('000002.SZ', '万科A'),
        ('600000.SH', '浦发银行'),
        ('600036.SH', '招商银行'),
        ('000858.SZ', '五粮液'),
        ('600519.SH', '贵州茅台'),
        ('000651.SZ', '格力电器'),
        ('002415.SZ', '海康威视')
    ]
    
    # 回测时间段
    start_date = '20220101'
    end_date = '20240131'
    
    all_results = {}
    
    # 回测每只股票
    for stock_code, stock_name in test_stocks:
        stock_results = backtest_stock(pro, stock_code, stock_name, start_date, end_date)
        if stock_results:
            all_results[stock_code] = stock_results
    
    # 汇总分析
    print("\n" + "="*80)
    print("综合回测结果汇总")
    print("="*80)
    
    # 按Agent类型汇总
    agent_summary = {}
    for stock_code, stock_results in all_results.items():
        for agent_type, result in stock_results.items():
            if agent_type not in agent_summary:
                agent_summary[agent_type] = {
                    'total_predictions': 0,
                    'correct_predictions': 0,
                    'returns_1d': [],
                    'returns_5d': [],
                    'returns_20d': [],
                    'buy_ratios': [],
                    'sell_ratios': [],
                    'hold_ratios': []
                }
            
            agent_summary[agent_type]['total_predictions'] += result['total_predictions']
            agent_summary[agent_type]['correct_predictions'] += result['correct_predictions']
            agent_summary[agent_type]['returns_1d'].append(result['avg_return_1d'])
            agent_summary[agent_type]['returns_5d'].append(result['avg_return_5d'])
            agent_summary[agent_type]['returns_20d'].append(result['avg_return_20d'])
            agent_summary[agent_type]['buy_ratios'].append(result['buy_ratio'])
            agent_summary[agent_type]['sell_ratios'].append(result['sell_ratio'])
            agent_summary[agent_type]['hold_ratios'].append(result['hold_ratio'])
    
    # 输出汇总结果
    print("Agent类型 | 预测准确率 | 1日收益率 | 5日收益率 | 20日收益率 | BUY比例 | SELL比例 | HOLD比例")
    print("-" * 80)
    
    for agent_type, summary in agent_summary.items():
        accuracy = summary['correct_predictions'] / summary['total_predictions'] if summary['total_predictions'] > 0 else 0
        avg_return_1d = np.mean(summary['returns_1d'])
        avg_return_5d = np.mean(summary['returns_5d'])
        avg_return_20d = np.mean(summary['returns_20d'])
        avg_buy_ratio = np.mean(summary['buy_ratios'])
        avg_sell_ratio = np.mean(summary['sell_ratios'])
        avg_hold_ratio = np.mean(summary['hold_ratios'])
        
        print("{:<15} | {:>8.2%} | {:>8.2%} | {:>8.2%} | {:>9.2%} | {:>7.1%} | {:>8.1%} | {:>8.1%}".format(
            agent_type, accuracy, avg_return_1d, avg_return_5d, avg_return_20d,
            avg_buy_ratio, avg_sell_ratio, avg_hold_ratio
        ))
    
    # 详细个股结果
    print("\n详细个股结果:")
    print("="*80)
    
    for stock_code, stock_results in all_results.items():
        print("\n{}:".format(stock_code))
        for agent_type, result in stock_results.items():
            print("  {}: 准确率 {:.2%}, 20日收益 {:.2%}, 预测 {} 次".format(
                agent_type, 
                result['accuracy'], 
                result['avg_return_20d'],
                result['total_predictions']
            ))
    
    # 保存结果到JSON
    with open('comprehensive_backtest_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {k: {
                'accuracy': v['correct_predictions'] / v['total_predictions'] if v['total_predictions'] > 0 else 0,
                'avg_return_1d': float(np.mean(v['returns_1d'])),
                'avg_return_5d': float(np.mean(v['returns_5d'])),
                'avg_return_20d': float(np.mean(v['returns_20d'])),
                'avg_buy_ratio': float(np.mean(v['buy_ratios'])),
                'avg_sell_ratio': float(np.mean(v['sell_ratios'])),
                'avg_hold_ratio': float(np.mean(v['hold_ratios']))
            } for k, v in agent_summary.items()},
            'detailed_results': all_results
        }, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n结果已保存到 comprehensive_backtest_results.json")
    
    return all_results, agent_summary

if __name__ == "__main__":
    results, summary = run_comprehensive_backtest()