#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于真实tushare数据的增强因子系统
结合qlib本地数据和tushare实时数据
"""

import tushare as ts
import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime, timedelta
import time

class TushareEnhancedFactorSystem:
    """
    结合tushare和qlib的增强因子系统
    """
    
    def __init__(self, tushare_token):
        print("🚀 初始化Tushare增强因子系统...")
        
        # 初始化tushare
        ts.set_token(tushare_token)
        self.pro = ts.pro_api()
        
        # qlib数据库路径
        self.qlib_db_path = '/Users/jx/Downloads/qlib-main/databases/real_tushare_factor_analysis.db'
        
        print("✅ 系统初始化完成")
    
    def get_hybrid_stock_data(self, stock_code, start_date='20250701', end_date='20250731', use_tushare=True):
        """
        获取混合数据：优先tushare实时，备用qlib历史
        """
        print(f"🔍 获取 {stock_code} 的混合数据...")
        
        if use_tushare:
            try:
                # 从tushare获取实时数据
                print("  📡 正在从tushare获取实时数据...")
                df_tushare = self.pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
                
                if not df_tushare.empty:
                    df_tushare['trade_date'] = pd.to_datetime(df_tushare['trade_date'])
                    df_tushare = df_tushare.sort_values('trade_date').reset_index(drop=True)
                    
                    # 获取基本面数据
                    latest_date = df_tushare.iloc[0]['trade_date'].strftime('%Y%m%d')
                    daily_basic = self.pro.daily_basic(ts_code=stock_code, trade_date=latest_date,
                                                     fields='ts_code,pe,pb,total_mv,turnover_rate')
                    
                    # 添加基本面信息
                    if not daily_basic.empty:
                        basic_info = daily_basic.iloc[0]
                        df_tushare['pe_ratio'] = basic_info['pe']
                        df_tushare['pb_ratio'] = basic_info['pb'] 
                        df_tushare['market_cap'] = basic_info['total_mv']
                        df_tushare['turnover_rate'] = basic_info['turnover_rate']
                    
                    print(f"  ✅ tushare数据获取成功: {len(df_tushare)} 条记录")
                    return df_tushare, 'tushare'
                    
            except Exception as e:
                print(f"  ⚠️ tushare获取失败: {e}")
        
        # 备用方案：从qlib数据库获取
        try:
            print("  🗄️ 从qlib数据库获取备用数据...")
            conn = sqlite3.connect(self.qlib_db_path)
            
            query = """
            SELECT ts_code, trade_date, open, high, low, close, vol, amount, pct_chg
            FROM factor_data 
            WHERE ts_code = ? 
            ORDER BY trade_date DESC
            LIMIT 50
            """
            
            df_qlib = pd.read_sql_query(query, conn, params=[stock_code])
            conn.close()
            
            if not df_qlib.empty:
                df_qlib['trade_date'] = pd.to_datetime(df_qlib['trade_date'])
                print(f"  ✅ qlib数据获取成功: {len(df_qlib)} 条记录")
                return df_qlib, 'qlib'
                
        except Exception as e:
            print(f"  ❌ qlib数据获取失败: {e}")
        
        return pd.DataFrame(), 'none'
    
    def calculate_comprehensive_factors(self, df, data_source='tushare'):
        """
        计算综合因子（比之前更全面）
        """
        print(f"⚙️ 计算综合因子 (数据源: {data_source})...")
        
        if df.empty:
            return {}
        
        factors = {}
        n = len(df)
        
        # 1. 价格动量因子
        print("  📈 计算价格动量因子...")
        for period in [1, 3, 5, 10, 20]:
            if period < n:
                factors[f'momentum_{period}d'] = (df['close'] - df['close'].shift(period)) / df['close'].shift(period)
                factors[f'return_{period}d'] = df['close'].pct_change(period)
        
        # 2. 波动率因子
        print("  📊 计算波动率因子...")
        returns = df['close'].pct_change()
        for period in [5, 10, 20]:
            if period < n:
                factors[f'volatility_{period}d'] = returns.rolling(period).std()
                factors[f'vol_rank_{period}d'] = factors[f'volatility_{period}d'].rank(pct=True)
        
        # 3. 技术指标因子
        print("  🔧 计算技术指标因子...")
        
        # RSI
        for period in [14, 21]:
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            rs = gain / loss
            factors[f'rsi_{period}'] = 100 - (100 / (1 + rs))
        
        # 移动平均
        for period in [5, 10, 20, 60]:
            if period < n:
                ma = df['close'].rolling(period).mean()
                factors[f'ma_{period}'] = ma
                factors[f'ma_ratio_{period}'] = df['close'] / ma
                factors[f'ma_distance_{period}'] = (df['close'] - ma) / ma
        
        # 4. 成交量因子
        print("  💰 计算成交量因子...")
        for period in [5, 10, 20]:
            if period < n:
                vol_ma = df['vol'].rolling(period).mean()
                factors[f'volume_ma_{period}'] = vol_ma
                factors[f'volume_ratio_{period}'] = df['vol'] / vol_ma
        
        # 量价相关性
        for period in [10, 20]:
            if period < n:
                factors[f'volume_price_corr_{period}'] = returns.rolling(period).corr(df['vol'].pct_change())
        
        # 5. 价格位置因子
        print("  📍 计算价格位置因子...")
        for period in [10, 20, 60]:
            if period < n:
                high_max = df['high'].rolling(period).max()
                low_min = df['low'].rolling(period).min()
                factors[f'price_position_{period}'] = (df['close'] - low_min) / (high_max - low_min)
                factors[f'price_percentile_{period}'] = df['close'].rolling(period).rank(pct=True)
        
        # 6. 高级技术因子
        print("  🎯 计算高级技术因子...")
        
        # 布林带
        for period in [20]:
            sma = df['close'].rolling(period).mean()
            std = df['close'].rolling(period).std()
            factors[f'bb_upper_{period}'] = sma + 2 * std
            factors[f'bb_lower_{period}'] = sma - 2 * std
            factors[f'bb_width_{period}'] = (factors[f'bb_upper_{period}'] - factors[f'bb_lower_{period}']) / sma
            factors[f'bb_position_{period}'] = (df['close'] - factors[f'bb_lower_{period}']) / (factors[f'bb_upper_{period}'] - factors[f'bb_lower_{period}'])
        
        # ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift(1))
        low_close = np.abs(df['low'] - df['close'].shift(1))
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        factors['atr_14'] = true_range.rolling(14).mean()
        factors['atr_ratio'] = factors['atr_14'] / df['close']
        
        # 7. 如果有基本面数据，添加估值因子
        if data_source == 'tushare' and 'pe_ratio' in df.columns:
            print("  💼 添加基本面因子...")
            factors['pe_ratio'] = df['pe_ratio']
            factors['pb_ratio'] = df['pb_ratio'] 
            factors['market_cap_log'] = np.log(df['market_cap'].fillna(df['market_cap'].median()))
            if 'turnover_rate' in df.columns:
                factors['turnover_rate'] = df['turnover_rate']
        
        # 8. 计算未来收益率标签
        print("  🎯 计算预测目标...")
        for period in [1, 3, 5, 10, 20]:
            factors[f'future_return_{period}d'] = df['close'].shift(-period) / df['close'] - 1
        
        print(f"  ✅ 完成因子计算: {len([k for k in factors.keys() if not k.startswith('future_return')])} 个因子")
        return factors
    
    def analyze_factor_effectiveness_advanced(self, factors, target_period=5):
        """
        高级因子有效性分析
        """
        print(f"🔬 进行高级因子有效性分析 (预测{target_period}日收益)...")
        
        target_col = f'future_return_{target_period}d'
        if target_col not in factors:
            print("❌ 缺少预测目标")
            return {}
        
        future_returns = pd.Series(factors[target_col]).dropna()
        if len(future_returns) < 20:
            print("❌ 有效样本不足")
            return {}
        
        results = {}
        factor_names = [k for k in factors.keys() if not k.startswith('future_return')]
        
        print(f"  📊 分析 {len(factor_names)} 个因子的有效性...")
        
        for factor_name in factor_names:
            factor_values = pd.Series(factors[factor_name])
            
            # 对齐数据
            aligned_data = pd.DataFrame({
                'factor': factor_values,
                'return': future_returns
            }).dropna()
            
            if len(aligned_data) < 10:
                continue
            
            factor_vals = aligned_data['factor']
            return_vals = aligned_data['return']
            
            # 1. 相关性分析
            ic = factor_vals.corr(return_vals)
            rank_ic = factor_vals.rank().corr(return_vals.rank())
            
            # 2. 分组回测
            try:
                # 分为5组
                factor_vals_copy = factor_vals.copy()
                quantiles = pd.qcut(factor_vals_copy, 5, duplicates='drop')
                group_returns = return_vals.groupby(quantiles).agg(['mean', 'std', 'count'])
                
                if len(group_returns) >= 3:
                    # 计算多空收益
                    long_short_return = group_returns['mean'].iloc[-1] - group_returns['mean'].iloc[0]
                    
                    # 计算单调性
                    mean_returns = group_returns['mean'].values
                    monotonic_up = sum(mean_returns[i+1] >= mean_returns[i] for i in range(len(mean_returns)-1))
                    monotonic_down = sum(mean_returns[i+1] <= mean_returns[i] for i in range(len(mean_returns)-1))
                    monotonicity = max(monotonic_up, monotonic_down) / (len(mean_returns) - 1)
                    
                    # 计算信息比率
                    if group_returns['std'].iloc[-1] > 0 and group_returns['std'].iloc[0] > 0:
                        long_ir = group_returns['mean'].iloc[-1] / group_returns['std'].iloc[-1]
                        short_ir = group_returns['mean'].iloc[0] / group_returns['std'].iloc[0]
                        info_ratio = abs(long_ir) + abs(short_ir)
                    else:
                        info_ratio = 0
                else:
                    long_short_return = 0
                    monotonicity = 0
                    info_ratio = 0
                    
            except:
                long_short_return = 0
                monotonicity = 0
                info_ratio = 0
            
            # 综合评分
            ic_score = abs(ic) if not np.isnan(ic) else 0
            rank_ic_score = abs(rank_ic) if not np.isnan(rank_ic) else 0
            long_short_score = abs(long_short_return) * 100  # 转换为百分比
            
            final_score = (ic_score * 0.3 + 
                          rank_ic_score * 0.3 + 
                          monotonicity * 0.2 + 
                          long_short_score * 0.2)
            
            results[factor_name] = {
                'ic': ic,
                'rank_ic': rank_ic,
                'long_short_return': long_short_return,
                'monotonicity': monotonicity,
                'info_ratio': info_ratio,
                'sample_size': len(aligned_data),
                'final_score': final_score
            }
        
        print(f"  ✅ 完成 {len(results)} 个因子的有效性分析")
        return results
    
    def run_comprehensive_analysis(self, stock_codes, start_date='20250701', end_date='20250731'):
        """
        运行综合分析
        """
        print("🚀 开始综合股票因子分析")
        print("=" * 80)
        
        all_results = {}
        
        for i, stock_code in enumerate(stock_codes, 1):
            print(f"\n📊 [{i}/{len(stock_codes)}] 分析 {stock_code}")
            print("-" * 60)
            
            # 获取数据
            df, data_source = self.get_hybrid_stock_data(stock_code, start_date, end_date)
            
            if df.empty:
                print(f"❌ {stock_code} 数据获取失败")
                continue
            
            # 计算因子
            factors = self.calculate_comprehensive_factors(df, data_source)
            
            if not factors:
                print(f"❌ {stock_code} 因子计算失败")
                continue
            
            # 分析有效性
            effectiveness = self.analyze_factor_effectiveness_advanced(factors, target_period=5)
            
            if not effectiveness:
                print(f"❌ {stock_code} 因子分析失败")
                continue
            
            # 保存结果
            all_results[stock_code] = {
                'data_source': data_source,
                'data_records': len(df),
                'factor_count': len([k for k in factors.keys() if not k.startswith('future_return')]),
                'effectiveness': effectiveness
            }
            
            # 显示top因子
            sorted_factors = sorted(effectiveness.items(), key=lambda x: x[1]['final_score'], reverse=True)
            print(f"\\n🏆 {stock_code} Top 5 因子:")
            for j, (factor_name, metrics) in enumerate(sorted_factors[:5], 1):
                print(f"  {j}. {factor_name:<25} | 得分: {metrics['final_score']:.4f} | IC: {metrics['ic']:.4f}")
            
            # 避免API频率限制
            if data_source == 'tushare' and i < len(stock_codes):
                print("  ⏳ 等待1秒避免API限制...")
                time.sleep(1)
        
        # 汇总分析
        if all_results:
            self._generate_summary_report(all_results)
        
        return all_results
    
    def _generate_summary_report(self, all_results):
        """
        生成汇总报告
        """
        print("\\n" + "=" * 80)
        print("📋 综合分析汇总报告")
        print("=" * 80)
        
        # 统计信息
        total_stocks = len(all_results)
        tushare_count = sum(1 for r in all_results.values() if r['data_source'] == 'tushare')
        qlib_count = total_stocks - tushare_count
        
        print(f"📊 分析概况:")
        print(f"  总股票数: {total_stocks}")
        print(f"  tushare数据: {tushare_count} 只")
        print(f"  qlib数据: {qlib_count} 只")
        
        # 收集所有因子得分
        all_factor_scores = {}
        for stock_code, result in all_results.items():
            for factor_name, metrics in result['effectiveness'].items():
                if factor_name not in all_factor_scores:
                    all_factor_scores[factor_name] = []
                all_factor_scores[factor_name].append(metrics['final_score'])
        
        # 计算平均得分
        avg_scores = {factor: np.mean(scores) for factor, scores in all_factor_scores.items()}
        top_universal_factors = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:15]
        
        print(f"\\n🏆 跨股票通用优秀因子 (Top 15):")
        for i, (factor_name, avg_score) in enumerate(top_universal_factors, 1):
            print(f"  {i:2d}. {factor_name:<30} | 平均得分: {avg_score:.4f}")
        
        # 保存详细报告
        self._save_comprehensive_report(all_results, top_universal_factors)
    
    def _save_comprehensive_report(self, all_results, top_factors):
        """
        保存详细报告
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'tushare_enhanced_analysis_{timestamp}.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Tushare增强因子系统分析报告\\n\\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
            
            f.write("## 分析概况\\n\\n")
            f.write(f"- 分析股票数: {len(all_results)}\\n")
            f.write(f"- 数据源分布: tushare {sum(1 for r in all_results.values() if r['data_source'] == 'tushare')} | qlib {sum(1 for r in all_results.values() if r['data_source'] == 'qlib')}\\n\\n")
            
            f.write("## 各股票分析结果\\n\\n")
            for stock_code, result in all_results.items():
                f.write(f"### {stock_code}\\n")
                f.write(f"- 数据源: {result['data_source']}\\n")
                f.write(f"- 数据记录数: {result['data_records']}\\n")
                f.write(f"- 计算因子数: {result['factor_count']}\\n\\n")
            
            f.write("## 通用优秀因子排名\\n\\n")
            for i, (factor_name, avg_score) in enumerate(top_factors, 1):
                f.write(f"{i}. **{factor_name}** - 平均得分: {avg_score:.4f}\\n")
        
        print(f"\\n💾 详细报告已保存: {report_file}")

def main():
    """
    主程序
    """
    print("🌟 启动Tushare增强因子系统")
    
    # 初始化系统
    system = TushareEnhancedFactorSystem('b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065')
    
    # 测试股票列表
    test_stocks = ['000001.SZ', '000002.SZ', '000006.SZ', '600036.SH', '600000.SH']
    
    # 运行综合分析
    results = system.run_comprehensive_analysis(test_stocks)
    
    print("\\n🎊 Tushare增强因子系统分析完成！")

if __name__ == "__main__":
    main()