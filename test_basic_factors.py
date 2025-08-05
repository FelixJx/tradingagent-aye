# /Applications/tradingagent/test_basic_factors.py
"""
基础因子测试脚本 - 立即开始测试有效因子
使用您的tushare token: b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065
"""

import sys
import os
sys.path.append('/Applications/tradingagent')

import pandas as pd
import numpy as np
import tushare as ts
import warnings
warnings.filterwarnings('ignore')

# 您的tushare token
TUSHARE_TOKEN = "b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065"

class BasicFactorTester:
    """
    基础因子测试器 - 独立运行版本
    """
    
    def __init__(self, tushare_token: str = TUSHARE_TOKEN):
        self.ts_pro = ts.pro_api(tushare_token)
        print(f"? Tushare API 初始化成功")
    
    def get_stock_data(self, stock_code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取股票数据
        """
        if start_date is None:
            start_date = (pd.Timestamp.now() - pd.Timedelta(days=365)).strftime('%Y%m%d')
        if end_date is None:
            end_date = pd.Timestamp.now().strftime('%Y%m%d')
        
        try:
            print(f"? 正在获取 {stock_code} 的数据...")
            data = self.ts_pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
            
            if data.empty:
                print(f"? 无法获取 {stock_code} 的数据")
                return pd.DataFrame()
            
            data['trade_date'] = pd.to_datetime(data['trade_date'])
            data = data.set_index('trade_date').sort_index()
            
            # 标准化列名
            data.columns = [col.lower() for col in data.columns]
            
            print(f"? 成功获取 {len(data)} 个交易日的数据")
            print(f"? 数据范围: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}")
            
            return data
            
        except Exception as e:
            print(f"? 数据获取失败: {e}")
            return pd.DataFrame()
    
    def generate_basic_factors(self, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        生成基础技术因子
        """
        print(f"? 正在生成基础因子...")
        
        factors = pd.DataFrame(index=stock_data.index)
        
        # 价格和成交量数据
        price = stock_data['close']
        volume = stock_data.get('vol', pd.Series(index=stock_data.index))
        high = stock_data.get('high', price)
        low = stock_data.get('low', price)
        open_price = stock_data.get('open', price)
        
        try:
            # === 动量因子 ===
            print("  ? 生成动量因子...")
            factors['momentum_5'] = price.pct_change(5)      # 5日动量
            factors['momentum_20'] = price.pct_change(20)    # 20日动量
            factors['momentum_60'] = price.pct_change(60)    # 60日动量
            
            # 风险调整动量
            returns = price.pct_change()
            vol_20 = returns.rolling(20).std()
            factors['momentum_risk_adj'] = factors['momentum_20'] / vol_20
            
            # === 反转因子 ===
            print("  ? 生成反转因子...")
            factors['reversal_1'] = -price.pct_change(1)    # 短期反转
            factors['reversal_5'] = -price.pct_change(5)    # 中期反转
            
            # === 波动率因子 ===
            print("  ? 生成波动率因子...")
            factors['volatility_20'] = vol_20               # 20日波动率
            factors['volatility_60'] = returns.rolling(60).std()  # 60日波动率
            factors['volatility_ratio'] = factors['volatility_20'] / factors['volatility_60']
            
            # === 成交量因子 ===
            if not volume.isna().all():
                print("  ? 生成成交量因子...")
                factors['volume_ratio'] = volume / volume.rolling(20).mean()
                factors['volume_price_corr'] = returns.rolling(20).corr(volume.pct_change())
                
                # 成交量激增
                vol_ma = volume.rolling(20).mean()
                vol_std = volume.rolling(20).std()
                factors['volume_surge'] = (volume - vol_ma) / vol_std
            
            # === 价格形态因子 ===
            print("  ? 生成价格形态因子...")
            factors['high_low_ratio'] = (high - low) / price
            factors['gap_ratio'] = (open_price - price.shift(1)) / price.shift(1)
            
            # === 高级因子 ===
            print("  ? 生成高级因子...")
            # 价格位置
            price_min_20 = price.rolling(20).min()
            price_max_20 = price.rolling(20).max()
            factors['price_position'] = (price - price_min_20) / (price_max_20 - price_min_20)
            
            # 动量强度
            factors['momentum_strength'] = returns.rolling(10).sum() / returns.rolling(10).std()
            
            # 数据清理
            factors = factors.replace([np.inf, -np.inf], np.nan)
            factors = factors.dropna()
            
            print(f"? 成功生成 {len(factors.columns)} 个因子，有效数据 {len(factors)} 行")
            
            return factors
            
        except Exception as e:
            print(f"? 因子生成失败: {e}")
            return pd.DataFrame()
    
    def test_factor_effectiveness(self, factors: pd.DataFrame, stock_data: pd.DataFrame, 
                                forward_days: int = 10) -> dict:
        """
        测试因子有效性
        """
        print(f"? 正在测试因子有效性 (前瞻{forward_days}日收益率)...")
        
        if factors.empty:
            return {"error": "因子数据为空"}
        
        price = stock_data['close']
        returns = price.pct_change()
        forward_returns = returns.shift(-forward_days)
        
        results = {}
        
        for i, factor_name in enumerate(factors.columns, 1):
            print(f"  测试因子 {i}/{len(factors.columns)}: {factor_name}")
            
            factor_values = factors[factor_name].dropna()
            
            if len(factor_values) < 50:
                print(f"    ?? 数据点不足: {len(factor_values)}")
                continue
            
            # 对齐数据
            aligned_data = pd.concat([factor_values, forward_returns], axis=1).dropna()
            
            if len(aligned_data) < 30:
                print(f"    ?? 对齐后数据不足: {len(aligned_data)}")
                continue
            
            factor_col = aligned_data.iloc[:, 0]
            return_col = aligned_data.iloc[:, 1]
            
            # 计算IC指标
            ic = factor_col.corr(return_col)
            rank_ic = factor_col.rank().corr(return_col.rank())
            
            # 分组分析
            try:
                quantiles = pd.qcut(factor_col, q=5, labels=False, duplicates='drop')
                group_returns = pd.DataFrame({
                    'factor_group': quantiles,
                    'returns': return_col
                }).groupby('factor_group')['returns'].mean()
                
                # 单调性
                if len(group_returns) >= 3:
                    diffs = group_returns.diff().dropna()
                    if len(diffs) > 0:
                        positive_diffs = (diffs > 0).sum()
                        negative_diffs = (diffs < 0).sum()
                        monotonicity = max(positive_diffs, negative_diffs) / len(diffs)
                    else:
                        monotonicity = 0.5
                else:
                    monotonicity = 0.5
                
                spread = group_returns.max() - group_returns.min()
                
            except Exception as e:
                print(f"    ?? 分组分析失败: {e}")
                monotonicity = 0.5
                spread = 0
            
            # 稳定性分析
            stability = self._calculate_stability(factor_col, return_col)
            
            # 综合评分
            ic_score = abs(ic) * 0.4
            monotonicity_score = monotonicity * 0.3
            spread_score = min(abs(spread) * 100, 1.0) * 0.2
            stability_score = stability * 0.1
            
            final_score = ic_score + monotonicity_score + spread_score + stability_score
            
            results[factor_name] = {
                'IC': ic,
                'Rank_IC': rank_ic,
                'IC_abs': abs(ic),
                'monotonicity': monotonicity,
                'spread': spread,
                'stability': stability,
                'sample_size': len(aligned_data),
                'final_score': final_score
            }
            
            # 实时显示结果
            if abs(ic) > 0.03:  # 显著的IC
                print(f"    ? IC: {ic:.4f}, 评分: {final_score:.4f}")
            else:
                print(f"    ? IC: {ic:.4f}, 评分: {final_score:.4f}")
        
        # 按评分排序
        sorted_results = dict(sorted(results.items(), key=lambda x: x[1]['final_score'], reverse=True))
        
        print(f"? 因子有效性测试完成，共测试 {len(results)} 个因子")
        
        return sorted_results
    
    def _calculate_stability(self, factor_values: pd.Series, returns: pd.Series, window: int = 60) -> float:
        """
        计算因子稳定性
        """
        try:
            rolling_ic = []
            for i in range(window, len(factor_values)):
                window_factor = factor_values.iloc[i-window:i]
                window_returns = returns.iloc[i-window:i]
                ic = window_factor.corr(window_returns)
                if not np.isnan(ic):
                    rolling_ic.append(ic)
            
            if len(rolling_ic) > 5:
                ic_mean = np.mean(rolling_ic)
                ic_std = np.std(rolling_ic)
                stability = 1 - ic_std / (abs(ic_mean) + 0.001)
                return max(0, min(1, stability))
            else:
                return 0.5
        except:
            return 0.5
    
    def run_complete_test(self, stock_code: str, start_date: str = None, end_date: str = None):
        """
        运行完整的因子测试流程
        """
        print(f"? 开始对 {stock_code} 进行完整因子测试")
        print("="*60)
        
        # 1. 获取数据
        stock_data = self.get_stock_data(stock_code, start_date, end_date)
        if stock_data.empty:
            print("? 测试失败：无法获取股票数据")
            return
        
        # 2. 生成因子
        factors = self.generate_basic_factors(stock_data)
        if factors.empty:
            print("? 测试失败：无法生成因子")
            return
        
        # 3. 测试因子有效性
        factor_results = self.test_factor_effectiveness(factors, stock_data)
        if not factor_results or 'error' in factor_results:
            print("? 测试失败：因子有效性测试失败")
            return
        
        # 4. 生成简化报告
        print(f"""
? {stock_code} 因子测试结果
==============================

? 数据概况:
- 数据范围: {stock_data.index[0].strftime('%Y-%m-%d')} 至 {stock_data.index[-1].strftime('%Y-%m-%d')}
- 交易日数量: {len(stock_data)} 天
- 生成因子数量: {len(factors.columns)} 个
- 有效因子数量: {len(factor_results)} 个

? Top 5 最有效因子:""")
        
        if factor_results:
            for i, (factor_name, metrics) in enumerate(list(factor_results.items())[:5], 1):
                ic = metrics['IC']
                final_score = metrics['final_score']
                
                # 评级
                if abs(ic) > 0.05:
                    grade = "? 优秀"
                elif abs(ic) > 0.03:
                    grade = "? 良好"
                elif abs(ic) > 0.01:
                    grade = "? 一般"
                else:
                    grade = "? 较差"
                
                print(f"""{i}. {factor_name} {grade}
   - IC系数: {ic:.4f}
   - Rank IC: {metrics['Rank_IC']:.4f}
   - 单调性: {metrics['monotonicity']:.3f}
   - 稳定性: {metrics['stability']:.3f}
   - 综合评分: {final_score:.4f}
""")
            
            # 投资建议
            top_factor = list(factor_results.keys())[0]
            top_ic = factor_results[top_factor]['IC']
            
            print("? 投资建议:")
            if abs(top_ic) > 0.05:
                suggestion = "? 强烈推荐使用多因子选股策略"
            elif abs(top_ic) > 0.03:
                suggestion = "? 推荐使用因子选股，注意风险控制"
            elif abs(top_ic) > 0.01:
                suggestion = "?? 因子效果一般，建议结合其他分析方法"
            else:
                suggestion = "? 因子效果较差，不建议单独使用"
            
            print(f"""{suggestion}

? 推荐策略:
- 核心因子: {top_factor} (IC: {top_ic:.4f})
- 建议使用多因子组合而非单一因子
- 定期(3-6个月)重新评估因子有效性

==============================
测试完成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
==============================""")
        
        return {
            'stock_data': stock_data,
            'factors': factors,
            'factor_results': factor_results
        }


def main():
    """
    主函数 - 演示如何使用
    """
    print("? 基础因子测试系统启动")
    print("使用您的Tushare Token进行测试")
    print("="*60)
    
    # 初始化测试器
    tester = BasicFactorTester()
    
    # 测试股票列表 (您可以修改这里)
    test_stocks = [
        "000001.SZ",  # 平安银行
        "000002.SZ",  # 万科A  
        "600000.SH",  # 浦发银行
        "600036.SH",  # 招商银行
        "000858.SZ"   # 五粮液
    ]
    
    print(f"? 测试股票列表: {test_stocks}")
    
    # 选择要测试的股票
    while True:
        print("\n" + "="*40)
        print("请选择要测试的股票:")
        for i, stock in enumerate(test_stocks, 1):
            print(f"{i}. {stock}")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选择 (0-5): ").strip()
            
            if choice == '0':
                print("? 测试结束")
                break
            elif choice in ['1', '2', '3', '4', '5']:
                stock_code = test_stocks[int(choice) - 1]
                print(f"\n? 开始测试 {stock_code}")
                
                # 运行完整测试
                results = tester.run_complete_test(stock_code)
                
                if results:
                    print(f"\n? {stock_code} 测试完成!")
                    
                    # 询问是否继续
                    continue_test = input("\n是否继续测试其他股票? (y/n): ").strip().lower()
                    if continue_test != 'y':
                        print("? 测试结束")
                        break
                else:
                    print(f"\n? {stock_code} 测试失败")
                    
            else:
                print("?? 无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n? 用户取消，测试结束")
            break
        except Exception as e:
            print(f"\n? 测试过程中出现错误: {e}")
            continue


if __name__ == "__main__":
    main()