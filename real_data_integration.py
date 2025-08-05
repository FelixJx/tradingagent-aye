#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real Data Integration for Trading Agent
真实数据集成模块 - 替换模拟数据
"""

import os
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RealDataIntegrator:
    """真实数据集成器"""
    
    def __init__(self):
        self.tushare_token = os.getenv('TUSHARE_TOKEN')
        self.dashscope_api_key = os.getenv('DASHSCOPE_API_KEY')
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        
        # 检查API配置状态
        self.tushare_enabled = bool(self.tushare_token)
        self.dashscope_enabled = bool(self.dashscope_api_key)
        self.tavily_enabled = bool(self.tavily_api_key)
        
        logger.info(f"Real data integration initialized - Tushare: {self.tushare_enabled}, DashScope: {self.dashscope_enabled}, Tavily: {self.tavily_enabled}")

    def get_real_stock_data(self, symbol: str) -> Dict[str, Any]:
        """获取真实股票数据"""
        if self.tushare_enabled:
            try:
                return self._get_tushare_data(symbol)
            except Exception as e:
                logger.error(f"Tushare data fetch failed: {e}")
                return self._get_akshare_fallback(symbol)
        else:
            logger.warning("Tushare not configured, using AKShare fallback")
            return self._get_akshare_fallback(symbol)
    
    def _get_tushare_data(self, symbol: str) -> Dict[str, Any]:
        """使用Tushare获取数据"""
        try:
            import tushare as ts
            ts.set_token(self.tushare_token)
            pro = ts.pro_api()
            
            # 转换股票代码格式
            ts_symbol = self._convert_symbol_format(symbol)
            
            # 获取基本信息
            basic_info = pro.stock_basic(ts_code=ts_symbol, fields='ts_code,symbol,name,area,industry,market,pe,pb')
            
            if basic_info.empty:
                raise ValueError(f"Stock {symbol} not found in Tushare")
            
            # 获取最新价格数据
            today = datetime.now().strftime('%Y%m%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
            
            daily_data = pro.daily(ts_code=ts_symbol, start_date=yesterday, end_date=today)
            
            if not daily_data.empty:
                latest = daily_data.iloc[0]
                stock_info = basic_info.iloc[0]
                
                return {
                    'symbol': symbol,
                    'name': stock_info['name'],
                    'current_price': latest['close'],
                    'open_price': latest['open'],
                    'high_price': latest['high'],
                    'low_price': latest['low'],
                    'volume': latest['vol'],
                    'turnover': latest['pct_chg'],
                    'pe_ratio': stock_info['pe'] if stock_info['pe'] else 20.0,
                    'pb_ratio': stock_info['pb'] if stock_info['pb'] else 2.0,
                    'market_cap': latest['amount'],
                    'data_source': 'tushare'
                }
            else:
                raise ValueError("No recent trading data available")
                
        except Exception as e:
            logger.error(f"Tushare API error: {e}")
            raise
    
    def _get_akshare_fallback(self, symbol: str) -> Dict[str, Any]:
        """使用AKShare作为备用数据源"""
        try:
            import akshare as ak
            
            # 转换为akshare格式
            ak_symbol = symbol.replace('.SH', '').replace('.SZ', '')
            
            # 获取实时数据
            stock_info = ak.stock_individual_info_em(symbol=ak_symbol)
            stock_data = ak.stock_zh_a_spot_em()
            
            # 查找对应股票
            stock_row = stock_data[stock_data['代码'] == ak_symbol]
            
            if not stock_row.empty:
                row = stock_row.iloc[0]
                
                return {
                    'symbol': symbol,
                    'name': row['名称'],
                    'current_price': float(row['最新价']),
                    'open_price': float(row['今开']),
                    'high_price': float(row['最高']),
                    'low_price': float(row['最低']),
                    'volume': float(row['成交量']),
                    'turnover': float(row['涨跌幅']),
                    'pe_ratio': float(row['市盈率-动态']) if row['市盈率-动态'] != '-' else 20.0,
                    'pb_ratio': float(row['市净率']) if row['市净率'] != '-' else 2.0,
                    'market_cap': float(row['总市值']),
                    'data_source': 'akshare'
                }
            else:
                raise ValueError(f"Stock {symbol} not found in AKShare")
                
        except Exception as e:
            logger.error(f"AKShare API error: {e}")
            return self._get_mock_data(symbol)
    
    def get_real_news_analysis(self, symbol: str) -> Dict[str, Any]:
        """获取真实新闻分析"""
        if self.tavily_enabled:
            try:
                return self._search_with_tavily(symbol)
            except Exception as e:
                logger.error(f"Tavily search failed: {e}")
                return self._get_mock_news_data(symbol)
        else:
            logger.warning("Tavily not configured, using mock news data")
            return self._get_mock_news_data(symbol)
    
    def _search_with_tavily(self, symbol: str) -> Dict[str, Any]:
        """使用Tavily搜索新闻"""
        try:
            from tavily import TavilyClient
            
            client = TavilyClient(api_key=self.tavily_api_key)
            
            # 获取股票名称用于搜索
            stock_name = self._get_stock_name(symbol)
            query = f"{stock_name} 股票 最新新闻 分析 2024"
            
            # 搜索新闻
            response = client.search(
                query=query,
                search_depth="basic",
                max_results=5,
                include_domains=["finance.sina.com.cn", "money.163.com", "finance.qq.com"]
            )
            
            if response and 'results' in response:
                news_items = response['results']
                
                # 分析情感
                sentiment_score = self._analyze_news_sentiment(news_items)
                
                return {
                    'sentiment_score': sentiment_score,
                    'sentiment_text': self._get_sentiment_text(sentiment_score),
                    'news_count': len(news_items),
                    'summary': f'根据最近{len(news_items)}条新闻分析，市场对{stock_name}的情感偏向{self._get_sentiment_text(sentiment_score)}',
                    'key_news': [item['title'] for item in news_items[:3]],
                    'data_source': 'tavily'
                }
            else:
                raise ValueError("No news results found")
                
        except Exception as e:
            logger.error(f"Tavily API error: {e}")
            raise
    
    def get_real_llm_analysis(self, prompt: str, context: Dict = None) -> str:
        """获取真实LLM分析"""
        if self.dashscope_enabled:
            try:
                return self._call_dashscope_api(prompt, context)
            except Exception as e:
                logger.error(f"DashScope API failed: {e}")
                return self._get_mock_analysis(prompt)
        else:
            logger.warning("DashScope not configured, using mock analysis")
            return self._get_mock_analysis(prompt)
    
    def _call_dashscope_api(self, prompt: str, context: Dict = None) -> str:
        """调用DashScope API"""
        try:
            import dashscope
            from dashscope import Generation
            
            dashscope.api_key = self.dashscope_api_key
            
            # 构建完整的提示
            full_prompt = f"""
