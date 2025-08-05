#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实数据分析器 - 连接Tushare API和网络搜索
配置真实数据源，禁止使用模拟数据
"""

import os
import json
import requests
from datetime import datetime, timedelta
import time

# 配置环境变量
os.environ['TUSHARE_TOKEN'] = 'b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065'
os.environ['TAVILY_API_KEY'] = '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'

class RealDataConnector:
    """真实数据连接器"""
    
    def __init__(self):
        self.tushare_token = os.environ.get('TUSHARE_TOKEN')
        self.tavily_api_key = os.environ.get('TAVILY_API_KEY')
        self.tushare_base_url = 'http://api.waditu.com'
        self.tavily_base_url = 'https://api.tavily.com'
        
        print("🔌 初始化真实数据连接器...")
        print("✅ Tushare Token: {}...".format(self.tushare_token[:20]))
        print("✅ Tavily API Key: {}...".format(self.tavily_api_key[:20]))
    
    def test_tushare_connection(self):
        """测试Tushare连接"""
        print("\n🧪 测试Tushare API连接...")
        
        try:
            # 测试API连接
            payload = {
                'api_name': 'stock_basic',
                'token': self.tushare_token,
                'params': {
                    'list_status': 'L',
                    'limit': 5
                },
                'fields': 'ts_code,symbol,name,area,industry,market'
            }
            
            response = requests.post(self.tushare_base_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    print("✅ Tushare连接成功！")
                    print("📊 获取到 {} 条股票基础信息".format(len(result['data']['items'])))
                    return True
                else:
                    print("❌ Tushare API错误: {}".format(result.get('msg', 'Unknown error')))
                    return False
            else:
                print("❌ HTTP错误: {}".format(response.status_code))
                return False
                
        except requests.exceptions.Timeout:
            print("❌ Tushare连接超时")
            return False
        except Exception as e:
            print("❌ Tushare连接失败: {}".format(str(e)))
            return False
    
    def test_tavily_connection(self):
        """测试Tavily搜索连接"""
        print("\n🧪 测试Tavily搜索API连接...")
        
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                'api_key': self.tavily_api_key,
                'query': '华康洁净 688015 最新消息',
                'search_depth': 'basic',
                'max_results': 3
            }
            
            response = requests.post(
                '{}/search'.format(self.tavily_base_url),
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Tavily搜索连接成功！")
                print("🔍 搜索到 {} 条相关信息".format(len(result.get('results', []))))
                return True
            else:
                print("❌ Tavily HTTP错误: {}".format(response.status_code))
                print("响应内容: {}".format(response.text[:200]))
                return False
                
        except requests.exceptions.Timeout:
            print("❌ Tavily连接超时")
            return False
        except Exception as e:
            print("❌ Tavily连接失败: {}".format(str(e)))
            return False
    
    def get_stock_basic_info(self, stock_code):
        """获取股票基础信息"""
        print("\n📊 获取 {} 基础信息...".format(stock_code))
        
        try:
            payload = {
                'api_name': 'stock_basic',
                'token': self.tushare_token,
                'params': {
                    'ts_code': stock_code
                },
                'fields': 'ts_code,symbol,name,area,industry,market,list_date'
            }
            
            response = requests.post(self.tushare_base_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0 and result['data']['items']:
                    data = result['data']['items'][0]
                    stock_info = {
                        'ts_code': data[0],
                        'symbol': data[1], 
                        'name': data[2],
                        'area': data[3],
                        'industry': data[4],
                        'market': data[5],
                        'list_date': data[6]
                    }
                    print("✅ 获取基础信息成功: {}({})".format(stock_info['name'], stock_info['ts_code']))
                    return stock_info
                else:
                    print("❌ 未找到股票信息或API错误")
                    return None
            else:
                print("❌ 请求失败: {}".format(response.status_code))
                return None
                
        except Exception as e:
            print("❌ 获取基础信息失败: {}".format(str(e)))
            return None
    
    def get_daily_price_data(self, stock_code, start_date='20240101', end_date=None):
        """获取日线数据"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
            
        print("\n📈 获取 {} 价格数据 ({} - {})...".format(stock_code, start_date, end_date))
        
        try:
            payload = {
                'api_name': 'daily',
                'token': self.tushare_token,
                'params': {
                    'ts_code': stock_code,
                    'start_date': start_date,
                    'end_date': end_date
                },
                'fields': 'ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount'
            }
            
            response = requests.post(self.tushare_base_url, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    items = result['data']['items']
                    print("✅ 获取价格数据成功: {} 条记录".format(len(items)))
                    
                    # 转换为更易用的格式
                    price_data = []
                    for item in items:
                        price_data.append({
                            'trade_date': item[1],
                            'open': item[2],
                            'high': item[3], 
                            'low': item[4],
                            'close': item[5],
                            'pre_close': item[6],
                            'change': item[7],
                            'pct_chg': item[8],
                            'vol': item[9],
                            'amount': item[10]
                        })
                    
                    return price_data
                else:
                    print("❌ API错误: {}".format(result.get('msg', 'Unknown error')))
                    return None
            else:
                print("❌ 请求失败: {}".format(response.status_code))
                return None
                
        except Exception as e:
            print("❌ 获取价格数据失败: {}".format(str(e)))
            return None
    
    def get_financial_data(self, stock_code, start_date='20230101', end_date=None):
        """获取财务数据"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
            
        print("\n💰 获取 {} 财务数据...".format(stock_code))
        
        try:
            # 获取利润表数据
            payload = {
                'api_name': 'income',
                'token': self.tushare_token,
                'params': {
                    'ts_code': stock_code,
                    'start_date': start_date,
                    'end_date': end_date,
                    'report_type': '1'  # 1-定期报告
                },
                'fields': 'ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,total_revenue,revenue,oper_cost,gross_profit,sell_exp,admin_exp,fin_exp,oper_profit,total_profit,income_tax,n_income,n_income_attr_p'
            }
            
            response = requests.post(self.tushare_base_url, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    items = result['data']['items']
                    print("✅ 获取财务数据成功: {} 条记录".format(len(items)))
                    return items
                else:
                    print("❌ 财务数据API错误: {}".format(result.get('msg', 'Unknown error')))
                    return None
            else:
                print("❌ 财务数据请求失败: {}".format(response.status_code))
                return None
                
        except Exception as e:
            print("❌ 获取财务数据失败: {}".format(str(e)))
            return None
    
    def search_stock_news(self, stock_name, stock_code, max_results=5):
        """搜索股票相关新闻"""
        print("\n🔍 搜索 {}({}) 相关新闻...".format(stock_name, stock_code))
        
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            query = "{} {} 最新消息 财报 业绩".format(stock_name, stock_code)
            
            payload = {
                'api_key': self.tavily_api_key,
                'query': query,
                'search_depth': 'advanced',
                'max_results': max_results,
                'include_domains': ['sina.com.cn', 'eastmoney.com', 'cnstock.com', 'stcn.com'],
                'include_answer': True
            }
            
            response = requests.post(
                '{}/search'.format(self.tavily_base_url),
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                news_results = result.get('results', [])
                print("✅ 搜索新闻成功: {} 条相关新闻".format(len(news_results)))
                
                # 格式化新闻结果
                formatted_news = []
                for news in news_results:
                    formatted_news.append({
                        'title': news.get('title', ''),
                        'url': news.get('url', ''),
                        'content': news.get('content', '')[:200] + '...',
                        'published_date': news.get('published_date', ''),
                        'score': news.get('score', 0)
                    })
                
                return formatted_news
            else:
                print("❌ 新闻搜索失败: {}".format(response.status_code))
                return None
                
        except Exception as e:
            print("❌ 搜索新闻失败: {}".format(str(e)))
            return None

class RealDataAnalyzer:
    """基于真实数据的分析器"""
    
    def __init__(self):
        self.connector = RealDataConnector()
        self.analysis_time = datetime.now()
    
    def comprehensive_real_analysis(self, stock_code):
        """基于真实数据的综合分析"""
        print("="*80)
        print("🎯 {} 真实数据全面分析".format(stock_code))
        print("="*80)
        print("📅 分析时间: {}".format(self.analysis_time.strftime('%Y-%m-%d %H:%M:%S')))
        print("🔍 数据源: Tushare实时API + Tavily搜索")
        
        # 测试连接
        tushare_ok = self.connector.test_tushare_connection()
        tavily_ok = self.connector.test_tavily_connection()
        
        if not tushare_ok:
            print("❌ 无法连接Tushare，请检查网络和Token")
            return None
        
        # 获取真实数据
        analysis_result = {}
        
        # 1. 基础信息
        basic_info = self.connector.get_stock_basic_info(stock_code)
        if basic_info:
            analysis_result['basic_info'] = basic_info
        
        # 2. 价格数据
        price_data = self.connector.get_daily_price_data(stock_code)
        if price_data:
            analysis_result['price_data'] = price_data
            
            # 计算基础指标
            latest_data = price_data[0] if price_data else None
            if latest_data:
                print("\n📊 最新价格信息")
                print("-" * 40)
                print("当前价格: {} 元".format(latest_data['close']))
                print("涨跌幅: {}%".format(latest_data['pct_chg']))
                print("成交量: {} 手".format(int(latest_data['vol'])))
                print("成交额: {:.2f} 万元".format(latest_data['amount'] / 10))
        
        # 3. 财务数据
        financial_data = self.connector.get_financial_data(stock_code)
        if financial_data:
            analysis_result['financial_data'] = financial_data
            
            if financial_data:
                latest_financial = financial_data[0]
                print("\n💰 最新财务信息")
                print("-" * 40)
                print("报告期: {}".format(latest_financial[3]))
                print("营业收入: {:.2f} 万元".format((latest_financial[6] or 0) / 10000))
                print("净利润: {:.2f} 万元".format((latest_financial[16] or 0) / 10000))
        
        # 4. 新闻搜索
        if tavily_ok and basic_info:
            news_data = self.connector.search_stock_news(
                basic_info['name'], 
                stock_code
            )
            if news_data:
                analysis_result['news_data'] = news_data
                
                print("\n📰 最新相关新闻")
                print("-" * 40)
                for i, news in enumerate(news_data[:3], 1):
                    print("{}. {}".format(i, news['title']))
                    print("   {}".format(news['content']))
                    print()
        
        # 保存真实数据分析结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = "{}_真实数据分析_{}.json".format(
            basic_info['name'] if basic_info else stock_code, 
            timestamp
        )
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2, default=str)
        
        print("\n📄 真实数据分析报告已保存: {}".format(filename))
        
        return analysis_result

def main():
    """主函数 - 测试真实数据连接"""
    print("🚀 启动真实数据分析系统")
    print("🔗 连接Tushare API + Tavily搜索")
    print("🚫 严禁使用模拟数据")
    
    analyzer = RealDataAnalyzer()
    
    # 分析华康洁净
    stock_code = '688015.SH'
    result = analyzer.comprehensive_real_analysis(stock_code)
    
    if result:
        print("\n🎉 真实数据分析完成！")
    else:
        print("\n❌ 真实数据获取失败，请检查网络连接和API配置")

if __name__ == "__main__":
    main()