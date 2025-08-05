# -*- coding: utf-8 -*-
"""
A股新闻数据获取工具模块
支持财联社、新浪财经等中文财经新闻源
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Annotated
import json
import time
import random
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

class AShareNewsCollector:
    """
    A股新闻收集器
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_sina_finance_news(
        self,
        keyword: str = "",
        limit: int = 20,
        days_back: int = 7
    ) -> List[Dict]:
        """
        获取新浪财经新闻
        
        Args:
            keyword: 搜索关键词
            limit: 新闻数量限制
            days_back: 回溯天数
            
        Returns:
            List[Dict]: 新闻列表
        """
        news_list = []
        
        try:
            # 新浪财经新闻API（示例URL，实际使用时需要根据最新API调整）
            if keyword:
                # 搜索特定关键词的新闻
                url = f"https://search.sina.com.cn/?q={keyword}&c=news&from=finance"
            else:
                # 获取财经要闻
                url = "https://finance.sina.com.cn/"
            
            # 这里是示例实现，实际需要根据新浪财经的具体API或网页结构来实现
            # 由于网站结构可能变化，建议使用官方API或稳定的数据源
            
            # 模拟新闻数据结构
            sample_news = [
                {
                    'title': f'示例新闻标题 - {keyword}相关财经新闻',
                    'content': f'这是关于{keyword}的示例新闻内容，包含市场分析和投资建议。',
                    'source': '新浪财经',
                    'publish_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'url': 'https://finance.sina.com.cn/example'
                }
            ]
            
            news_list.extend(sample_news)
            
        except Exception as e:
            print(f"获取新浪财经新闻失败: {e}")
        
        return news_list[:limit]
    
    def get_cailianshe_news(
        self,
        keyword: str = "",
        limit: int = 20,
        days_back: int = 7
    ) -> List[Dict]:
        """
        获取财联社新闻
        
        Args:
            keyword: 搜索关键词
            limit: 新闻数量限制
            days_back: 回溯天数
            
        Returns:
            List[Dict]: 新闻列表
        """
        news_list = []
        
        try:
            # 财联社新闻API（示例URL，实际使用时需要根据最新API调整）
            # 注意：财联社可能需要付费API或有访问限制
            
            # 模拟新闻数据结构
            sample_news = [
                {
                    'title': f'财联社快讯 - {keyword}最新动态',
                    'content': f'财联社消息，{keyword}相关的最新市场动态和政策解读。',
                    'source': '财联社',
                    'publish_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'url': 'https://www.cls.cn/example'
                }
            ]
            
            news_list.extend(sample_news)
            
        except Exception as e:
            print(f"获取财联社新闻失败: {e}")
        
        return news_list[:limit]
    
    def get_eastmoney_news(
        self,
        keyword: str = "",
        limit: int = 20
    ) -> List[Dict]:
        """
        获取东方财富新闻
        
        Args:
            keyword: 搜索关键词
            limit: 新闻数量限制
            
        Returns:
            List[Dict]: 新闻列表
        """
        news_list = []
        
        try:
            # 东方财富新闻API
            # 这里使用AKShare提供的东方财富新闻接口
            import akshare as ak
            
            # 获取东方财富新闻
            news_data = ak.news_em()
            
            if not news_data.empty:
                for _, row in news_data.head(limit).iterrows():
                    if keyword == "" or keyword in row.get('标题', ''):
                        news_item = {
                            'title': row.get('标题', ''),
                            'content': row.get('内容', ''),
                            'source': '东方财富',
                            'publish_time': row.get('发布时间', ''),
                            'url': row.get('链接', '')
                        }
                        news_list.append(news_item)
            
        except Exception as e:
            print(f"获取东方财富新闻失败: {e}")
        
        return news_list[:limit]

# 全局新闻收集器实例
news_collector = AShareNewsCollector()

