# -*- coding: utf-8 -*-
"""
增强版Agent分析系统
包含更多创新的评估角度和量化指标
"""

import tushare as ts
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class EnhancedAgentAnalysis:
    """
    增强版Agent分析系统
    包含创新的评估维度和量化指标
    """
    
    def __init__(self, tushare_token: str):
        """初始化"""
        ts.set_token(tushare_token)
        self.pro = ts.pro_api()
    
    def calculate_advanced_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算高级技术指标
        
        Args:
            df: 股票数据
            
        Returns:
            添加高级指标的DataFrame
        """
        if df.empty or len(df) < 100:
            return df
        
        # 确保数据类型正确
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df['vol'] = pd.to_numeric(df['vol'], errors='coerce')
        
        # 基础指标
        df = self._calculate_basic_indicators(df)
        
        # 高级趋势指标
        df = self._calculate_trend_indicators(df)
        
        # 市场微观结构指标
        df = self._calculate_microstructure_indicators(df)
        
        # 动量和反转指标
        df = self._calculate_momentum_indicators(df)
        
        # 资金流向指标
        df = self._calculate_money_flow_indicators(df)
        
        # 波动率和风险指标
        df = self._calculate_volatility_indicators(df)
        
        return df
    
    def _calculate_basic_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算基础技术指标"""
        # 移动平均线系统
        for period in [5, 10, 20, 30, 60, 120]:
            df[f'ma{period}'] = df['close'].rolling(window=period).mean()
            df[f'ema{period}'] = df['close'].ewm(span=period).mean()
        
        # MACD系统
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # RSI系统
        for period in [6, 14, 21]:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            df[f'rsi{period}'] = 100 - (100 / (1 + rs))
        
        # 布林带
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        return df
    
    def _calculate_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算趋势指标"""
        # 简化版ADX计算
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift(1))
        low_close = np.abs(df['low'] - df['close'].shift(1))
        ranges = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = ranges.rolling(14).mean()
        
        plus_dm = np.where((df['high'] - df['high'].shift(1)) > (df['low'].shift(1) - df['low']), 
                          np.maximum(df['high'] - df['high'].shift(1), 0), 0)
        minus_dm = np.where((df['low'].shift(1) - df['low']) > (df['high'] - df['high'].shift(1)), 
                           np.maximum(df['low'].shift(1) - df['low'], 0), 0)
        
        plus_di = 100 * (plus_dm / atr).rolling(14).mean()
        minus_di = 100 * (minus_dm / atr).rolling(14).mean()
        
        df['di_plus'] = plus_di
        df['di_minus'] = minus_di
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        df['adx'] = dx.rolling(14).mean()
        
        # Aroon指标简化实现
        period = 14
        df['aroon_up'] = 100 * (period - df['high'].rolling(period).apply(lambda x: period - 1 - x.argmax())) / period
        df['aroon_down'] = 100 * (period - df['low'].rolling(period).apply(lambda x: period - 1 - x.argmin())) / period
        df['aroon_osc'] = df['aroon_up'] - df['aroon_down']
        
        # 趋势质量指标
        df['trend_strength'] = np.where(df['adx'] > 25, 1, 0) * np.where(df['di_plus'] > df['di_minus'], 1, -1)
        
        # 均线排列指标
        ma_cols = ['ma5', 'ma10', 'ma20', 'ma60']
        df['ma_alignment'] = 0
        for i in range(len(ma_cols) - 1):
            df['ma_alignment'] += np.where(df[ma_cols[i]] > df[ma_cols[i+1]], 1, -1)
        
        return df
    
    def _calculate_microstructure_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算市场微观结构指标"""
        # 价格跳空指标
        df['gap'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)
        df['gap_up'] = np.where(df['gap'] > 0.02, 1, 0)  # 2%以上向上跳空
        df['gap_down'] = np.where(df['gap'] < -0.02, 1, 0)  # 2%以上向下跳空
        
        # 影线分析
        df['upper_shadow'] = df['high'] - np.maximum(df['open'], df['close'])
        df['lower_shadow'] = np.minimum(df['open'], df['close']) - df['low']
        df['body'] = abs(df['close'] - df['open'])
        df['shadow_ratio'] = (df['upper_shadow'] + df['lower_shadow']) / df['body']
        
        # 内外盘比例（简化版）
        df['buy_pressure'] = np.where(df['close'] > df['open'], df['vol'], 0)
        df['sell_pressure'] = np.where(df['close'] < df['open'], df['vol'], 0)
        df['buy_sell_ratio'] = df['buy_pressure'].rolling(5).sum() / df['sell_pressure'].rolling(5).sum()
        
        return df
    
    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算动量指标"""
        # 多时间框架动量
        for period in [5, 10, 20, 60]:
            df[f'momentum{period}'] = (df['close'] - df['close'].shift(period)) / df['close'].shift(period)
        
        # 相对强弱比较（与大盘）
        # 这里需要大盘数据，简化处理
        df['relative_strength'] = df['close'].pct_change(20).rolling(20).mean()
        
        # 价格动量振荡器
        df['pmo'] = df['close'].pct_change(10) * 100
        df['pmo_signal'] = df['pmo'].ewm(span=10).mean()
        
        # 资金流向动量 (简化版)
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['vol']
        positive_flow = money_flow.where(df['close'] > df['close'].shift(1), 0).rolling(14).sum()
        negative_flow = money_flow.where(df['close'] < df['close'].shift(1), 0).rolling(14).sum()
        df['cmf'] = (positive_flow - negative_flow) / (positive_flow + negative_flow)
        
        return df
    
    def _calculate_money_flow_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算资金流向指标"""
        # 资金流量指标 (MFI简化实现)
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        raw_money_flow = typical_price * df['vol']
        
        positive_flow = raw_money_flow.where(typical_price > typical_price.shift(1), 0).rolling(14).sum()
        negative_flow = raw_money_flow.where(typical_price < typical_price.shift(1), 0).rolling(14).sum()
        money_ratio = positive_flow / negative_flow
        df['mfi'] = 100 - (100 / (1 + money_ratio))
        
        # 成交量加权平均价
        df['vwap'] = (df['close'] * df['vol']).cumsum() / df['vol'].cumsum()
        df['vwap_5'] = ((df['close'] * df['vol']).rolling(5).sum() / df['vol'].rolling(5).sum())
        
        # 成交量相关指标
        df['vol_ma5'] = df['vol'].rolling(5).mean()
        df['vol_ma20'] = df['vol'].rolling(20).mean()
        df['vol_ratio'] = df['vol'] / df['vol_ma20']
        df['vol_surge'] = np.where(df['vol_ratio'] > 2, 1, 0)  # 放量信号
        
        # 价量关系
        df['price_volume_trend'] = ((df['close'] - df['close'].shift(1)) / df['close'].shift(1) * df['vol']).cumsum()
        
        return df
    
    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算波动率指标"""
        # ATR - 真实波动范围
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift(1))
        low_close = np.abs(df['low'] - df['close'].shift(1))
        ranges = np.maximum(high_low, np.maximum(high_close, low_close))
        df['atr'] = ranges.rolling(14).mean()
        df['atr_ratio'] = df['atr'] / df['close']
        
        # 历史波动率
        df['returns'] = df['close'].pct_change()
        df['volatility_5'] = df['returns'].rolling(5).std() * np.sqrt(252)
        df['volatility_20'] = df['returns'].rolling(20).std() * np.sqrt(252)
        
        # VIX类指标（简化版）
        df['fear_greed'] = df['rsi14'].rolling(5).std()  # 恐慌贪婪指标
        
        return df
    
    def generate_enhanced_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生成增强版交易信号
        
        Args:
            df: 带有技术指标的DataFrame
            
        Returns:
            带有交易信号的DataFrame
        """
        # 初始化信号列
        df['signal_trend'] = 0
        df['signal_momentum'] = 0
        df['signal_volume'] = 0
        df['signal_volatility'] = 0
        df['signal_microstructure'] = 0
        df['signal_composite'] = 0
        
        # 趋势信号
        trend_conditions = [
            (df['ma_alignment'] >= 2) & (df['adx'] > 25),  # 强趋势
            (df['aroon_osc'] > 50) & (df['close'] > df['ma20']),  # 上升趋势
            (df['di_plus'] > df['di_minus']) & (df['macd'] > df['macd_signal'])  # 多头排列
        ]
        df['signal_trend'] = np.select(
            [sum(trend_conditions) >= 2, sum(trend_conditions) <= -2],
            [1, -1], 0
        )
        
        # 动量信号
        momentum_conditions = [
            df['rsi14'] > 50,
            df['momentum20'] > 0.05,
            df['pmo'] > df['pmo_signal']
        ]
        df['signal_momentum'] = np.select(
            [sum(momentum_conditions) >= 2, sum(momentum_conditions) <= -2],
            [1, -1], 0
        )
        
        # 成交量信号
        volume_conditions = [
            df['vol_ratio'] > 1.5,
            df['mfi'] > 50,
            df['cmf'] > 0
        ]
        df['signal_volume'] = np.select(
            [sum(volume_conditions) >= 2, sum(volume_conditions) <= -2],
            [1, -1], 0
        )
        
        # 波动率信号
        volatility_conditions = [
            df['atr_ratio'] < df['atr_ratio'].rolling(20).mean(),  # 低波动率
            df['bb_width'] < df['bb_width'].rolling(20).mean(),  # 收敛
            df['fear_greed'] < df['fear_greed'].rolling(20).mean()  # 低恐慌
        ]
        df['signal_volatility'] = np.select(
            [sum(volatility_conditions) >= 2],
            [1], 0
        )
        
        # 微观结构信号
        microstructure_conditions = [
            df['gap_up'] == 1,
            df['buy_sell_ratio'] > 1.2,
            df['shadow_ratio'] < 0.5  # 实体相对较大
        ]
        df['signal_microstructure'] = np.select(
            [sum(microstructure_conditions) >= 2, sum(microstructure_conditions) <= -2],
            [1, -1], 0
        )
        
        # 综合信号
        signal_weights = {
            'trend': 0.3,
            'momentum': 0.25,
            'volume': 0.2,
            'volatility': 0.15,
            'microstructure': 0.1
        }
        
        df['signal_composite'] = (
            df['signal_trend'] * signal_weights['trend'] +
            df['signal_momentum'] * signal_weights['momentum'] +
            df['signal_volume'] * signal_weights['volume'] +
            df['signal_volatility'] * signal_weights['volatility'] +
            df['signal_microstructure'] * signal_weights['microstructure']
        )
        
        # 生成最终交易建议
        df['recommendation'] = np.select(
            [df['signal_composite'] > 0.3, df['signal_composite'] < -0.3],
            ['BUY', 'SELL'], 'HOLD'
        )
        
        df['confidence'] = abs(df['signal_composite'])
        
        return df
    
    def calculate_agent_innovation_score(self, predictions: List[Dict]) -> Dict:
        """
        计算Agent创新得分
        
        Args:
            predictions: 预测结果列表
            
        Returns:
            创新得分字典
        """
        innovation_scores = {
            'diversity_score': 0.0,  # 多样性得分
            'complexity_score': 0.0,  # 复杂性得分
            'adaptability_score': 0.0,  # 适应性得分
            'timing_score': 0.0,  # 时机把握得分
            'risk_awareness_score': 0.0,  # 风险意识得分
            'overall_innovation': 0.0  # 总体创新得分
        }
        
        if not predictions:
            return innovation_scores
        
        # 多样性得分 - 基于使用的特征数量
        all_features = set()
        for pred in predictions:
            if 'features' in pred:
                all_features.update(pred['features'].keys())
        innovation_scores['diversity_score'] = min(len(all_features) / 20, 1.0)  # 最多20个特征
        
        # 复杂性得分 - 基于信号的复杂程度
        complex_signals = 0
        for pred in predictions:
            if 'signals' in pred and len(pred['signals']) > 3:
                complex_signals += 1
        innovation_scores['complexity_score'] = complex_signals / len(predictions)
        
        # 适应性得分 - 基于置信度的变化
        confidences = [pred.get('confidence', 0.5) for pred in predictions]
        confidence_std = np.std(confidences)
        innovation_scores['adaptability_score'] = min(confidence_std * 2, 1.0)
        
        # 时机把握得分 - 基于预测频率的合理性
        prediction_intervals = []
        for i in range(1, len(predictions)):
            interval = predictions[i]['index'] - predictions[i-1]['index']
            prediction_intervals.append(interval)
        
        if prediction_intervals:
            interval_cv = np.std(prediction_intervals) / np.mean(prediction_intervals)
            innovation_scores['timing_score'] = max(0, 1 - interval_cv)  # 间隔越规律得分越高
        
        # 风险意识得分 - 基于HOLD建议的比例
        hold_ratio = sum(1 for pred in predictions if pred.get('prediction') == 'HOLD') / len(predictions)
        innovation_scores['risk_awareness_score'] = min(hold_ratio * 2, 1.0)  # 适度保守
        
        # 总体创新得分
        weights = {
            'diversity': 0.25,
            'complexity': 0.2,
            'adaptability': 0.2,
            'timing': 0.2,
            'risk_awareness': 0.15
        }
        
        innovation_scores['overall_innovation'] = (
            innovation_scores['diversity_score'] * weights['diversity'] +
            innovation_scores['complexity_score'] * weights['complexity'] +
            innovation_scores['adaptability_score'] * weights['adaptability'] +
            innovation_scores['timing_score'] * weights['timing'] +
            innovation_scores['risk_awareness_score'] * weights['risk_awareness']
        )
        
        return innovation_scores
    
    def generate_improvement_suggestions(self, agent_type: str, backtest_results: Dict, 
                                       innovation_scores: Dict) -> List[str]:
        """
        生成改进建议
        
        Args:
            agent_type: Agent类型
            backtest_results: 回测结果
            innovation_scores: 创新得分
            
        Returns:
            改进建议列表
        """
        suggestions = []
        
        # 基于准确率的建议
        accuracy = backtest_results.get('accuracy', 0)
        if accuracy < 0.4:
            suggestions.append("预测准确率过低，建议重新审视核心预测逻辑")
            suggestions.append("考虑增加更多确认信号，减少噪音交易")
        elif accuracy < 0.6:
            suggestions.append("预测准确率中等，建议优化信号过滤机制")
        
        # 基于创新得分的建议
        if innovation_scores['diversity_score'] < 0.3:
            suggestions.append("指标多样性不足，建议引入更多维度的分析指标")
            suggestions.append("考虑添加宏观经济指标、行业轮动指标等")
        
        if innovation_scores['complexity_score'] < 0.3:
            suggestions.append("分析逻辑过于简单，建议增加多信号确认机制")
            suggestions.append("考虑使用机器学习方法进行特征组合")
        
        if innovation_scores['adaptability_score'] < 0.3:
            suggestions.append("适应性不足，建议增加动态参数调整机制")
            suggestions.append("考虑根据市场环境调整分析策略")
        
        if innovation_scores['risk_awareness_score'] < 0.3:
            suggestions.append("风险意识不足，建议增加更多风险控制措施")
            suggestions.append("考虑在不确定性高时保持观望")
        
        # 基于Agent类型的特定建议
        if agent_type == 'market_analyst':
            suggestions.extend([
                "建议整合更多市场微观结构指标",
                "考虑加入跨市场关联分析",
                "增加高频数据分析能力"
            ])
        elif agent_type == 'fundamental_analyst':
            suggestions.extend([
                "建议加入ESG评分等新兴基本面指标",
                "考虑整合另类数据源（如卫星数据、社交媒体情绪等）",
                "增加行业比较和相对估值分析"
            ])
        elif agent_type in ['bull_researcher', 'bear_researcher']:
            suggestions.extend([
                "建议减少立场偏见，增加客观分析",
                "考虑加入反向确认机制",
                "增加多时间周期的分析视角"
            ])
        
        # 收益率相关建议
        avg_return = backtest_results.get('avg_return_20d', 0)
        if avg_return < 0:
            suggestions.append("长期收益为负，建议重新评估选股和择时策略")
        elif avg_return < 0.05:
            suggestions.append("收益率偏低，建议提高信号质量或调整风险收益比")
        
        return suggestions


