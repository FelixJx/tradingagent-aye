#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行qlib数据库集成的增强因子系统
"""

import sys
import os
import sqlite3
# Note: removed typing import for Python 3.3 compatibility

# 简化版的pandas功能（避免依赖问题）
class SimpleDataFrame:
    def __init__(self, data=None, columns=None):
        if isinstance(data, dict):
            self.data = data
            self.columns = list(data.keys()) if columns is None else columns
        elif isinstance(data, list) and columns:
            self.data = {}
            for i, col in enumerate(columns):
                self.data[col] = [row[i] if i < len(row) else None for row in data]
            self.columns = columns
        else:
            self.data = {}
            self.columns = []
    
    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        return []
    
    def __len__(self):
        if self.columns:
            return len(self.data[self.columns[0]])
        return 0
    
    def empty(self):
        return len(self) == 0

class QlibIntegratedFactorSystem:
    """
    qlib数据库集成的增强因子系统
    """
    
    def __init__(self):
        self.qlib_db_path = '/Users/jx/Downloads/qlib-main/databases/real_tushare_factor_analysis.db'
        print("🚀 初始化qlib集成因子系统...")
        
        if not os.path.exists(self.qlib_db_path):
            print("❌ qlib数据库不存在")
            return
        
        print("✅ qlib数据库连接就绪")
    
    def load_stock_data(self, stock_code: str, start_date: str = '2025-05-01', end_date: str = '2025-07-15'):
        """从qlib数据库加载股票数据"""
        try:
            conn = sqlite3.connect(self.qlib_db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT ts_code, trade_date, open, high, low, close, vol, amount, pct_chg,
                   volatility_5d, volatility_10d, volatility_20d, 
                   volume_ratio_5d, volume_ratio_10d, volume_ratio_20d,
                   rsi_14, ma_distance_5d, ma_distance_10d
            FROM factor_data 
            WHERE ts_code = ? 
            AND trade_date >= ? 
            AND trade_date <= ?
            ORDER BY trade_date
            """
            
            cursor.execute(query, [stock_code, start_date, end_date])
            rows = cursor.fetchall()
            
            columns = [
                'ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount', 'pct_chg',
                'volatility_5d', 'volatility_10d', 'volatility_20d', 
                'volume_ratio_5d', 'volume_ratio_10d', 'volume_ratio_20d',
                'rsi_14', 'ma_distance_5d', 'ma_distance_10d'
            ]
            
            df = SimpleDataFrame(rows, columns)
            conn.close()
            
            print("✅ 加载 {} 数据: {} 条记录".format(stock_code, len(df)))
            return df
            
        except Exception as e:
            print("❌ 加载数据失败: {}".format(e))
            return SimpleDataFrame()
    
    def calculate_enhanced_factors(self, df):
        """计算增强因子"""
        if df.empty():
            return {}
        
        factors = {}
        n = len(df)
        
        # 基础价格因子
        close_prices = df['close']
        
        # 动量因子
        for period in [1, 3, 5, 10, 20]:
            if period < n:
                momentum = []
                for i in range(n):
                    if i >= period and close_prices[i-period] and close_prices[i]:
                        mom = (close_prices[i] - close_prices[i-period]) / close_prices[i-period]
                        momentum.append(mom)
                    else:
                        momentum.append(None)
                factors['momentum_{}d'.format(period)] = momentum
        
        # 波动率因子 (使用已有的数据)
        if 'volatility_5d' in df.data:
            factors['volatility_5d'] = df['volatility_5d']
        if 'volatility_10d' in df.data:
            factors['volatility_10d'] = df['volatility_10d']
        if 'volatility_20d' in df.data:
            factors['volatility_20d'] = df['volatility_20d']
        
        # 成交量比率因子
        if 'volume_ratio_5d' in df.data:
            factors['volume_ratio_5d'] = df['volume_ratio_5d']
        if 'volume_ratio_10d' in df.data:
            factors['volume_ratio_10d'] = df['volume_ratio_10d']
        if 'volume_ratio_20d' in df.data:
            factors['volume_ratio_20d'] = df['volume_ratio_20d']
        
        # RSI因子
        if 'rsi_14' in df.data:
            factors['rsi_14'] = df['rsi_14']
        
        # MA距离因子
        if 'ma_distance_5d' in df.data:
            factors['ma_distance_5d'] = df['ma_distance_5d']
        if 'ma_distance_10d' in df.data:
            factors['ma_distance_10d'] = df['ma_distance_10d']
        
        # 高级因子：价格位置
        high_prices = df['high']
        low_prices = df['low']
        
        for period in [10, 20]:
            if period < n:
                price_position = []
                for i in range(n):
                    if i >= period-1:
                        # 计算period天内的最高最低价
                        period_highs = [high_prices[j] for j in range(max(0, i-period+1), i+1) if high_prices[j]]
                        period_lows = [low_prices[j] for j in range(max(0, i-period+1), i+1) if low_prices[j]]
                        
                        if period_highs and period_lows and close_prices[i]:
                            high_max = max(period_highs)
                            low_min = min(period_lows)
                            if high_max > low_min:
                                pos = (close_prices[i] - low_min) / (high_max - low_min)
                                price_position.append(pos)
                            else:
                                price_position.append(0.5)
                        else:
                            price_position.append(None)
                    else:
                        price_position.append(None)
                factors['price_position_{}d'.format(period)] = price_position
        
        # 计算未来收益率作为目标
        future_returns_5d = []
        future_returns_20d = []
        
        for i in range(n):
            # 5日未来收益
            if i + 5 < n and close_prices[i] and close_prices[i+5]:
                ret_5d = (close_prices[i+5] - close_prices[i]) / close_prices[i]
                future_returns_5d.append(ret_5d)
            else:
                future_returns_5d.append(None)
            
            # 20日未来收益
            if i + 20 < n and close_prices[i] and close_prices[i+20]:
                ret_20d = (close_prices[i+20] - close_prices[i]) / close_prices[i]
                future_returns_20d.append(ret_20d)
            else:
                future_returns_20d.append(None)
        
        factors['future_return_5d'] = future_returns_5d
        factors['future_return_20d'] = future_returns_20d
        
        return factors
    
    def analyze_factor_performance(self, factors):
        """分析因子表现"""
        if not factors or 'future_return_20d' not in factors:
            return {}
        
        future_returns = [x for x in factors['future_return_20d'] if x is not None]
        
        if len(future_returns) < 20:
            print("⚠️ 有效样本不足，无法进行因子分析")
            return {}
        
        results = {}
        
        print("📊 分析因子有效性 (有效样本: {})".format(len(future_returns)))
        
        for factor_name, factor_values in factors.items():
            if factor_name.startswith('future_return'):
                continue
            
            # 获取有效的因子值和对应的未来收益
            valid_pairs = []
            for i, fval in enumerate(factor_values):
                if (fval is not None and i < len(factors['future_return_20d']) and 
                    factors['future_return_20d'][i] is not None):
                    valid_pairs.append((fval, factors['future_return_20d'][i]))
            
            if len(valid_pairs) < 10:
                continue
            
            factor_vals = [pair[0] for pair in valid_pairs]
            return_vals = [pair[1] for pair in valid_pairs]
            
            # 计算相关系数 (简化版)
            n_pairs = len(valid_pairs)
            mean_factor = sum(factor_vals) / n_pairs
            mean_return = sum(return_vals) / n_pairs
            
            # 协方差和方差
            covariance = sum((f - mean_factor) * (r - mean_return) for f, r in zip(factor_vals, return_vals)) / (n_pairs - 1)
            var_factor = sum((f - mean_factor) ** 2 for f in factor_vals) / (n_pairs - 1)
            var_return = sum((r - mean_return) ** 2 for r in return_vals) / (n_pairs - 1)
            
            # 相关系数
            if var_factor > 0 and var_return > 0:
                correlation = covariance / (var_factor ** 0.5 * var_return ** 0.5)
            else:
                correlation = 0
            
            # 分组测试（分为5组）
            sorted_pairs = sorted(valid_pairs, key=lambda x: x[0])
            group_size = len(sorted_pairs) // 5
            
            group_returns = []
            for g in range(5):
                start_idx = g * group_size
                end_idx = start_idx + group_size if g < 4 else len(sorted_pairs)
                group_data = sorted_pairs[start_idx:end_idx]
                
                if group_data:
                    avg_return = sum(pair[1] for pair in group_data) / len(group_data)
                    group_returns.append(avg_return)
                else:
                    group_returns.append(0)
            
            # 多空收益 (最高组 - 最低组)
            long_short_return = group_returns[-1] - group_returns[0] if len(group_returns) >= 2 else 0
            
            # 单调性检测
            monotonic_increases = sum(1 for i in range(len(group_returns)-1) if group_returns[i+1] > group_returns[i])
            monotonic_decreases = sum(1 for i in range(len(group_returns)-1) if group_returns[i+1] < group_returns[i])
            monotonicity = max(monotonic_increases, monotonic_decreases) / (len(group_returns) - 1) if len(group_returns) > 1 else 0
            
            results[factor_name] = {
                'correlation': correlation,
                'long_short_return': long_short_return,
                'monotonicity': monotonicity,
                'sample_size': n_pairs,
                'score': abs(correlation) * 0.4 + abs(long_short_return) * 100 * 0.4 + monotonicity * 0.2
            }
        
        return results
    
    def run_full_analysis(self, stock_code):
        """运行完整分析"""
        print("🔍 开始分析 {}".format(stock_code))
        print("=" * 60)
        
        # 加载数据
        df = self.load_stock_data(stock_code)
        if df.empty():
            print("❌ {} 数据加载失败".format(stock_code))
            return None
        
        # 计算因子
        print("计算增强因子...")
        factors = self.calculate_enhanced_factors(df)
        
        if not factors:
            print("❌ 因子计算失败")
            return None
        
        print("✅ 计算出 {} 个因子".format(len(factors)))
        
        # 分析因子有效性
        print("分析因子有效性...")
        analysis = self.analyze_factor_performance(factors)
        
        if not analysis:
            print("❌ 因子分析失败")
            return None
        
        # 显示结果
        print("\n📊 {} 因子分析结果".format(stock_code))
        print("-" * 60)
        
        # 按得分排序
        sorted_factors = sorted(analysis.items(), key=lambda x: x[1]['score'], reverse=True)
        
        print("Top 10 最佳因子:")
        print("因子名称 | 相关系数 | 多空收益 | 单调性 | 样本数 | 综合得分")
        print("-" * 80)
        
        for i, (factor_name, metrics) in enumerate(sorted_factors[:10]):
            print("{:<20} | {:7.4f} | {:8.4f} | {:6.3f} | {:6d} | {:8.4f}".format(
                factor_name, metrics['correlation'], metrics['long_short_return'], 
                metrics['monotonicity'], metrics['sample_size'], metrics['score']))
        
        # 选择最佳因子（得分>0.1的因子）
        best_factors = [name for name, metrics in sorted_factors if metrics['score'] > 0.1]
        
        print("\n✅ 选择的最佳因子 ({}个):".format(len(best_factors)))
        for factor in best_factors[:8]:  # 显示前8个
            print("  - {}".format(factor))
        
        return {
            'stock_code': stock_code,
            'factors': factors,
            'analysis': analysis,
            'best_factors': best_factors,
            'data_records': len(df)
        }

