#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
华康洁净(301235.SZ)实时数据获取
使用Tushare API获取最新交易数据
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime

class HuakangRealtimeTushare:
    """华康洁净实时数据获取器"""
    
    def __init__(self):
        self.tushare_token = 'b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065'
        self.tushare_base_url = 'http://api.waditu.com'
        self.stock_code = '301235.SZ'
        
    def get_realtime_data(self):
        """获取实时数据"""
        print("🔍 正在获取华康洁净(301235.SZ)实时数据...")
        print("=" * 60)
        
        try:
            # 构建请求数据
            data = {
                'api_name': 'daily',
                'token': self.tushare_token,
                'params': {
                    'ts_code': self.stock_code,
                    'start_date': '20250801',
                    'end_date': '20250804'
                },
                'fields': 'ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount'
            }
            
            # 转换为JSON并编码
            json_data = json.dumps(data).encode('utf-8')
            
            # 创建请求
            req = urllib.request.Request(
                self.tushare_base_url,
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print("📡 连接Tushare API...")
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('code') == 0:
                    items = result.get('data', {}).get('items', [])
                    
                    if items:
                        print("✅ 获取数据成功！")
                        print("\n📊 华康洁净(301235.SZ)最新交易数据：")
                        print("-" * 60)
                        
                        # 显示最新的交易数据
                        for item in items:
                            trade_date = item[1]
                            open_price = item[2]
                            high = item[3]
                            low = item[4]
                            close = item[5]
                            pre_close = item[6]
                            change = item[7]
                            pct_chg = item[8]
                            vol = item[9]
                            amount = item[10]
                            
                            print("\n📅 交易日期: {}".format(trade_date))
                            print("💰 收盘价: {:.2f}元".format(close))
                            print("📊 涨跌幅: {:.2f}%".format(pct_chg))
                            print("📈 涨跌额: {:.2f}元".format(change))
                            print("🔄 开盘价: {:.2f}元".format(open_price))
                            print("📊 最高价: {:.2f}元".format(high))
                            print("📊 最低价: {:.2f}元".format(low))
                            print("📊 前收盘: {:.2f}元".format(pre_close))
                            print("📊 成交量: {:.0f}手".format(vol))
                            print("💰 成交额: {:.2f}万元".format(amount/10))
                            
                        # 分析最新数据
                        latest = items[0]
                        latest_date = latest[1]
                        latest_close = latest[5]
                        latest_pct_chg = latest[8]
                        
                        print("\n" + "=" * 60)
                        print("⚠️ 重要发现：")
                        
                        if latest_pct_chg < -5:
                            print("❌ 股价大幅下跌 {:.2f}%！".format(latest_pct_chg))
                            print("⚠️ 需要立即重新评估投资建议！")
                        elif latest_pct_chg < -3:
                            print("⚠️ 股价显著下跌 {:.2f}%".format(latest_pct_chg))
                            print("📊 可能出现获利回吐或调整")
                        elif latest_pct_chg < 0:
                            print("📊 股价小幅下跌 {:.2f}%".format(latest_pct_chg))
                        else:
                            print("📈 股价上涨 {:.2f}%".format(latest_pct_chg))
                        
                        # 技术分析
                        print("\n📊 技术分析：")
                        print("-" * 30)
                        
                        # 从7月29日27.66元到最新价格的累计涨幅
                        base_price = 27.66
                        total_gain = (latest_close - base_price) / base_price * 100
                        
                        print("📈 自7月29日累计涨幅: {:.2f}%".format(total_gain))
                        
                        if total_gain > 30:
                            print("⚠️ 短期涨幅过大，存在回调风险")
                        
                        # 保存数据
                        analysis_result = {
                            "获取时间": datetime.now().isoformat(),
                            "股票代码": self.stock_code,
                            "最新数据": {
                                "日期": latest_date,
                                "收盘价": latest_close,
                                "涨跌幅": latest_pct_chg,
                                "成交量": latest[9],
                                "成交额": latest[10]
                            },
                            "历史数据": items,
                            "技术分析": {
                                "累计涨幅": total_gain,
                                "风险提示": "短期涨幅过大" if total_gain > 30 else "正常"
                            }
                        }
                        
                        # 保存结果
                        filename = "华康洁净_实时数据_{}.json".format(
                            datetime.now().strftime('%Y%m%d_%H%M%S')
                        )
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
                        
                        print("\n💾 数据已保存至: {}".format(filename))
                        
                        return analysis_result
                        
                    else:
                        print("❌ 未找到交易数据")
                        return None
                        
                else:
                    print("❌ Tushare API错误: {}".format(result.get('msg', 'Unknown error')))
                    return None
                    
        except urllib.error.URLError as e:
            print("❌ 网络连接错误: {}".format(str(e)))
            return None
        except Exception as e:
            print("❌ 发生错误: {}".format(str(e)))
            return None

def main():
    """主函数"""
    print("🚀 启动华康洁净实时数据获取系统")
    print("📊 数据源: Tushare实时API")
    print("🔍 股票代码: 301235.SZ")
    
    fetcher = HuakangRealtimeTushare()
    result = fetcher.get_realtime_data()
    
    if result:
        print("\n✅ 实时数据获取成功！")
    else:
        print("\n❌ 实时数据获取失败")

if __name__ == "__main__":
    main()