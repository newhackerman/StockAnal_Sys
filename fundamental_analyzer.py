# -*- coding: utf-8 -*-
"""
智能分析系统（股票） - 多数据源基本面分析系统
开发者：熊猫大侠
版本：v2.2.0 - 多数据源财务分析
许可证：MIT License
"""

import akshare as ak
import pandas as pd
import numpy as np
import requests
import json
import time
import warnings
warnings.filterwarnings('ignore')

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("yfinance未安装，美股和港股功能将受限")

class FundamentalAnalyzer:
    def __init__(self, config=None):
        """初始化基础分析类"""
        self.data_cache = {}
        
        # 默认配置
        self.data_sources = {
            'A': ['akshare', 'eastmoney'],
            'HK': ['yfinance', 'akshare'] if YFINANCE_AVAILABLE else ['akshare'],
            'US': ['yfinance'] if YFINANCE_AVAILABLE else []
        }
        
        self.api_config = {
            'eastmoney_base': 'http://push2.eastmoney.com/api/qt/stock/get',
            'timeout': 10
        }
    
    def get_financial_indicators(self, stock_code, market_type='A'):
        """获取财务指标数据"""
        try:
            detected_market = self._detect_market_type(stock_code, market_type)
            print(f"股票 {stock_code} 检测到市场类型: {detected_market}")
            
            if detected_market == 'HK':
                return self._get_hk_financial_indicators(stock_code)
            elif detected_market == 'US':
                return self._get_us_financial_indicators(stock_code)
            else:
                return self._get_a_share_financial_indicators(stock_code)
        except Exception as e:
            print(f"获取财务指标出错: {str(e)}")
            return self._get_default_indicators_structure(f'获取财务指标出错: {str(e)}')
    
    def get_growth_data(self, stock_code, market_type='A'):
        """获取成长性数据"""
        try:
            detected_market = self._detect_market_type(stock_code, market_type)
            
            if detected_market == 'HK':
                return self._get_hk_growth_data(stock_code)
            elif detected_market == 'US':
                return self._get_us_growth_data(stock_code)
            else:
                return self._get_a_share_growth_data(stock_code)
        except Exception as e:
            print(f"获取成长数据出错: {str(e)}")
            return {
                'revenue_growth_3y': None,
                'profit_growth_3y': None,
                'revenue_growth_5y': None,
                'profit_growth_5y': None,
                'data_available': False,
                'error': str(e)
            }
    
    def calculate_fundamental_score(self, stock_code):
        """计算基本面综合评分"""
        try:
            market_type = self._detect_market_type(stock_code, 'A')
            
            indicators = self.get_financial_indicators(stock_code, market_type)
            growth = self.get_growth_data(stock_code, market_type)
            
            if not isinstance(indicators, dict):
                indicators = {}
            if not isinstance(growth, dict):
                growth = {}

            is_hk_stock = self._is_hk_stock(stock_code)
            is_us_stock = market_type == 'US'
            
            # 估值评分 (30分)
            valuation_score = 0
            if indicators.get('pe_ttm') is not None and indicators['pe_ttm'] > 0:
                pe = indicators['pe_ttm']
                if pe < 15:
                    valuation_score += 25
                elif pe < 25:
                    valuation_score += 20
                elif pe < 35:
                    valuation_score += 15
                elif pe < 50:
                    valuation_score += 10
                else:
                    valuation_score += 5

            if indicators.get('pb') is not None and indicators['pb'] > 0:
                pb = indicators['pb']
                if pb < 1:
                    valuation_score += 5
                elif pb < 2:
                    valuation_score += 3
                else:
                    valuation_score += 1

            # 财务健康评分 (40分)
            financial_score = 0
            
            if indicators.get('roe') is not None:
                roe = indicators['roe']
                if roe > 20:
                    financial_score += 15
                elif roe > 15:
                    financial_score += 12
                elif roe > 10:
                    financial_score += 8
                elif roe > 5:
                    financial_score += 4

            if indicators.get('debt_ratio') is not None:
                debt_ratio = indicators['debt_ratio']
                if debt_ratio < 30:
                    financial_score += 15
                elif debt_ratio < 50:
                    financial_score += 10
                elif debt_ratio < 70:
                    financial_score += 5

            # 成长性评分 (30分)
            growth_score = 0
            if growth.get('data_available', False):
                if growth.get('revenue_growth_3y') is not None:
                    rev_growth = growth['revenue_growth_3y']
                    if rev_growth > 30:
                        growth_score += 15
                    elif rev_growth > 20:
                        growth_score += 12
                    elif rev_growth > 10:
                        growth_score += 8
                    elif rev_growth > 0:
                        growth_score += 4

                if growth.get('profit_growth_3y') is not None:
                    profit_growth = growth['profit_growth_3y']
                    if profit_growth > 30:
                        growth_score += 15
                    elif profit_growth > 20:
                        growth_score += 12
                    elif profit_growth > 10:
                        growth_score += 8
                    elif profit_growth > 0:
                        growth_score += 4

            total_score = valuation_score + financial_score + growth_score

            # 数据质量评估
            data_quality = 'high'
            if is_hk_stock or is_us_stock or not growth.get('data_available', True):
                data_quality = 'limited'
            elif not indicators.get('data_available', True):
                data_quality = 'low'

            return {
                'success': True,
                'total': total_score,
                'valuation': valuation_score,
                'financial_health': financial_score,
                'growth': growth_score,
                'data_quality': data_quality,
                'is_hk_stock': is_hk_stock,
                'is_us_stock': is_us_stock,
                'raw_data': {
                    'indicators': indicators,
                    'growth': growth
                }
            }
            
        except Exception as e:
            print(f"计算基本面评分出错: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'total': 0,
                'valuation': 0,
                'financial_health': 0,
                'growth': 0,
                'data_quality': 'error',
                'message': f'评分计算失败: {str(e)}'
            }
    
    def _detect_market_type(self, stock_code, provided_market_type):
        """智能检测股票市场类型"""
        if provided_market_type in ['HK', 'US']:
            return provided_market_type
        
        if isinstance(stock_code, str):
            if self._is_hk_stock(stock_code):
                return 'HK'
            
            if any(c.isalpha() for c in stock_code):
                return 'US'
            
            if stock_code.isdigit() and len(stock_code) == 6:
                return 'A'
        
        return 'A'
    
    def _is_hk_stock(self, stock_code):
        """判断是否为港股代码"""
        if isinstance(stock_code, str) and stock_code.isdigit():
            if len(stock_code) == 6:
                return False  # A股
            
            if len(stock_code) >= 4 and len(stock_code) <= 5:
                clean_code = stock_code.lstrip('0')
                if clean_code and int(clean_code) <= 99999:
                    return True
        return False
    
    def _get_a_share_financial_indicators(self, stock_code):
        """获取A股财务指标"""
        cache_key = f"a_indicators_{stock_code}"
        if cache_key in self.data_cache:
            cache_time, cached_data = self.data_cache[cache_key]
            if time.time() - cache_time < 600:
                return cached_data
        
        indicators = {}
        
        # 方法1: akshare财务指标
        try:
            print(f"获取A股 {stock_code} 财务指标...")
            financial_data = ak.stock_financial_analysis_indicator(symbol=stock_code, start_year="2022")
            if financial_data is not None and not financial_data.empty:
                latest_data = financial_data.iloc[0]
                
                # ROE
                roe_columns = ['加权净资产收益率(%)', 'ROE(%)', '净资产收益率(%)']
                for col in roe_columns:
                    if col in financial_data.columns and pd.notna(latest_data[col]):
                        try:
                            indicators['roe'] = float(latest_data[col])
                            break
                        except (ValueError, TypeError):
                            continue
                
                # 毛利率
                margin_columns = ['销售毛利率(%)', '毛利率(%)']
                for col in margin_columns:
                    if col in financial_data.columns and pd.notna(latest_data[col]):
                        try:
                            indicators['gross_margin'] = float(latest_data[col])
                            break
                        except (ValueError, TypeError):
                            continue
                
                # 净利润率
                net_margin_columns = ['总资产净利润率(%)', '净利润率(%)']
                for col in net_margin_columns:
                    if col in financial_data.columns and pd.notna(latest_data[col]):
                        try:
                            indicators['net_profit_margin'] = float(latest_data[col])
                            break
                        except (ValueError, TypeError):
                            continue
                
                # 资产负债率
                debt_columns = ['资产负债率(%)', '负债率(%)']
                for col in debt_columns:
                    if col in financial_data.columns and pd.notna(latest_data[col]):
                        try:
                            indicators['debt_ratio'] = float(latest_data[col])
                            break
                        except (ValueError, TypeError):
                            continue
        except Exception as e:
            print(f"akshare财务指标获取失败: {str(e)}")
        
        # 方法2: akshare估值数据
        try:
            valuation = ak.stock_value_em(symbol=stock_code)
            if valuation is not None and not valuation.empty:
                val_data = valuation.iloc[0]
                
                # PE
                pe_columns = ['PE(TTM)', 'PE', '市盈率']
                for col in pe_columns:
                    if col in valuation.columns and pd.notna(val_data[col]):
                        try:
                            pe_val = val_data[col]
                            if pe_val != '-' and str(pe_val) != 'nan':
                                indicators['pe_ttm'] = float(pe_val)
                                break
                        except (ValueError, TypeError):
                            continue
                
                # PB
                pb_columns = ['市净率', 'PB']
                for col in pb_columns:
                    if col in valuation.columns and pd.notna(val_data[col]):
                        try:
                            pb_val = val_data[col]
                            if pb_val != '-' and str(pb_val) != 'nan':
                                indicators['pb'] = float(pb_val)
                                break
                        except (ValueError, TypeError):
                            continue
                
                # PS
                ps_columns = ['市销率', 'PS']
                for col in ps_columns:
                    if col in valuation.columns and pd.notna(val_data[col]):
                        try:
                            ps_val = val_data[col]
                            if ps_val != '-' and str(ps_val) != 'nan':
                                indicators['ps_ttm'] = float(ps_val)
                                break
                        except (ValueError, TypeError):
                            continue
        except Exception as e:
            print(f"akshare估值数据获取失败: {str(e)}")
        
        if indicators:
            indicators['data_available'] = True
            indicators['data_source'] = 'akshare'
        else:
            indicators = self._get_default_indicators_structure('A股财务数据获取失败')
        
        self.data_cache[cache_key] = (time.time(), indicators)
        return indicators
    
    def _get_hk_financial_indicators(self, stock_code):
        """获取港股财务指标"""
        if not YFINANCE_AVAILABLE:
            return self._get_default_indicators_structure('yfinance未安装，港股功能不可用')
        
        cache_key = f"hk_indicators_{stock_code}"
        if cache_key in self.data_cache:
            cache_time, cached_data = self.data_cache[cache_key]
            if time.time() - cache_time < 300:
                return cached_data
        
        try:
            hk_code = stock_code.zfill(5)
            yahoo_symbol = f"{hk_code}.HK"
            
            stock = yf.Ticker(yahoo_symbol)
            info = stock.info
            
            if info and len(info) > 5:
                indicators = {}
                
                if 'trailingPE' in info and info['trailingPE']:
                    indicators['pe_ttm'] = float(info['trailingPE'])
                
                if 'priceToBook' in info and info['priceToBook']:
                    indicators['pb'] = float(info['priceToBook'])
                
                if 'priceToSalesTrailing12Months' in info and info['priceToSalesTrailing12Months']:
                    indicators['ps_ttm'] = float(info['priceToSalesTrailing12Months'])
                
                if 'marketCap' in info and info['marketCap']:
                    indicators['market_cap'] = float(info['marketCap'])
                
                if 'returnOnEquity' in info and info['returnOnEquity']:
                    indicators['roe'] = float(info['returnOnEquity']) * 100
                
                if 'grossMargins' in info and info['grossMargins']:
                    indicators['gross_margin'] = float(info['grossMargins']) * 100
                
                if 'profitMargins' in info and info['profitMargins']:
                    indicators['net_profit_margin'] = float(info['profitMargins']) * 100
                
                if 'debtToEquity' in info and info['debtToEquity']:
                    debt_to_equity = float(info['debtToEquity'])
                    indicators['debt_ratio'] = (debt_to_equity / (1 + debt_to_equity)) * 100
                
                if indicators:
                    indicators['data_available'] = True
                    indicators['data_source'] = 'yfinance'
                    self.data_cache[cache_key] = (time.time(), indicators)
                    return indicators
        except Exception as e:
            print(f"港股数据获取失败: {str(e)}")
        
        result = self._get_default_indicators_structure('港股财务数据获取失败')
        self.data_cache[cache_key] = (time.time(), result)
        return result
    
    def _get_us_financial_indicators(self, stock_code):
        """获取美股财务指标"""
        if not YFINANCE_AVAILABLE:
            return self._get_default_indicators_structure('yfinance未安装，美股功能不可用')
        
        cache_key = f"us_indicators_{stock_code}"
        if cache_key in self.data_cache:
            cache_time, cached_data = self.data_cache[cache_key]
            if time.time() - cache_time < 600:
                return cached_data
        
        try:
            stock = yf.Ticker(stock_code)
            info = stock.info
            
            if info and len(info) > 5:
                indicators = {}
                
                if 'trailingPE' in info and info['trailingPE']:
                    indicators['pe_ttm'] = float(info['trailingPE'])
                
                if 'priceToBook' in info and info['priceToBook']:
                    indicators['pb'] = float(info['priceToBook'])
                
                if 'priceToSalesTrailing12Months' in info and info['priceToSalesTrailing12Months']:
                    indicators['ps_ttm'] = float(info['priceToSalesTrailing12Months'])
                
                if 'returnOnEquity' in info and info['returnOnEquity']:
                    indicators['roe'] = float(info['returnOnEquity']) * 100
                
                if 'grossMargins' in info and info['grossMargins']:
                    indicators['gross_margin'] = float(info['grossMargins']) * 100
                
                if 'profitMargins' in info and info['profitMargins']:
                    indicators['net_profit_margin'] = float(info['profitMargins']) * 100
                
                if 'debtToEquity' in info and info['debtToEquity']:
                    debt_to_equity = float(info['debtToEquity'])
                    indicators['debt_ratio'] = (debt_to_equity / (1 + debt_to_equity)) * 100
                
                if 'marketCap' in info and info['marketCap']:
                    indicators['market_cap'] = float(info['marketCap'])
                
                if indicators:
                    indicators['data_available'] = True
                    indicators['data_source'] = 'yfinance'
                    self.data_cache[cache_key] = (time.time(), indicators)
                    return indicators
        except Exception as e:
            print(f"美股数据获取失败: {str(e)}")
        
        result = self._get_default_indicators_structure('美股财务数据获取失败')
        self.data_cache[cache_key] = (time.time(), result)
        return result
    
    def _get_a_share_growth_data(self, stock_code):
        """获取A股成长数据"""
        cache_key = f"a_growth_{stock_code}"
        if cache_key in self.data_cache:
            cache_time, cached_data = self.data_cache[cache_key]
            if time.time() - cache_time < 900:
                return cached_data
        
        try:
            financial_data = ak.stock_financial_abstract(symbol=stock_code)
            
            if financial_data is not None and not financial_data.empty:
                growth_data = {}
                
                # 处理新的数据结构
                if '指标' in financial_data.columns:
                    financial_data = financial_data.set_index('指标')
                    
                    # 查找营业收入
                    revenue_indicators = ['营业收入', '营业总收入', '主营业务收入']
                    for indicator in revenue_indicators:
                        if indicator in financial_data.index:
                            revenue_row = financial_data.loc[indicator]
                            year_columns = [col for col in revenue_row.index if col.endswith('1231')]
                            if year_columns:
                                year_columns.sort(reverse=True)
                                revenue_values = []
                                for col in year_columns:
                                    try:
                                        val = pd.to_numeric(revenue_row[col], errors='coerce')
                                        if pd.notna(val):
                                            revenue_values.append(val)
                                    except:
                                        continue
                                
                                if len(revenue_values) >= 3:
                                    revenue_data = pd.Series(revenue_values)
                                    growth_data['revenue_growth_3y'] = self._calculate_cagr(revenue_data, 3)
                                    if len(revenue_values) >= 5:
                                        growth_data['revenue_growth_5y'] = self._calculate_cagr(revenue_data, 5)
                                    break
                    
                    # 查找净利润
                    profit_indicators = ['净利润', '归属于母公司所有者的净利润', '归母净利润']
                    for indicator in profit_indicators:
                        if indicator in financial_data.index:
                            profit_row = financial_data.loc[indicator]
                            year_columns = [col for col in profit_row.index if col.endswith('1231')]
                            if year_columns:
                                year_columns.sort(reverse=True)
                                profit_values = []
                                for col in year_columns:
                                    try:
                                        val = pd.to_numeric(profit_row[col], errors='coerce')
                                        if pd.notna(val):
                                            profit_values.append(val)
                                    except:
                                        continue
                                
                                if len(profit_values) >= 3:
                                    profit_data = pd.Series(profit_values)
                                    growth_data['profit_growth_3y'] = self._calculate_cagr(profit_data, 3)
                                    if len(profit_values) >= 5:
                                        growth_data['profit_growth_5y'] = self._calculate_cagr(profit_data, 5)
                                    break
                
                if growth_data:
                    growth_data['data_available'] = True
                    growth_data['data_source'] = 'akshare'
                    self.data_cache[cache_key] = (time.time(), growth_data)
                    return growth_data
        except Exception as e:
            print(f"A股成长数据获取失败: {str(e)}")
        
        result = {
            'revenue_growth_3y': None,
            'profit_growth_3y': None,
            'revenue_growth_5y': None,
            'profit_growth_5y': None,
            'data_available': False,
            'message': 'A股成长性数据获取失败'
        }
        self.data_cache[cache_key] = (time.time(), result)
        return result
    
    def _get_hk_growth_data(self, stock_code):
        """获取港股成长数据"""
        if not YFINANCE_AVAILABLE:
            return {
                'revenue_growth_3y': None,
                'profit_growth_3y': None,
                'revenue_growth_5y': None,
                'profit_growth_5y': None,
                'data_available': False,
                'message': 'yfinance未安装，港股成长数据不可用'
            }
        
        cache_key = f"hk_growth_{stock_code}"
        if cache_key in self.data_cache:
            cache_time, cached_data = self.data_cache[cache_key]
            if time.time() - cache_time < 900:
                return cached_data
        
        try:
            hk_code = stock_code.zfill(5)
            yahoo_symbol = f"{hk_code}.HK"
            
            stock = yf.Ticker(yahoo_symbol)
            financials = stock.financials
            
            if financials is not None and not financials.empty:
                growth_data = {}
                
                # 获取营业收入数据
                revenue_keys = ['Total Revenue', 'Revenue', 'Net Sales']
                for key in revenue_keys:
                    if key in financials.index:
                        revenue_data = financials.loc[key].dropna()
                        if len(revenue_data) >= 3:
                            growth_data['revenue_growth_3y'] = self._calculate_cagr(revenue_data, 3)
                            if len(revenue_data) >= 5:
                                growth_data['revenue_growth_5y'] = self._calculate_cagr(revenue_data, 5)
                            break
                
                # 获取净利润数据
                profit_keys = ['Net Income', 'Net Income Common Stockholders']
                for key in profit_keys:
                    if key in financials.index:
                        profit_data = financials.loc[key].dropna()
                        if len(profit_data) >= 3:
                            growth_data['profit_growth_3y'] = self._calculate_cagr(profit_data, 3)
                            if len(profit_data) >= 5:
                                growth_data['profit_growth_5y'] = self._calculate_cagr(profit_data, 5)
                            break
                
                if growth_data:
                    growth_data['data_available'] = True
                    growth_data['data_source'] = 'yfinance'
                    self.data_cache[cache_key] = (time.time(), growth_data)
                    return growth_data
        except Exception as e:
            print(f"港股成长数据获取失败: {str(e)}")
        
        result = {
            'revenue_growth_3y': None,
            'profit_growth_3y': None,
            'revenue_growth_5y': None,
            'profit_growth_5y': None,
            'data_available': False,
            'message': '港股成长性数据获取失败'
        }
        self.data_cache[cache_key] = (time.time(), result)
        return result
    
    def _get_us_growth_data(self, stock_code):
        """获取美股成长数据"""
        if not YFINANCE_AVAILABLE:
            return {
                'revenue_growth_3y': None,
                'profit_growth_3y': None,
                'revenue_growth_5y': None,
                'profit_growth_5y': None,
                'data_available': False,
                'message': 'yfinance未安装，美股成长数据不可用'
            }
        
        cache_key = f"us_growth_{stock_code}"
        if cache_key in self.data_cache:
            cache_time, cached_data = self.data_cache[cache_key]
            if time.time() - cache_time < 900:
                return cached_data
        
        try:
            stock = yf.Ticker(stock_code)
            financials = stock.financials
            
            if financials is not None and not financials.empty:
                growth_data = {}
                
                # 获取营业收入数据
                revenue_keys = ['Total Revenue', 'Revenue', 'Net Sales']
                for key in revenue_keys:
                    if key in financials.index:
                        revenue_data = financials.loc[key].dropna()
                        if len(revenue_data) >= 3:
                            growth_data['revenue_growth_3y'] = self._calculate_cagr(revenue_data, 3)
                            if len(revenue_data) >= 5:
                                growth_data['revenue_growth_5y'] = self._calculate_cagr(revenue_data, 5)
                            break
                
                # 获取净利润数据
                profit_keys = ['Net Income', 'Net Income Common Stockholders']
                for key in profit_keys:
                    if key in financials.index:
                        profit_data = financials.loc[key].dropna()
                        if len(profit_data) >= 3:
                            growth_data['profit_growth_3y'] = self._calculate_cagr(profit_data, 3)
                            if len(profit_data) >= 5:
                                growth_data['profit_growth_5y'] = self._calculate_cagr(profit_data, 5)
                            break
                
                if growth_data:
                    growth_data['data_available'] = True
                    growth_data['data_source'] = 'yfinance'
                    self.data_cache[cache_key] = (time.time(), growth_data)
                    return growth_data
        except Exception as e:
            print(f"美股成长数据获取失败: {str(e)}")
        
        result = {
            'revenue_growth_3y': None,
            'profit_growth_3y': None,
            'revenue_growth_5y': None,
            'profit_growth_5y': None,
            'data_available': False,
            'message': '美股成长性数据获取失败'
        }
        self.data_cache[cache_key] = (time.time(), result)
        return result
    
    def _calculate_cagr(self, series, years):
        """计算复合年增长率"""
        if len(series) < years:
            return None

        latest = series.iloc[0]
        earlier = series.iloc[min(years, len(series) - 1)]

        if earlier <= 0:
            return None

        return ((latest / earlier) ** (1 / years) - 1) * 100
    
    def _get_default_indicators_structure(self, message):
        """获取默认的指标结构"""
        return {
            'pe_ttm': None,
            'pb': None,
            'ps_ttm': None,
            'roe': None,
            'gross_margin': None,
            'net_profit_margin': None,
            'debt_ratio': None,
            'market_cap': None,
            'data_available': False,
            'message': message
        }