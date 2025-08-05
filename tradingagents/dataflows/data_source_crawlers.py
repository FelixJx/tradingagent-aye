# -*- coding: utf-8 -*-
"""
A股各大数据源爬虫模块
实现巨潮信息网、新浪财经、东方财富网、中国证券网、深交所互动易、第一财经、韭研公社等数据源的爬取
"""

import os
import time
import random
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging

import requests
import pandas as pd
from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..agents.data_collector_agent import DataSourceCrawler, DataSourceType, DataCollectionTask, DataCollectionResult

logger = logging.getLogger(__name__)

class EnhancedSinaCrawler(DataSourceCrawler):
    """增强版新浪财经爬虫"""
    
    def __init__(self):
        super().__init__(DataSourceType.SINA)
        self.base_url = "https://finance.sina.com.cn"
        self.api_base = "https://finance.sina.com.cn/api"
        
    def crawl(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取新浪财经数据"""
        try:
            if task.data_type == "news":
                return self._crawl_stock_news(task)
            elif task.data_type == "financial":
                return self._crawl_financial_data(task)
            elif task.data_type == "realtime":
                return self._crawl_realtime_data(task)
            else:
                return DataCollectionResult(
                    task=task,
                    success=False,
                    error_msg=f"不支持的数据类型: {task.data_type}"
                )
        except Exception as e:
            logger.error(f"新浪财经爬取失败: {str(e)}")
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )
    
    def _crawl_stock_news(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取股票新闻"""
        try:
            # 新浪财经股票新闻API
            news_url = f"https://finance.sina.com.cn/stock/stockprompt/{task.target}.shtml"
            response = self.session.get(news_url, timeout=task.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_list = []
            
            # 解析新闻列表
            news_items = soup.find_all('div', class_='feed-card-item')
            for item in news_items[:20]:  # 限制20条新闻
                try:
                    title_elem = item.find('h2') or item.find('a')
                    if title_elem:
                        title = title_elem.get_text().strip()
                        link = title_elem.get('href', '')
                        
                        # 获取时间
                        time_elem = item.find('span', class_='time')
                        publish_time = time_elem.get_text().strip() if time_elem else ''
                        
                        news_list.append({
                            'title': title,
                            'url': link if link.startswith('http') else f"https://finance.sina.com.cn{link}",
                            'publish_time': publish_time,
                            'stock_code': task.target,
                            'source': '新浪财经',
                            'content': ''
                        })
                except Exception as e:
                    logger.warning(f"解析新闻项失败: {str(e)}")
                    continue
            
            # 尝试获取新闻详细内容
            for news in news_list[:5]:  # 只获取前5条的详细内容
                try:
                    content = self._get_news_content(news['url'])
                    news['content'] = content
                    time.sleep(random.uniform(1, 2))  # 避免过于频繁
                except Exception as e:
                    logger.warning(f"获取新闻内容失败: {str(e)}")
            
            return DataCollectionResult(
                task=task,
                success=True,
                data=news_list
            )
            
        except Exception as e:
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )
    
    def _get_news_content(self, url: str) -> str:
        """获取新闻详细内容"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试多种内容选择器
            content_selectors = [
                'div.article',
                'div.artibody',
                'div.content',
                'div.main-content',
                'div#artibody'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # 清理内容
                    for script in content_elem(["script", "style"]):
                        script.decompose()
                    return content_elem.get_text().strip()[:1000]  # 限制长度
            
            return ""
        except:
            return ""

class EastMoneyCrawler(DataSourceCrawler):
    """东方财富网爬虫"""
    
    def __init__(self):
        super().__init__(DataSourceType.EASTMONEY)
        self.base_url = "https://www.eastmoney.com"
        self.api_base = "https://push2.eastmoney.com/api"
        
    def crawl(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取东方财富数据"""
        try:
            if task.data_type == "news":
                return self._crawl_stock_news(task)
            elif task.data_type == "announcement":
                return self._crawl_announcements(task)
            elif task.data_type == "research_report":
                return self._crawl_research_reports(task)
            else:
                return DataCollectionResult(
                    task=task,
                    success=False,
                    error_msg=f"不支持的数据类型: {task.data_type}"
                )
        except Exception as e:
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )
    
    def _crawl_stock_news(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取股票新闻"""
        try:
            # 东方财富股票新闻API
            api_url = f"{self.api_base}/qt/stock/news"
            params = {
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'np': '1',
                'fltt': '2',
                'invt': '2',
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152',
                'secid': self._convert_stock_code(task.target),
                'pageSize': '50',
                'pageIndex': '1'
            }
            
            response = self.session.get(api_url, params=params, timeout=task.timeout)
            response.raise_for_status()
            
            # 处理JSONP响应
            content = response.text
            if content.startswith('var'):
                # 提取JSON部分
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                data = json.loads(json_str)
            else:
                data = response.json()
            
            news_list = []
            if 'data' in data and 'list' in data['data']:
                for item in data['data']['list']:
                    news_list.append({
                        'title': item.get('title', ''),
                        'content': item.get('content', ''),
                        'url': item.get('url', ''),
                        'publish_time': item.get('showTime', ''),
                        'source': '东方财富网',
                        'stock_code': task.target
                    })
            
            return DataCollectionResult(
                task=task,
                success=True,
                data=news_list
            )
            
        except Exception as e:
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )
    
    def _convert_stock_code(self, stock_code: str) -> str:
        """转换股票代码格式"""
        if stock_code.startswith('6'):
            return f"1.{stock_code}"  # 上海
        elif stock_code.startswith(('0', '3')):
            return f"0.{stock_code}"  # 深圳
        return stock_code

class CNSCrawler(DataSourceCrawler):
    """中国证券网爬虫"""
    
    def __init__(self):
        super().__init__(DataSourceType.CNS)
        self.base_url = "https://www.cs.com.cn"
        
    def crawl(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取中国证券网数据"""
        try:
            if task.data_type == "news":
                return self._crawl_news(task)
            elif task.data_type == "policy":
                return self._crawl_policy_news(task)
            else:
                return DataCollectionResult(
                    task=task,
                    success=False,
                    error_msg=f"不支持的数据类型: {task.data_type}"
                )
        except Exception as e:
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )
    
    def _crawl_news(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取新闻"""
        try:
            # 使用搜索功能
            search_url = f"{self.base_url}/search"
            params = {
                'keyword': task.target,
                'pageSize': 20,
                'pageNum': 1
            }
            
            response = self.session.get(search_url, params=params, timeout=task.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_list = []
            
            # 解析搜索结果
            news_items = soup.find_all('div', class_='search-item') or soup.find_all('li', class_='news-item')
            
            for item in news_items:
                try:
                    title_elem = item.find('a') or item.find('h3')
                    if title_elem:
                        title = title_elem.get_text().strip()
                        link = title_elem.get('href', '')
                        
                        # 补全链接
                        if link and not link.startswith('http'):
                            link = f"{self.base_url}{link}"
                        
                        # 获取时间
                        time_elem = item.find('span', class_='time') or item.find('div', class_='date')
                        publish_time = time_elem.get_text().strip() if time_elem else ''
                        
                        news_list.append({
                            'title': title,
                            'url': link,
                            'publish_time': publish_time,
                            'source': '中国证券网',
                            'keyword': task.target,
                            'content': ''
                        })
                except Exception as e:
                    logger.warning(f"解析新闻项失败: {str(e)}")
                    continue
            
            return DataCollectionResult(
                task=task,
                success=True,
                data=news_list
            )
            
        except Exception as e:
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )

class YicaiCrawler(DataSourceCrawler):
    """第一财经爬虫"""
    
    def __init__(self):
        super().__init__(DataSourceType.YICAI)
        self.base_url = "https://www.yicai.com"
        self.api_base = "https://www.yicai.com/api"
        
    def crawl(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取第一财经数据"""
        try:
            if task.data_type == "news":
                return self._crawl_news(task)
            elif task.data_type == "video":
                return self._crawl_video_content(task)
            else:
                return DataCollectionResult(
                    task=task,
                    success=False,
                    error_msg=f"不支持的数据类型: {task.data_type}"
                )
        except Exception as e:
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )
    
    def _crawl_news(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取新闻"""
        try:
            # 第一财经搜索API
            search_url = f"{self.base_url}/search"
            params = {
                'q': task.target,
                'page': 1,
                'size': 20
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': self.base_url
            }
            
            response = self.session.get(search_url, params=params, headers=headers, timeout=task.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_list = []
            
            # 解析搜索结果
            news_items = soup.find_all('div', class_='m-news-item') or soup.find_all('article')
            
            for item in news_items:
                try:
                    title_elem = item.find('h3') or item.find('a', class_='title')
                    if title_elem:
                        title = title_elem.get_text().strip()
                        link = title_elem.find('a') if title_elem.name != 'a' else title_elem
                        url = link.get('href', '') if link else ''
                        
                        if url and not url.startswith('http'):
                            url = f"{self.base_url}{url}"
                        
                        # 获取摘要
                        summary_elem = item.find('p', class_='summary') or item.find('div', class_='desc')
                        summary = summary_elem.get_text().strip() if summary_elem else ''
                        
                        # 获取时间
                        time_elem = item.find('span', class_='time') or item.find('time')
                        publish_time = time_elem.get_text().strip() if time_elem else ''
                        
                        news_list.append({
                            'title': title,
                            'url': url,
                            'content': summary,
                            'publish_time': publish_time,
                            'source': '第一财经',
                            'keyword': task.target
                        })
                except Exception as e:
                    logger.warning(f"解析新闻项失败: {str(e)}")
                    continue
            
            return DataCollectionResult(
                task=task,
                success=True,
                data=news_list
            )
            
        except Exception as e:
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )

class JiuyanCrawler(DataSourceCrawler):
    """韭研公社爬虫"""
    
    def __init__(self):
        super().__init__(DataSourceType.JIUYAN)
        self.base_url = "https://www.jiuyangongshe.com"
        
    def crawl(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取韭研公社数据"""
        try:
            if task.data_type == "research":
                return self._crawl_research_content(task)
            elif task.data_type == "discussion":
                return self._crawl_discussions(task)
            else:
                return DataCollectionResult(
                    task=task,
                    success=False,
                    error_msg=f"不支持的数据类型: {task.data_type}"
                )
        except Exception as e:
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )
    
    def _crawl_research_content(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取研究内容"""
        try:
            # 韭研公社可能需要特殊处理，这里提供基础框架
            search_url = f"{self.base_url}/search"
            params = {
                'keyword': task.target,
                'type': 'research'
            }
            
            response = self.session.get(search_url, params=params, timeout=task.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            research_list = []
            
            # 根据实际网站结构解析内容
            items = soup.find_all('div', class_='research-item')
            
            for item in items:
                try:
                    title_elem = item.find('h3') or item.find('a', class_='title')
                    if title_elem:
                        title = title_elem.get_text().strip()
                        link = title_elem.get('href', '') if title_elem.name == 'a' else title_elem.find('a').get('href', '')
                        
                        if link and not link.startswith('http'):
                            link = f"{self.base_url}{link}"
                        
                        research_list.append({
                            'title': title,
                            'url': link,
                            'source': '韭研公社',
                            'type': 'research',
                            'keyword': task.target
                        })
                except Exception as e:
                    logger.warning(f"解析研究内容失败: {str(e)}")
                    continue
            
            return DataCollectionResult(
                task=task,
                success=True,
                data=research_list
            )
            
        except Exception as e:
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )

class SeleniumBasedCrawler:
    """基于Selenium的高级爬虫（用于需要JS渲染的网站）"""
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
        
    def setup_driver(self):
        """设置Selenium驱动"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
        except Exception as e:
            logger.warning(f"Selenium驱动设置失败: {str(e)}")
            self.driver = None
    
    def crawl_dynamic_content(self, url: str, wait_selector: str = None) -> str:
        """爬取动态内容"""
        if not self.driver:
            return ""
        
        try:
            self.driver.get(url)
            
            if wait_selector:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                )
            else:
                time.sleep(3)  # 等待页面加载
            
            return self.driver.page_source
            
        except Exception as e:
            logger.error(f"Selenium爬取失败: {str(e)}")
            return ""
    
    def __del__(self):
        if self.driver:
            self.driver.quit()

class CrawlerFactory:
    """爬虫工厂类"""
    
    @staticmethod
    def create_crawler(source_type: DataSourceType) -> DataSourceCrawler:
        """创建对应的爬虫实例"""
        crawler_map = {
            DataSourceType.SINA: EnhancedSinaCrawler,
            DataSourceType.EASTMONEY: EastMoneyCrawler,
            DataSourceType.CNS: CNSCrawler,
            DataSourceType.YICAI: YicaiCrawler,
            DataSourceType.JIUYAN: JiuyanCrawler,
        }
        
        crawler_class = crawler_map.get(source_type)
        if crawler_class:
            return crawler_class()
        else:
            raise ValueError(f"不支持的数据源类型: {source_type}")

# 导出所有爬虫
__all__ = [
    'EnhancedSinaCrawler',
    'EastMoneyCrawler', 
    'CNSCrawler',
    'YicaiCrawler',
    'JiuyanCrawler',
    'SeleniumBasedCrawler',
    'CrawlerFactory'
]