def main():
    """测试增强版分析系统"""
    # 初始化系统
    enhanced_analysis = EnhancedAgentAnalysis('b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065')
    
    # 获取测试数据
    test_stock = '000001.SZ'
    df = enhanced_analysis.pro.daily(ts_code=test_stock, start_date='20230101', end_date='20231231')
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date')
    
    # 计算高级指标
    df = enhanced_analysis.calculate_advanced_indicators(df)
    
    # 生成交易信号
    df = enhanced_analysis.generate_enhanced_signals(df)
    
    # 提取预测结果
    predictions = []
    for i, row in df.iterrows():
        if not pd.isna(row['recommendation']):
            predictions.append({
                'index': i,
                'date': row['trade_date'],
                'prediction': row['recommendation'],
                'confidence': row['confidence'],
                'features': {
                    'ma_alignment': row['ma_alignment'],
                    'adx': row['adx'],
                    'rsi14': row['rsi14'],
                    'vol_ratio': row['vol_ratio'],
                    'signal_composite': row['signal_composite']
                }
            })
    
    # 计算创新得分
    innovation_scores = enhanced_analysis.calculate_agent_innovation_score(predictions)
    
    print("创新得分:", innovation_scores)
    
    # 生成改进建议
    backtest_results = {'accuracy': 0.45, 'avg_return_20d': 0.03}
    suggestions = enhanced_analysis.generate_improvement_suggestions(
        'market_analyst', backtest_results, innovation_scores
    )
    
    print("\n改进建议:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")


if __name__ == "__main__":
    main()