作为专业的股票分析师，请基于以下信息进行深度分析：

{prompt}

上下文信息: {context if context else '无'}

请提供专业、详细的分析，包括：
1. 技术面分析
2. 基本面评估  
3. 市场情感判断
4. 风险提示
5. 投资建议

请确保分析客观、专业，并包含具体的数据支撑。
"""
            
            response = Generation.call(
                model='qwen-turbo',
                prompt=full_prompt,
                max_tokens=1500,
                temperature=0.7
            )
            
            if response.status_code == 200:
                return response.output.text
            else:
                raise ValueError(f"DashScope API error: {response.message}")
                
        except Exception as e:
            logger.error(f"DashScope API call error: {e}")
            raise
    
    # 辅助方法
    def _convert_symbol_format(self, symbol: str) -> str:
        """转换股票代码格式为Tushare格式"""
        if '.SH' in symbol:
            return symbol
        elif '.SZ' in symbol:
            return symbol
        else:
            # 根据代码判断市场
            code = symbol.replace('.', '')
            if code.startswith('6'):
                return f"{code}.SH"
            else:
                return f"{code}.SZ"
    
    def _get_stock_name(self, symbol: str) -> str:
        """获取股票名称"""
        names = {
            '000001.SZ': '平安银行',
            '000002.SZ': '万科A', 
            '600036.SH': '招商银行',
            '600519.SH': '贵州茅台',
            '000858.SZ': '五粮液',
            '002415.SZ': '海康威视',
            '300059.SZ': '东方财富'
        }
        return names.get(symbol, f'股票{symbol.split(".")[0]}')
    
    def _analyze_news_sentiment(self, news_items: List[Dict]) -> float:
        """分析新闻情感"""
        # 简单的关键词情感分析
        positive_keywords = ['上涨', '增长', '利好', '突破', '买入', '推荐', '看好']
        negative_keywords = ['下跌', '下降', '利空', '风险', '卖出', '谨慎', '看空']
        
        total_score = 0
        for item in news_items:
            title = item.get('title', '')
            content = item.get('content', '')
            text = title + ' ' + content
            
            pos_count = sum(1 for word in positive_keywords if word in text)
            neg_count = sum(1 for word in negative_keywords if word in text)
            
            if pos_count > neg_count:
                total_score += 0.3
            elif neg_count > pos_count:
                total_score -= 0.3
        
        return max(-1.0, min(1.0, total_score))
    
    def _get_sentiment_text(self, score: float) -> str:
        """获取情感文本描述"""
        if score > 0.3:
            return '积极'
        elif score < -0.3:
            return '消极'
        else:
            return '中性'
    
    # 备用模拟数据方法
    def _get_mock_data(self, symbol: str) -> Dict[str, Any]:
        """备用模拟数据"""
        base_price = 100 + (hash(symbol) % 50)
        return {
            'symbol': symbol,
            'name': self._get_stock_name(symbol),
            'current_price': round(base_price + (hash(symbol + str(datetime.now().day)) % 20 - 10), 2),
            'open_price': round(base_price + (hash(symbol + 'open') % 15 - 7), 2),
            'high_price': round(base_price + (hash(symbol + 'high') % 25), 2),
            'low_price': round(base_price - (hash(symbol + 'low') % 15), 2),
            'volume': (hash(symbol + 'vol') % 1000000) + 100000,
            'turnover': round((hash(symbol + 'turn') % 100) / 10, 2),
            'pe_ratio': round(15 + (hash(symbol + 'pe') % 30), 2),
            'pb_ratio': round(1 + (hash(symbol + 'pb') % 50) / 10, 2), 
            'market_cap': (hash(symbol + 'cap') % 5000) + 1000,
            'data_source': 'mock'
        }
    
    def _get_mock_news_data(self, symbol: str) -> Dict[str, Any]:
        """备用模拟新闻数据"""
        sentiment_score = round((hash(symbol + 'news') % 200 - 100) / 100, 2)
        news_count = hash(symbol + 'count') % 20 + 5
        stock_name = self._get_stock_name(symbol)
        
        return {
            'sentiment_score': sentiment_score,
            'sentiment_text': self._get_sentiment_text(sentiment_score),
            'news_count': news_count,
            'summary': f'根据最近{news_count}条新闻分析，市场对{stock_name}的情感偏向{self._get_sentiment_text(sentiment_score)}',
            'key_news': [
                f'{stock_name}发布最新财报，业绩超预期',
                f'机构调研显示对{stock_name}前景看好',
                f'{stock_name}获得重要合作项目'
            ][:news_count//3 + 1],
            'data_source': 'mock'
        }
    
    def _get_mock_analysis(self, prompt: str) -> str:
        """备用模拟分析"""
        return f"基于模拟数据的分析结果：{prompt[:100]}... (DashScope API未配置，使用模拟分析)"

# 全局实例
real_data_integrator = RealDataIntegrator()

def get_real_stock_data(symbol: str) -> Dict[str, Any]:
    """全局函数：获取真实股票数据"""
    return real_data_integrator.get_real_stock_data(symbol)

def get_real_news_analysis(symbol: str) -> Dict[str, Any]:
    """全局函数：获取真实新闻分析"""
    return real_data_integrator.get_real_news_analysis(symbol)

def get_real_llm_analysis(prompt: str, context: Dict = None) -> str:
    """全局函数：获取真实LLM分析"""
    return real_data_integrator.get_real_llm_analysis(prompt, context)