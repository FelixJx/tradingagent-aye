# -*- coding: utf-8 -*-
"""
增强版因子系统 - 独立实现，不依赖qlib
整合您的4层因子架构 + GitHub工具 + 机器学习
"""

import tushare as ts
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import warnings
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')

# 尝试导入GitHub增强工具
try:
    import pandas_ta as ta
    PANDAS_TA_AVAILABLE = True
    print("✅ pandas-ta可用，启用150+技术指标")
except ImportError:
    PANDAS_TA_AVAILABLE = False
    print("⚠️ pandas-ta不可用，使用基础指标")

try:
    import finta
    FINTA_AVAILABLE = True
    print("✅ finta可用，启用金融技术分析")
except ImportError:
    FINTA_AVAILABLE = False
    print("⚠️ finta不可用，使用备用方案")

# 机器学习工具
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
    print("✅ 机器学习工具可用")
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ 机器学习工具不可用")

class EnhancedFactorSystem:
    """
    增强版因子系统
    实现您提出的4层因子架构 + 机器学习增强
    """
    
    def __init__(self, tushare_token: str):
        """初始化系统"""
        ts.set_token(tushare_token)
        self.pro = ts.pro_api()
        self.factor_cache = {}  # 因子缓存
        self.model_cache = {}   # 模型缓存
        
    # ==================== Layer 1: 基础技术因子 ====================
    
    def calculate_layer1_basic_factors(self, df: pd.DataFrame) -> Dict:
        """Layer 1: 基础技术因子 (用您的tushare数据)"""
        factors = {}
        
        # 价格因子
        for period in [1, 5, 10, 20, 60]:
            factors[f'momentum_{period}'] = (df['close'] - df['close'].shift(period)) / df['close'].shift(period)
            factors[f'reversal_{period}'] = -factors[f'momentum_{period}']  # 反转因子
        
        # 波动率因子
        returns = df['close'].pct_change()
        for period in [5, 20, 60]:
            factors[f'volatility_{period}'] = returns.rolling(period).std()
            factors[f'vol_ratio_{period}'] = factors[f'volatility_{period}'] / factors[f'volatility_{period}'].rolling(60).mean()
        
        # 成交量因子
        for period in [5, 20, 60]:
            factors[f'volume_ratio_{period}'] = df['vol'] / df['vol'].rolling(period).mean()
            factors[f'volume_price_corr_{period}'] = returns.rolling(period).corr(df['vol'].pct_change())
        
        # 价格位置因子
        for period in [20, 60, 120]:
            high_max = df['high'].rolling(period).max()
            low_min = df['low'].rolling(period).min()
            factors[f'price_position_{period}'] = (df['close'] - low_min) / (high_max - low_min)
        
        return factors
    
    # ==================== Layer 2: 高级技术因子 ====================
    
    def calculate_layer2_advanced_factors(self, df: pd.DataFrame) -> Dict:
        """Layer 2: 高级技术因子 (需要pandas-ta等工具)"""
        factors = {}
        
        if PANDAS_TA_AVAILABLE:
            # 使用pandas-ta的150+指标
            
            # 趋势指标
            factors['adx'] = ta.adx(df['high'], df['low'], df['close'])['ADX_14']
            factors['aroon_up'] = ta.aroon(df['high'], df['low'])['AROONU_14']
            factors['aroon_down'] = ta.aroon(df['high'], df['low'])['AROOND_14']
            
            # 动量指标
            factors['cci'] = ta.cci(df['high'], df['low'], df['close'])
            factors['cmo'] = ta.cmo(df['close'])
            factors['roc'] = ta.roc(df['close'])
            
            # 波动率指标
            factors['atr'] = ta.atr(df['high'], df['low'], df['close'])
            factors['natr'] = ta.natr(df['high'], df['low'], df['close'])
            factors['true_range'] = ta.true_range(df['high'], df['low'], df['close'])
            
            # 成交量指标
            factors['ad'] = ta.ad(df['high'], df['low'], df['close'], df['vol'])
            factors['adosc'] = ta.adosc(df['high'], df['low'], df['close'], df['vol'])
            factors['cmf'] = ta.cmf(df['high'], df['low'], df['close'], df['vol'])
            factors['mfi'] = ta.mfi(df['high'], df['low'], df['close'], df['vol'])
            factors['nvi'] = ta.nvi(df['close'], df['vol'])
            factors['pvi'] = ta.pvi(df['close'], df['vol'])
            
            # 统计指标
            factors['zscore'] = ta.zscore(df['close'])
            factors['entropy'] = ta.entropy(df['close'])
            
        else:
            # 手动实现关键高级指标
            factors.update(self._manual_advanced_factors(df))
        
        # 自研高级因子
        returns = df['close'].pct_change()
        
        # 风险调整动量因子
        for period in [10, 20, 60]:
            momentum = factors.get(f'momentum_{period}', (df['close'] - df['close'].shift(period)) / df['close'].shift(period))
            volatility = returns.rolling(period).std()
            factors[f'risk_adj_momentum_{period}'] = momentum / volatility
        
        # 动量偏度因子
        for period in [20, 60]:
            factors[f'momentum_skew_{period}'] = returns.rolling(period).skew()
            factors[f'momentum_kurt_{period}'] = returns.rolling(period).kurt()
        
        # 价格冲击因子
        factors['price_impact'] = returns / np.log(df['vol'] + 1)  # 避免log(0)
        
        # 订单不平衡代理
        factors['order_imbalance_proxy'] = (df['vol'] * np.sign(returns)).cumsum()
        
        return factors
    
    def _manual_advanced_factors(self, df: pd.DataFrame) -> Dict:
        """手动实现高级因子（pandas-ta不可用时的备用方案）"""
        factors = {}
        
        # 手动ADX
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
        
        # 手动MFI
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        raw_money_flow = typical_price * df['vol']
        
        positive_flow = raw_money_flow.where(typical_price > typical_price.shift(1), 0).rolling(14).sum()
        negative_flow = raw_money_flow.where(typical_price < typical_price.shift(1), 0).rolling(14).sum()
        money_ratio = positive_flow / negative_flow
        factors['mfi'] = 100 - (100 / (1 + money_ratio))
        
        return factors
    
    # ==================== Layer 3: 基本面因子 ====================
    
    def calculate_layer3_fundamental_factors(self, stock_code: str, end_date: str) -> Dict:
        """Layer 3: 基本面因子 (tushare pro接口)"""
        factors = {}
        
        try:
            # 获取最新财务数据
            
            # 利润表数据
            income = self.pro.income(ts_code=stock_code, period=end_date[:4] + '1231')
            if not income.empty:
                income_data = income.iloc[0]
                factors['revenue'] = income_data.get('revenue', 0)
                factors['net_profit'] = income_data.get('n_income', 0)
                factors['operate_profit'] = income_data.get('operate_profit', 0)
            
            # 资产负债表数据
            balance = self.pro.balancesheet(ts_code=stock_code, period=end_date[:4] + '1231')
            if not balance.empty:
                balance_data = balance.iloc[0]
                factors['total_assets'] = balance_data.get('total_assets', 0)
                factors['total_liab'] = balance_data.get('total_liab', 0)
                factors['total_equity'] = balance_data.get('total_hldr_eqy_exc_min_int', 0)
            
            # 现金流量表数据
            cashflow = self.pro.cashflow(ts_code=stock_code, period=end_date[:4] + '1231')
            if not cashflow.empty:
                cf_data = cashflow.iloc[0]
                factors['operate_cash_flow'] = cf_data.get('n_cashflow_act', 0)
                factors['invest_cash_flow'] = cf_data.get('n_cashflow_inv_act', 0)
                factors['finance_cash_flow'] = cf_data.get('n_cashflow_fin_act', 0)
            
            # 估值因子
            if factors.get('net_profit', 0) != 0:
                # 获取市值数据
                daily_basic = self.pro.daily_basic(ts_code=stock_code, trade_date=end_date.replace('-', ''))
                if not daily_basic.empty:
                    market_cap = daily_basic.iloc[0].get('total_mv', 0) * 10000  # 万元转元
                    factors['pe_ratio'] = market_cap / factors['net_profit'] if factors['net_profit'] > 0 else np.nan
                    factors['pb_ratio'] = market_cap / factors['total_equity'] if factors.get('total_equity', 0) > 0 else np.nan
            
            # 成长因子 - 需要历史数据对比
            prev_year = str(int(end_date[:4]) - 1) + '1231'
            prev_income = self.pro.income(ts_code=stock_code, period=prev_year)
            if not prev_income.empty and not income.empty:
                prev_revenue = prev_income.iloc[0].get('revenue', 0)
                prev_profit = prev_income.iloc[0].get('n_income', 0)
                
                if prev_revenue > 0:
                    factors['revenue_growth'] = (factors.get('revenue', 0) - prev_revenue) / prev_revenue
                if prev_profit > 0:
                    factors['profit_growth'] = (factors.get('net_profit', 0) - prev_profit) / prev_profit
            
            # 盈利质量因子
            if factors.get('net_profit', 0) != 0 and factors.get('operate_cash_flow', 0) != 0:
                factors['accrual_ratio'] = (factors['operate_cash_flow'] - factors['net_profit']) / abs(factors['net_profit'])
            
            # ROE、ROA等
            if factors.get('total_equity', 0) > 0:
                factors['roe'] = factors.get('net_profit', 0) / factors['total_equity']
            if factors.get('total_assets', 0) > 0:
                factors['roa'] = factors.get('net_profit', 0) / factors['total_assets']
                factors['asset_turnover'] = factors.get('revenue', 0) / factors['total_assets']
            
        except Exception as e:
            print(f"获取基本面数据失败: {e}")
            # 返回空因子，避免系统崩溃
            factors = {'fundamental_error': 1}
        
        return factors
    
    # ==================== Layer 4: 另类因子 ====================
    
    def calculate_layer4_alternative_factors(self, stock_code: str, df: pd.DataFrame) -> Dict:
        """Layer 4: 另类因子 (需要外部数据源)"""
        factors = {}
        
        try:
            # 资金流向因子
            
            # 获取资金流向数据
            recent_date = df.iloc[-1]['trade_date'].strftime('%Y%m%d')
            
            # 主力资金流向
            money_flow = self.pro.moneyflow(ts_code=stock_code, trade_date=recent_date)
            if not money_flow.empty:
                mf_data = money_flow.iloc[0]
                factors['main_net_inflow'] = mf_data.get('net_mf_amount', 0)  # 主力净流入
                factors['main_net_inflow_rate'] = mf_data.get('net_mf_rate', 0)  # 主力净流入率
            
            # 北向资金（如果是港股通标的）
            try:
                hsgt_holder = self.pro.hk_hold(ts_code=stock_code, trade_date=recent_date)
                if not hsgt_holder.empty:
                    factors['northbound_holding'] = hsgt_holder.iloc[0].get('shareholding', 0)
            except:
                factors['northbound_holding'] = 0
            
            # 融资融券数据
            try:
                margin = self.pro.margin(ts_code=stock_code, trade_date=recent_date)
                if not margin.empty:
                    margin_data = margin.iloc[0]
                    factors['margin_balance'] = margin_data.get('rzye', 0)  # 融资余额
                    factors['margin_buy'] = margin_data.get('rzmre', 0)      # 融资买入额
                    
                    # 融资余额趋势
                    prev_margin = self.pro.margin(ts_code=stock_code, 
                                                trade_date=(pd.to_datetime(recent_date) - timedelta(days=5)).strftime('%Y%m%d'))
                    if not prev_margin.empty:
                        prev_balance = prev_margin.iloc[0].get('rzye', 0)
                        if prev_balance > 0:
                            factors['margin_trend'] = (factors['margin_balance'] - prev_balance) / prev_balance
            except:
                factors['margin_balance'] = 0
                factors['margin_buy'] = 0
                factors['margin_trend'] = 0
            
            # 情绪代理指标
            
            # 换手率作为关注度代理
            if len(df) > 20:
                factors['turnover_rate_avg'] = df['turnover_rate'].tail(20).mean()
                factors['turnover_rate_spike'] = df['turnover_rate'].iloc[-1] / factors['turnover_rate_avg'] if factors['turnover_rate_avg'] > 0 else 1
            
            # 涨跌停信息作为情绪指标
            factors['limit_up_days'] = sum(df['pct_chg'].tail(20) >= 9.8)  # 近20日涨停次数
            factors['limit_down_days'] = sum(df['pct_chg'].tail(20) <= -9.8)  # 近20日跌停次数
            
            # 行业相对强度
            # 获取行业分类
            try:
                industry_info = self.pro.stock_basic(ts_code=stock_code, fields='ts_code,industry')
                if not industry_info.empty:
                    industry = industry_info.iloc[0]['industry']
                    # 这里可以扩展为获取行业指数对比
                    factors['industry'] = hash(industry) % 1000  # 简化的行业编码
            except:
                factors['industry'] = 0
                
        except Exception as e:
            print(f"获取另类数据失败: {e}")
            # 返回默认值
            factors.update({
                'main_net_inflow': 0,
                'main_net_inflow_rate': 0,
                'northbound_holding': 0,
                'margin_balance': 0,
                'margin_trend': 0,
                'turnover_rate_avg': 0,
                'turnover_rate_spike': 1
            })
        
        return factors
    
    # ==================== 因子处理：线性 vs 机器学习组合 ====================
    
    def process_factors_linear_ml_combo(self, factor_df: pd.DataFrame, future_returns: pd.Series) -> Dict:
        """因子处理：线性+机器学习组合策略"""
        
        # 第1层：线性快速筛选
        linear_scores = self.linear_factor_screening(factor_df, future_returns)
        
        # 第2层：非线性深度挖掘
        if ML_AVAILABLE:
            ml_scores = self.ml_factor_analysis(factor_df, future_returns)
        else:
            ml_scores = {}
        
        # 第3层：集成优化
        final_scores = self.ensemble_factor_scoring(linear_scores, ml_scores)
        
        return {
            'linear_scores': linear_scores,
            'ml_scores': ml_scores,
            'final_scores': final_scores,
            'selected_factors': self.select_top_factors(final_scores)
        }
    
    def linear_factor_screening(self, factor_df: pd.DataFrame, future_returns: pd.Series) -> Dict:
        """第1层：线性快速筛选"""
        scores = {}
        
        for factor_name in factor_df.columns:
            factor_values = factor_df[factor_name].dropna()
            aligned_returns = future_returns.loc[factor_values.index]
            
            if len(factor_values) > 20:  # 确保有足够数据
                # IC分数
                ic_score = factor_values.corr(aligned_returns)
                
                # Rank IC分数
                rank_ic = factor_values.rank().corr(aligned_returns.rank())
                
                # 单调性检验
                monotonicity = self.calculate_monotonicity(factor_values, aligned_returns)
                
                scores[factor_name] = {
                    'ic': ic_score if not np.isnan(ic_score) else 0,
                    'rank_ic': rank_ic if not np.isnan(rank_ic) else 0,
                    'monotonicity': monotonicity,
                    'linear_score': abs(ic_score) * 0.6 + abs(rank_ic) * 0.4 if not np.isnan(ic_score) and not np.isnan(rank_ic) else 0
                }
        
        return scores
    
    def ml_factor_analysis(self, factor_df: pd.DataFrame, future_returns: pd.Series) -> Dict:
        """第2层：非线性深度挖掘"""
        scores = {}
        
        try:
            # 准备数据
            clean_df = factor_df.fillna(0)
            aligned_returns = future_returns.loc[clean_df.index]
            
            if len(clean_df) > 50:  # 确保有足够数据训练模型
                
                # 随机森林特征重要性
                rf = RandomForestRegressor(n_estimators=100, random_state=42)
                rf.fit(clean_df, aligned_returns)
                
                feature_importance = rf.feature_importances_
                
                for i, factor_name in enumerate(clean_df.columns):
                    scores[factor_name] = {
                        'rf_importance': feature_importance[i],
                        'rf_score': rf.score(clean_df, aligned_returns)
                    }
                
                # 交互项分析（选择前10个最重要的因子）
                top_factors = sorted(scores.items(), key=lambda x: x[1]['rf_importance'], reverse=True)[:10]
                
                for i, (factor1, _) in enumerate(top_factors):
                    for j, (factor2, _) in enumerate(top_factors[i+1:], i+1):
                        interaction_name = f"{factor1}_x_{factor2}"
                        interaction_values = clean_df[factor1] * clean_df[factor2]
                        
                        # 计算交互项的预测能力
                        rf_inter = RandomForestRegressor(n_estimators=50, random_state=42)
                        rf_inter.fit(interaction_values.values.reshape(-1, 1), aligned_returns)
                        
                        scores[interaction_name] = {
                            'rf_importance': rf_inter.score(interaction_values.values.reshape(-1, 1), aligned_returns),
                            'rf_score': rf_inter.score(interaction_values.values.reshape(-1, 1), aligned_returns),
                            'is_interaction': True
                        }
        
        except Exception as e:
            print(f"机器学习因子分析失败: {e}")
        
        return scores
    
    def calculate_monotonicity(self, factor_values: pd.Series, returns: pd.Series) -> float:
        """计算因子单调性"""
        try:
            # 分为5个分位数组
            quantiles = pd.qcut(factor_values, 5, duplicates='drop')
            group_returns = returns.groupby(quantiles).mean()
            
            # 计算单调性（相邻组收益率是否单调）
            monotonic_increases = sum(group_returns.iloc[i+1] > group_returns.iloc[i] 
                                    for i in range(len(group_returns)-1))
            monotonic_decreases = sum(group_returns.iloc[i+1] < group_returns.iloc[i] 
                                    for i in range(len(group_returns)-1))
            
            total_comparisons = len(group_returns) - 1
            if total_comparisons > 0:
                return max(monotonic_increases, monotonic_decreases) / total_comparisons
            else:
                return 0
        except:
            return 0
    
    def ensemble_factor_scoring(self, linear_scores: Dict, ml_scores: Dict) -> Dict:
        """第3层：集成优化"""
        final_scores = {}
        
        # 合并所有因子
        all_factors = set(linear_scores.keys()) | set(ml_scores.keys())
        
        for factor in all_factors:
            linear_score = linear_scores.get(factor, {}).get('linear_score', 0)
            ml_score = ml_scores.get(factor, {}).get('rf_importance', 0)
            
            # 权重组合
            if ML_AVAILABLE and ml_score > 0:
                final_score = 0.6 * linear_score + 0.4 * ml_score
            else:
                final_score = linear_score
            
            final_scores[factor] = {
                'linear_component': linear_score,
                'ml_component': ml_score,
                'final_score': final_score,
                'source': 'ensemble'
            }
        
        return final_scores
    
    def select_top_factors(self, final_scores: Dict, max_factors: int = 15) -> List[str]:
        """选择top因子，考虑相关性"""
        # 按分数排序
        sorted_factors = sorted(final_scores.items(), key=lambda x: x[1]['final_score'], reverse=True)
        
        selected = []
        for factor_name, scores in sorted_factors:
            if len(selected) >= max_factors:
                break
            
            # 简单的相关性过滤（可以进一步优化）
            if not any(self.factor_name_similarity(factor_name, selected_factor) > 0.8 
                      for selected_factor in selected):
                selected.append(factor_name)
        
        return selected
    
    def factor_name_similarity(self, name1: str, name2: str) -> float:
        """简单的因子名称相似度"""
        # 提取数字和关键词
        import re
        
        # 提取基础名称（去掉数字）
        base1 = re.sub(r'_\d+', '', name1)
        base2 = re.sub(r'_\d+', '', name2)
        
        if base1 == base2:
            return 1.0
        elif base1 in name2 or base2 in name1:
            return 0.8
        else:
            return 0.0
    
    # ==================== 主要接口函数 ====================
    
    def generate_complete_factor_matrix(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """生成完整因子矩阵"""
        print(f"开始生成 {stock_code} 的完整因子矩阵...")
        
        # 获取基础价格数据
        df = self.pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        if df.empty:
            print(f"无法获取 {stock_code} 的数据")
            return pd.DataFrame()
        
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values('trade_date').reset_index(drop=True)
        
        print(f"获取到 {len(df)} 条价格数据")
        
        # Layer 1: 基础技术因子
        print("计算Layer 1: 基础技术因子...")
        layer1_factors = self.calculate_layer1_basic_factors(df)
        
        # Layer 2: 高级技术因子
        print("计算Layer 2: 高级技术因子...")
        layer2_factors = self.calculate_layer2_advanced_factors(df)
        
        # Layer 3: 基本面因子
        print("计算Layer 3: 基本面因子...")
        layer3_factors = self.calculate_layer3_fundamental_factors(stock_code, end_date)
        
        # Layer 4: 另类因子
        print("计算Layer 4: 另类因子...")
        layer4_factors = self.calculate_layer4_alternative_factors(stock_code, df)
        
        # 合并所有因子
        all_factors = {}
        all_factors.update(layer1_factors)
        all_factors.update(layer2_factors)
        
        # 基本面和另类因子需要广播到时间序列
        for factor_name, factor_value in layer3_factors.items():
            all_factors[f"fundamental_{factor_name}"] = [factor_value] * len(df)
        
        for factor_name, factor_value in layer4_factors.items():
            all_factors[f"alternative_{factor_name}"] = [factor_value] * len(df)
        
        # 创建因子DataFrame
        factor_df = pd.DataFrame(all_factors, index=df.index)
        factor_df['trade_date'] = df['trade_date']
        factor_df['close'] = df['close']
        factor_df['future_return_5d'] = df['close'].shift(-5) / df['close'] - 1  # 5日未来收益
        factor_df['future_return_20d'] = df['close'].shift(-20) / df['close'] - 1  # 20日未来收益
        
        print(f"生成完整因子矩阵: {factor_df.shape[1]} 个因子")
        
        return factor_df
    
    def analyze_factor_effectiveness(self, factor_df: pd.DataFrame) -> Dict:
        """分析因子有效性"""
        print("开始因子有效性分析...")
        
        if 'future_return_20d' not in factor_df.columns:
            print("缺少未来收益数据，无法进行有效性分析")
            return {}
        
        future_returns = factor_df['future_return_20d'].dropna()
        factor_columns = [col for col in factor_df.columns 
                         if col not in ['trade_date', 'close', 'future_return_5d', 'future_return_20d']]
        
        factor_data = factor_df[factor_columns].loc[future_returns.index]
        
        # 进行线性+机器学习组合分析
        analysis_results = self.process_factors_linear_ml_combo(factor_data, future_returns)
        
        print(f"因子分析完成，发现 {len(analysis_results['selected_factors'])} 个有效因子")
        
        return analysis_results

def main():
    """测试增强因子系统"""
    
    # 初始化系统
    enhanced_system = EnhancedFactorSystem('b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065')
    
    # 测试单只股票
    test_stock = '000001.SZ'
    start_date = '20230101'
    end_date = '20240131'
    
    # 生成因子矩阵
    factor_matrix = enhanced_system.generate_complete_factor_matrix(test_stock, start_date, end_date)
    
    if not factor_matrix.empty:
        print(f"\n因子矩阵生成成功: {factor_matrix.shape}")
        print(f"因子列表: {list(factor_matrix.columns)}")
        
        # 分析因子有效性
        effectiveness = enhanced_system.analyze_factor_effectiveness(factor_matrix)
        
        if effectiveness:
            print(f"\n顶级因子: {effectiveness['selected_factors']}")
            
            # 显示前10个因子的得分
            top_10 = sorted(effectiveness['final_scores'].items(), 
                           key=lambda x: x[1]['final_score'], reverse=True)[:10]
            
            print("\n前10个因子得分:")
            for factor_name, scores in top_10:
                print(f"  {factor_name}: {scores['final_score']:.4f}")
        
        # 保存结果
        factor_matrix.to_csv(f'{test_stock}_enhanced_factors.csv', index=False)
        print(f"\n因子矩阵已保存: {test_stock}_enhanced_factors.csv")

if __name__ == "__main__":
    main()