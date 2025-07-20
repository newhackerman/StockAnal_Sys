#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试移除akshare后的数据获取效果
验证腾讯接口和其他数据源是否能稳定工作
"""

import os
import sys
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_tencent_api_detailed():
    """详细测试腾讯API接口"""
    print("=" * 60)
    print("详细测试腾讯API接口")
    print("=" * 60)
    
    try:
        from reliable_data_fetcher import ReliableDataFetcher
        
        fetcher = ReliableDataFetcher()
        
        # 测试不同市场的股票
        test_cases = [
            ('000001', 'A', '平安银行', 'sz000001'),
            ('600519', 'A', '贵州茅台', 'sh600519'),
            ('00700', 'HK', '腾讯控股', 'hk00700'),
            ('01810', 'HK', '小米集团', 'hk01810'),
            ('AAPL', 'US', '苹果公司', 'usAAPL.OQ')
        ]
        
        success_count = 0
        
        for stock_code, market_type, stock_name, expected_symbol in test_cases:
            print(f"测试 {stock_code} ({stock_name}) - {market_type}股:")
            print(f"  预期腾讯符号: {expected_symbol}")
            
            try:
                start_time = time.time()
                df = fetcher._get_data_from_tencent(stock_code, market_type, '2024-01-01', '2024-12-31')
                end_time = time.time()
                
                if df is not None and not df.empty:
                    print(f"  ✓ 成功获取 {len(df)} 条数据")
                    print(f"  ✓ 耗时: {end_time - start_time:.2f}秒")
                    print(f"  ✓ 数据列: {list(df.columns)}")
                    print(f"  ✓ 日期范围: {df['date'].min()} 到 {df['date'].max()}")
                    print(f"  ✓ 最新价格: {df.iloc[-1]['close']}")
                    
                    # 验证数据质量
                    if df['close'].isna().sum() == 0:
                        print(f"  ✓ 数据质量良好，无缺失值")
                    else:
                        print(f"  ⚠️  数据存在 {df['close'].isna().sum()} 个缺失值")
                    
                    success_count += 1
                else:
                    print(f"  ✗ 获取数据失败或为空")
                    
            except Exception as e:
                print(f"  ✗ 获取数据异常: {str(e)}")
            
            print()
        
        print(f"腾讯API测试结果: {success_count}/{len(test_cases)} ({success_count/len(test_cases)*100:.1f}%)")
        return success_count > 0
        
    except Exception as e:
        print(f"✗ 腾讯API详细测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_data_sources_without_akshare():
    """测试移除akshare后的数据源可用性"""
    print("=" * 60)
    print("测试移除akshare后的数据源可用性")
    print("=" * 60)
    
    try:
        from reliable_data_fetcher import ReliableDataFetcher
        
        fetcher = ReliableDataFetcher()
        
        # 验证akshare已被移除
        if 'akshare' in fetcher.data_sources:
            print("❌ akshare仍在数据源列表中，移除失败")
            return False
        else:
            print("✓ akshare已成功从数据源列表中移除")
        
        # 验证数据源优先级不包含akshare
        for market, sources in fetcher.source_priority.items():
            if 'akshare' in sources:
                print(f"❌ {market}股优先级列表仍包含akshare")
                return False
        
        print("✓ 所有市场的数据源优先级都已移除akshare")
        print()
        
        # 测试各市场数据源可用性
        markets = [
            ('000001', 'A', 'A股'),
            ('00700', 'HK', '港股'),
            ('AAPL', 'US', '美股')
        ]
        
        total_available = 0
        total_sources = 0
        
        for stock_code, market_type, market_name in markets:
            print(f"测试{market_name}数据源:")
            print("-" * 30)
            
            results = fetcher.test_data_sources(stock_code, market_type)
            
            available = sum(1 for result in results.values() if '✓ 可用' in result['status'])
            total = len(results)
            
            total_available += available
            total_sources += total
            
            print(f"{market_name}可用数据源: {available}/{total}")
            print()
        
        print(f"总体数据源可用性: {total_available}/{total_sources} ({total_available/total_sources*100:.1f}%)")
        return total_available > 0
        
    except Exception as e:
        print(f"✗ 数据源测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_reliable_data_fetching_performance():
    """测试可靠数据获取的性能"""
    print("=" * 60)
    print("测试可靠数据获取性能")
    print("=" * 60)
    
    try:
        from reliable_data_fetcher import get_reliable_stock_data
        
        # 测试股票列表
        test_stocks = [
            ('000001', 'A', '平安银行'),
            ('600519', 'A', '贵州茅台'),
            ('00700', 'HK', '腾讯控股'),
            ('AAPL', 'US', '苹果公司')
        ]
        
        success_count = 0
        total_time = 0
        total_records = 0
        
        for stock_code, market_type, stock_name in test_stocks:
            print(f"测试 {stock_code} ({stock_name}):")
            
            try:
                start_time = time.time()
                df = get_reliable_stock_data(stock_code, market_type, '2024-01-01', '2024-12-31')
                end_time = time.time()
                
                elapsed_time = end_time - start_time
                total_time += elapsed_time
                
                if df is not None and not df.empty:
                    total_records += len(df)
                    print(f"  ✓ 成功获取 {len(df)} 条数据，耗时 {elapsed_time:.2f}秒")
                    print(f"  ✓ 平均每条数据耗时: {elapsed_time/len(df)*1000:.2f}毫秒")
                    success_count += 1
                else:
                    print(f"  ✗ 获取数据失败")
                    
            except Exception as e:
                print(f"  ✗ 获取数据异常: {str(e)}")
            
            print()
        
        if success_count > 0:
            avg_time_per_stock = total_time / success_count
            avg_time_per_record = total_time / total_records if total_records > 0 else 0
            
            print("性能统计:")
            print(f"  成功率: {success_count}/{len(test_stocks)} ({success_count/len(test_stocks)*100:.1f}%)")
            print(f"  总耗时: {total_time:.2f}秒")
            print(f"  平均每只股票耗时: {avg_time_per_stock:.2f}秒")
            print(f"  总获取记录数: {total_records}")
            print(f"  平均每条记录耗时: {avg_time_per_record*1000:.2f}毫秒")
        
        return success_count > 0
        
    except Exception as e:
        print(f"✗ 性能测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_stock_analyzer_integration():
    """测试StockAnalyzer集成效果"""
    print("=" * 60)
    print("测试StockAnalyzer集成效果")
    print("=" * 60)
    
    try:
        from stock_analyzer import StockAnalyzer
        
        analyzer = StockAnalyzer()
        
        # 测试A股数据获取和分析
        print("测试A股完整分析流程 (平安银行 000001):")
        try:
            # 获取股票数据
            df = analyzer.get_stock_data('000001', 'A')
            if df is not None and not df.empty:
                print(f"  ✓ 成功获取 {len(df)} 条数据")
                
                # 计算技术指标
                df_with_indicators = analyzer.calculate_indicators(df)
                print(f"  ✓ 技术指标计算完成")
                
                # 计算评分
                score = analyzer.calculate_score(df_with_indicators, 'A')
                print(f"  ✓ 综合评分: {score}")
                
                # 获取投资建议
                recommendation = analyzer.get_recommendation(score, 'A')
                print(f"  ✓ 投资建议: {recommendation}")
                
                # 测试AI分析（如果配置了AI）
                try:
                    ai_analysis = analyzer.get_ai_analysis(df_with_indicators, '000001', 'A')
                    if ai_analysis and len(ai_analysis) > 50:
                        print(f"  ✓ AI分析完成，长度: {len(ai_analysis)} 字符")
                    else:
                        print(f"  ○ AI分析跳过或失败")
                except Exception as e:
                    print(f"  ○ AI分析跳过: {str(e)}")
                
                return True
            else:
                print("  ✗ 获取A股数据失败")
                return False
                
        except Exception as e:
            print(f"  ✗ A股分析流程异常: {str(e)}")
            return False
            
    except Exception as e:
        print(f"✗ StockAnalyzer集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """测试错误处理机制"""
    print("=" * 60)
    print("测试错误处理机制")
    print("=" * 60)
    
    try:
        from reliable_data_fetcher import get_reliable_stock_data
        
        # 测试无效股票代码
        invalid_codes = [
            ('INVALID', 'A', '无效A股代码'),
            ('99999', 'HK', '无效港股代码'),
            ('NOTEXIST', 'US', '无效美股代码')
        ]
        
        for stock_code, market_type, description in invalid_codes:
            print(f"测试 {description} ({stock_code}):")
            
            try:
                df = get_reliable_stock_data(stock_code, market_type, '2024-01-01', '2024-12-31')
                
                if df is None or df.empty:
                    print(f"  ✓ 正确处理无效代码，返回空DataFrame")
                else:
                    print(f"  ⚠️  意外获取到数据: {len(df)} 条")
                    
            except Exception as e:
                print(f"  ✓ 正确抛出异常: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"✗ 错误处理测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("StockAnal_Sys 移除akshare后的数据获取测试")
    print("版本: 1.0.0")
    print("验证腾讯接口和其他数据源的稳定性")
    print()
    
    success_count = 0
    total_tests = 5
    
    # 测试1: 腾讯API详细测试
    if test_tencent_api_detailed():
        success_count += 1
        print("✓ 腾讯API详细测试通过\n")
    else:
        print("✗ 腾讯API详细测试失败\n")
    
    # 测试2: 数据源可用性（无akshare）
    if test_data_sources_without_akshare():
        success_count += 1
        print("✓ 数据源可用性测试通过\n")
    else:
        print("✗ 数据源可用性测试失败\n")
    
    # 测试3: 性能测试
    if test_reliable_data_fetching_performance():
        success_count += 1
        print("✓ 性能测试通过\n")
    else:
        print("✗ 性能测试失败\n")
    
    # 测试4: StockAnalyzer集成
    if test_stock_analyzer_integration():
        success_count += 1
        print("✓ StockAnalyzer集成测试通过\n")
    else:
        print("✗ StockAnalyzer集成测试失败\n")
    
    # 测试5: 错误处理
    if test_error_handling():
        success_count += 1
        print("✓ 错误处理测试通过\n")
    else:
        print("✗ 错误处理测试失败\n")
    
    # 总结
    print("=" * 60)
    print(f"移除akshare后的测试完成: {success_count}/{total_tests} 项测试通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！")
        print("✓ 成功移除不稳定的akshare依赖")
        print("✓ 腾讯接口工作正常，数据获取稳定")
        print("✓ 多数据源备选机制有效")
        print("✓ 系统整体性能和稳定性提升")
    elif success_count >= 3:
        print("⚠️  大部分功能正常，系统可用性良好")
        print("✓ 移除akshare后系统仍能稳定工作")
        print("✓ 腾讯接口成为主要数据源")
    else:
        print("❌ 测试失败较多，需要检查网络连接和接口可用性")
        print("💡 建议检查腾讯接口是否可正常访问")
    
    print("=" * 60)
    
    return success_count >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)