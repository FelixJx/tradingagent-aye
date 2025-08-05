# -*- coding: utf-8 -*-
"""
A股数据获取工具模块
支持通过Tushare和AKShare获取A股市场数据
"""

import os
import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Annotated
import warnings
warnings.filterwarnings('ignore')

try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    print("Tushare not installed. Only AKShare will be available.")

# 初始化Tushare（如果可用）
if TUSHARE_AVAILABLE:
    tushare_token = os.getenv('TUSHARE_TOKEN')
    if tushare_token:
        ts.set_token(tushare_token)
    else:
        print("Warning: TUSHARE_TOKEN not found in environment variables")

def get_ashare_stock_list() -> pd.DataFrame:
    """
    获取A股所有股票列表
    
    Returns:
        pd.DataFrame: 包含股票代码、名称、市场等信息的DataFrame
    """
    try:
        # 使用AKShare获取股票列表
        stock_info = ak.stock_info_a_code_name()
        return stock_info
    except Exception as e:
        print(f"获取A股股票列表失败: {e}")
        return pd.DataFrame()

def get_ashare_stock_data(
    stock_code: Annotated[str, "A股股票代码，如'000001'或'600036'"],
    start_date: Annotated[str, "开始日期，格式：YYYY-MM-DD"],
    end_date: Annotated[str, "结束日期，格式：YYYY-MM-DD"],
    period: Annotated[str, "数据周期：daily/weekly/monthly"] = "daily"
) -> str:
    """
    获取A股股票历史价格数据
    
    Args:
        stock_code: A股股票代码
        start_date: 开始日期
        end_date: 结束日期
        period: 数据周期
        
    Returns:
        str: 格式化的股票价格数据报告
    """
    try:
        # 使用AKShare获取股票历史数据
        stock_data = ak.stock_zh_a_hist(
            symbol=stock_code,
            period=period,
            start_date=start_date.replace('-', ''),
            end_date=end_date.replace('-', ''),
            adjust="qfq"  # 前复权
        )
        
        if stock_data.empty:
            return f"未找到股票 {stock_code} 在 {start_date} 到 {end_date} 期间的数据"
        
        # 格式化数据
        latest_data = stock_data.tail(10)  # 最近10个交易日
        
        report = f"## {stock_code} 股票价格数据 ({start_date} 到 {end_date})\n\n"
        report += "### 最近10个交易日数据:\n"
        report += latest_data.to_string(index=False)
        report += "\n\n### 统计信息:\n"
        report += f"- 期间最高价: {stock_data['最高'].max():.2f}\n"
        report += f"- 期间最低价: {stock_data['最低'].min():.2f}\n"
        report += f"- 期间平均价: {stock_data['收盘'].mean():.2f}\n"
        report += f"- 期间总成交量: {stock_data['成交量'].sum():,.0f}\n"
        report += f"- 期间总成交额: {stock_data['成交额'].sum():,.0f}\n"
        
        return report
        
    except Exception as e:
        return f"获取股票 {stock_code} 数据失败: {str(e)}"

def get_ashare_financial_data(
    stock_code: Annotated[str, "A股股票代码"],
    report_type: Annotated[str, "报告类型：balance_sheet/income/cashflow"] = "income"
) -> str:
    """
    获取A股上市公司财务数据
    
    Args:
        stock_code: A股股票代码
        report_type: 财务报告类型
        
    Returns:
        str: 格式化的财务数据报告
    """
    try:
        if report_type == "balance_sheet":
            # 资产负债表
            data = ak.stock_balance_sheet_by_report_em(symbol=stock_code)
            title = "资产负债表"
        elif report_type == "income":
            # 利润表
            data = ak.stock_profit_sheet_by_report_em(symbol=stock_code)
            title = "利润表"
        elif report_type == "cashflow":
            # 现金流量表
            data = ak.stock_cash_flow_sheet_by_report_em(symbol=stock_code)
            title = "现金流量表"
        else:
            return f"不支持的报告类型: {report_type}"
        
        if data.empty:
            return f"未找到股票 {stock_code} 的{title}数据"
        
        # 获取最新的财务数据
        latest_data = data.head(1)
        
        report = f"## {stock_code} {title}数据\n\n"
        report += "### 最新财务数据:\n"
        report += latest_data.to_string(index=False)
        
        return report
        
    except Exception as e:
        return f"获取股票 {stock_code} 财务数据失败: {str(e)}"

