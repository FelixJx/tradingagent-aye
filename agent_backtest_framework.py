# -*- coding: utf-8 -*-
"""
智能体回测框架 - 评估股票分析Agent的准确性
基于tushare真实数据的历史回测系统
"""

import tushare as ts
import pandas as pd
import numpy as np
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class AgentBacktestFramework:
    """
    Agent回测框架主类
    """
    
    def __init__(self, tushare_token: str):
        """
        初始化回测框架
        
        Args:
            tushare_token: tushare API token
        """
        ts.set_token(tushare_token)
        self.pro = ts.pro_api()
        self.db_path = "agent_backtest.db"
        self._init_database()
        
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建回测结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_type TEXT,
                stock_code TEXT,
                analysis_date TEXT,
                prediction_type TEXT,
                prediction_confidence REAL,
                actual_return_1d REAL,
                actual_return_5d REAL,
                actual_return_20d REAL,
                prediction_accuracy INTEGER,
                analysis_features TEXT,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建Agent分析历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_type TEXT,
                stock_code TEXT,
                analysis_date TEXT,
                analysis_result TEXT,
                key_indicators TEXT,
                prediction TEXT,
                confidence_score REAL,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_stock_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取股票历史数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            股票数据DataFrame
        """
        try:
            df = self.pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df = df.sort_values('trade_date')
            return df
        except Exception as e:
            print(f"获取股票数据失败: {e}")
            return pd.DataFrame()
    
    def get_financial_data(self, stock_code: str, period: str = '20231231') -> Dict:
        """
        获取财务数据
        
        Args:
            stock_code: 股票代码
            period: 报告期
            
        Returns:
            财务数据字典
        """
        try:
            # 获取利润表数据
            income = self.pro.income(ts_code=stock_code, period=period)
            # 获取资产负债表数据
            balancesheet = self.pro.balancesheet(ts_code=stock_code, period=period)
            # 获取现金流量表数据
            cashflow = self.pro.cashflow(ts_code=stock_code, period=period)
            
            return {
                'income': income.to_dict('records')[0] if not income.empty else {},
                'balance': balancesheet.to_dict('records')[0] if not balancesheet.empty else {},
                'cashflow': cashflow.to_dict('records')[0] if not cashflow.empty else {}
            }
        except Exception as e:
            print(f"获取财务数据失败: {e}")
            return {}
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            df: 股票价格数据
            
        Returns:
            添加技术指标的DataFrame
        """
        if df.empty:
            return df
            
        # 移动平均线
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # 布林带
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # 成交量相关指标
        df['vol_ma5'] = df['vol'].rolling(window=5).mean()
        df['vol_ratio'] = df['vol'] / df['vol_ma5']
        
        return df
    
    def analyze_agent_performance(self, agent_type: str, stock_codes: List[str], 
                                start_date: str, end_date: str) -> Dict:
        """
        分析Agent性能
        
        Args:
            agent_type: Agent类型
            stock_codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            性能分析结果
        """
        results = {
            'agent_type': agent_type,
            'total_predictions': 0,
            'correct_predictions': 0,
            'accuracy': 0.0,
            'avg_return_1d': 0.0,
            'avg_return_5d': 0.0,
            'avg_return_20d': 0.0,
            'stock_results': []
        }
        
        for stock_code in stock_codes:
            stock_result = self._backtest_single_stock(agent_type, stock_code, start_date, end_date)
            if stock_result:
                results['stock_results'].append(stock_result)
                results['total_predictions'] += stock_result['total_predictions']
                results['correct_predictions'] += stock_result['correct_predictions']
        
        if results['total_predictions'] > 0:
            results['accuracy'] = results['correct_predictions'] / results['total_predictions']
            
            # 计算平均收益
            all_returns_1d = []
            all_returns_5d = []
            all_returns_20d = []
            
            for stock_result in results['stock_results']:
                all_returns_1d.extend(stock_result['returns_1d'])
                all_returns_5d.extend(stock_result['returns_5d'])
                all_returns_20d.extend(stock_result['returns_20d'])
            
            results['avg_return_1d'] = np.mean(all_returns_1d) if all_returns_1d else 0.0
            results['avg_return_5d'] = np.mean(all_returns_5d) if all_returns_5d else 0.0
            results['avg_return_20d'] = np.mean(all_returns_20d) if all_returns_20d else 0.0
        
        return results
    
    def _backtest_single_stock(self, agent_type: str, stock_code: str, 
                              start_date: str, end_date: str) -> Dict:
        """
        单只股票的回测
        
        Args:
            agent_type: Agent类型
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            单只股票的回测结果
        """
        # 获取股票数据
        df = self.get_stock_data(stock_code, start_date, end_date)
        if df.empty:
            return None
        
        # 计算技术指标
        df = self.calculate_technical_indicators(df)
        
        # 模拟Agent分析逻辑
        predictions = self._simulate_agent_analysis(agent_type, df, stock_code)
        
        if not predictions:
            return None
        
        # 计算实际收益率
        returns_1d = []
        returns_5d = []
        returns_20d = []
        correct_predictions = 0
        
        for pred in predictions:
            idx = pred['index']
            prediction_type = pred['prediction']
            
            # 计算未来收益率
            if idx + 1 < len(df):
                ret_1d = (df.iloc[idx + 1]['close'] - df.iloc[idx]['close']) / df.iloc[idx]['close']
                returns_1d.append(ret_1d)
                
                # 判断预测准确性（简化逻辑）
                if prediction_type == 'BUY' and ret_1d > 0.02:  # 2%阈值
                    correct_predictions += 1
                elif prediction_type == 'SELL' and ret_1d < -0.02:
                    correct_predictions += 1
                elif prediction_type == 'HOLD' and abs(ret_1d) <= 0.02:
                    correct_predictions += 1
            
            if idx + 5 < len(df):
                ret_5d = (df.iloc[idx + 5]['close'] - df.iloc[idx]['close']) / df.iloc[idx]['close']
                returns_5d.append(ret_5d)
            
            if idx + 20 < len(df):
                ret_20d = (df.iloc[idx + 20]['close'] - df.iloc[idx]['close']) / df.iloc[idx]['close']
                returns_20d.append(ret_20d)
        
        return {
            'stock_code': stock_code,
            'total_predictions': len(predictions),
            'correct_predictions': correct_predictions,
            'accuracy': correct_predictions / len(predictions) if predictions else 0,
            'returns_1d': returns_1d,
            'returns_5d': returns_5d,
            'returns_20d': returns_20d,
            'predictions': predictions
        }
    
    def _simulate_agent_analysis(self, agent_type: str, df: pd.DataFrame, stock_code: str) -> List[Dict]:
        """
        模拟Agent分析逻辑
        
        Args:
            agent_type: Agent类型
            df: 股票数据
            stock_code: 股票代码
            
        Returns:
            预测结果列表
        """
        predictions = []
        
        # 根据不同Agent类型实现不同的分析逻辑
        if agent_type == 'market_analyst':
            predictions = self._simulate_market_analyst(df)
        elif agent_type == 'fundamental_analyst':
            predictions = self._simulate_fundamental_analyst(df, stock_code)
        elif agent_type == 'bull_researcher':
            predictions = self._simulate_bull_researcher(df)
        elif agent_type == 'bear_researcher':
            predictions = self._simulate_bear_researcher(df)
        
        return predictions
    
    def _simulate_market_analyst(self, df: pd.DataFrame) -> List[Dict]:
        """模拟市场分析师逻辑"""
        predictions = []
        
        for i in range(60, len(df)):  # 需要足够的历史数据
            row = df.iloc[i]
            
            # 技术指标信号
            signals = []
            
            # MACD信号
            if row['macd'] > row['macd_signal'] and df.iloc[i-1]['macd'] <= df.iloc[i-1]['macd_signal']:
                signals.append('MACD_GOLDEN_CROSS')
            elif row['macd'] < row['macd_signal'] and df.iloc[i-1]['macd'] >= df.iloc[i-1]['macd_signal']:
                signals.append('MACD_DEATH_CROSS')
            
            # MA信号
            if row['close'] > row['ma20'] and row['ma5'] > row['ma10']:
                signals.append('MA_BULLISH')
            elif row['close'] < row['ma20'] and row['ma5'] < row['ma10']:
                signals.append('MA_BEARISH')
            
            # RSI信号
            if row['rsi'] < 30:
                signals.append('RSI_OVERSOLD')
            elif row['rsi'] > 70:
                signals.append('RSI_OVERBOUGHT')
            
            # 基于信号生成预测
            bullish_signals = ['MACD_GOLDEN_CROSS', 'MA_BULLISH', 'RSI_OVERSOLD']
            bearish_signals = ['MACD_DEATH_CROSS', 'MA_BEARISH', 'RSI_OVERBOUGHT']
            
            bull_count = sum(1 for s in signals if s in bullish_signals)
            bear_count = sum(1 for s in signals if s in bearish_signals)
            
            if bull_count > bear_count:
                prediction = 'BUY'
                confidence = bull_count / (bull_count + bear_count) if (bull_count + bear_count) > 0 else 0.5
            elif bear_count > bull_count:
                prediction = 'SELL'
                confidence = bear_count / (bull_count + bear_count) if (bull_count + bear_count) > 0 else 0.5
            else:
                prediction = 'HOLD'
                confidence = 0.5
            
            predictions.append({
                'index': i,
                'date': row['trade_date'],
                'prediction': prediction,
                'confidence': confidence,
                'signals': signals,
                'features': {
                    'rsi': row['rsi'],
                    'macd': row['macd'],
                    'ma5': row['ma5'],
                    'ma20': row['ma20'],
                    'close': row['close']
                }
            })
        
        return predictions
    
    def _simulate_fundamental_analyst(self, df: pd.DataFrame, stock_code: str) -> List[Dict]:
        """模拟基本面分析师逻辑"""
        predictions = []
        
        # 获取财务数据（简化处理）
        financial_data = self.get_financial_data(stock_code)
        
        for i in range(20, len(df), 20):  # 每20个交易日分析一次
            row = df.iloc[i]
            
            # 简化的基本面评分
            fundamental_score = 0
            
            # 价格趋势评分
            if row['close'] > row['ma20']:
                fundamental_score += 1
            
            # 成交量评分
            if row['vol_ratio'] > 1.2:  # 放量
                fundamental_score += 1
            
            # 基于评分生成预测
            if fundamental_score >= 2:
                prediction = 'BUY'
                confidence = 0.7
            elif fundamental_score <= 0:
                prediction = 'SELL'
                confidence = 0.7
            else:
                prediction = 'HOLD'
                confidence = 0.6
            
            predictions.append({
                'index': i,
                'date': row['trade_date'],
                'prediction': prediction,
                'confidence': confidence,
                'fundamental_score': fundamental_score,
                'features': {
                    'close': row['close'],
                    'ma20': row['ma20'],
                    'vol_ratio': row['vol_ratio']
                }
            })
        
        return predictions
    
    def _simulate_bull_researcher(self, df: pd.DataFrame) -> List[Dict]:
        """模拟多头研究员逻辑"""
        predictions = []
        
        for i in range(20, len(df), 10):  # 每10个交易日分析一次
            row = df.iloc[i]
            
            # 多头偏向逻辑
            bull_score = 0
            
            # 趋势向上
            if row['ma5'] > row['ma10'] > row['ma20']:
                bull_score += 2
            
            # 价格突破
            if row['close'] > row['ma20'] * 1.05:  # 突破5%
                bull_score += 1
            
            # 成交量放大
            if row['vol_ratio'] > 1.5:
                bull_score += 1
            
            # 多头研究员更倾向于BUY
            if bull_score >= 2:
                prediction = 'BUY'
                confidence = 0.8
            elif bull_score == 1:
                prediction = 'BUY'
                confidence = 0.6
            else:
                prediction = 'HOLD'
                confidence = 0.5
            
            predictions.append({
                'index': i,
                'date': row['trade_date'],
                'prediction': prediction,
                'confidence': confidence,
                'bull_score': bull_score,
                'features': {
                    'ma5': row['ma5'],
                    'ma10': row['ma10'],
                    'ma20': row['ma20'],
                    'close': row['close'],
                    'vol_ratio': row['vol_ratio']
                }
            })
        
        return predictions
    
    def _simulate_bear_researcher(self, df: pd.DataFrame) -> List[Dict]:
        """模拟空头研究员逻辑"""
        predictions = []
        
        for i in range(20, len(df), 10):  # 每10个交易日分析一次
            row = df.iloc[i]
            
            # 空头偏向逻辑
            bear_score = 0
            
            # 趋势向下
            if row['ma5'] < row['ma10'] < row['ma20']:
                bear_score += 2
            
            # 价格跌破
            if row['close'] < row['ma20'] * 0.95:  # 跌破5%
                bear_score += 1
            
            # RSI过高
            if row['rsi'] > 70:
                bear_score += 1
            
            # 空头研究员更倾向于SELL
            if bear_score >= 2:
                prediction = 'SELL'
                confidence = 0.8
            elif bear_score == 1:
                prediction = 'SELL'
                confidence = 0.6
            else:
                prediction = 'HOLD'
                confidence = 0.5
            
            predictions.append({
                'index': i,
                'date': row['trade_date'],
                'prediction': prediction,
                'confidence': confidence,
                'bear_score': bear_score,
                'features': {
                    'ma5': row['ma5'],
                    'ma10': row['ma10'],
                    'ma20': row['ma20'],
                    'close': row['close'],
                    'rsi': row['rsi']
                }
            })
        
        return predictions
    
    def generate_performance_report(self, results: Dict) -> str:
        """
        生成性能报告
        
        Args:
            results: 分析结果
            
        Returns:
            报告字符串
        """
        report = f"""
# {results['agent_type']} 回测性能报告

## 总体表现
- **总预测次数**: {results['total_predictions']}
- **正确预测次数**: {results['correct_predictions']}
- **预测准确率**: {results['accuracy']:.2%}

## 收益表现
- **1日平均收益率**: {results['avg_return_1d']:.2%}
- **5日平均收益率**: {results['avg_return_5d']:.2%}
- **20日平均收益率**: {results['avg_return_20d']:.2%}

## 个股表现详情
"""
        
        for stock_result in results['stock_results']:
            report += f"""
### {stock_result['stock_code']}
- 预测次数: {stock_result['total_predictions']}
- 准确率: {stock_result['accuracy']:.2%}
- 1日平均收益: {np.mean(stock_result['returns_1d']):.2%}
- 5日平均收益: {np.mean(stock_result['returns_5d']):.2%}
- 20日平均收益: {np.mean(stock_result['returns_20d']):.2%}
"""
        
        return report
    
    def save_results_to_db(self, results: Dict):
        """将结果保存到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for stock_result in results['stock_results']:
            for pred in stock_result['predictions']:
                cursor.execute('''
                    INSERT INTO backtest_results 
                    (agent_type, stock_code, analysis_date, prediction_type, 
                     prediction_confidence, analysis_features)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    results['agent_type'],
                    stock_result['stock_code'],
                    pred['date'].strftime('%Y-%m-%d'),
                    pred['prediction'],
                    pred['confidence'],
                    json.dumps(pred['features'])
                ))
        
        conn.commit()
        conn.close()


def main():
    """主函数"""
    # 初始化回测框架
    framework = AgentBacktestFramework('b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065')
    
    # 测试股票列表
    test_stocks = ['000001.SZ', '000002.SZ', '600000.SH', '600036.SH']
    
    # 回测时间范围
    start_date = '20230101'
    end_date = '20231231'
    
    # 分析不同Agent类型
    agent_types = ['market_analyst', 'fundamental_analyst', 'bull_researcher', 'bear_researcher']
    
    all_results = {}
    
    for agent_type in agent_types:
        print(f"正在回测 {agent_type}...")
        results = framework.analyze_agent_performance(agent_type, test_stocks, start_date, end_date)
        all_results[agent_type] = results
        
        # 生成报告
        report = framework.generate_performance_report(results)
        
        # 保存报告
        with open(f"{agent_type}_backtest_report.md", 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 保存结果到数据库
        framework.save_results_to_db(results)
        
        print(f"{agent_type} 回测完成，准确率: {results['accuracy']:.2%}")
    
    # 生成对比报告
    comparison_report = "# Agent性能对比报告\n\n"
    comparison_report += "| Agent类型 | 预测准确率 | 1日收益率 | 5日收益率 | 20日收益率 |\n"
    comparison_report += "|----------|------------|-----------|-----------|------------|\n"
    
    for agent_type, results in all_results.items():
        comparison_report += f"| {agent_type} | {results['accuracy']:.2%} | {results['avg_return_1d']:.2%} | {results['avg_return_5d']:.2%} | {results['avg_return_20d']:.2%} |\n"
    
    with open("agent_performance_comparison.md", 'w', encoding='utf-8') as f:
        f.write(comparison_report)
    
    print("所有Agent回测完成！")


if __name__ == "__main__":
    main()