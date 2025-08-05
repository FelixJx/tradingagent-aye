#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试qlib真实数据集成
"""

from real_data_factor_system import RealDataFactorSystem

def main():
    print("🚀 开始测试qlib真实数据集成...")
    
    # 初始化系统
    system = RealDataFactorSystem(
        tushare_token='b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065',
        data_dir='./factor_data'
    )
    
    # 测试从qlib数据库获取真实数据
    print("\n测试股票: 000001.SZ (平安银行)")
    results = system.run_full_analysis(
        stock_code='000001.SZ',
        start_date='2025-05-01',
        end_date='2025-07-15'
    )
    
    if results:
        print('\n🎉 使用qlib真实数据分析成功！')
        factor_data = results['factor_data']
        analysis = results['analysis_results']
        
        date_min = factor_data["trade_date"].min()
        date_max = factor_data["trade_date"].max()
        print('数据时间范围: {} 到 {}'.format(date_min, date_max))
        print('数据条数: {}'.format(len(factor_data)))
        
        factor_cols = [col for col in factor_data.columns if col not in ["trade_date", "close"]]
        print('计算的因子数量: {}'.format(len(factor_cols)))
        
        if analysis and 'selected_factors' in analysis:
            print('最佳因子数量: {}'.format(len(analysis["selected_factors"])))
            selected_preview = analysis["selected_factors"][:5]
            print('选择的最佳因子: {}'.format(selected_preview))
            
            # 显示统计信息
            if 'summary_stats' in analysis:
                stats = analysis['summary_stats']
                print('\n📊 分析统计:')
                print('  - 总因子数: {}'.format(stats["total_factors"]))
                print('  - 有效样本: {}'.format(stats["valid_samples"]))
                print('  - 目标收益率均值: {:.4f}'.format(stats["target_mean"]))
                print('  - 目标收益率标准差: {:.4f}'.format(stats["target_std"]))
        
        # 测试其他股票
        print("\n\n测试其他股票...")
        for stock_code in ['000002.SZ', '000006.SZ']:
            print("\n测试股票: {}".format(stock_code))
            test_results = system.run_full_analysis(
                stock_code=stock_code,
                start_date='2025-06-01', 
                end_date='2025-07-10'
            )
            
            if test_results:
                test_data = test_results['factor_data']
                print('✅ {}: {} 条数据记录'.format(stock_code, len(test_data)))
            else:
                print('❌ {}: 数据获取失败'.format(stock_code))
    
    else:
        print('❌ 分析失败')
    
    print("\n🎉 qlib真实数据集成测试完成！")

if __name__ == "__main__":
    main()