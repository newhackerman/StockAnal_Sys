# -*- coding: utf-8 -*-
"""
智能分析系统（股票） - 股票市场数据分析系统
开发者：熊猫大侠
版本：v2.1.0
许可证：MIT License
"""
# fundamental_analyzer.py
import akshare as ak
import pandas as pd
import numpy as np


class FundamentalAnalyzer:
    def __init__(self):
        """初始化基础分析类"""
        self.data_cache = {}

    def get_financial_indicators(self, stock_code, market_type='A'):
        """获取财务指标数据"""
        try:
            # 判断市场类型
            if self._is_hk_stock(stock_code) or market_type == 'HK':
                return self._get_hk_financial_indicators(stock_code)
            elif market_type == 'US':
                return self._get_us_financial_indicators(stock_code)
            else:
                return self._get_a_share_financial_indicators(stock_code)
        except Exception as e:
            print(f"获取财务指标出错: {str(e)}")
            return {}
    
    def _is_hk_stock(self, stock_code):
        """判断是否为港股代码"""
        # 港股代码通常是5位数字，前面可能有0
        if isinstance(stock_code, str):
            # 移除可能的前缀0
            clean_code = stock_code.lstrip('0')
            # 港股代码通常是1-5位数字
            return len(stock_code) >= 4 and stock_code.isdigit() and int(clean_code) <= 99999
        return False
    
    def _get_a_share_financial_indicators(self, stock_code):
        """获取A股财务指标"""
        try:
            # 获取基本财务指标
            financial_data = ak.stock_financial_analysis_indicator(symbol=stock_code, start_year="2022")
            
            if financial_data is None or financial_data.empty:
                return {}

            # 获取最新估值指标
            valuation = ak.stock_value_em(symbol=stock_code)
            
            if valuation is None or valuation.empty:
                return {}

            # 整合数据
            indicators = {
                'pe_ttm': float(valuation['PE(TTM)'].iloc[0]) if 'PE(TTM)' in valuation.columns else None,
                'pb': float(valuation['市净率'].iloc[0]) if '市净率' in valuation.columns else None,
                'ps_ttm': float(valuation['市销率'].iloc[0]) if '市销率' in valuation.columns else None,
                'roe': float(financial_data['加权净资产收益率(%)'].iloc[0]) if '加权净资产收益率(%)' in financial_data.columns else None,
                'gross_margin': float(financial_data['销售毛利率(%)'].iloc[0]) if '销售毛利率(%)' in financial_data.columns else None,
                'net_profit_margin': float(financial_data['总资产净利润率(%)'].iloc[0]) if '总资产净利润率(%)' in financial_data.columns else None,
                'debt_ratio': float(financial_data['资产负债率(%)'].iloc[0]) if '资产负债率(%)' in financial_data.columns else None
            }

            # 过滤掉None值
            indicators = {k: v for k, v in indicators.items() if v is not None}
            return indicators
        except Exception as e:
            print(f"获取A股财务指标出错: {str(e)}")
            return {}
    
    def _get_hk_financial_indicators(self, stock_code):
        """获取港股财务指标"""
        try:
            # 尝试使用akshare的港股接口
            # 港股代码需要特殊处理
            hk_code = stock_code.zfill(5)  # 补齐到5位
            
            # 尝试获取港股基本信息
            try:
                # 使用港股实时数据接口获取基本信息
                hk_data = ak.stock_hk_spot_em()
                if hk_data is not None and not hk_data.empty:
                    # 查找对应股票
                    stock_info = hk_data[hk_data['代码'] == hk_code]
                    if not stock_info.empty:
                        indicators = {}
                        # 从实时数据中提取可用的财务指标
                        if '市盈率' in stock_info.columns:
                            pe_value = stock_info['市盈率'].iloc[0]
                            if pd.notna(pe_value) and pe_value != '-':
                                indicators['pe_ttm'] = float(pe_value)
                        
                        if '市净率' in stock_info.columns:
                            pb_value = stock_info['市净率'].iloc[0]
                            if pd.notna(pb_value) and pb_value != '-':
                                indicators['pb'] = float(pb_value)
                        
                        return indicators
            except Exception as e:
                print(f"获取港股实时数据失败: {str(e)}")
            
            # 如果上述方法失败，返回空字典而不是None
            print(f"港股 {stock_code} 财务数据暂不可用")
            return {}
            
        except Exception as e:
            print(f"获取港股财务指标出错: {str(e)}")
            return {}
    
    def _get_us_financial_indicators(self, stock_code):
        """获取美股财务指标"""
        try:
            # 美股财务数据获取逻辑
            # 这里可以添加美股专用的数据获取逻辑
            print(f"美股 {stock_code} 财务数据获取功能待完善")
            return {}
        except Exception as e:
            print(f"获取美股财务指标出错: {str(e)}")
            return {}

    def get_growth_data(self, stock_code):
        """获取成长性数据"""
        try:
            # 获取历年财务数据
            financial_data = ak.stock_financial_abstract(symbol=stock_code)

            # 计算各项成长率
            revenue = financial_data['营业收入'].astype(float)
            net_profit = financial_data['净利润'].astype(float)

            growth = {
                'revenue_growth_3y': self._calculate_cagr(revenue, 3),
                'profit_growth_3y': self._calculate_cagr(net_profit, 3),
                'revenue_growth_5y': self._calculate_cagr(revenue, 5),
                'profit_growth_5y': self._calculate_cagr(net_profit, 5)
            }

            return growth
        except Exception as e:
            print(f"获取成长数据出错: {str(e)}")
            return {}

    def _calculate_cagr(self, series, years):
        """计算复合年增长率"""
        if len(series) < years:
            return None

        latest = series.iloc[0]
        earlier = series.iloc[min(years, len(series) - 1)]

        if earlier <= 0:
            return None

        return ((latest / earlier) ** (1 / years) - 1) * 100

    def calculate_fundamental_score(self, stock_code):
        """计算基本面综合评分"""
        indicators = self.get_financial_indicators(stock_code)
        growth = self.get_growth_data(stock_code)

        # 估值评分 (30分)
        valuation_score = 0
        if 'pe_ttm' in indicators and indicators['pe_ttm'] > 0:
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

        # 财务健康评分 (40分)
        financial_score = 0
        if 'roe' in indicators:
            roe = indicators['roe']
            if roe > 20:
                financial_score += 15
            elif roe > 15:
                financial_score += 12
            elif roe > 10:
                financial_score += 8
            elif roe > 5:
                financial_score += 4

        if 'debt_ratio' in indicators:
            debt_ratio = indicators['debt_ratio']
            if debt_ratio < 30:
                financial_score += 15
            elif debt_ratio < 50:
                financial_score += 10
            elif debt_ratio < 70:
                financial_score += 5

        # 成长性评分 (30分)
        growth_score = 0
        if 'revenue_growth_3y' in growth and growth['revenue_growth_3y']:
            rev_growth = growth['revenue_growth_3y']
            if rev_growth > 30:
                growth_score += 15
            elif rev_growth > 20:
                growth_score += 12
            elif rev_growth > 10:
                growth_score += 8
            elif rev_growth > 0:
                growth_score += 4

        if 'profit_growth_3y' in growth and growth['profit_growth_3y']:
            profit_growth = growth['profit_growth_3y']
            if profit_growth > 30:
                growth_score += 15
            elif profit_growth > 20:
                growth_score += 12
            elif profit_growth > 10:
                growth_score += 8
            elif profit_growth > 0:
                growth_score += 4

        # 计算总分
        total_score = valuation_score + financial_score + growth_score

        return {
            'total': total_score,
            'valuation': valuation_score,
            'financial_health': financial_score,
            'growth': growth_score,
            'details': {
                'indicators': indicators,
                'growth': growth
            }
        }