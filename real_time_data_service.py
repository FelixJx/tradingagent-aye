#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time Data Service
集成Tushare和AKShare获取实时金融数据
"""

import os
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

# 数据源导入
try:
    import tushare as ts
    HAS_TUSHARE = True
    print("✅ Tushare successfully imported")
except ImportError:
    HAS_TUSHARE = False
    print("❌ Tushare not available")

try:
    import akshare as ak
    HAS_AKSHARE = True
    print("✅ AKShare successfully imported")
except ImportError:
    HAS_AKSHARE = False
    print("❌ AKShare not available")

class RealTimeDataService:
    """实时数据服务"""
    
    def __init__(self, tushare_token: str = None):
        self.tushare_token = tushare_token or os.getenv('TUSHARE_TOKEN')
        self.ts_api = None
        self.initialize_tushare()
    
    def initialize_tushare(self):
        """初始化Tushare"""
        if HAS_TUSHARE and self.tushare_token:
            try:
                ts.set_token(self.tushare_token)
                self.ts_api = ts.pro_api()
                print(f"✅ Tushare initialized with token: {self.tushare_token[:10]}...")
            except Exception as e:
                print(f"❌ Tushare initialization failed: {e}")
                self.ts_api = None
        else:
            print("⚠️ Tushare token not available")
    
    async def get_real_time_quote(self, symbol: str) -> Dict[str, Any]:
        """获取实时行情数据"""
        quote_data = {}
        
        # 1. 尝试Tushare实时数据
        if self.ts_api:
            try:
                ts_quote = await self._get_tushare_realtime(symbol)
                if ts_quote:
                    quote_data.update(ts_quote)
                    quote_data['data_source'] = 'tushare'
                    print(f"✅ Tushare real-time data for {symbol}")
            except Exception as e:
                print(f"⚠️ Tushare real-time failed: {e}")
        
        # 2. 尝试AKShare作为备用/补充
        if HAS_AKSHARE:
            try:
                ak_quote = await self._get_akshare_realtime(symbol)
                if ak_quote:
                    # 合并数据，Tushare优先
                    for key, value in ak_quote.items():
                        if key not in quote_data:
                            quote_data[key] = value
                    if 'data_source' not in quote_data:
                        quote_data['data_source'] = 'akshare'
                    else:
                        quote_data['data_source'] += '+akshare'
                    print(f"✅ AKShare real-time data for {symbol}")
            except Exception as e:
                print(f"⚠️ AKShare real-time failed: {e}")
        
        # 3. 添加时间戳
        quote_data['timestamp'] = datetime.now().isoformat()
        quote_data['symbol'] = symbol
        
        return quote_data
    
    async def _get_tushare_realtime(self, symbol: str) -> Dict[str, Any]:
        """获取Tushare实时数据"""
        if not self.ts_api:
            return {}
        
        try:
            # 转换股票代码格式（如600036 -> 600036.SH）
            ts_symbol = self._convert_to_tushare_symbol(symbol)
            
            # 获取实时行情
            df = self.ts_api.daily(ts_code=ts_symbol, trade_date=datetime.now().strftime('%Y%m%d'))
            
            if df.empty:
                # 尝试获取最近交易日数据
                end_date = datetime.now()
                for i in range(7):  # 查找最近7天
                    check_date = (end_date - timedelta(days=i)).strftime('%Y%m%d')
                    df = self.ts_api.daily(ts_code=ts_symbol, trade_date=check_date)
                    if not df.empty:
                        break
            
            if not df.empty:
                row = df.iloc[0]
                return {
                    'current_price': float(row['close']),
                    'open_price': float(row['open']),
                    'high_price': float(row['high']),
                    'low_price': float(row['low']),
                    'volume': int(row['vol']) * 100,  # 转换为股
                    'amount': float(row['amount']) * 1000,  # 转换为元
                    'change_pct': float(row['pct_chg']),
                    'trade_date': row['trade_date']
                }
        except Exception as e:
            print(f"Tushare real-time error: {e}")
            return {}
    
    async def _get_akshare_realtime(self, symbol: str) -> Dict[str, Any]:
        """获取AKShare实时数据"""
        if not HAS_AKSHARE:
            return {}
        
        try:
            # 获取实时行情
            stock_zh_a_spot_df = ak.stock_zh_a_spot_em()
            stock_info = stock_zh_a_spot_df[stock_zh_a_spot_df['代码'] == symbol]
            
            if not stock_info.empty:
                info = stock_info.iloc[0]
                return {
                    'current_price': float(info['最新价']),
                    'open_price': float(info['今开']),
                    'high_price': float(info['最高']),
                    'low_price': float(info['最低']),
                    'volume': float(info['成交量']),
                    'amount': float(info['成交额']),
                    'change_pct': float(info['涨跌幅']),
                    'change_amount': float(info['涨跌额']),
                    'pe_ratio': float(info['市盈率-动态']) if info['市盈率-动态'] != '-' else 0,
                    'pb_ratio': float(info['市净率']) if info['市净率'] != '-' else 0,
                    'total_market_cap': float(info.get('总市值', 0)) if info.get('总市值', 0) != '-' else 0,
                    'circulation_market_cap': float(info.get('流通市值', 0)) if info.get('流通市值', 0) != '-' else 0,
                    'turnover_rate': float(info.get('换手率', 0)) if info.get('换手率', 0) != '-' else 0
                }
        except Exception as e:
            print(f"AKShare real-time error: {e}")
            return {}
    
    def _convert_to_tushare_symbol(self, symbol: str) -> str:
        """转换股票代码为Tushare格式"""
        symbol = symbol.upper().replace('.SH', '').replace('.SZ', '')
        
        if symbol.startswith('6'):
            return f"{symbol}.SH"
        elif symbol.startswith(('0', '2', '3')):
            return f"{symbol}.SZ"
        else:
            return f"{symbol}.SH"  # 默认上海
    
    async def get_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """获取历史数据"""
        if self.ts_api:
            return await self._get_tushare_historical(symbol, period)
        elif HAS_AKSHARE:
            return await self._get_akshare_historical(symbol, period)
        else:
            return pd.DataFrame()
    
    async def _get_tushare_historical(self, symbol: str, period: str) -> pd.DataFrame:
        """获取Tushare历史数据"""
        try:
            ts_symbol = self._convert_to_tushare_symbol(symbol)
            
            # 计算日期范围
            end_date = datetime.now()
            if period == "1y":
                start_date = end_date - timedelta(days=365)
            elif period == "6m":
                start_date = end_date - timedelta(days=180)
            elif period == "3m":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=365)
            
            df = self.ts_api.daily(
                ts_code=ts_symbol,
                start_date=start_date.strftime('%Y%m%d'),
                end_date=end_date.strftime('%Y%m%d')
            )
            
            if not df.empty:
                # 重命名列以保持一致性
                df = df.rename(columns={
                    'trade_date': '日期',
                    'open': '开盘',
                    'high': '最高',
                    'low': '最低',
                    'close': '收盘',
                    'vol': '成交量',
                    'amount': '成交额'
                })
                df['日期'] = pd.to_datetime(df['日期'])
                df = df.sort_values('日期')
                df.set_index('日期', inplace=True)
            
            return df
        except Exception as e:
            print(f"Tushare historical error: {e}")
            return pd.DataFrame()
    
    async def _get_akshare_historical(self, symbol: str, period: str) -> pd.DataFrame:
        """获取AKShare历史数据"""
        try:
            end_date = datetime.now()
            if period == "1y":
                start_date = end_date - timedelta(days=365)
            elif period == "6m":
                start_date = end_date - timedelta(days=180)
            elif period == "3m":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=365)
            
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust="qfq"
            )
            
            if not df.empty:
                df['日期'] = pd.to_datetime(df['日期'])
                df.set_index('日期', inplace=True)
            
            return df
        except Exception as e:
            print(f"AKShare historical error: {e}")
            return pd.DataFrame()
    
    async def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """获取公司基本信息"""
        info = {}
        
        if self.ts_api:
            try:
                ts_symbol = self._convert_to_tushare_symbol(symbol)
                # 获取股票基本信息
                basic_info = self.ts_api.stock_basic(ts_code=ts_symbol)
                if not basic_info.empty:
                    row = basic_info.iloc[0]
                    info.update({
                        'symbol': row['ts_code'],
                        'name': row['name'],
                        'area': row.get('area', ''),
                        'industry': row.get('industry', ''),
                        'market': row.get('market', ''),
                        'list_date': row.get('list_date', ''),
                        'data_source': 'tushare'
                    })
            except Exception as e:
                print(f"Tushare company info error: {e}")
        
        return info

# 全局实例
_data_service = None

def get_data_service() -> RealTimeDataService:
    """获取数据服务实例"""
    global _data_service
    if _data_service is None:
        _data_service = RealTimeDataService()
    return _data_service

# 测试函数
async def test_data_service():
    """测试数据服务"""
    service = get_data_service()
    
    # 测试实时数据
    print("=== 测试实时数据 ===")
    quote = await service.get_real_time_quote("600036")
    print(json.dumps(quote, indent=2, ensure_ascii=False, default=str))
    
    # 测试历史数据
    print("\n=== 测试历史数据 ===")
    hist = await service.get_historical_data("600036", "1m")
    print(f"历史数据: {len(hist)} 条记录")
    if not hist.empty:
        print(hist.tail())

if __name__ == "__main__":
    asyncio.run(test_data_service())