def get_ashare_technical_indicators(
    stock_code: Annotated[str, "A股股票代码"],
    curr_date: Annotated[str, "当前日期，格式：YYYY-MM-DD"],
    lookback_days: Annotated[int, "回看天数"] = 30
) -> str:
    """
    获取A股股票技术指标
    
    Args:
        stock_code: A股股票代码
        curr_date: 当前日期
        lookback_days: 回看天数
        
    Returns:
        str: 格式化的技术指标报告
    """
    try:
        # 计算开始日期
        end_date = datetime.strptime(curr_date, '%Y-%m-%d')
        start_date = end_date - timedelta(days=lookback_days + 50)  # 多取一些数据用于计算指标
        
        # 获取股票数据
        stock_data = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date.strftime('%Y%m%d'),
            end_date=end_date.strftime('%Y%m%d'),
            adjust="qfq"
        )
        
        if stock_data.empty:
            return f"未找到股票 {stock_code} 的数据"
        
        # 计算技术指标
        stock_data = stock_data.sort_values('日期')
        
        # 移动平均线
        stock_data['MA5'] = stock_data['收盘'].rolling(window=5).mean()
        stock_data['MA10'] = stock_data['收盘'].rolling(window=10).mean()
        stock_data['MA20'] = stock_data['收盘'].rolling(window=20).mean()
        
        # RSI
        def calculate_rsi(prices, window=14):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        stock_data['RSI'] = calculate_rsi(stock_data['收盘'])
        
        # 获取最新数据
        latest = stock_data.iloc[-1]
        
        report = f"## {stock_code} 技术指标分析 (截至 {curr_date})\n\n"
        report += "### 价格信息:\n"
        report += f"- 最新收盘价: {latest['收盘']:.2f}\n"
        report += f"- 最新成交量: {latest['成交量']:,.0f}\n"
        report += f"- 涨跌幅: {latest['涨跌幅']:.2f}%\n"
        
        report += "\n### 移动平均线:\n"
        report += f"- MA5: {latest['MA5']:.2f}\n"
        report += f"- MA10: {latest['MA10']:.2f}\n"
        report += f"- MA20: {latest['MA20']:.2f}\n"
        
        report += "\n### 技术指标:\n"
        report += f"- RSI(14): {latest['RSI']:.2f}\n"
        
        # 简单的技术分析
        report += "\n### 技术分析建议:\n"
        if latest['收盘'] > latest['MA5'] > latest['MA10'] > latest['MA20']:
            report += "- 均线排列：多头排列，趋势向上\n"
        elif latest['收盘'] < latest['MA5'] < latest['MA10'] < latest['MA20']:
            report += "- 均线排列：空头排列，趋势向下\n"
        else:
            report += "- 均线排列：震荡整理\n"
        
        if latest['RSI'] > 70:
            report += "- RSI指标：超买区域，注意回调风险\n"
        elif latest['RSI'] < 30:
            report += "- RSI指标：超卖区域，可能存在反弹机会\n"
        else:
            report += "- RSI指标：正常区域\n"
        
        return report
        
    except Exception as e:
        return f"获取股票 {stock_code} 技术指标失败: {str(e)}"

