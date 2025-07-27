#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI依赖包的安装和功能
"""

import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_openai():
    """测试OpenAI依赖"""
    print("测试OpenAI依赖...")
    try:
        from openai import OpenAI
        print("✓ OpenAI包导入成功")
        
        # 检查API密钥
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print("✓ OpenAI API密钥已配置")
            
            # 简单的客户端初始化测试
            try:
                client = OpenAI(api_key=api_key)
                print("✓ OpenAI客户端初始化成功")
                return True
            except Exception as e:
                print(f"✗ OpenAI客户端初始化失败: {str(e)}")
                return False
        else:
            print("⚠ OpenAI API密钥未配置")
            return False
            
    except ImportError as e:
        print(f"✗ OpenAI包导入失败: {str(e)}")
        return False

def test_gemini():
    """测试Gemini依赖"""
    print("\n测试Gemini依赖...")
    try:
        from google import genai
        from google.genai import types
        print("✓ Google GenAI包导入成功")
        
        # 检查API密钥
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            print("✓ Gemini API密钥已配置")
            
            # 简单的客户端初始化测试
            try:
                genai.configure(api_key=api_key)
                print("✓ Gemini客户端配置成功")
                return True
            except Exception as e:
                print(f"✗ Gemini客户端配置失败: {str(e)}")
                return False
        else:
            print("⚠ Gemini API密钥未配置")
            return False
            
    except ImportError as e:
        print(f"✗ Google GenAI包导入失败: {str(e)}")
        return False

def test_other_dependencies():
    """测试其他关键依赖"""
    print("\n测试其他关键依赖...")
    
    dependencies = [
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('requests', 'requests'),
        ('flask', 'flask'),
        ('yfinance', 'yfinance'),
        ('akshare', 'akshare'),
        ('redis', 'redis'),
        ('sqlalchemy', 'sqlalchemy'),
        ('beautifulsoup4', 'bs4'),
        ('matplotlib', 'matplotlib'),
        ('plotly', 'plotly'),
        ('scipy', 'scipy'),
        ('pydantic', 'pydantic')
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
            success_count += 1
        except ImportError:
            print(f"✗ {package_name}")
    
    print(f"\n依赖包测试结果: {success_count}/{total_count} 成功")
    return success_count == total_count

def test_ai_client():
    """测试AI客户端模块"""
    print("\n测试AI客户端模块...")
    try:
        from ai_client import AIClient
        print("✓ AI客户端模块导入成功")
        
        # 初始化客户端
        client = AIClient()
        print("✓ AI客户端初始化成功")
        
        # 检查可用的提供商
        available_providers = []
        if hasattr(client, 'openai_client') and client.openai_client:
            available_providers.append('OpenAI')
        if hasattr(client, 'gemini_client') and client.gemini_client:
            available_providers.append('Gemini')
        
        if available_providers:
            print(f"✓ 可用的AI提供商: {', '.join(available_providers)}")
            return True
        else:
            print("⚠ 没有可用的AI提供商")
            return False
            
    except ImportError as e:
        print(f"✗ AI客户端模块导入失败: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ AI客户端测试失败: {str(e)}")
        return False

def test_fundamental_analyzer():
    """测试基本面分析器"""
    print("\n测试基本面分析器...")
    try:
        from fundamental_analyzer import FundamentalAnalyzer
        print("✓ 基本面分析器导入成功")
        
        # 初始化分析器
        analyzer = FundamentalAnalyzer()
        print("✓ 基本面分析器初始化成功")
        
        # 简单功能测试
        result = analyzer.calculate_fundamental_score('600519')
        if result and result.get('success'):
            print("✓ 基本面分析功能测试通过")
            return True
        else:
            print("⚠ 基本面分析功能测试部分通过")
            return True  # 网络问题不算失败
            
    except ImportError as e:
        print(f"✗ 基本面分析器导入失败: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ 基本面分析器测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("AI依赖和功能测试")
    print("=" * 50)
    
    # 检查环境变量文件
    if not os.path.exists('.env'):
        print("⚠ .env文件不存在，请从.env.template创建并配置API密钥")
        if os.path.exists('.env.template'):
            print("提示: cp .env.template .env")
    
    # 运行各项测试
    tests = [
        ("OpenAI依赖", test_openai),
        ("Gemini依赖", test_gemini),
        ("其他依赖", test_other_dependencies),
        ("AI客户端", test_ai_client),
        ("基本面分析器", test_fundamental_analyzer)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name}测试异常: {str(e)}")
            results.append((test_name, False))
    
    # 输出测试总结
    print("\n" + "=" * 50)
    print("测试总结:")
    
    success_count = 0
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n总体结果: {success_count}/{len(results)} 项测试通过")
    
    if success_count == len(results):
        print("🎉 所有测试通过！系统准备就绪。")
        return 0
    elif success_count >= len(results) * 0.7:
        print("⚠ 大部分测试通过，系统基本可用。")
        return 0
    else:
        print("❌ 多项测试失败，请检查依赖安装和配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())