#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
果麦文化详细财务数据获取脚本
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def get_guomai_comprehensive_data():
    """获取果麦文化的综合财务数据"""
    stock_code = '301052'
    company_name = '果麦文化'
    
    print(f"🔍 开始获取{company_name}({stock_code})详细财务数据")
    print("="*60)
    
    results = {}
    
    # 1. 基本信息
    print("\n📊 1. 基本信息")
    print("-" * 40)
    try:
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        if not stock_info.empty:
            print("✅ 基本信息获取成功")
            basic_info = {}
            for _, row in stock_info.iterrows():
                basic_info[row['item']] = row['value']
                print(f"{row['item']}: {row['value']}")
            results['基本信息'] = basic_info
        else:
            print("❌ 基本信息为空")
            results['基本信息'] = "数据为空"
    except Exception as e:
        error_msg = f"基本信息获取失败: {str(e)}"
        print(f"❌ {error_msg}")
        results['基本信息'] = error_msg
    
    # 2. 历史股价数据
    print("\n📊 2. 历史股价数据")
    print("-" * 40)
    try:
        hist_data = ak.stock_zh_a_hist(
            symbol=stock_code,
            period='daily',
            start_date='20220101',
            end_date='20250726',
            adjust='qfq'
        )
        if not hist_data.empty:
            print(f"✅ 历史数据获取成功，共{len(hist_data)}条记录")
            
            # 最新数据
            latest = hist_data.iloc[-1]
            print(f"最新交易日: {latest['日期']}")
            print(f"收盘价: {latest['收盘']}")
            print(f"涨跌幅: {latest['涨跌幅']}%")
            print(f"成交量: {latest['成交量']:,}")
            print(f"成交额: {latest['成交额']:,}")
            
            # 统计信息
            print(f"最高价: {hist_data['最高'].max()}")
            print(f"最低价: {hist_data['最低'].min()}")
            print(f"平均成交量: {hist_data['成交量'].mean():,.0f}")
            
            results['历史股价'] = {
                '数据条数': len(hist_data),
                '最新价格': latest['收盘'],
                '最新日期': str(latest['日期']),
                '涨跌幅': latest['涨跌幅'],
                '成交量': latest['成交量'],
                '成交额': latest['成交额'],
                '期间最高': hist_data['最高'].max(),
                '期间最低': hist_data['最低'].min()
            }
        else:
            print("❌ 历史数据为空")
            results['历史股价'] = "数据为空"
    except Exception as e:
        error_msg = f"历史数据获取失败: {str(e)}"
        print(f"❌ {error_msg}")
        results['历史股价'] = error_msg

    # 3. 财务指标
    print("\n📊 3. 财务指标数据")
    print("-" * 40)
    try:
        # 尝试获取财务指标
        indicators = ak.stock_financial_abstract(symbol=stock_code)
        if not indicators.empty:
            print(f"✅ 财务指标获取成功，共{len(indicators)}条记录")
            print("最新财务指标:")
            
            indicator_data = {}
            for col in indicators.columns:
                if col != '股票代码':
                    value = indicators[col].iloc[0] if len(indicators) > 0 else 'N/A'
                    indicator_data[col] = value
                    print(f"  {col}: {value}")
            
            results['财务指标'] = indicator_data
        else:
            print("❌ 财务指标数据为空")
            results['财务指标'] = "数据为空"
    except Exception as e:
        error_msg = f"财务指标获取失败: {str(e)}"
        print(f"❌ {error_msg}")
        results['财务指标'] = error_msg

    # 4. 利润表数据
    print("\n📊 4. 利润表数据")
    print("-" * 40)
    try:
        profit_data = ak.stock_profit_sheet_by_report_em(symbol=stock_code)
        if not profit_data.empty:
            print(f"✅ 利润表数据获取成功，共{len(profit_data)}条记录")
            
            # 显示最新3个报告期
            recent_profits = profit_data.head(3)
            profit_summary = []
            
            for i, (_, row) in enumerate(recent_profits.iterrows()):
                period_data = {
                    '报告期': row.get('报告期', 'N/A'),
                    '营业总收入': row.get('营业总收入', 'N/A'),
                    '净利润': row.get('净利润', 'N/A'),
                    '毛利润': row.get('毛利润', 'N/A'),
                    '营业利润': row.get('营业利润', 'N/A')
                }
                profit_summary.append(period_data)
                
                print(f"报告期 {i+1}: {period_data['报告期']}")
                print(f"  营业总收入: {period_data['营业总收入']}")
                print(f"  净利润: {period_data['净利润']}")
                print(f"  毛利润: {period_data['毛利润']}")
                print(f"  营业利润: {period_data['营业利润']}")
                print()
            
            results['利润表'] = profit_summary
        else:
            print("❌ 利润表数据为空")
            results['利润表'] = "数据为空"
    except Exception as e:
        error_msg = f"利润表获取失败: {str(e)}"
        print(f"❌ {error_msg}")
        results['利润表'] = error_msg

    # 5. 资产负债表
    print("\n📊 5. 资产负债表数据")
    print("-" * 40)
    try:
        balance_data = ak.stock_balance_sheet_by_report_em(symbol=stock_code)
        if not balance_data.empty:
            print(f"✅ 资产负债表数据获取成功，共{len(balance_data)}条记录")
            
            # 最新资产负债数据
            latest_balance = balance_data.iloc[0]
            balance_info = {
                '报告期': latest_balance.get('报告期', 'N/A'),
                '总资产': latest_balance.get('总资产', 'N/A'),
                '总负债': latest_balance.get('总负债', 'N/A'),
                '股东权益合计': latest_balance.get('股东权益合计', 'N/A'),
                '流动资产合计': latest_balance.get('流动资产合计', 'N/A'),
                '流动负债合计': latest_balance.get('流动负债合计', 'N/A')
            }
            
            for key, value in balance_info.items():
                print(f"{key}: {value}")
            
            results['资产负债表'] = balance_info
        else:
            print("❌ 资产负债表数据为空")
            results['资产负债表'] = "数据为空"
    except Exception as e:
        error_msg = f"资产负债表获取失败: {str(e)}"
        print(f"❌ {error_msg}")
        results['资产负债表'] = error_msg

    # 6. 现金流量表
    print("\n📊 6. 现金流量表数据")
    print("-" * 40)
    try:
        cashflow_data = ak.stock_cash_flow_sheet_by_report_em(symbol=stock_code)
        if not cashflow_data.empty:
            print(f"✅ 现金流量表数据获取成功，共{len(cashflow_data)}条记录")
            
            # 最新现金流数据
            latest_cashflow = cashflow_data.iloc[0]
            cashflow_info = {
                '报告期': latest_cashflow.get('报告期', 'N/A'),
                '经营活动产生的现金流量净额': latest_cashflow.get('经营活动产生的现金流量净额', 'N/A'),
                '投资活动产生的现金流量净额': latest_cashflow.get('投资活动产生的现金流量净额', 'N/A'),
                '筹资活动产生的现金流量净额': latest_cashflow.get('筹资活动产生的现金流量净额', 'N/A'),
                '现金及现金等价物净增加额': latest_cashflow.get('现金及现金等价物净增加额', 'N/A')
            }
            
            for key, value in cashflow_info.items():
                print(f"{key}: {value}")
            
            results['现金流量表'] = cashflow_info
        else:
            print("❌ 现金流量表数据为空")
            results['现金流量表'] = "数据为空"
    except Exception as e:
        error_msg = f"现金流量表获取失败: {str(e)}"
        print(f"❌ {error_msg}")
        results['现金流量表'] = error_msg

    # 7. 技术指标
    print("\n📊 7. 技术指标分析")
    print("-" * 40)
    try:
        # 使用历史数据计算技术指标
        if 'hist_data' in locals() and not hist_data.empty:
            # 计算移动平均线
            hist_data_sorted = hist_data.sort_values('日期')
            hist_data_sorted['MA5'] = hist_data_sorted['收盘'].rolling(window=5).mean()
            hist_data_sorted['MA10'] = hist_data_sorted['收盘'].rolling(window=10).mean()
            hist_data_sorted['MA20'] = hist_data_sorted['收盘'].rolling(window=20).mean()
            
            latest_tech = hist_data_sorted.iloc[-1]
            
            technical_data = {
                '最新价': latest_tech['收盘'],
                'MA5': latest_tech['MA5'],
                'MA10': latest_tech['MA10'],
                'MA20': latest_tech['MA20'],
                '成交量': latest_tech['成交量'],
                '换手率': latest_tech.get('换手率', 'N/A')
            }
            
            for key, value in technical_data.items():
                print(f"{key}: {value}")
            
            results['技术指标'] = technical_data
        else:
            print("❌ 无法计算技术指标，缺少历史数据")
            results['技术指标'] = "缺少历史数据"
    except Exception as e:
        error_msg = f"技术指标计算失败: {str(e)}"
        print(f"❌ {error_msg}")
        results['技术指标'] = error_msg

    # 输出总结
    print("\n📋 数据采集总结")
    print("="*60)
    successful_items = sum(1 for v in results.values() if not isinstance(v, str) or not v.startswith('数据为空') and not '失败' in str(v))
    total_items = len(results)
    
    print(f"总采集项目: {total_items}")
    print(f"成功项目: {successful_items}")
    print(f"失败项目: {total_items - successful_items}")
    print(f"成功率: {successful_items/total_items*100:.1f}%")
    
    # 保存结果
    try:
        import json
        output_file = f"果麦文化财务数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n✅ 数据已保存到: {output_file}")
    except Exception as e:
        print(f"❌ 保存文件失败: {str(e)}")
    
    return results

if __name__ == "__main__":
    get_guomai_comprehensive_data()