def get_ashare_market_sentiment(
    curr_date: Annotated[str, "当前日期，格式：YYYY-MM-DD"]
) -> str:
    """
    获取A股市场整体情绪数据
    
    Args:
        curr_date: 当前日期
        
    Returns:
        str: 格式化的市场情绪报告
    """
    try:
        # 获取市场概况
        market_data = ak.stock_zh_a_spot_em()
        
        # 计算涨跌统计
        total_stocks = len(market_data)
        rising_stocks = len(market_data[market_data['涨跌幅'] > 0])
        falling_stocks = len(market_data[market_data['涨跌幅'] < 0])
        flat_stocks = total_stocks - rising_stocks - falling_stocks
        
        # 获取主要指数
        try:
            sh_index = ak.stock_zh_index_spot_em(symbol="000001")  # 上证指数
            sz_index = ak.stock_zh_index_spot_em(symbol="399001")  # 深证成指
            cy_index = ak.stock_zh_index_spot_em(symbol="399006")  # 创业板指
        except:
            sh_index = sz_index = cy_index = None
        
        report = f"## A股市场情绪分析 (截至 {curr_date})\n\n"
        
        report += "### 市场涨跌统计:\n"
        report += f"- 上涨股票数: {rising_stocks} ({rising_stocks/total_stocks*100:.1f}%)\n"
        report += f"- 下跌股票数: {falling_stocks} ({falling_stocks/total_stocks*100:.1f}%)\n"
        report += f"- 平盘股票数: {flat_stocks} ({flat_stocks/total_stocks*100:.1f}%)\n"
        report += f"- 总股票数: {total_stocks}\n"
        
        if sh_index is not None:
            report += "\n### 主要指数表现:\n"
            report += f"- 上证指数: {sh_index['最新价'].iloc[0]:.2f} ({sh_index['涨跌幅'].iloc[0]:.2f}%)\n"
            if sz_index is not None:
                report += f"- 深证成指: {sz_index['最新价'].iloc[0]:.2f} ({sz_index['涨跌幅'].iloc[0]:.2f}%)\n"
            if cy_index is not None:
                report += f"- 创业板指: {cy_index['最新价'].iloc[0]:.2f} ({cy_index['涨跌幅'].iloc[0]:.2f}%)\n"
        
        # 市场情绪判断
        report += "\n### 市场情绪判断:\n"
        if rising_stocks / total_stocks > 0.6:
            report += "- 市场情绪：乐观，多数股票上涨\n"
        elif falling_stocks / total_stocks > 0.6:
            report += "- 市场情绪：悲观，多数股票下跌\n"
        else:
            report += "- 市场情绪：中性，涨跌相对均衡\n"
        
        return report
        
    except Exception as e:
        return f"获取市场情绪数据失败: {str(e)}"

def get_ashare_industry_analysis(
    stock_code: Annotated[str, "A股股票代码"]
) -> str:
    """
    获取A股股票所属行业分析
    
    Args:
        stock_code: A股股票代码
        
    Returns:
        str: 格式化的行业分析报告
    """
    try:
        # 获取股票基本信息
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        
        if stock_info.empty:
            return f"未找到股票 {stock_code} 的基本信息"
        
        # 提取行业信息
        industry_info = stock_info[stock_info['item'].str.contains('行业', na=False)]
        
        report = f"## {stock_code} 行业分析\n\n"
        
        if not industry_info.empty:
            report += "### 行业归属:\n"
            for _, row in industry_info.iterrows():
                report += f"- {row['item']}: {row['value']}\n"
        
        # 获取同行业股票表现（简化版）
        try:
            # 这里可以扩展为更详细的行业分析
            report += "\n### 行业分析说明:\n"
            report += "- 建议关注同行业其他公司的表现进行对比分析\n"
            report += "- 关注行业政策变化和发展趋势\n"
            report += "- 分析公司在行业中的竞争地位\n"
        except:
            pass
        
        return report
        
    except Exception as e:
        return f"获取股票 {stock_code} 行业分析失败: {str(e)}"

def search_ashare_stocks(
    keyword: Annotated[str, "搜索关键词，可以是公司名称或概念"],
    limit: Annotated[int, "返回结果数量限制"] = 20
) -> str:
    """
    搜索A股股票
    
    Args:
        keyword: 搜索关键词
        limit: 返回结果数量限制
        
    Returns:
        str: 格式化的搜索结果
    """
    try:
        # 获取所有股票列表
        stock_list = get_ashare_stock_list()
        
        if stock_list.empty:
            return "无法获取股票列表"
        
        # 搜索匹配的股票
        matched_stocks = stock_list[
            stock_list['name'].str.contains(keyword, na=False) |
            stock_list['code'].str.contains(keyword, na=False)
        ].head(limit)
        
        if matched_stocks.empty:
            return f"未找到包含关键词 '{keyword}' 的股票"
        
        report = f"## 搜索结果：'{keyword}'\n\n"
        report += "### 匹配的股票:\n"
        
        for _, stock in matched_stocks.iterrows():
            report += f"- {stock['code']}: {stock['name']}\n"
        
        return report
        
    except Exception as e:
        return f"搜索股票失败: {str(e)}"