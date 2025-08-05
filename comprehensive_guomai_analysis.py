#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
果麦文化(301052)综合财务分析脚本
尝试多种数据源获取完整的财务和投资数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

def get_comprehensive_guomai_analysis():
    """获取果麦文化的综合分析数据"""
    stock_code = '301052'
    company_name = '果麦文化'
    
    print(f"🔍 {company_name}({stock_code}) 综合投资分析报告")
    print("="*80)
    
    analysis_results = {}
    
    # 1. 基本信息和估值数据
    print("\n📊 1. 公司基本信息和估值")
    print("-" * 60)
    try:
        # 基本信息
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        basic_info = {}
        if not stock_info.empty:
            for _, row in stock_info.iterrows():
                basic_info[row['item']] = row['value']
        
        # 实时行情
        current_data = ak.stock_zh_a_spot_em()
        guomai_current = current_data[current_data['代码'] == stock_code]
        
        if not guomai_current.empty:
            current_info = guomai_current.iloc[0]
            basic_info.update({
                '实时股价': current_info['最新价'],
                '今日涨跌幅': f"{current_info['涨跌幅']}%",
                '今日涨跌额': current_info['涨跌额'],
                '今日成交量': current_info['成交量'],
                '今日成交额': current_info['成交额'],
                '市盈率TTM': current_info.get('市盈率-TTM', 'N/A'),
                '市净率': current_info.get('市净率', 'N/A'),
                '总市值': current_info['总市值'],
                '流通市值': current_info['流通市值']
            })
        
        analysis_results['基本信息和估值'] = basic_info
        
        print("✅ 基本信息获取成功")
        print(f"公司名称: {basic_info.get('股票简称', 'N/A')}")
        print(f"行业分类: {basic_info.get('行业', 'N/A')}")
        print(f"上市时间: {basic_info.get('上市时间', 'N/A')}")
        print(f"实时股价: {basic_info.get('实时股价', 'N/A')}")
        print(f"总市值: {basic_info.get('总市值', 'N/A')}")
        print(f"市盈率TTM: {basic_info.get('市盈率TTM', 'N/A')}")
        print(f"市净率: {basic_info.get('市净率', 'N/A')}")
        
    except Exception as e:
        error_msg = f"基本信息获取失败: {str(e)}"
        print(f"❌ {error_msg}")
        analysis_results['基本信息和估值'] = error_msg

    # 2. 近3年股价表现分析
    print("\n📊 2. 近3年股价表现分析")
    print("-" * 60)
    try:
        # 获取3年历史数据
        start_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')
        
        hist_data = ak.stock_zh_a_hist(
            symbol=stock_code,
            period='daily',
            start_date=start_date,
            end_date=end_date,
            adjust='qfq'
        )
        
        if not hist_data.empty:
            # 计算关键统计数据
            hist_data['日期'] = pd.to_datetime(hist_data['日期'])
            hist_data = hist_data.sort_values('日期')
            
            # 年度表现
            yearly_performance = {}
            for year in [2022, 2023, 2024]:
                year_data = hist_data[hist_data['日期'].dt.year == year]
                if not year_data.empty:
                    start_price = year_data['收盘'].iloc[0]
                    end_price = year_data['收盘'].iloc[-1]
                    year_return = ((end_price - start_price) / start_price) * 100
                    yearly_performance[f'{year}年收益率'] = f"{year_return:.2f}%"
                    yearly_performance[f'{year}年最高价'] = year_data['最高'].max()
                    yearly_performance[f'{year}年最低价'] = year_data['最低'].min()
            
            # 波动率分析
            hist_data['日收益率'] = hist_data['收盘'].pct_change()
            volatility_annual = hist_data['日收益率'].std() * (252**0.5) * 100
            
            # 技术指标
            hist_data['MA5'] = hist_data['收盘'].rolling(5).mean()
            hist_data['MA20'] = hist_data['收盘'].rolling(20).mean()
            hist_data['MA60'] = hist_data['收盘'].rolling(60).mean()
            
            latest_data = hist_data.iloc[-1]
            
            price_analysis = {
                '数据期间': f"{hist_data['日期'].min().strftime('%Y-%m-%d')} 至 {hist_data['日期'].max().strftime('%Y-%m-%d')}",
                '总交易日数': len(hist_data),
                '期间最高价': hist_data['最高'].max(),
                '期间最低价': hist_data['最低'].min(),
                '当前价格': latest_data['收盘'],
                '年化波动率': f"{volatility_annual:.2f}%",
                'MA5': round(latest_data['MA5'], 2),
                'MA20': round(latest_data['MA20'], 2),
                'MA60': round(latest_data['MA60'], 2),
                **yearly_performance
            }
            
            analysis_results['股价表现分析'] = price_analysis
            
            print("✅ 股价分析完成")
            print(f"期间最高价: {price_analysis['期间最高价']}")
            print(f"期间最低价: {price_analysis['期间最低价']}")
            print(f"年化波动率: {price_analysis['年化波动率']}")
            for year in [2022, 2023, 2024]:
                if f'{year}年收益率' in price_analysis:
                    print(f"{year}年收益率: {price_analysis[f'{year}年收益率']}")
        
    except Exception as e:
        error_msg = f"股价分析失败: {str(e)}"
        print(f"❌ {error_msg}")
        analysis_results['股价表现分析'] = error_msg

    # 3. 财务指标趋势分析
    print("\n📊 3. 财务指标趋势分析")
    print("-" * 60)
    try:
        # 获取多个财务指标
        financial_indicators = {}
        
        # 营业收入
        try:
            revenue_data = ak.stock_financial_abstract(symbol=stock_code, indicator="营业总收入")
            if not revenue_data.empty:
                recent_revenue = {}
                for col in revenue_data.columns:
                    if col != '股票代码' and col != '指标' and col != '选项':
                        recent_revenue[col] = revenue_data[col].iloc[0]
                financial_indicators['营业收入'] = recent_revenue
        except:
            pass
            
        # 净利润
        try:
            profit_data = ak.stock_financial_abstract(symbol=stock_code, indicator="归母净利润")
            if not profit_data.empty:
                recent_profit = {}
                for col in profit_data.columns:
                    if col != '股票代码' and col != '指标' and col != '选项':
                        recent_profit[col] = profit_data[col].iloc[0]
                financial_indicators['净利润'] = recent_profit
        except:
            pass
        
        # ROE数据
        try:
            roe_data = ak.stock_financial_abstract(symbol=stock_code, indicator="净资产收益率")
            if not roe_data.empty:
                recent_roe = {}
                for col in roe_data.columns:
                    if col != '股票代码' and col != '指标' and col != '选项':
                        recent_roe[col] = roe_data[col].iloc[0]
                financial_indicators['净资产收益率ROE'] = recent_roe
        except:
            pass
        
        # 毛利率
        try:
            margin_data = ak.stock_financial_abstract(symbol=stock_code, indicator="销售毛利率")
            if not margin_data.empty:
                recent_margin = {}
                for col in margin_data.columns:
                    if col != '股票代码' and col != '指标' and col != '选项':
                        recent_margin[col] = margin_data[col].iloc[0]
                financial_indicators['销售毛利率'] = recent_margin
        except:
            pass
        
        analysis_results['财务指标趋势'] = financial_indicators
        
        print("✅ 财务指标分析完成")
        for indicator, data in financial_indicators.items():
            print(f"\n{indicator}:")
            # 显示最近4个报告期
            periods = sorted([k for k in data.keys() if k.isdigit()], reverse=True)[:4]
            for period in periods:
                value = data.get(period, 'N/A')
                print(f"  {period}: {value}")
                
    except Exception as e:
        error_msg = f"财务指标分析失败: {str(e)}"
        print(f"❌ {error_msg}")
        analysis_results['财务指标趋势'] = error_msg

    # 4. 行业对比分析
    print("\n📊 4. 行业对比分析")
    print("-" * 60)
    try:
        # 获取文化传媒行业数据
        industry_stocks = []
        
        # 查找同行业公司
        all_stocks = ak.stock_info_a_code_name()
        media_stocks = all_stocks[all_stocks['name'].str.contains('文化|传媒|出版|影视', na=False)]
        
        # 选择一些知名的文化传媒股票进行对比
        comparable_stocks = ['301052', '300251', '002739', '600373', '000156']  # 果麦、光线、万达、中文传媒、华数传媒
        
        industry_comparison = {}
        
        for code in comparable_stocks:
            try:
                stock_current = ak.stock_zh_a_spot_em()
                stock_info = stock_current[stock_current['代码'] == code]
                if not stock_info.empty:
                    stock_data = stock_info.iloc[0]
                    industry_comparison[stock_data['名称']] = {
                        '股票代码': code,
                        '最新价': stock_data['最新价'],
                        '涨跌幅': f"{stock_data['涨跌幅']}%",
                        '市盈率TTM': stock_data.get('市盈率-TTM', 'N/A'),
                        '市净率': stock_data.get('市净率', 'N/A'),
                        '总市值': stock_data['总市值']
                    }
            except:
                continue
        
        analysis_results['行业对比'] = industry_comparison
        
        print("✅ 行业对比分析完成")
        print("文化传媒行业主要公司对比:")
        for company, data in industry_comparison.items():
            print(f"\n{company}({data['股票代码']}):")
            print(f"  最新价: {data['最新价']}")
            print(f"  涨跌幅: {data['涨跌幅']}")
            print(f"  市盈率: {data['市盈率TTM']}")
            print(f"  总市值: {data['总市值']}")
        
    except Exception as e:
        error_msg = f"行业对比分析失败: {str(e)}"
        print(f"❌ {error_msg}")
        analysis_results['行业对比'] = error_msg

    # 5. 最新公告和新闻
    print("\n📊 5. 最新公告和新闻")
    print("-" * 60)
    try:
        # 尝试获取公告信息
        news_info = {}
        
        # 获取最新公告（尝试不同的API）
        try:
            announcements = ak.stock_notice_report(symbol=stock_code)
            if not announcements.empty:
                recent_announcements = announcements.head(5)
                announcement_list = []
                for _, row in recent_announcements.iterrows():
                    announcement_list.append({
                        '日期': str(row.get('公告日期', row.get('日期', 'N/A'))),
                        '标题': str(row.get('公告标题', row.get('标题', 'N/A'))),
                        '类型': str(row.get('公告类型', 'N/A'))
                    })
                news_info['最新公告'] = announcement_list
        except:
            news_info['最新公告'] = "公告数据获取失败"
        
        # 搜索相关新闻（简化版）
        news_info['数据说明'] = f"建议关注{company_name}的最新业务动态、财报发布、重大合作等公告信息"
        
        analysis_results['公告新闻'] = news_info
        
        if '最新公告' in news_info and isinstance(news_info['最新公告'], list):
            print("✅ 公告信息获取成功")
            print("最新公告:")
            for i, announcement in enumerate(news_info['最新公告'][:3]):
                print(f"  {i+1}. {announcement['日期']}: {announcement['标题']}")
        else:
            print("❌ 公告信息获取失败")
        
    except Exception as e:
        error_msg = f"新闻公告获取失败: {str(e)}"
        print(f"❌ {error_msg}")
        analysis_results['公告新闻'] = error_msg

    # 6. 投资建议总结
    print("\n📊 6. 投资分析总结")
    print("-" * 60)
    
    investment_summary = {
        '分析日期': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '股票代码': stock_code,
        '公司名称': company_name,
        '所属行业': '文化传媒',
        '分析维度': [
            '基本面分析：公司基本信息、估值水平',
            '技术面分析：股价走势、技术指标',
            '财务分析：营收、利润、ROE等关键指标',
            '行业对比：与同行业公司对比',
            '消息面：最新公告和新闻动态'
        ],
        '数据来源': 'AKShare - 开源财经数据接口库',
        '风险提示': '本分析仅供参考，投资有风险，决策需谨慎'
    }
    
    analysis_results['投资分析总结'] = investment_summary
    
    print("✅ 投资分析总结")
    print(f"分析日期: {investment_summary['分析日期']}")
    print(f"数据来源: {investment_summary['数据来源']}")
    print(f"风险提示: {investment_summary['风险提示']}")

    # 输出最终总结
    print("\n📋 分析报告总结")
    print("="*80)
    successful_sections = sum(1 for v in analysis_results.values() 
                            if not isinstance(v, str) or not '失败' in str(v))
    total_sections = len(analysis_results)
    
    print(f"总分析模块: {total_sections}")
    print(f"成功模块: {successful_sections}")
    print(f"成功率: {successful_sections/total_sections*100:.1f}%")
    
    # 保存完整分析结果
    try:
        output_file = f"果麦文化综合投资分析_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n✅ 完整分析报告已保存到: {output_file}")
        
        # 生成Excel格式报告
        excel_file = f"果麦文化投资分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # 基本信息
            if '基本信息和估值' in analysis_results and isinstance(analysis_results['基本信息和估值'], dict):
                basic_df = pd.DataFrame(list(analysis_results['基本信息和估值'].items()), 
                                       columns=['项目', '数值'])
                basic_df.to_excel(writer, sheet_name='基本信息', index=False)
            
            # 股价分析
            if '股价表现分析' in analysis_results and isinstance(analysis_results['股价表现分析'], dict):
                price_df = pd.DataFrame(list(analysis_results['股价表现分析'].items()), 
                                       columns=['指标', '数值'])
                price_df.to_excel(writer, sheet_name='股价分析', index=False)
            
            # 行业对比
            if '行业对比' in analysis_results and isinstance(analysis_results['行业对比'], dict):
                industry_df = pd.DataFrame(analysis_results['行业对比']).T
                industry_df.to_excel(writer, sheet_name='行业对比')
        
        print(f"✅ Excel格式报告已保存到: {excel_file}")
        
    except Exception as e:
        print(f"❌ 保存报告失败: {str(e)}")
    
    return analysis_results

if __name__ == "__main__":
    get_comprehensive_guomai_analysis()