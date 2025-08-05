# -*- coding: utf-8 -*-
"""
增强版因子系统演示 - 使用模拟数据
展示4层因子架构 + 线性/机器学习组合处理
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import warnings
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')

# 机器学习工具
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error
    ML_AVAILABLE = True
    print("✅ 机器学习工具可用")
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ 机器学习工具不可用")

class EnhancedFactorDemo:
    """
    增强版因子系统演示
    展示完整的4层因子架构和处理流程
    """
    
    def __init__(self):
        """初始化演示系统"""
        np.random.seed(42)  # 确保结果可重现
        
    def generate_mock_stock_data(self, start_date: str, end_date: str, stock_count: int = 1) -> pd.DataFrame:
        """生成模拟股票数据"""
        dates = pd.date_range(start_date, end_date, freq='D')
        # 只保留工作日
        dates = dates[dates.weekday < 5]
        
        print(f"生成模拟数据: {len(dates)} 个交易日")
        
        # 生成价格数据（使用几何布朗运动）
        returns = np.random.normal(0.001, 0.02, len(dates))  # 日收益率
        price = 100 * np.exp(np.cumsum(returns))  # 价格序列
        
        # 生成OHLC数据
        df = pd.DataFrame({
            'trade_date': dates,
            'open': price * (1 + np.random.normal(0, 0.005, len(dates))),
            'high': price * (1 + abs(np.random.normal(0, 0.01, len(dates)))),
            'low': price * (1 - abs(np.random.normal(0, 0.01, len(dates)))),
            'close': price,
            'vol': np.random.lognormal(15, 0.5, len(dates)),  # 成交量
            'turnover_rate': np.random.uniform(0.5, 5.0, len(dates)),  # 换手率
            'pct_chg': returns * 100  # 涨跌幅
        })
        
        # 确保OHLC逻辑正确
        df['high'] = np.maximum(df['high'], df[['open', 'close']].max(axis=1))
        df['low'] = np.minimum(df['low'], df[['open', 'close']].min(axis=1))
        
        return df
    
    # ==================== Layer 1: 基础技术因子 ====================
    
    def calculate_layer1_basic_factors(self, df: pd.DataFrame) -> Dict:
        """Layer 1: 基础技术因子"""
        factors = {}
        
        print("  - 计算价格动量因子...")
        # 价格因子
        for period in [1, 5, 10, 20, 60]:
            factors[f'momentum_{period}'] = (df['close'] - df['close'].shift(period)) / df['close'].shift(period)
            factors[f'reversal_{period}'] = -factors[f'momentum_{period}']  # 反转因子
        
        print("  - 计算波动率因子...")
        # 波动率因子
        returns = df['close'].pct_change()
        for period in [5, 20, 60]:
            factors[f'volatility_{period}'] = returns.rolling(period).std()
            factors[f'vol_ratio_{period}'] = factors[f'volatility_{period}'] / factors[f'volatility_{period}'].rolling(60).mean()
        
        print("  - 计算成交量因子...")
        # 成交量因子
        for period in [5, 20, 60]:
            factors[f'volume_ratio_{period}'] = df['vol'] / df['vol'].rolling(period).mean()
            factors[f'volume_price_corr_{period}'] = returns.rolling(period).corr(df['vol'].pct_change())
        
        print("  - 计算价格位置因子...")
        # 价格位置因子
        for period in [20, 60, 120]:
            high_max = df['high'].rolling(period).max()
            low_min = df['low'].rolling(period).min()
            factors[f'price_position_{period}'] = (df['close'] - low_min) / (high_max - low_min)
        
        print(f"  ✅ Layer 1完成: {len(factors)} 个基础因子")
        return factors
    
    # ==================== Layer 2: 高级技术因子 ====================
    
    def calculate_layer2_advanced_factors(self, df: pd.DataFrame) -> Dict:
        """Layer 2: 高级技术因子"""
        factors = {}
        
        print("  - 计算高级趋势因子...")
        # 手动实现高级指标
        
        # ADX (平均趋向指标)
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
        
        factors['adx'] = (100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)).rolling(14).mean()
        factors['atr'] = atr
        factors['atr_ratio'] = atr / df['close']
        
        print("  - 计算动量增强因子...")
        # 风险调整动量因子
        returns = df['close'].pct_change()
        for period in [10, 20, 60]:
            momentum = factors.get(f'momentum_{period}', (df['close'] - df['close'].shift(period)) / df['close'].shift(period))
            volatility = returns.rolling(period).std()
            factors[f'risk_adj_momentum_{period}'] = momentum / (volatility + 1e-8)  # 避免除零
        
        print("  - 计算高阶统计因子...")
        # 动量偏度和峰度因子
        for period in [20, 60]:
            factors[f'momentum_skew_{period}'] = returns.rolling(period).skew()
            factors[f'momentum_kurt_{period}'] = returns.rolling(period).kurt()
        
        # 价格冲击因子
        factors['price_impact'] = returns / np.log(df['vol'] + 1)
        
        # 订单不平衡代理
        factors['order_imbalance_proxy'] = (df['vol'] * np.sign(returns)).cumsum()
        
        print("  - 计算市场微观结构因子...")
        # 微观结构因子
        factors['bid_ask_proxy'] = (df['high'] - df['low']) / df['close']  # 买卖价差代理
        factors['intraday_momentum'] = (df['close'] - df['open']) / df['open']  # 日内动量
        factors['gap'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)  # 跳空
        
        # 成交量价格趋势
        factors['volume_price_trend'] = ((df['close'] - df['close'].shift(1)) / df['close'].shift(1) * df['vol']).cumsum()
        
        print(f"  ✅ Layer 2完成: {len(factors)} 个高级因子")
        return factors
    
    # ==================== Layer 3: 基本面因子 (模拟) ====================
    
    def calculate_layer3_fundamental_factors(self, df: pd.DataFrame) -> Dict:
        """Layer 3: 基本面因子 (模拟数据)"""
        factors = {}
        
        print("  - 生成模拟基本面数据...")
        
        # 模拟财务指标（通常是季度数据，这里简化为常数）
        np.random.seed(42)
        
        # 估值因子
        factors['pe_ratio'] = 15 + np.random.normal(0, 5)  # 市盈率
        factors['pb_ratio'] = 1.5 + np.random.normal(0, 0.5)  # 市净率
        factors['ps_ratio'] = 2.0 + np.random.normal(0, 0.8)  # 市销率
        
        # 成长因子
        factors['revenue_growth'] = 0.15 + np.random.normal(0, 0.1)  # 营收增长率
        factors['profit_growth'] = 0.12 + np.random.normal(0, 0.15)  # 利润增长率
        factors['roe_growth'] = 0.08 + np.random.normal(0, 0.08)  # ROE增长
        
        # 盈利能力因子
        factors['roe'] = 0.12 + np.random.normal(0, 0.05)  # 净资产收益率
        factors['roa'] = 0.06 + np.random.normal(0, 0.03)  # 总资产收益率
        factors['gross_margin'] = 0.25 + np.random.normal(0, 0.08)  # 毛利率
        factors['net_margin'] = 0.08 + np.random.normal(0, 0.04)  # 净利率
        
        # 财务健康因子
        factors['debt_ratio'] = 0.4 + np.random.normal(0, 0.15)  # 资产负债率
        factors['current_ratio'] = 1.5 + np.random.normal(0, 0.3)  # 流动比率
        factors['quick_ratio'] = 1.2 + np.random.normal(0, 0.25)  # 速动比率
        
        # 现金流因子
        factors['ocf_to_revenue'] = 0.12 + np.random.normal(0, 0.05)  # 经营现金流/营收
        factors['fcf_yield'] = 0.05 + np.random.normal(0, 0.03)  # 自由现金流收益率
        
        # 基本面质量综合评分
        factors['fundamental_quality'] = (
            (factors['roe'] - 0.1) * 2 +  # ROE权重
            (factors['revenue_growth'] - 0.1) * 1.5 +  # 成长性权重  
            (0.5 - factors['debt_ratio']) * 1 +  # 财务安全权重
            factors['ocf_to_revenue'] * 3  # 现金流权重
        )
        
        print(f"  ✅ Layer 3完成: {len(factors)} 个基本面因子")
        return factors
    
    # ==================== Layer 4: 另类因子 (模拟) ====================
    
    def calculate_layer4_alternative_factors(self, df: pd.DataFrame) -> Dict:
        """Layer 4: 另类因子 (模拟数据)"""
        factors = {}
        
        print("  - 生成模拟另类数据...")
        
        # 资金流向因子
        factors['main_net_inflow'] = np.random.normal(1000000, 5000000)  # 主力净流入
        factors['main_net_inflow_rate'] = np.random.normal(0.02, 0.05)  # 主力净流入率
        factors['northbound_holding'] = max(0, np.random.normal(50000000, 20000000))  # 北向资金持股
        
        # 融资融券因子
        factors['margin_balance'] = max(0, np.random.normal(100000000, 50000000))  # 融资余额
        factors['margin_buy_ratio'] = np.random.uniform(0.05, 0.3)  # 融资买入占比
        factors['margin_trend'] = np.random.normal(0.01, 0.1)  # 融资余额变化趋势
        
        # 情绪因子
        factors['turnover_anomaly'] = df['turnover_rate'].iloc[-20:].mean() / df['turnover_rate'].mean()  # 换手率异常
        factors['volume_spike'] = df['vol'].iloc[-5:].mean() / df['vol'].iloc[-20:].mean()  # 成交量放大
        
        # 技术面情绪
        factors['limit_up_freq'] = sum(df['pct_chg'].tail(60) >= 9.8) / 60  # 涨停频率
        factors['limit_down_freq'] = sum(df['pct_chg'].tail(60) <= -9.8) / 60  # 跌停频率
        
        # 相对强度因子
        market_return = np.random.normal(0.001, 0.015, len(df))  # 模拟市场收益
        stock_return = df['close'].pct_change()
        factors['relative_strength_60'] = (stock_return.tail(60).mean() - np.mean(market_return[-60:]))  # 相对强度
        
        # 行业轮动因子
        factors['industry_momentum'] = np.random.normal(0.02, 0.08)  # 行业动量
        factors['industry_relative_pe'] = np.random.normal(1.0, 0.3)  # 行业相对估值
        
        # 宏观敏感性因子
        factors['macro_beta'] = np.random.normal(1.0, 0.4)  # 宏观敏感度
        factors['policy_sensitivity'] = np.random.uniform(0.1, 2.0)  # 政策敏感度
        
        # 另类数据综合得分
        factors['alternative_composite'] = (
            factors['main_net_inflow_rate'] * 2 +
            factors['relative_strength_60'] * 3 +
            factors['industry_momentum'] * 1.5 +
            (factors['turnover_anomaly'] - 1) * 1
        )
        
        print(f"  ✅ Layer 4完成: {len(factors)} 个另类因子")
        return factors
    
    # ==================== 因子处理：线性 vs 机器学习 ====================
    
    def process_factors_hybrid_approach(self, factor_df: pd.DataFrame, future_returns: pd.Series) -> Dict:
        """混合处理方法：线性筛选 + 机器学习增强"""
        
        print("\n开始因子处理分析...")
        
        # 第1层：线性快速筛选
        print("  Step 1: 线性关系筛选...")
        linear_results = self.linear_factor_screening(factor_df, future_returns)
        
        # 第2层：机器学习深度分析
        print("  Step 2: 机器学习深度分析...")
        if ML_AVAILABLE:
            ml_results = self.ml_factor_analysis(factor_df, future_returns)
        else:
            ml_results = {}
        
        # 第3层：集成评分
        print("  Step 3: 集成评分优化...")
        final_results = self.ensemble_factor_scoring(linear_results, ml_results)
        
        # 第4层：因子选择
        print("  Step 4: 最优因子组合选择...")
        selected_factors = self.greedy_factor_selection(final_results, factor_df)
        
        return {
            'linear_results': linear_results,
            'ml_results': ml_results,
            'final_scores': final_results,
            'selected_factors': selected_factors,
            'summary': self.generate_analysis_summary(linear_results, ml_results, final_results)
        }
    
    def linear_factor_screening(self, factor_df: pd.DataFrame, future_returns: pd.Series) -> Dict:
        """线性关系筛选"""
        results = {}
        
        for factor_name in factor_df.columns:
            factor_values = factor_df[factor_name].dropna()
            if len(factor_values) < 30:  # 数据不足
                continue
                
            aligned_returns = future_returns.loc[factor_values.index]
            
            # IC (信息系数)
            ic = factor_values.corr(aligned_returns)
            
            # Rank IC
            rank_ic = factor_values.rank().corr(aligned_returns.rank())
            
            # 分组单调性测试
            monotonicity = self.calculate_monotonicity(factor_values, aligned_returns)
            
            # 稳定性测试
            stability = self.calculate_ic_stability(factor_values, aligned_returns)
            
            results[factor_name] = {
                'ic': ic if not np.isnan(ic) else 0,
                'rank_ic': rank_ic if not np.isnan(rank_ic) else 0,
                'monotonicity': monotonicity,
                'stability': stability,
                'linear_score': self.calculate_linear_composite_score(ic, rank_ic, monotonicity, stability)
            }
        
        return results
    
    def ml_factor_analysis(self, factor_df: pd.DataFrame, future_returns: pd.Series) -> Dict:
        """机器学习因子分析"""
        results = {}
        
        try:
            # 数据清洗
            clean_df = factor_df.fillna(method='ffill').fillna(0)
            aligned_returns = future_returns.loc[clean_df.index]
            
            if len(clean_df) < 50:
                return results
            
            # 特征重要性分析
            rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            rf.fit(clean_df, aligned_returns)
            
            feature_importance = rf.feature_importances_
            model_score = rf.score(clean_df, aligned_returns)
            
            # 单因子非线性分析
            for i, factor_name in enumerate(clean_df.columns):
                factor_data = clean_df[[factor_name]]
                
                # 单因子随机森林
                single_rf = RandomForestRegressor(n_estimators=50, random_state=42)
                single_rf.fit(factor_data, aligned_returns)
                single_score = single_rf.score(factor_data, aligned_returns)
                
                # 非线性关系检测
                nonlinear_score = self.detect_nonlinear_relationship(clean_df[factor_name], aligned_returns)
                
                results[factor_name] = {
                    'feature_importance': feature_importance[i],
                    'single_factor_r2': single_score,
                    'nonlinear_score': nonlinear_score,
                    'ml_composite_score': (feature_importance[i] * 0.5 + 
                                         single_score * 0.3 + 
                                         nonlinear_score * 0.2)
                }
            
            # 交互项分析 (选择top 10因子)
            top_factors = sorted(results.items(), key=lambda x: x[1]['feature_importance'], reverse=True)[:10]
            
            for i, (factor1, _) in enumerate(top_factors[:5]):  # 限制交互项数量
                for j, (factor2, _) in enumerate(top_factors[i+1:6], i+1):
                    interaction_name = f"{factor1}_x_{factor2}"
                    interaction_values = clean_df[factor1] * clean_df[factor2]
                    
                    # 交互项预测能力
                    interaction_rf = RandomForestRegressor(n_estimators=30, random_state=42)
                    interaction_rf.fit(interaction_values.values.reshape(-1, 1), aligned_returns)
                    interaction_score = interaction_rf.score(interaction_values.values.reshape(-1, 1), aligned_returns)
                    
                    results[interaction_name] = {
                        'feature_importance': 0,  # 交互项没有直接重要性
                        'single_factor_r2': interaction_score,
                        'nonlinear_score': interaction_score,
                        'ml_composite_score': interaction_score * 0.8,  # 交互项权重稍低
                        'is_interaction': True
                    }
            
        except Exception as e:
            print(f"    机器学习分析失败: {e}")
        
        return results
    
    def detect_nonlinear_relationship(self, factor_values: pd.Series, returns: pd.Series) -> float:
        """检测非线性关系"""
        try:
            # 使用多项式特征检测非线性关系
            from sklearn.preprocessing import PolynomialFeatures
            from sklearn.linear_model import LinearRegression
            
            # 线性关系
            linear_r2 = LinearRegression().fit(factor_values.values.reshape(-1, 1), returns).score(
                factor_values.values.reshape(-1, 1), returns)
            
            # 二次关系
            poly_features = PolynomialFeatures(degree=2)
            factor_poly = poly_features.fit_transform(factor_values.values.reshape(-1, 1))
            poly_r2 = LinearRegression().fit(factor_poly, returns).score(factor_poly, returns)
            
            # 非线性提升度
            nonlinear_improvement = max(0, poly_r2 - linear_r2)
            
            return min(nonlinear_improvement * 5, 1.0)  # 归一化到[0,1]
            
        except:
            return 0.0
    
    def calculate_monotonicity(self, factor_values: pd.Series, returns: pd.Series) -> float:
        """计算因子单调性"""
        try:
            # 分为5个分位数组
            quantiles = pd.qcut(factor_values, 5, duplicates='drop')
            group_returns = returns.groupby(quantiles).mean()
            
            if len(group_returns) < 3:
                return 0
            
            # 计算单调性
            monotonic_increases = sum(group_returns.iloc[i+1] >= group_returns.iloc[i] 
                                    for i in range(len(group_returns)-1))
            monotonic_decreases = sum(group_returns.iloc[i+1] <= group_returns.iloc[i] 
                                    for i in range(len(group_returns)-1))
            
            total_comparisons = len(group_returns) - 1
            return max(monotonic_increases, monotonic_decreases) / total_comparisons
            
        except:
            return 0
    
    def calculate_ic_stability(self, factor_values: pd.Series, returns: pd.Series, window: int = 60) -> float:
        """计算IC稳定性"""
        try:
            if len(factor_values) < window * 2:
                return 0
            
            rolling_ics = []
            for i in range(window, len(factor_values)):
                window_factor = factor_values.iloc[i-window:i]
                window_returns = returns.iloc[i-window:i]
                ic = window_factor.corr(window_returns)
                if not np.isnan(ic):
                    rolling_ics.append(ic)
            
            if len(rolling_ics) < 5:
                return 0
            
            # IC稳定性 = 1 - IC标准差/IC均值的绝对值
            ic_mean = np.mean(rolling_ics)
            ic_std = np.std(rolling_ics)
            
            if abs(ic_mean) > 0:
                stability = 1 - min(ic_std / abs(ic_mean), 2)  # 限制在合理范围
                return max(stability, 0)
            else:
                return 0
                
        except:
            return 0
    
    def calculate_linear_composite_score(self, ic: float, rank_ic: float, monotonicity: float, stability: float) -> float:
        """计算线性综合得分"""
        # 权重配置
        weights = {
            'ic': 0.4,
            'rank_ic': 0.3,
            'monotonicity': 0.2,
            'stability': 0.1
        }
        
        # 处理NaN值
        ic = ic if not np.isnan(ic) else 0
        rank_ic = rank_ic if not np.isnan(rank_ic) else 0
        
        score = (abs(ic) * weights['ic'] + 
                abs(rank_ic) * weights['rank_ic'] +
                monotonicity * weights['monotonicity'] +
                stability * weights['stability'])
        
        return score
    
    def ensemble_factor_scoring(self, linear_results: Dict, ml_results: Dict) -> Dict:
        """集成因子评分"""
        final_scores = {}
        
        all_factors = set(linear_results.keys()) | set(ml_results.keys())
        
        for factor in all_factors:
            linear_score = linear_results.get(factor, {}).get('linear_score', 0)
            ml_score = ml_results.get(factor, {}).get('ml_composite_score', 0)
            
            # 动态权重：如果ML分析可用且效果好，增加ML权重
            if ML_AVAILABLE and ml_score > 0.1:
                ml_weight = 0.6
                linear_weight = 0.4
            else:
                ml_weight = 0.2
                linear_weight = 0.8
            
            final_score = linear_weight * linear_score + ml_weight * ml_score
            
            final_scores[factor] = {
                'linear_component': linear_score,
                'ml_component': ml_score,
                'final_score': final_score,
                'linear_weight': linear_weight,
                'ml_weight': ml_weight
            }
        
        return final_scores
    
    def greedy_factor_selection(self, final_scores: Dict, factor_df: pd.DataFrame, max_factors: int = 12) -> List[str]:
        """贪心算法选择最优因子组合"""
         
        # 按得分排序
        sorted_factors = sorted(final_scores.items(), key=lambda x: x[1]['final_score'], reverse=True)
        
        selected = []
        correlation_matrix = factor_df.corr()
        
        for factor_name, scores in sorted_factors:
            if len(selected) >= max_factors:
                break
            
            if factor_name not in correlation_matrix.columns:
                continue
            
            # 检查与已选因子的相关性
            max_correlation = 0
            if selected:
                correlations = [abs(correlation_matrix.loc[factor_name, selected_factor]) 
                              for selected_factor in selected 
                              if selected_factor in correlation_matrix.columns]
                max_correlation = max(correlations) if correlations else 0
            
            # 相关性阈值：避免选择高度相关的因子
            if max_correlation < 0.7:  # 相关性阈值
                selected.append(factor_name)
        
        return selected
    
    def generate_analysis_summary(self, linear_results: Dict, ml_results: Dict, final_results: Dict) -> Dict:
        """生成分析总结"""
        summary = {
            'total_factors_analyzed': len(final_results),
            'linear_analysis': {
                'factors_count': len(linear_results),
                'avg_ic': np.mean([r['ic'] for r in linear_results.values()]),
                'avg_rank_ic': np.mean([r['rank_ic'] for r in linear_results.values()]),
                'avg_monotonicity': np.mean([r['monotonicity'] for r in linear_results.values()]),
                'avg_stability': np.mean([r['stability'] for r in linear_results.values()])
            },
            'ml_analysis': {
                'factors_count': len(ml_results),
                'avg_feature_importance': np.mean([r['feature_importance'] for r in ml_results.values()]) if ml_results else 0,
                'avg_r2_score': np.mean([r['single_factor_r2'] for r in ml_results.values()]) if ml_results else 0,
                'interaction_factors': sum(1 for r in ml_results.values() if r.get('is_interaction', False))
            },
            'final_ranking': {
                'top_10_factors': sorted(final_results.items(), key=lambda x: x[1]['final_score'], reverse=True)[:10]
            }
        }
        
        return summary
    
    # ==================== 主要演示接口 ====================
    
    def run_complete_demo(self):
        """运行完整演示"""
        print("🚀 开始增强版因子系统完整演示")
        print("=" * 60)
        
        # 1. 生成模拟数据
        print("\n📊 Step 1: 生成模拟股票数据")
        df = self.generate_mock_stock_data('2023-01-01', '2024-01-31')
        
        # 2. 4层因子计算
        print("\n🧮 Step 2: 计算4层因子架构")
        
        # Layer 1
        print("\nLayer 1: 基础技术因子")
        layer1_factors = self.calculate_layer1_basic_factors(df)
        
        # Layer 2  
        print("\nLayer 2: 高级技术因子")
        layer2_factors = self.calculate_layer2_advanced_factors(df)
        
        # Layer 3
        print("\nLayer 3: 基本面因子")
        layer3_factors = self.calculate_layer3_fundamental_factors(df)
        
        # Layer 4
        print("\nLayer 4: 另类因子")
        layer4_factors = self.calculate_layer4_alternative_factors(df)
        
        # 3. 合并因子矩阵
        print("\n🔗 Step 3: 构建完整因子矩阵")
        all_factors = {}
        all_factors.update(layer1_factors)
        all_factors.update(layer2_factors)
        
        # 广播基本面和另类因子到时间序列
        for factor_name, factor_value in layer3_factors.items():
            all_factors[f"fundamental_{factor_name}"] = [factor_value] * len(df)
        
        for factor_name, factor_value in layer4_factors.items():
            all_factors[f"alternative_{factor_name}"] = [factor_value] * len(df)
        
        factor_df = pd.DataFrame(all_factors, index=df.index)
        factor_df['future_return_20d'] = df['close'].shift(-20) / df['close'] - 1
        
        print(f"  ✅ 因子矩阵构建完成: {factor_df.shape[1]-1} 个因子")
        
        # 4. 因子分析处理
        print("\n🔍 Step 4: 因子有效性分析")
        future_returns = factor_df['future_return_20d'].dropna()
        factor_data = factor_df.drop('future_return_20d', axis=1).loc[future_returns.index]
        
        analysis_results = self.process_factors_hybrid_approach(factor_data, future_returns)
        
        # 5. 结果展示
        print("\n📈 Step 5: 分析结果展示")
        self.display_results(analysis_results, factor_df)
        
        # 6. 保存结果
        print("\n💾 Step 6: 保存分析结果")
        self.save_demo_results(factor_df, analysis_results)
        
        print("\n🎉 演示完成！")
        return factor_df, analysis_results
    
    def display_results(self, analysis_results: Dict, factor_df: pd.DataFrame):
        """展示分析结果"""
        
        print("\n" + "="*60)
        print("📊 因子分析结果总结")
        print("="*60)
        
        summary = analysis_results['summary']
        
        print(f"\n🔢 分析概况:")
        print(f"  - 总因子数量: {summary['total_factors_analyzed']}")
        print(f"  - 线性分析因子: {summary['linear_analysis']['factors_count']}")
        print(f"  - 机器学习分析因子: {summary['ml_analysis']['factors_count']}")
        print(f"  - 交互项因子: {summary['ml_analysis']['interaction_factors']}")
        
        print(f"\n📏 线性分析表现:")
        print(f"  - 平均IC: {summary['linear_analysis']['avg_ic']:.4f}")
        print(f"  - 平均Rank IC: {summary['linear_analysis']['avg_rank_ic']:.4f}")
        print(f"  - 平均单调性: {summary['linear_analysis']['avg_monotonicity']:.4f}")
        print(f"  - 平均稳定性: {summary['linear_analysis']['avg_stability']:.4f}")
        
        if ML_AVAILABLE:
            print(f"\n🤖 机器学习表现:")
            print(f"  - 平均特征重要性: {summary['ml_analysis']['avg_feature_importance']:.4f}")
            print(f"  - 平均R²得分: {summary['ml_analysis']['avg_r2_score']:.4f}")
        
        print(f"\n🏆 Top 10 最佳因子:")
        for i, (factor_name, scores) in enumerate(summary['final_ranking']['top_10_factors'], 1):
            print(f"  {i:2d}. {factor_name:<25} | 得分: {scores['final_score']:.4f} "
                  f"| 线性: {scores['linear_component']:.4f} | ML: {scores['ml_component']:.4f}")
        
        print(f"\n✅ 最终选择的因子组合 ({len(analysis_results['selected_factors'])}个):")
        for i, factor in enumerate(analysis_results['selected_factors'], 1):
            score = analysis_results['final_scores'][factor]['final_score']
            print(f"  {i:2d}. {factor:<25} | 得分: {score:.4f}")
    
    def save_demo_results(self, factor_df: pd.DataFrame, analysis_results: Dict):
        """保存演示结果"""
        
        # 保存因子矩阵
        factor_df_clean = factor_df.fillna(0)
        factor_df_clean.to_csv('enhanced_factor_demo_matrix.csv', index=False)
        
        # 保存分析结果
        results_summary = {
            'analysis_summary': analysis_results['summary'],
            'selected_factors': analysis_results['selected_factors'],
            'top_10_scores': {
                factor: scores for factor, scores in 
                sorted(analysis_results['final_scores'].items(), 
                       key=lambda x: x[1]['final_score'], reverse=True)[:10]
            }
        }
        
        import json
        with open('enhanced_factor_demo_results.json', 'w', encoding='utf-8') as f:
            json.dump(results_summary, f, ensure_ascii=False, indent=2)
        
        print("  ✅ 因子矩阵已保存: enhanced_factor_demo_matrix.csv")
        print("  ✅ 分析结果已保存: enhanced_factor_demo_results.json")

def main():
    """主演示函数"""
    demo = EnhancedFactorDemo()
    factor_df, analysis_results = demo.run_complete_demo()
    
    print(f"\n💡 系统能力展示:")
    print(f"  ✅ 4层因子架构: Layer1(基础) + Layer2(高级) + Layer3(基本面) + Layer4(另类)")
    print(f"  ✅ 混合处理方法: 线性筛选 + 机器学习增强 + 集成评分")
    print(f"  ✅ 智能因子选择: 贪心算法 + 相关性过滤")
    print(f"  ✅ 完整分析报告: 线性/非线性/稳定性/单调性全面评估")
    
    print(f"\n🎯 相比原有Agent系统的提升:")
    print(f"  📈 因子数量: 20个基础指标 → {factor_df.shape[1]-1}个高级因子 (提升{((factor_df.shape[1]-1)/20-1)*100:.0f}%)")
    print(f"  🔍 分析维度: 单一技术分析 → 4层多维度分析")
    print(f"  🤖 处理方法: 纯线性逻辑 → 线性+机器学习混合")
    print(f"  📊 评估标准: 简单准确率 → IC/单调性/稳定性综合评估")

if __name__ == "__main__":
    main()