def main():
    """主程序"""
    print("🚀 启动qlib集成增强因子系统测试...")
    
    system = QlibIntegratedFactorSystem()
    
    # 测试多只股票
    test_stocks = ['000001.SZ', '000002.SZ', '000006.SZ']
    results = {}
    
    for stock_code in test_stocks:
        print("\n" + "="*80)
        result = system.run_full_analysis(stock_code)
        if result:
            results[stock_code] = result
        print("="*80)
    
    # 汇总结果
    print("\n🎉 分析完成！成功分析了 {} 只股票".format(len(results)))
    
    if results:
        print("\n📈 各股票最佳因子汇总:")
        all_best_factors = set()
        
        for stock_code, result in results.items():
            best_factors = result['best_factors'][:5]  # 每只股票前5个最佳因子
            all_best_factors.update(best_factors)
            print("  {}: {} 个有效因子".format(stock_code, len(result['best_factors'])))
        
        print("\n🏆 跨股票通用的优秀因子 (共{}个):".format(len(all_best_factors)))
        for factor in sorted(all_best_factors):
            print("  - {}".format(factor))
        
        # 保存结果
        result_file = 'qlib_integrated_factor_analysis_results.txt'
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write("qlib集成增强因子系统分析结果\\n")
            f.write("="*60 + "\\n\\n")
            
            for stock_code, result in results.items():
                f.write("股票: {}\\n".format(stock_code))
                f.write("数据记录数: {}\\n".format(result['data_records']))
                f.write("有效因子数: {}\\n".format(len(result['best_factors'])))
                f.write("最佳因子: {}\\n\\n".format(', '.join(result['best_factors'][:5])))
            
            f.write("通用优秀因子:\\n")
            for factor in sorted(all_best_factors):
                f.write("  - {}\\n".format(factor))
        
        print("\\n💾 结果已保存到: {}".format(result_file))
    
    print("\\n🎊 qlib集成测试完成！")

if __name__ == "__main__":
    main()