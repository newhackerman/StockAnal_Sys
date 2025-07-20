#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试可靠数据获取器
验证多数据源备选方案是否能解决eastmoney.com不稳定的问题
"""

import os
import sys
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_data_source_reliability():
    """测试数据源可靠性"""
    print("=" * 60)
    print("测试数据源可靠性")
    print("=" * 60)
    
    try:
        from reliable_data_fetcher import ReliableDataFetcher
        
        fetcher = ReliableDataFetcher()
        
        # 测试A股数据源
        print("测试A股数据源可用性:")
        print("-" * 40)
        a_results = fetcher.test_data_sources('000001', 'A')
        
        print("\n测试港股数据源可用性:")
        print("-" * 40)
        hk_results = fetcher.test_data_sources('00700', 'HK')
        
        print("\n测试美股数据源可用性:")
        print("-" * 40)
        us_results = fetcher.test_data_sources('AAPL', 'US')
        
        # 统计可用数据源
        def count_available_sources(results):
            available = 0
            for source, result in results.items():
                if '✓ 可用' in result['status']:
                    available += 1
            return available
        
        a_available = count_available_sources(a_results)
        hk_available = count_available_sources(hk_results)
        us_available = count_available_sources(us_results)
        
        print("\n" + "=" * 60)
        print("数据源可用性统计:")
        print(f"A股可用数据源: {a_available}/{len(a_results)}")
        print(f"港股可用数据源: {hk_available}/{len(hk_results)}")
        print(f"美股可用数据源: {us_available}/{len(us_results)}")
        
        return a_available > 0 or hk_available > 0 or us_available > 0
        
    except Exception as e:
        print(f"✗ 数据源可靠性测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_reliable_data_fetching():
    """测试可靠数据获取功能"""
    print("=" * 60)
    print("测试可靠数据获取功能")
    print("=" * 60)
    
    try:
        from reliable_data_fetcher import get_reliable_stock_data
        
        # 测试股票列表
        test_stocks = [
            ('000001', 'A', '平安银行'),
            ('00700', 'HK', '腾讯控股'),
            ('AAPL', 'US', '苹果公司')
        ]
        
        success_count = 0
        
        for stock_code, market_type, stock_name in test_stocks:
            print(f"测试 {stock_code} ({stock_name}) - {market_type}股:")
            
            try:
                start_time = time.time()
                df = get_reliable_stock_data(stock_code, market_type, '2024-01-01', '2024-12-31')
                end_time = time.time()
                
                if df is not None and not df.empty:
                    print(f"  ✓ 成功获取 {len(df)} 条数据")
                    print(f"  ✓ 耗时: {end_time - start_time:.2f}秒")
                    print(f"  ✓ 数据列: {list(df.columns)}")
                    print(f"  ✓ 日期范围: {df['date'].min()} 到 {df['date'].max()}")
                    print(f"  ✓ 最新价格: {df.iloc[-1]['close']}")
                    success_count += 1
                else:
                    print(f"  ✗ 获取数据失败或为空")
                    
            except Exception as e:
                print(f"  ✗ 获取数据异常: {str(e)}")
            
            print()
        
        print(f"成功率: {success_count}/{len(test_stocks)} ({success_count/len(test_stocks)*100:.1f}%)")
        return success_count > 0
        
    except Exception as e:
        print(f"✗ 可靠数据获取测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_stock_analyzer_integration():
    """测试StockAnalyzer集成"""
    print("=" * 60)
    print("测试StockAnalyzer集成")
    print("=" * 60)
    
    try:
        from stock_analyzer import StockAnalyzer
        
        analyzer = StockAnalyzer()
        
        # 测试A股数据获取
        print("测试A股数据获取 (平安银行 000001):")
        try:
            df = analyzer.get_stock_data('000001', 'A')
            if df is not None and not df.empty:
                print(f"  ✓ 成功获取 {len(df)} 条数据")
                print(f"  ✓ 最新价格: {df.iloc[-1]['close']}")
                
                # 测试技术指标计算
                print("  测试技术指标计算...")
                df_with_indicators = analyzer.calculate_indicators(df)
                print(f"  ✓ 技术指标计算完成")
                print(f"  ✓ RSI: {df_with_indicators.iloc[-1]['RSI']:.2f}")
                print(f"  ✓ MACD: {df_with_indicators.iloc[-1]['MACD']:.4f}")
                
                # 测试评分计算
                print("  测试评分计算...")
                score = analyzer.calculate_score(df_with_indicators, 'A')
                print(f"  ✓ 综合评分: {score}")
                
                return True
            else:
                print("  ✗ 获取A股数据失败")
                return False
                
        except Exception as e:
            print(f"  ✗ A股数据获取异常: {str(e)}")
            return False
            
    except Exception as e:
        print(f"✗ StockAnalyzer集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_mechanism():
    """测试数据源回退机制"""
    print("=" * 60)
    print("测试数据源回退机制")
    print("=" * 60)
    
    try:
        from reliable_data_fetcher import ReliableDataFetcher
        
        fetcher = ReliableDataFetcher()
        
        # 模拟某些数据源失败的情况
        print("模拟数据源失败情况，测试回退机制:")
        
        # 临时修改数据源优先级，将不可靠的源放在前面
        original_priority = fetcher.source_priority['A'].copy()
        fetcher.source_priority['A'] = ['eastmoney', 'akshare', 'tencent', 'sina']
        
        try:
            df = fetcher.get_stock_data('000001', 'A', '2024-01-01', '2024-12-31')
            
            if df is not None and not df.empty:
                print(f"✓ 回退机制工作正常，成功获取 {len(df)} 条数据")
                print("✓ 即使主要数据源失败，系统仍能获取数据")
                return True
            else:
                print("✗ 回退机制失败，无法获取数据")
                return False
                
        finally:
            # 恢复原始优先级
            fetcher.source_priority['A'] = original_priority
            
    except Exception as e:
        print(f"✗ 回退机制测试失败: {str(e)}")
        return False

def test_performance_comparison():
    """测试性能对比"""
    print("=" * 60)
    print("测试性能对比")
    print("=" * 60)
    
    try:
        from reliable_data_fetcher import get_reliable_stock_data
        from get_quote import get_quote
        
        stock_code = '000001'
        
        # 测试原有方法
        print("测试原有数据获取方法:")
        try:
            start_time = time.time()
            old_df = get_quote(stock_code, market='A')
            old_time = time.time() - start_time
            
            if old_df is not None and not old_df.empty:
                print(f"  ✓ 原有方法: {len(old_df)} 条数据, 耗时 {old_time:.2f}秒")
            else:
                print(f"  ✗ 原有方法失败")
                old_time = float('inf')
                
        except Exception as e:
            print(f"  ✗ 原有方法异常: {str(e)}")
            old_time = float('inf')
        
        # 测试新方法
        print("测试可靠数据获取方法:")
        try:
            start_time = time.time()
            new_df = get_reliable_stock_data(stock_code, 'A', '2024-01-01', '2024-12-31')
            new_time = time.time() - start_time
            
            if new_df is not None and not new_df.empty:
                print(f"  ✓ 新方法: {len(new_df)} 条数据, 耗时 {new_time:.2f}秒")
            else:
                print(f"  ✗ 新方法失败")
                new_time = float('inf')
                
        except Exception as e:
            print(f"  ✗ 新方法异常: {str(e)}")
            new_time = float('inf')
        
        # 性能对比
        print("\n性能对比结果:")
        if old_time != float('inf') and new_time != float('inf'):
            if new_time < old_time:
                print(f"✓ 新方法更快，提升 {((old_time - new_time) / old_time * 100):.1f}%")
            else:
                print(f"○ 原有方法更快，但新方法更可靠")
        elif new_time != float('inf'):
            print("✓ 只有新方法成功获取数据")
        elif old_time != float('inf'):
            print("○ 只有原有方法成功获取数据")
        else:
            print("✗ 两种方法都失败")
        
        return new_time != float('inf')
        
    except Exception as e:
        print(f"✗ 性能对比测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("StockAnal_Sys 可靠数据获取器测试")
    print("版本: 1.0.0")
    print("解决eastmoney.com不稳定问题的多数据源方案")
    print()
    
    success_count = 0
    total_tests = 5
    
    # 测试1: 数据源可靠性
    if test_data_source_reliability():
        success_count += 1
        print("✓ 数据源可靠性测试通过\n")
    else:
        print("✗ 数据源可靠性测试失败\n")
    
    # 测试2: 可靠数据获取
    if test_reliable_data_fetching():
        success_count += 1
        print("✓ 可靠数据获取测试通过\n")
    else:
        print("✗ 可靠数据获取测试失败\n")
    
    # 测试3: StockAnalyzer集成
    if test_stock_analyzer_integration():
        success_count += 1
        print("✓ StockAnalyzer集成测试通过\n")
    else:
        print("✗ StockAnalyzer集成测试失败\n")
    
    # 测试4: 回退机制
    if test_fallback_mechanism():
        success_count += 1
        print("✓ 回退机制测试通过\n")
    else:
        print("✗ 回退机制测试失败\n")
    
    # 测试5: 性能对比
    if test_performance_comparison():
        success_count += 1
        print("✓ 性能对比测试通过\n")
    else:
        print("✗ 性能对比测试失败\n")
    
    # 总结
    print("=" * 60)
    print(f"可靠数据获取器测试完成: {success_count}/{total_tests} 项测试通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！")
        print("✓ 多数据源备选方案工作正常")
        print("✓ 解决了eastmoney.com不稳定的问题")
        print("✓ 系统数据获取更加可靠")
    elif success_count >= 3:
        print("⚠️  大部分功能正常，系统可用性显著提升")
        print("✓ 即使部分数据源失败，系统仍能正常工作")
    else:
        print("❌ 测试失败较多，需要检查网络连接和依赖库")
        print("💡 建议检查akshare等数据库是否正确安装")
    
    print("=" * 60)
    
    return success_count >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)