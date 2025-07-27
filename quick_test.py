#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试多数据源基本面分析
"""

from fundamental_analyzer import FundamentalAnalyzer

def main():
    print("多数据源基本面分析系统测试")
    print("=" * 40)
    
    analyzer = FundamentalAnalyzer()
    
    # 测试A股
    print("\n测试A股 600519 (茅台)...")
    try:
        result = analyzer.calculate_fundamental_score('600519')
        print(f"A股评分: {result.get('total', 0)}")
        print(f"数据质量: {result.get('data_quality', 'unknown')}")
        print(f"成功: {result.get('success', False)}")
    except Exception as e:
        print(f"A股测试失败: {str(e)}")
    
    # 测试美股
    print("\n测试美股 AAPL (苹果)...")
    try:
        result = analyzer.calculate_fundamental_score('AAPL')
        print(f"美股评分: {result.get('total', 0)}")
        print(f"数据质量: {result.get('data_quality', 'unknown')}")
        print(f"成功: {result.get('success', False)}")
    except Exception as e:
        print(f"美股测试失败: {str(e)}")
    
    # 测试港股
    print("\n测试港股 00700 (腾讯)...")
    try:
        result = analyzer.calculate_fundamental_score('00700')
        print(f"港股评分: {result.get('total', 0)}")
        print(f"数据质量: {result.get('data_quality', 'unknown')}")
        print(f"成功: {result.get('success', False)}")
    except Exception as e:
        print(f"港股测试失败: {str(e)}")
    
    print("\n" + "=" * 40)
    print("多数据源基本面分析系统测试完成！")

if __name__ == "__main__":
    main()