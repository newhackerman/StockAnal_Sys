#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多数据源基本面分析功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fundamental_analyzer import FundamentalAnalyzer

def test_data_sources():
    """测试各个数据源的可用性"""
    print("=" * 60)
    print("测试数据源可用性")
    print("=" * 60)
    
    analyzer = FundamentalAnalyzer()
    
    # 测试A股数据源
    print("\n测试A股数据源:")
    a_stock = "600519"  # 茅台
    
    for source in analyzer.data_sources['A']:
        try:
            print(f"  测试 {source}...")
            if source == 'akshare':
                result = analyzer._get_a_share_from_akshare(a_stock)
            elif source == 'eastmoney':
                result = analyzer._get_a_share_from_eastmoney(a_stock)
            elif source == 'sina':
                result = analyzer._get_a_share_from_sina(a_stock)
            
            if result and result.get('data_available'):
                print(f"    ✓ {source} 可用，获取到 {len([k for k, v in result.items() if v is not None and k != 'data_available'])} 个指标")
            else:
                print(f"    ✗ {source} 不可用")
        except Exception as e:
            print(f"    ✗ {source} 错误: {str(e)}")
    
    # 测试港股数据源
    print("\n测试港股数据源:")
    hk_stock = "00700"  # 腾讯
    
    for source in analyzer.data_sources['HK']:
        try:
            print(f"  测试 {source}...")
            if source == 'yfinance':
                result = analyzer._get_hk_from_yfinance(hk_stock)
            elif source == 'akshare':
                result = analyzer._get_hk_from_akshare(hk_stock)
            elif source == 'yahoo':
                result = analyzer._get_hk_from_yahoo(hk_stock)
            
            if result and result.get('data_available'):
                print(f"    ✓ {source} 可用，获取到 {len([k for k, v in result.items() if v is not None and k != 'data_available'])} 个指标")
            else:
                print(f"    ✗ {source} 不可用")
        except Exception as e:
            print(f"    ✗ {source} 错误: {str(e)}")
    
    # 测试美股数据源
    print("\n测试美股数据源:")
    us_stock = "AAPL"  # 苹果
    
    for source in analyzer.data_sources['US']:
        try:
            print(f"  测试 {source}...")
            if source == 'yfinance':
                result = analyzer._get_us_from_yfinance(us_stock)
            elif source == 'yahoo':
                result = analyzer._get_us_from_yahoo(us_stock)
            elif source == 'alpha_vantage':
                result = analyzer._get_us_from_alpha_vantage(us_stock)
            
            if result and result.get('data_available'):
                print(f"    ✓ {source} 可用，获取到 {len([k for k, v in result.items() if v is not None and k != 'data_available'])} 个指标")
            else:
                print(f"    ✗ {source} 不可用")
        except Exception as e:
            print(f"    ✗ {source} 错误: {str(e)}")

def test_comprehensive_analysis():
    """测试综合分析功能"""
    print("\n" + "=" * 60)
    print("测试综合分析功能")
    print("=" * 60)
    
    analyzer = FundamentalAnalyzer()
    
    test_stocks = [
        ('600519', 'A', 'A股茅台'),
        ('000001', 'A', 'A股平安银行'),
        ('00700', 'HK', '港股腾讯'),
        ('00981', 'HK', '港股中芯国际'),
        ('AAPL', 'US', '美股苹果'),
        ('TSLA', 'US', '美股特斯拉')
    ]
    
    for stock_code, market, description in test_stocks:
        print(f"\n测试 {description} ({stock_code}):")
        print("-" * 40)
        
        try:
            # 测试财务指标获取
            print("1. 财务指标:")
            indicators = analyzer.get_financial_indicators(stock_code, market)
            print(f"   数据源: {indicators.get('data_source', 'unknown')}")
            print(f"   数据可用: {indicators.get('data_available', False)}")
            
            available_indicators = [k for k, v in indicators.items() 
                                  if v is not None and k not in ['data_available', 'data_source', 'message', 'error']]
            print(f"   可用指标: {len(available_indicators)} 个")
            
            if indicators.get('pe_ttm'):
                print(f"   PE(TTM): {indicators['pe_ttm']:.2f}")
            if indicators.get('pb'):
                print(f"   PB: {indicators['pb']:.2f}")
            if indicators.get('roe'):
                print(f"   ROE: {indicators['roe']:.2f}%")
            
            # 测试成长数据获取
            print("2. 成长数据:")
            growth = analyzer.get_growth_data(stock_code, market)
            print(f"   数据源: {growth.get('data_source', 'unknown')}")
            print(f"   数据可用: {growth.get('data_available', False)}")
            
            if growth.get('revenue_growth_3y'):
                print(f"   营收3年增长: {growth['revenue_growth_3y']:.2f}%")
            if growth.get('profit_growth_3y'):
                print(f"   利润3年增长: {growth['profit_growth_3y']:.2f}%")
            
            # 测试综合评分
            print("3. 综合评分:")
            score = analyzer.calculate_fundamental_score(stock_code)
            print(f"   总分: {score.get('total', 0)}")
            print(f"   数据质量: {score.get('data_quality', 'unknown')}")
            print(f"   成功: {score.get('success', False)}")
            
        except Exception as e:
            print(f"   测试失败: {str(e)}")

def test_performance():
    """测试性能和缓存"""
    print("\n" + "=" * 60)
    print("测试性能和缓存")
    print("=" * 60)
    
    analyzer = FundamentalAnalyzer()
    
    import time
    
    # 测试缓存效果
    stock_code = "AAPL"
    
    print(f"首次获取 {stock_code} 数据...")
    start_time = time.time()
    result1 = analyzer.get_financial_indicators(stock_code, 'US')
    first_time = time.time() - start_time
    print(f"首次获取耗时: {first_time:.2f}秒")
    
    print(f"再次获取 {stock_code} 数据（应该使用缓存）...")
    start_time = time.time()
    result2 = analyzer.get_financial_indicators(stock_code, 'US')
    second_time = time.time() - start_time
    print(f"缓存获取耗时: {second_time:.2f}秒")
    
    print(f"缓存加速比: {first_time/second_time:.1f}x")
    print(f"缓存命中: {'是' if second_time < 0.1 else '否'}")

if __name__ == "__main__":
    print("多数据源基本面分析测试")
    print("=" * 60)
    
    # 测试数据源可用性
    test_data_sources()
    
    # 测试综合分析功能
    test_comprehensive_analysis()
    
    # 测试性能和缓存
    test_performance()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)