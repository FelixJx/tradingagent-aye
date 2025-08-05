#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
News and Search Service
集成Tavily API和新闻搜索功能
"""

import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

# Tavily搜索导入
try:
    from tavily import TavilyClient
    HAS_TAVILY = True
    print("✅ Tavily successfully imported")
except ImportError:
    HAS_TAVILY = False
    print("❌ Tavily not available")

# AKShare新闻导入
try:
    import akshare as ak
    HAS_AKSHARE_NEWS = True
except ImportError:
    HAS_AKSHARE_NEWS = False

class NewsSearchService:
    """新闻搜索服务"""
    
    def __init__(self, tavily_api_key: str = None):
        self.tavily_api_key = tavily_api_key or os.getenv('TAVILY_API_KEY')
        self.tavily_client = None
        self.initialize_tavily()
    
    def initialize_tavily(self):
        """初始化Tavily客户端"""
        if HAS_TAVILY and self.tavily_api_key:
            try:
                self.tavily_client = TavilyClient(api_key=self.tavily_api_key)
                print(f"✅ Tavily initialized with key: {self.tavily_api_key[:10]}...")
            except Exception as e:
                print(f"❌ Tavily initialization failed: {e}")
                self.tavily_client = None
        else:
            print("⚠️ Tavily API key not available")
    
    async def search_stock_news(self, symbol: str, company_name: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索股票相关新闻"""
        all_news = []
        
        # 1. 使用Tavily搜索最新新闻
        if self.tavily_client:
            try:
                tavily_news = await self._search_tavily_news(symbol, company_name, limit//2)
                all_news.extend(tavily_news)
                print(f"✅ Tavily found {len(tavily_news)} news items for {symbol}")
            except Exception as e:
                print(f"⚠️ Tavily search failed: {e}")
        
        # 2. 使用AKShare获取股票新闻
        if HAS_AKSHARE_NEWS:
            try:
                akshare_news = await self._get_akshare_news(symbol, limit//2)
                all_news.extend(akshare_news)
                print(f"✅ AKShare found {len(akshare_news)} news items for {symbol}")
            except Exception as e:
                print(f"⚠️ AKShare news failed: {e}")
        
        # 3. 去重和排序
        all_news = self._deduplicate_news(all_news)
        all_news = sorted(all_news, key=lambda x: x.get('published_date', ''), reverse=True)
        
        return all_news[:limit]
    
    async def _search_tavily_news(self, symbol: str, company_name: str, limit: int) -> List[Dict[str, Any]]:
        """使用Tavily搜索新闻"""
        if not self.tavily_client:
            return []
        
        try:
            # 构建搜索查询
            queries = [
                f"{symbol} 股票 最新消息",
                f"{company_name} 公司新闻" if company_name else f"{symbol} A股",
                f"{symbol} 财经新闻 投资",
            ]
            
            all_results = []
            
            for query in queries[:2]:  # 限制查询次数
                try:
                    response = self.tavily_client.search(
                        query=query,
                        search_depth="basic",
                        include_domains=["sina.com.cn", "eastmoney.com", "cnstock.com", "stcn.com", "cs.com.cn"],
                        max_results=limit//2
                    )
                    
                    if response and 'results' in response:
                        for item in response['results']:
                            news_item = {
                                'title': item.get('title', ''),
                                'content': item.get('content', ''),
                                'url': item.get('url', ''),
                                'published_date': item.get('published_date', datetime.now().isoformat()),
                                'source': self._extract_domain(item.get('url', '')),
                                'score': item.get('score', 0),
                                'data_source': 'tavily',
                                'query': query
                            }
                            all_results.append(news_item)
                            
                except Exception as e:
                    print(f"Tavily query error for '{query}': {e}")
                    continue
            
            return all_results
            
        except Exception as e:
            print(f"Tavily search error: {e}")
            return []
    
    async def _get_akshare_news(self, symbol: str, limit: int) -> List[Dict[str, Any]]:
        """获取AKShare股票新闻"""
        if not HAS_AKSHARE_NEWS:
            return []
            
        try:
            # 获取个股新闻
            news_df = ak.stock_news_em(symbol=symbol)
            
            if news_df.empty:
                return []
            
            news_list = []
            for idx, row in news_df.head(limit).iterrows():
                news_item = {
                    'title': row.get('新闻标题', ''),
                    'content': row.get('新闻内容', ''),
                    'url': row.get('新闻链接', ''),
                    'published_date': str(row.get('发布时间', '')),
                    'source': row.get('新闻来源', ''),
                    'data_source': 'akshare'
                }
                news_list.append(news_item)
            
            return news_list
            
        except Exception as e:
            print(f"AKShare news error: {e}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """提取域名"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return "unknown"
    
    def _deduplicate_news(self, news_list: List[Dict]) -> List[Dict]:
        """新闻去重"""
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            title = news.get('title', '').strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(news)
        
        return unique_news
    
    async def search_market_sentiment(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索市场情绪相关信息"""
        if not self.tavily_client:
            return []
        
        try:
            response = self.tavily_client.search(
                query=f"{query} 市场情绪 投资者 分析",
                search_depth="advanced",
                include_domains=["sina.com.cn", "eastmoney.com", "wallstreetcn.com", "xueqiu.com"],
                max_results=limit
            )
            
            results = []
            if response and 'results' in response:
                for item in response['results']:
                    results.append({
                        'title': item.get('title', ''),
                        'content': item.get('content', ''),
                        'url': item.get('url', ''),
                        'score': item.get('score', 0),
                        'source': self._extract_domain(item.get('url', '')),
                        'type': 'sentiment'
                    })
            
            return results
            
        except Exception as e:
            print(f"Market sentiment search error: {e}")
            return []
    
    async def search_industry_news(self, industry: str, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索行业新闻"""
        if not self.tavily_client:
            return []
        
        try:
            response = self.tavily_client.search(
                query=f"{industry} 行业新闻 发展趋势 政策",
                search_depth="basic",
                max_results=limit
            )
            
            results = []
            if response and 'results' in response:
                for item in response['results']:
                    results.append({
                        'title': item.get('title', ''),
                        'content': item.get('content', ''),
                        'url': item.get('url', ''),
                        'industry': industry,
                        'type': 'industry_news'
                    })
            
            return results
            
        except Exception as e:
            print(f"Industry news search error: {e}")
            return []
    
    async def get_comprehensive_analysis_data(self, symbol: str, company_name: str = None) -> Dict[str, Any]:
        """获取综合分析数据"""
        results = {
            'symbol': symbol,
            'company_name': company_name,
            'timestamp': datetime.now().isoformat(),
            'news': [],
            'sentiment': [],
            'industry_news': []
        }
        
        # 并行获取各类数据
        tasks = [
            self.search_stock_news(symbol, company_name, 15),
            self.search_market_sentiment(f"{symbol} {company_name or ''}", 5),
        ]
        
        try:
            news, sentiment = await asyncio.gather(*tasks, return_exceptions=True)
            
            if not isinstance(news, Exception):
                results['news'] = news
            if not isinstance(sentiment, Exception):
                results['sentiment'] = sentiment
                
        except Exception as e:
            print(f"Comprehensive analysis error: {e}")
        
        return results

# 全局实例
_news_service = None

def get_news_service() -> NewsSearchService:
    """获取新闻服务实例"""
    global _news_service
    if _news_service is None:
        _news_service = NewsSearchService()
    return _news_service

# 测试函数
async def test_news_service():
    """测试新闻服务"""
    service = get_news_service()
    
    print("=== 测试股票新闻搜索 ===")
    news = await service.search_stock_news("600036", "招商银行", 5)
    for item in news:
        print(f"标题: {item['title']}")
        print(f"来源: {item['source']} | 时间: {item['published_date']}")
        print("-" * 50)
    
    print("\n=== 测试市场情绪分析 ===")
    sentiment = await service.search_market_sentiment("招商银行 600036", 3)
    for item in sentiment:
        print(f"标题: {item['title']}")
        print(f"内容: {item['content'][:100]}...")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_news_service())