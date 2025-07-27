# -*- coding: utf-8 -*-
"""
测试优化后的get_codename.py功能
"""

import sys
import time
from get_codename import get_codename, get_stock_count, search_stocks, reload_static_data

def test_existing_stocks():
    """测试现有股票查询"""
    print("=== 测试现有股票查询 ===")
    
    test_cases = [
        ('长电科技', 'code'),
        ('00981', 'name'),
        ('AAPL', 'name'),
        ('000001', 'name')
    ]
    
    for stock, return_type in test_cases:
        result = get_codename(stock, return_type)
        print(f"{stock} -> {return_type}: {result}")

def test_real_time_query():
    """测试实时查询功能"""
    print("\n=== 测试实时查询功能 ===")
    
    # 测试一些可能不在静态数据中的股票
    test_cases = [
        ('比亚迪', 'code'),
        ('腾讯控股', 'code'),
        ('00700', 'name'),
        ('TSLA', 'name'),
        ('MSFT', 'name'),
        ('300750', 'name'),  # 宁德时代
    ]
    
    for stock, return_type in test_cases:
        print(f"查询 {stock} ({return_type})...")
        start_time = time.time()
        result = get_codename(stock, return_type)
        end_time = time.time()
        print(f"结果: {result} (耗时: {end_time - start_time:.2f}秒)")
        time.sleep(1)  # 避免请求过于频繁

def test_fuzzy_search():
    """测试模糊搜索功能"""
    print("\n=== 测试模糊搜索功能 ===")
    
    keywords = ['科技', '银行', '00', 'A']
    
    for keyword in keywords:
        print(f"\n搜索关键词: '{keyword}'")
        results = search_stocks(keyword, 5)
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['code']} - {result['name']}")

def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    error_cases = [
        None,
        '',
        '不存在的股票名称',
        'NONEXISTENT',
        '999999'
    ]
    
    for case in error_cases:
        result = get_codename(case)
        print(f"'{case}' -> {result}")

def main():
    """主测试函数"""
    print("开始测试优化后的get_codename.py功能")
    print(f"当前股票数量: {get_stock_count()}")
    
    # 运行各项测试
    test_existing_stocks()
    test_real_time_query()
    test_fuzzy_search()
    test_error_handling()
    
    print(f"\n测试完成！最终股票数量: {get_stock_count()}")
    
    # 重新加载数据测试
    print("\n=== 测试数据重新加载 ===")
    reload_static_data()
    print(f"重新加载后股票数量: {get_stock_count()}")

if __name__ == '__main__':
    main()