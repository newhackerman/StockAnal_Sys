# -*- coding: utf-8 -*-
"""
可靠的股票数据获取器
提供多个数据源的备选方案，解决eastmoney.com不稳定的问题
"""

import requests
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
import json
import random

class ReliableDataFetcher:
    """可靠的股票数据获取器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 配置多个数据源（移除不稳定的akshare）
        self.data_sources = {
            'tencent': self._get_data_from_tencent,
            'eastmoney': self._get_data_from_eastmoney,
            'sina': self._get_data_from_sina,
            'yahoo': self._get_data_from_yahoo,
            'netease': self._get_data_from_netease
        }
        
        # 数据源优先级（按可靠性排序，移除akshare）
        self.source_priority = {
            'A': ['tencent', 'netease', 'sina', 'eastmoney'],
            'HK': ['tencent', 'yahoo', 'sina', 'netease'],
            'US': ['yahoo', 'tencent', 'sina']
        }
        
        # 请求头，模拟浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def get_stock_data(self, stock_code, market_type='A', start_date=None, end_date=None, max_retries=3):
        """
        获取股票数据，使用多个数据源作为备选
        
        参数:
            stock_code: 股票代码
            market_type: 市场类型 (A/HK/US)
            start_date: 开始日期
            end_date: 结束日期
            max_retries: 最大重试次数
        
        返回:
            DataFrame: 股票数据
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # 获取该市场类型的数据源优先级
        sources = self.source_priority.get(market_type, ['tencent', 'netease', 'eastmoney'])
        
        for source_name in sources:
            for attempt in range(max_retries):
                try:
                    self.logger.info(f"尝试从 {source_name} 获取 {stock_code} 数据 (第{attempt+1}次)")
                    
                    # 获取数据源函数
                    source_func = self.data_sources.get(source_name)
                    if not source_func:
                        continue
                    
                    # 调用数据源
                    df = source_func(stock_code, market_type, start_date, end_date)
                    
                    if df is not None and not df.empty:
                        self.logger.info(f"✓ 成功从 {source_name} 获取到 {len(df)} 条数据")
                        return self._standardize_dataframe(df)
                    
                except Exception as e:
                    self.logger.warning(f"从 {source_name} 获取数据失败 (第{attempt+1}次): {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(random.uniform(1, 3))  # 随机延迟
                    continue
            
            self.logger.warning(f"从 {source_name} 获取数据失败，尝试下一个数据源")
        
        self.logger.error(f"所有数据源都无法获取 {stock_code} 的数据")
        return pd.DataFrame()
    

    
    def _get_data_from_tencent(self, stock_code, market_type, start_date, end_date):
        """
        从腾讯获取数据
        基于接口说明：https://web.ifzq.gtimg.cn/appstock/app/fqkline/get
        参数格式：param=代码,日k,开始日期,结束日期,获取多少个交易日,前复权
        """
        try:
            # 根据市场类型构建股票代码
            if market_type == 'A':
                # A股：sh600519（上海）或sz000001（深圳）
                if stock_code.startswith('6'):
                    symbol = f"sh{stock_code}"
                else:
                    symbol = f"sz{stock_code}"
            elif market_type == 'HK':
                # 港股：hk01810（需要补齐到5位）
                symbol = f"hk{stock_code.zfill(5)}"
            elif market_type == 'US':
                # 美股：usAAPL.OQ（需要拼接.OQ后缀）
                symbol = f"us{stock_code.upper()}.OQ"
            else:
                return pd.DataFrame()
            
            # 构建请求URL，使用腾讯接口格式
            # param=代码,day,开始日期,结束日期,550,qfq
            url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={symbol},day,{start_date},{end_date},550,qfq'
            
            self.logger.debug(f"腾讯接口URL: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if 'data' not in data or symbol not in data['data']:
                self.logger.warning(f"腾讯接口返回数据中未找到 {symbol}")
                return pd.DataFrame()
            
            # 尝试获取日线数据，优先使用前复权数据
            kline_data = None
            symbol_data = data['data'][symbol]
            
            if 'qfqday' in symbol_data and symbol_data['qfqday']:
                kline_data = symbol_data['qfqday']
                self.logger.debug(f"使用前复权数据，共 {len(kline_data)} 条")
            elif 'day' in symbol_data and symbol_data['day']:
                kline_data = symbol_data['day']
                self.logger.debug(f"使用普通日线数据，共 {len(kline_data)} 条")
            
            if not kline_data:
                self.logger.warning(f"腾讯接口未返回K线数据")
                return pd.DataFrame()
            
            # 转换为DataFrame
            df_data = []
            for item in kline_data:
                try:
                    # 腾讯数据格式：[日期, 开盘, 收盘, 最高, 最低, 成交量]
                    df_data.append({
                        'date': item[0],
                        'open': float(item[1]),
                        'close': float(item[2]),
                        'high': float(item[3]),
                        'low': float(item[4]),
                        'vol': int(float(item[5])) if len(item) > 5 else 0
                    })
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"解析腾讯数据行失败: {item}, 错误: {e}")
                    continue
            
            if not df_data:
                return pd.DataFrame()
            
            df = pd.DataFrame(df_data)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                # 计算涨跌幅
                df['zdf'] = df['close'].pct_change() * 100
                df['zdf'] = df['zdf'].round(2)
                df.fillna(0, inplace=True)
                
                # 按日期排序
                df = df.sort_values('date').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            self.logger.warning(f"腾讯数据获取失败: {str(e)}")
            return pd.DataFrame()
    
    def _get_data_from_eastmoney(self, stock_code, market_type, start_date, end_date):
        """从东方财富获取数据（原有方法的改进版）"""
        try:
            if market_type != 'A':
                return pd.DataFrame()  # 东方财富主要用于A股
            
            # 确定市场代码
            if stock_code.startswith('6'):
                market = 1  # 上海
            else:
                market = 0  # 深圳
            
            url = f'https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={market}.{stock_code}&ut=&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=1&end=20500101&lmt=550&_='
            
            response = requests.get(url, headers=self.headers, timeout=8)
            response.raise_for_status()
            
            json_data = response.json()
            if not json_data.get('data') or not json_data['data'].get('klines'):
                return pd.DataFrame()
            
            klines = json_data['data']['klines']
            df_data = []
            
            for line in klines:
                parts = line.split(',')
                df_data.append({
                    'date': parts[0],
                    'open': float(parts[1]),
                    'close': float(parts[2]),
                    'high': float(parts[3]),
                    'low': float(parts[4]),
                    'vol': int(float(parts[5])),
                    'zdf': float(parts[7])
                })
            
            df = pd.DataFrame(df_data)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
            
            return df
            
        except Exception as e:
            self.logger.warning(f"东方财富数据获取失败: {str(e)}")
            return pd.DataFrame()
    
    def _get_data_from_sina(self, stock_code, market_type, start_date, end_date):
        """从新浪获取数据"""
        try:
            if market_type != 'A':
                return pd.DataFrame()  # 新浪主要用于A股
            
            # 新浪A股接口
            if stock_code.startswith('6'):
                symbol = f"sh{stock_code}"
            else:
                symbol = f"sz{stock_code}"
            
            # 使用新浪的历史数据接口
            url = f'https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={symbol}&scale=240&ma=no&datalen=550'
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 新浪返回的是JSON数组格式
            try:
                data = response.json()
                if not data or not isinstance(data, list):
                    return pd.DataFrame()
                
                df_data = []
                for item in data:
                    if isinstance(item, dict):
                        df_data.append({
                            'date': item.get('day', ''),
                            'open': float(item.get('open', 0)),
                            'close': float(item.get('close', 0)),
                            'high': float(item.get('high', 0)),
                            'low': float(item.get('low', 0)),
                            'vol': int(float(item.get('volume', 0)))
                        })
                
                if df_data:
                    df = pd.DataFrame(df_data)
                    df['date'] = pd.to_datetime(df['date'])
                    # 计算涨跌幅
                    df['zdf'] = df['close'].pct_change() * 100
                    df['zdf'] = df['zdf'].round(2)
                    df.fillna(0, inplace=True)
                    return df
                    
            except (json.JSONDecodeError, ValueError):
                # 如果JSON解析失败，尝试其他方式
                pass
            
            return pd.DataFrame()
            
        except Exception as e:
            self.logger.warning(f"新浪数据获取失败: {str(e)}")
            return pd.DataFrame()
    
    def _get_data_from_yahoo(self, stock_code, market_type, start_date, end_date):
        """从Yahoo Finance获取数据"""
        try:
            if market_type == 'US':
                symbol = stock_code
            elif market_type == 'HK':
                symbol = f"{stock_code.zfill(4)}.HK"
            else:
                return pd.DataFrame()  # Yahoo主要用于美股和港股
            
            # 这里可以使用yfinance库，但为了减少依赖，暂时返回空DataFrame
            # 可以后续添加yfinance支持
            return pd.DataFrame()
            
        except Exception as e:
            self.logger.warning(f"Yahoo数据获取失败: {str(e)}")
            return pd.DataFrame()
    
    def _get_data_from_netease(self, stock_code, market_type, start_date, end_date):
        """从网易财经获取数据"""
        try:
            if market_type == 'A':
                # 网易A股接口
                if stock_code.startswith('6'):
                    symbol = f"0{stock_code}"  # 上海股票
                else:
                    symbol = f"1{stock_code}"  # 深圳股票
                
                # 网易财经历史数据接口
                url = f'https://img1.money.126.net/data/hs/kline/day/history/{symbol}.json'
            else:
                return pd.DataFrame()  # 网易主要用于A股
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data or 'data' not in data:
                return pd.DataFrame()
            
            # 解析网易数据格式
            df_data = []
            for item in data['data']:
                if len(item) >= 6:
                    df_data.append({
                        'date': item[0],
                        'open': float(item[1]),
                        'close': float(item[2]),
                        'high': float(item[3]),
                        'low': float(item[4]),
                        'vol': int(float(item[5]))
                    })
            
            if df_data:
                df = pd.DataFrame(df_data)
                df['date'] = pd.to_datetime(df['date'])
                # 计算涨跌幅
                df['zdf'] = df['close'].pct_change() * 100
                df['zdf'] = df['zdf'].round(2)
                df.fillna(0, inplace=True)
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            self.logger.warning(f"网易数据获取失败: {str(e)}")
            return pd.DataFrame()
    
    def _standardize_dataframe(self, df):
        """标准化DataFrame格式"""
        if df.empty:
            return df
        
        # 确保必要的列存在
        required_columns = ['date', 'open', 'close', 'high', 'low', 'vol']
        
        # 列名映射
        column_mapping = {
            '日期': 'date',
            '开盘': 'open', 
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'vol',
            '涨跌幅': 'zdf'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 确保日期格式
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # 确保数值列的类型
        numeric_columns = ['open', 'close', 'high', 'low', 'vol']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 添加volume列（兼容性）
        if 'vol' in df.columns and 'volume' not in df.columns:
            df['volume'] = df['vol']
        
        # 计算涨跌幅（如果不存在）
        if 'zdf' not in df.columns and 'close' in df.columns:
            df['zdf'] = df['close'].pct_change() * 100
            df['zdf'] = df['zdf'].round(2)
        
        # 删除重复数据并排序
        df = df.drop_duplicates(subset=['date'], keep='last')
        df = df.sort_values('date').reset_index(drop=True)
        
        # 填充NaN值
        df.fillna(0, inplace=True)
        
        return df
    
    def test_data_sources(self, stock_code='000001', market_type='A'):
        """测试各个数据源的可用性"""
        print(f"测试股票 {stock_code} ({market_type}股) 的数据源可用性:")
        print("=" * 60)
        
        sources = self.source_priority.get(market_type, list(self.data_sources.keys()))
        results = {}
        
        for source_name in sources:
            try:
                start_time = time.time()
                source_func = self.data_sources.get(source_name)
                
                if source_func:
                    df = source_func(stock_code, market_type, '2024-01-01', '2024-12-31')
                    end_time = time.time()
                    
                    if df is not None and not df.empty:
                        results[source_name] = {
                            'status': '✓ 可用',
                            'records': len(df),
                            'time': f"{end_time - start_time:.2f}秒"
                        }
                        print(f"{source_name:12} | ✓ 可用 | {len(df):3d} 条记录 | {end_time - start_time:.2f}秒")
                    else:
                        results[source_name] = {
                            'status': '✗ 无数据',
                            'records': 0,
                            'time': f"{end_time - start_time:.2f}秒"
                        }
                        print(f"{source_name:12} | ✗ 无数据 | {end_time - start_time:.2f}秒")
                else:
                    results[source_name] = {
                        'status': '✗ 未实现',
                        'records': 0,
                        'time': '0秒'
                    }
                    print(f"{source_name:12} | ✗ 未实现")
                    
            except Exception as e:
                results[source_name] = {
                    'status': f'✗ 错误: {str(e)[:30]}...',
                    'records': 0,
                    'time': '0秒'
                }
                print(f"{source_name:12} | ✗ 错误: {str(e)[:30]}...")
        
        print("=" * 60)
        return results

# 全局实例
reliable_fetcher = ReliableDataFetcher()

def get_reliable_stock_data(stock_code, market_type='A', start_date=None, end_date=None):
    """
    获取可靠的股票数据（替代原有的get_quote函数）
    
    参数:
        stock_code: 股票代码
        market_type: 市场类型 (A/HK/US)
        start_date: 开始日期
        end_date: 结束日期
    
    返回:
        DataFrame: 股票数据
    """
    return reliable_fetcher.get_stock_data(stock_code, market_type, start_date, end_date)

if __name__ == "__main__":
    # 测试数据源可用性
    fetcher = ReliableDataFetcher()
    
    print("测试A股数据源:")
    fetcher.test_data_sources('000001', 'A')
    
    print("\n测试港股数据源:")
    fetcher.test_data_sources('00700', 'HK')
    
    print("\n测试美股数据源:")
    fetcher.test_data_sources('AAPL', 'US')
    
    # 实际获取数据测试
    print("\n实际数据获取测试:")
    df = get_reliable_stock_data('000001', 'A')
    if not df.empty:
        print(f"成功获取 {len(df)} 条数据")
        print(df.head())
    else:
        print("获取数据失败")