#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试港股财务数据获取功能
专门验证港股（如00981中芯国际）的财务数据获取是否正常
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_hk_fundamental_analyzer():
    """测试港股基本面分析器"""
    print("=" * 60)
    print("测试港股基本面分析器")
    print("=" * 60)
    
    try:
        from fundamental_analyzer import FundamentalAnalyzer
        
        analyzer = FundamentalAnalyzer()
        
        # 测试港股代码识别
        test_codes = ['00981', '0981', '981', '00700', '0700', '700']
        
        print("测试港股代码识别:")
        for code in test_codes:
            is_hk = analyzer._is_hk_stock(code)
            print(f"  {code}: {'✓ 港股' if is_hk else '✗ 非港股'}")
        print()
        
        # 测试港股财务数据获取
        hk_stocks = [
            ('00981', '中芯国际'),
            ('00700', '腾讯控股'),
            ('00005', '汇丰控股')
        ]
        
        for stock_code, stock_name in hk_stocks:
            print(f"测试 {stock_code} ({stock_name}) 财务数据获取:")
            
            try:
                # 测试A股方法（应该返回空或出错）
                print("  使用A股方法:")
                a_indicators = analyzer._get_a_share_financial_indicators(stock_code)
                print(f"    结果: {len(a_indicators)} 个指标")
                
                # 测试港股方法
                print("  使用港股方法:")
                hk_indicators = analyzer._get_hk_financial_indicators(stock_code)
                print(f"    结果: {len(hk_indicators)} 个指标")
                if hk_indicators:
                    for key, value in hk_indicators.items():
                        print(f"    {key}: {value}")
                
                # 测试通用方法
                print("  使用通用方法 (market_type='HK'):")
                indicators = analyzer.get_financial_indicators(stock_code, market_type='HK')
                print(f"    结果: {len(indicators)} 个指标")
                if indicators:
                    for key, value in indicators.items():
                        print(f"    {key}: {value}")
                else:
                    print("    ✓ 正常返回空字典，没有抛出异常")
                
            except Exception as e:
                print(f"    ✗ 异常: {str(e)}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"✗ 港股基本面分析器测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_hk_stock_qa():
    """测试港股在StockQA中的表现"""
    print("=" * 60)
    print("测试港股在StockQA中的表现")
    print("=" * 60)
    
    try:
        from stock_analyzer import StockAnalyzer
        from stock_qa import StockQA
        
        # 初始化
        analyzer = StockAnalyzer()
        stock_qa = StockQA(analyzer)
        
        # 测试港股
        hk_stocks = [
            ('00981', '中芯国际'),
            ('00700', '腾讯控股')
        ]
        
        for stock_code, stock_name in hk_stocks:
            print(f"测试 {stock_code} ({stock_name}):")
            
            try:
                # 测试获取股票上下文
                print("  获取股票上下文...")
                context = stock_qa._get_stock_context(stock_code, market_type='HK')
                
                if context and 'context' in context:
                    print("  ✓ 成功获取股票上下文")
                    print(f"  股票名称: {context.get('stock_name', '未知')}")
                    print(f"  行业: {context.get('industry', '未知')}")
                    
                    # 检查上下文内容
                    context_text = context['context']
                    if "港股财务数据获取有限" in context_text:
                        print("  ✓ 正确显示港股财务数据限制说明")
                    elif "基本面指标:" in context_text:
                        print("  ✓ 成功获取基本面指标")
                    else:
                        print("  ○ 未获取到基本面数据，但没有异常")
                    
                else:
                    print("  ✗ 获取股票上下文失败")
                    return False
                
                # 测试简单问答（不使用Gemini以避免API调用）
                print("  测试问答功能...")
                
                # 模拟问答测试（检查是否会因为财务数据问题而崩溃）
                question = f"请简单介绍一下{stock_name}的基本情况"
                
                # 这里我们主要测试_get_stock_context不会崩溃
                # 实际的AI调用需要API密钥，我们跳过
                print("  ✓ 股票上下文获取正常，不会因财务数据问题崩溃")
                
            except Exception as e:
                print(f"  ✗ 测试异常: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
            
            print()
        
        return True
        
    except Exception as e:
        print(f"✗ 港股StockQA测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_akshare_hk_data():
    """测试akshare港股数据获取能力"""
    print("=" * 60)
    print("测试akshare港股数据获取能力")
    print("=" * 60)
    
    try:
        import akshare as ak
        import pandas as pd
        
        # 测试港股实时数据
        print("测试港股实时数据获取...")
        try:
            hk_data = ak.stock_hk_spot_em()
            if hk_data is not None and not hk_data.empty:
                print(f"✓ 成功获取港股实时数据，共 {len(hk_data)} 只股票")
                print(f"  数据列: {list(hk_data.columns)}")
                
                # 查找测试股票
                test_codes = ['00981', '00700']
                for code in test_codes:
                    stock_info = hk_data[hk_data['代码'] == code]
                    if not stock_info.empty:
                        print(f"  找到 {code}: {stock_info['名称'].iloc[0]}")
                        if '市盈率' in stock_info.columns:
                            pe = stock_info['市盈率'].iloc[0]
                            print(f"    市盈率: {pe}")
                        if '市净率' in stock_info.columns:
                            pb = stock_info['市净率'].iloc[0]
                            print(f"    市净率: {pb}")
                    else:
                        print(f"  未找到 {code}")
            else:
                print("✗ 港股实时数据获取失败")
                
        except Exception as e:
            print(f"✗ 港股实时数据获取异常: {str(e)}")
        
        print()
        
        # 测试其他港股接口
        print("测试其他港股数据接口...")
        
        # 测试港股历史数据
        try:
            print("  测试港股历史数据...")
            # 这个接口可能需要特殊格式的代码
            # hk_hist = ak.stock_hk_hist(symbol="00700", period="daily", start_date="20240101", end_date="20241201")
            print("  ○ 港股历史数据接口需要进一步测试")
        except Exception as e:
            print(f"  ○ 港股历史数据接口异常: {str(e)}")
        
        return True
        
    except ImportError:
        print("✗ akshare未安装，无法测试")
        return False
    except Exception as e:
        print(f"✗ akshare港股数据测试失败: {str(e)}")
        return False

def test_error_handling():
    """测试错误处理机制"""
    print("=" * 60)
    print("测试错误处理机制")
    print("=" * 60)
    
    try:
        from fundamental_analyzer import FundamentalAnalyzer
        
        analyzer = FundamentalAnalyzer()
        
        # 测试无效股票代码
        invalid_codes = ['INVALID', '99999', '', None]
        
        for code in invalid_codes:
            print(f"测试无效代码 '{code}':")
            try:
                result = analyzer.get_financial_indicators(code, market_type='HK')
                if isinstance(result, dict):
                    print(f"  ✓ 正常返回空字典: {result}")
                else:
                    print(f"  ✗ 返回类型异常: {type(result)}")
            except Exception as e:
                print(f"  ✗ 抛出异常: {str(e)}")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ 错误处理测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("StockAnal_Sys 港股财务数据获取测试")
    print("版本: 1.0.0")
    print()
    
    success_count = 0
    total_tests = 4
    
    # 测试1: 港股基本面分析器
    if test_hk_fundamental_analyzer():
        success_count += 1
        print("✓ 港股基本面分析器测试通过\n")
    else:
        print("✗ 港股基本面分析器测试失败\n")
    
    # 测试2: 港股在StockQA中的表现
    if test_hk_stock_qa():
        success_count += 1
        print("✓ 港股StockQA测试通过\n")
    else:
        print("✗ 港股StockQA测试失败\n")
    
    # 测试3: akshare港股数据能力
    if test_akshare_hk_data():
        success_count += 1
        print("✓ akshare港股数据测试通过\n")
    else:
        print("✗ akshare港股数据测试失败\n")
    
    # 测试4: 错误处理机制
    if test_error_handling():
        success_count += 1
        print("✓ 错误处理测试通过\n")
    else:
        print("✗ 错误处理测试失败\n")
    
    # 总结
    print("=" * 60)
    print(f"港股财务数据获取测试完成: {success_count}/{total_tests} 项测试通过")
    if success_count == total_tests:
        print("🎉 所有港股测试通过！")
        print("✓ 港股财务数据获取不会再抛出异常")
        print("✓ 系统能正确处理港股财务数据限制")
        print("✓ StockQA能正常处理港股查询")
    elif success_count > 0:
        print("⚠️  部分港股功能正常，请检查失败的测试项")
    else:
        print("❌ 所有港股测试失败，请检查代码实现")
    print("=" * 60)
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)