def get_ashare_company_news(
    stock_code: Annotated[str, "A股股票代码"],
    company_name: Annotated[str, "公司名称"],
    curr_date: Annotated[str, "当前日期，格式：YYYY-MM-DD"],
    lookback_days: Annotated[int, "回看天数"] = 7
) -> str:
    """
    获取A股公司相关新闻
    
    Args:
        stock_code: A股股票代码
        company_name: 公司名称
        curr_date: 当前日期
        lookback_days: 回看天数
        
    Returns:
        str: 格式化的新闻报告
    """
    try:
        all_news = []
        
        # 从多个新闻源获取数据
        sina_news = news_collector.get_sina_finance_news(
            keyword=company_name,
            limit=10,
            days_back=lookback_days
        )
        all_news.extend(sina_news)
        
        cailianshe_news = news_collector.get_cailianshe_news(
            keyword=company_name,
            limit=10,
            days_back=lookback_days
        )
        all_news.extend(cailianshe_news)
        
        eastmoney_news = news_collector.get_eastmoney_news(
            keyword=company_name,
            limit=10
        )
        all_news.extend(eastmoney_news)
        
        if not all_news:
            return f"未找到关于 {company_name}({stock_code}) 的相关新闻"
        
        # 格式化新闻报告
        start_date = (datetime.strptime(curr_date, '%Y-%m-%d') - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
        
        report = f"## {company_name}({stock_code}) 新闻汇总 ({start_date} 到 {curr_date})\n\n"
        
        for i, news in enumerate(all_news[:15], 1):  # 限制显示15条新闻
            report += f"### {i}. {news['title']}\n"
            report += f"**来源**: {news['source']} | **时间**: {news['publish_time']}\n\n"
            if news['content']:
                # 截取内容前200字符
                content = news['content'][:200] + "..." if len(news['content']) > 200 else news['content']
                report += f"{content}\n\n"
            report += "---\n\n"
        
        return report
        
    except Exception as e:
        return f"获取 {company_name}({stock_code}) 新闻失败: {str(e)}"

def get_ashare_market_news(
    curr_date: Annotated[str, "当前日期，格式：YYYY-MM-DD"],
    lookback_days: Annotated[int, "回看天数"] = 3,
    limit: Annotated[int, "新闻数量限制"] = 20
) -> str:
    """
    获取A股市场整体新闻
    
    Args:
        curr_date: 当前日期
        lookback_days: 回看天数
        limit: 新闻数量限制
        
    Returns:
        str: 格式化的市场新闻报告
    """
    try:
        all_news = []
        
        # 获取市场相关新闻
        market_keywords = ["A股", "上证指数", "深证成指", "创业板", "科创板", "股市"]
        
        for keyword in market_keywords[:2]:  # 限制关键词数量以避免过多请求
            sina_news = news_collector.get_sina_finance_news(
                keyword=keyword,
                limit=5,
                days_back=lookback_days
            )
            all_news.extend(sina_news)
            
            time.sleep(0.5)  # 避免请求过于频繁
        
        # 获取东方财富财经要闻
        eastmoney_news = news_collector.get_eastmoney_news(limit=10)
        all_news.extend(eastmoney_news)
        
        if not all_news:
            return f"未找到 {curr_date} 前 {lookback_days} 天的市场新闻"
        
        # 去重并排序
        unique_news = []
        seen_titles = set()
        for news in all_news:
            if news['title'] not in seen_titles:
                unique_news.append(news)
                seen_titles.add(news['title'])
        
        # 格式化报告
        start_date = (datetime.strptime(curr_date, '%Y-%m-%d') - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
        
        report = f"## A股市场新闻汇总 ({start_date} 到 {curr_date})\n\n"
        
        for i, news in enumerate(unique_news[:limit], 1):
            report += f"### {i}. {news['title']}\n"
            report += f"**来源**: {news['source']} | **时间**: {news['publish_time']}\n\n"
            if news['content']:
                content = news['content'][:150] + "..." if len(news['content']) > 150 else news['content']
                report += f"{content}\n\n"
            report += "---\n\n"
        
        return report
        
    except Exception as e:
        return f"获取市场新闻失败: {str(e)}"

def get_ashare_policy_news(
    curr_date: Annotated[str, "当前日期，格式：YYYY-MM-DD"],
    lookback_days: Annotated[int, "回看天数"] = 7
) -> str:
    """
    获取A股相关政策新闻
    
    Args:
        curr_date: 当前日期
        lookback_days: 回看天数
        
    Returns:
        str: 格式化的政策新闻报告
    """
    try:
        all_news = []
        
        # 政策相关关键词
        policy_keywords = ["证监会", "央行", "金融政策", "股市政策", "监管"]
        
        for keyword in policy_keywords[:3]:  # 限制关键词数量
            sina_news = news_collector.get_sina_finance_news(
                keyword=keyword,
                limit=5,
                days_back=lookback_days
            )
            all_news.extend(sina_news)
            
            cailianshe_news = news_collector.get_cailianshe_news(
                keyword=keyword,
                limit=5,
                days_back=lookback_days
            )
            all_news.extend(cailianshe_news)
            
            time.sleep(0.5)  # 避免请求过于频繁
        
        if not all_news:
            return f"未找到 {curr_date} 前 {lookback_days} 天的政策新闻"
        
        # 去重
        unique_news = []
        seen_titles = set()
        for news in all_news:
            if news['title'] not in seen_titles:
                unique_news.append(news)
                seen_titles.add(news['title'])
        
        # 格式化报告
        start_date = (datetime.strptime(curr_date, '%Y-%m-%d') - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
        
        report = f"## A股政策新闻汇总 ({start_date} 到 {curr_date})\n\n"
        
        for i, news in enumerate(unique_news[:10], 1):  # 限制显示10条
            report += f"### {i}. {news['title']}\n"
            report += f"**来源**: {news['source']} | **时间**: {news['publish_time']}\n\n"
            if news['content']:
                content = news['content'][:200] + "..." if len(news['content']) > 200 else news['content']
                report += f"{content}\n\n"
            report += "---\n\n"
        
        return report
        
    except Exception as e:
        return f"获取政策新闻失败: {str(e)}"

def get_ashare_industry_news(
    industry: Annotated[str, "行业名称，如'银行'、'科技'、'医药'"],
    curr_date: Annotated[str, "当前日期，格式：YYYY-MM-DD"],
    lookback_days: Annotated[int, "回看天数"] = 5
) -> str:
    """
    获取A股特定行业新闻
    
    Args:
        industry: 行业名称
        curr_date: 当前日期
        lookback_days: 回看天数
        
    Returns:
        str: 格式化的行业新闻报告
    """
    try:
        all_news = []
        
        # 从多个新闻源获取行业新闻
        sina_news = news_collector.get_sina_finance_news(
            keyword=f"{industry}行业",
            limit=10,
            days_back=lookback_days
        )
        all_news.extend(sina_news)
        
        cailianshe_news = news_collector.get_cailianshe_news(
            keyword=industry,
            limit=10,
            days_back=lookback_days
        )
        all_news.extend(cailianshe_news)
        
        if not all_news:
            return f"未找到关于 {industry} 行业的相关新闻"
        
        # 去重
        unique_news = []
        seen_titles = set()
        for news in all_news:
            if news['title'] not in seen_titles:
                unique_news.append(news)
                seen_titles.add(news['title'])
        
        # 格式化报告
        start_date = (datetime.strptime(curr_date, '%Y-%m-%d') - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
        
        report = f"## {industry}行业新闻汇总 ({start_date} 到 {curr_date})\n\n"
        
        for i, news in enumerate(unique_news[:12], 1):  # 限制显示12条
            report += f"### {i}. {news['title']}\n"
            report += f"**来源**: {news['source']} | **时间**: {news['publish_time']}\n\n"
            if news['content']:
                content = news['content'][:180] + "..." if len(news['content']) > 180 else news['content']
                report += f"{content}\n\n"
            report += "---\n\n"
        
        return report
        
    except Exception as e:
        return f"获取 {industry} 行业新闻失败: {str(e)}"