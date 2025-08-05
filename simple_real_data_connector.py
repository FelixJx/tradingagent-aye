#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版真实数据连接器
使用内置库进行API连接，避免外部依赖
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
import ssl

class SimpleRealDataConnector:
    """简化版真实数据连接器"""
    
    def __init__(self):
        self.tushare_token = 'b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065'
        self.tavily_api_key = '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'
        self.tushare_base_url = 'http://api.waditu.com'
        
        print("🔌 初始化简化版真实数据连接器...")
        print("✅ Tushare Token: {}...".format(self.tushare_token[:20]))
        print("✅ Tavily API Key: {}...".format(self.tavily_api_key[:20]))
        
        # SSL配置（根据Python版本调整）
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
        except AttributeError:
            pass  # 老版本Python可能没有这个属性
    
    def test_tushare_connection(self):
        """测试Tushare连接"""
        print("\n🧪 测试Tushare API连接...")
        
        try:
            # 构建测试请求
            data = {
                'api_name': 'stock_basic',
                'token': self.tushare_token,
                'params': {
                    'list_status': 'L',
                    'limit': 5
                },
                'fields': 'ts_code,symbol,name,area,industry,market'
            }
            
            # 转换为JSON并编码
            json_data = json.dumps(data).encode('utf-8')
            
            # 创建请求
            req = urllib.request.Request(
                self.tushare_base_url,
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('code') == 0:
                    print("✅ Tushare连接成功！")
                    data_items = result.get('data', {}).get('items', [])
                    print("📊 获取到 {} 条股票基础信息".format(len(data_items)))
                    return True
                else:
                    print("❌ Tushare API错误: {}".format(result.get('msg', 'Unknown error')))
                    return False
                    
        except urllib.error.URLError as e:
            print("❌ Tushare连接失败: {}".format(str(e)))
            return False
        except Exception as e:
            print("❌ Tushare连接异常: {}".format(str(e)))
            return False
    
    def get_stock_basic_info(self, stock_code):
        """获取股票基础信息"""
        print("\n📊 获取 {} 基础信息...".format(stock_code))
        
        try:
            data = {
                'api_name': 'stock_basic',
                'token': self.tushare_token,
                'params': {
                    'ts_code': stock_code
                },
                'fields': 'ts_code,symbol,name,area,industry,market,list_date'
            }
            
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                self.tushare_base_url,
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('code') == 0:
                    items = result.get('data', {}).get('items', [])
                    if items:
                        data_item = items[0]
                        stock_info = {
                            'ts_code': data_item[0],
                            'symbol': data_item[1],
                            'name': data_item[2],
                            'area': data_item[3],
                            'industry': data_item[4],
                            'market': data_item[5],
                            'list_date': data_item[6]
                        }
                        print("✅ 获取基础信息成功: {}({})".format(stock_info['name'], stock_info['ts_code']))
                        return stock_info
                    else:
                        print("❌ 未找到股票信息")
                        return None
                else:
                    print("❌ API错误: {}".format(result.get('msg', 'Unknown error')))
                    return None
                    
        except Exception as e:
            print("❌ 获取基础信息失败: {}".format(str(e)))
            return None
    
    def get_daily_price_data(self, stock_code, start_date='20240501', end_date=None):
        """获取日线数据"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
            
        print("\n📈 获取 {} 价格数据 ({} - {})...".format(stock_code, start_date, end_date))
        
        try:
            data = {
                'api_name': 'daily',
                'token': self.tushare_token,
                'params': {
                    'ts_code': stock_code,
                    'start_date': start_date,
                    'end_date': end_date
                },
                'fields': 'ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount'
            }
            
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                self.tushare_base_url,
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('code') == 0:
                    items = result.get('data', {}).get('items', [])
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
                    
        except Exception as e:
            print("❌ 获取价格数据失败: {}".format(str(e)))
            return None
    
    def get_financial_indicators(self, stock_code, start_date='20230101', end_date=None):
        """获取财务指标数据"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
            
        print("\n💰 获取 {} 财务指标数据...".format(stock_code))
        
        try:
            data = {
                'api_name': 'fina_indicator',
                'token': self.tushare_token,
                'params': {
                    'ts_code': stock_code,
                    'start_date': start_date,
                    'end_date': end_date
                },
                'fields': 'ts_code,ann_date,end_date,eps,dt_eps,total_revenue_ps,revenue_ps,capital_roe,weighted_roe,dt_roe,roa,npta,roic,roe_yearly,roa2_yearly,debt_to_assets,assets_to_eqt,dp_assets_to_eqt,ca_to_assets'
            }
            
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                self.tushare_base_url,
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('code') == 0:
                    items = result.get('data', {}).get('items', [])
                    print("✅ 获取财务指标成功: {} 条记录".format(len(items)))
                    return items
                else:
                    print("❌ 财务指标API错误: {}".format(result.get('msg', 'Unknown error')))
                    return None
                    
        except Exception as e:
            print("❌ 获取财务指标失败: {}".format(str(e)))
            return None

class SimpleRealDataAnalyzer:
    """基于真实数据的简化分析器"""
    
    def __init__(self):
        self.connector = SimpleRealDataConnector()
        self.analysis_time = datetime.now()
    
    def calculate_technical_indicators(self, price_data):
        """计算技术指标"""
        if not price_data or len(price_data) < 20:
            return None
        
        print("\n📊 计算技术指标...")
        
        # 按时间排序（最新的在前）
        sorted_data = sorted(price_data, key=lambda x: x['trade_date'], reverse=True)
        
        # 获取最近20日数据
        recent_data = sorted_data[:20]
        
        # 计算移动平均线
        ma5 = sum(item['close'] for item in recent_data[:5]) / 5
        ma10 = sum(item['close'] for item in recent_data[:10]) / 10
        ma20 = sum(item['close'] for item in recent_data) / 20
        
        # 计算波动率
        closes = [item['close'] for item in recent_data]
        if len(closes) > 1:
            returns = [(closes[i] - closes[i+1]) / closes[i+1] for i in range(len(closes)-1)]
            volatility = (sum(r*r for r in returns) / len(returns)) ** 0.5
        else:
            volatility = 0
        
        # 计算成交量比率
        recent_volumes = [item['vol'] for item in recent_data[:5]]
        avg_volume_5d = sum(recent_volumes) / len(recent_volumes)
        current_volume = recent_data[0]['vol']
        volume_ratio = current_volume / avg_volume_5d if avg_volume_5d > 0 else 1
        
        technical_indicators = {
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            'volatility_20d': volatility,
            'volume_ratio': volume_ratio,
            'latest_close': recent_data[0]['close'],
            'latest_change': recent_data[0]['change'],
            'latest_pct_chg': recent_data[0]['pct_chg']
        }
        
        print("✅ 技术指标计算完成")
        return technical_indicators
    
    def analyze_financial_health(self, financial_data):
        """分析财务健康状况"""
        if not financial_data:
            return None
        
        print("\n💎 分析财务健康状况...")
        
        # 获取最新财务数据
        latest_data = financial_data[0]
        
        financial_health = {
            'report_date': latest_data[2],  # end_date
            'eps': latest_data[3],          # 每股收益
            'roe': latest_data[5],          # 净资产收益率
            'roa': latest_data[7],          # 总资产收益率
            'debt_ratio': latest_data[14],  # 资产负债率
            'current_ratio': latest_data[17] # 流动比率
        }
        
        # 评估财务健康度
        health_score = 100
        
        # ROE评估
        roe = financial_health['roe'] or 0
        if roe < 5:
            health_score -= 20
        elif roe > 15:
            health_score += 10
        
        # 负债率评估
        debt_ratio = financial_health['debt_ratio'] or 0
        if debt_ratio > 60:
            health_score -= 15
        elif debt_ratio < 30:
            health_score += 5
        
        financial_health['health_score'] = max(0, min(100, health_score))
        
        print("✅ 财务健康分析完成")
        return financial_health
    
    def comprehensive_real_analysis(self, stock_code):
        """基于真实数据的综合分析"""
        print("="*80)
        print("🎯 {} 真实数据全面分析".format(stock_code))
        print("="*80)
        print("📅 分析时间: {}".format(self.analysis_time.strftime('%Y-%m-%d %H:%M:%S')))
        print("🔍 数据源: Tushare真实API")
        print("🚫 严禁模拟数据")
        
        # 测试连接
        if not self.connector.test_tushare_connection():
            print("❌ 无法连接Tushare，分析终止")
            return None
        
        analysis_result = {}
        
        # 1. 获取基础信息
        basic_info = self.connector.get_stock_basic_info(stock_code)
        if basic_info:
            analysis_result['basic_info'] = basic_info
            print("\n📋 股票基础信息")
            print("-" * 40)
            print("股票名称: {}".format(basic_info['name']))
            print("所属行业: {}".format(basic_info['industry']))
            print("上市日期: {}".format(basic_info['list_date']))
            print("交易市场: {}".format(basic_info['market']))
        
        # 2. 获取价格数据
        price_data = self.connector.get_daily_price_data(stock_code)
        if price_data:
            analysis_result['price_data'] = price_data
            
            # 显示最新价格信息
            latest_price = price_data[0]
            print("\n📊 最新交易数据")
            print("-" * 40)
            print("交易日期: {}".format(latest_price['trade_date']))
            print("收盘价: {:.2f} 元".format(latest_price['close']))
            print("涨跌幅: {:.2f}%".format(latest_price['pct_chg']))
            print("成交量: {:.0f} 手".format(latest_price['vol']))
            print("成交额: {:.2f} 万元".format(latest_price['amount'] / 10))
            
            # 计算技术指标
            technical_indicators = self.calculate_technical_indicators(price_data)
            if technical_indicators:
                analysis_result['technical_indicators'] = technical_indicators
                
                print("\n📈 技术指标分析")
                print("-" * 40)
                print("MA5: {:.2f}".format(technical_indicators['ma5']))
                print("MA10: {:.2f}".format(technical_indicators['ma10']))
                print("MA20: {:.2f}".format(technical_indicators['ma20']))
                print("20日波动率: {:.4f}".format(technical_indicators['volatility_20d']))
                print("成交量比率: {:.2f}".format(technical_indicators['volume_ratio']))
        
        # 3. 获取财务指标
        financial_data = self.connector.get_financial_indicators(stock_code)
        if financial_data:
            analysis_result['financial_data'] = financial_data
            
            # 分析财务健康度
            financial_health = self.analyze_financial_health(financial_data)
            if financial_health:
                analysis_result['financial_health'] = financial_health
                
                print("\n💰 财务健康分析")
                print("-" * 40)
                print("报告期: {}".format(financial_health['report_date']))
                print("每股收益: {:.2f} 元".format(financial_health['eps'] or 0))
                print("净资产收益率: {:.2f}%".format(financial_health['roe'] or 0))
                print("总资产收益率: {:.2f}%".format(financial_health['roa'] or 0))
                print("资产负债率: {:.2f}%".format(financial_health['debt_ratio'] or 0))
                print("财务健康评分: {}/100".format(financial_health['health_score']))
        
        # 生成投资建议
        investment_advice = self.generate_investment_advice(analysis_result)
        analysis_result['investment_advice'] = investment_advice
        
        print("\n🎯 投资建议")
        print("-" * 40)
        print("投资评级: {}".format(investment_advice['rating']))
        print("建议仓位: {}".format(investment_advice['position']))
        print("核心逻辑: {}".format(investment_advice['logic']))
        
        # 保存真实数据分析结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = "{}_真实数据分析_{}.json".format(
            basic_info['name'] if basic_info else stock_code,
            timestamp
        )
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2, default=str)
        
        print("\n📄 真实数据分析报告已保存: {}".format(filename))
        print("\n🎉 真实数据分析完成！")
        
        return analysis_result
    
    def generate_investment_advice(self, analysis_result):
        """生成投资建议"""
        if not analysis_result:
            return {'rating': '数据不足', 'position': '0%', 'logic': '无法获取充足数据'}
        
        score = 50  # 基础分
        
        # 技术面评分
        if 'technical_indicators' in analysis_result:
            tech = analysis_result['technical_indicators']
            current_price = tech['latest_close']
            
            # 均线排列
            if current_price > tech['ma5'] > tech['ma10'] > tech['ma20']:
                score += 15  # 多头排列
            elif current_price < tech['ma5'] < tech['ma10'] < tech['ma20']:
                score -= 15  # 空头排列
            
            # 波动率
            if tech['volatility_20d'] < 0.03:
                score += 5  # 低波动
            elif tech['volatility_20d'] > 0.08:
                score -= 10  # 高波动
        
        # 基本面评分
        if 'financial_health' in analysis_result:
            financial = analysis_result['financial_health']
            score += (financial['health_score'] - 50) * 0.4
        
        # 生成建议
        if score >= 75:
            rating = '买入'
            position = '3-5%'
            logic = '技术面和基本面均表现良好'
        elif score >= 60:
            rating = '谨慎买入'
            position = '1-3%'
            logic = '整体表现尚可，建议小仓位参与'
        elif score >= 40:
            rating = '观望'
            position = '0-1%'
            logic = '存在一定风险，建议观望'
        else:
            rating = '回避'
            position = '0%'
            logic = '风险较高，建议回避'
        
        return {
            'rating': rating,
            'position': position,
            'logic': logic,
            'score': score
        }

def main():
    """主函数"""
    print("🚀 启动真实数据分析系统")
    print("🔗 连接Tushare真实API")
    print("🚫 严禁使用模拟数据")
    
    analyzer = SimpleRealDataAnalyzer()
    
    # 分析华康洁净
    stock_code = '688015.SH'
    result = analyzer.comprehensive_real_analysis(stock_code)
    
    if result:
        print("\n✅ 真实数据分析成功完成！")
        print("📊 所有数据均来自Tushare实时API")
    else:
        print("\n❌ 真实数据获取失败")

if __name__ == "__main__":
    main()