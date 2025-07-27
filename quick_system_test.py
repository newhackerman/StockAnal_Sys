#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速系统测试脚本
"""

import sys
import os
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_basic_imports():
    """测试基本导入"""
    print("1. 测试基本导入...")
    try:
        import pandas as pd
        import numpy as np
        import requests
        print("   ✓ 核心库导入成功")
        return True
    except ImportError as e:
        print(f"   ✗ 核心库导入失败: {e}")
        return False

def test_ai_imports():
    """测试AI库导入"""
    print("2. 测试AI库导入...")
    success = True
    
    try:
        import openai
        print("   ✓ OpenAI库导入成功")
    except ImportError:
        print("   ✗ OpenAI库导入失败")
        success = False
    
    try:
        from google import genai
        print("   ✓ Google GenAI库导入成功")
    except ImportError:
        print("   ✗ Google GenAI库导入失败")
        success = False
    
    return success

def test_stock_data_sources():
    """测试股票数据源"""
    print("3. 测试股票数据源...")
    success = True
    
    try:
        import akshare as ak
        print("   ✓ AKShare导入成功")
    except ImportError:
        print("   ✗ AKShare导入失败")
        success = False
    
    try:
        import yfinance as yf
        print("   ✓ YFinance导入成功")
    except ImportError:
        print("   ✗ YFinance导入失败")
        success = False
    
    return success

def test_fundamental_analyzer():
    """测试基本面分析器"""
    print("4. 测试基本面分析器...")
    try:
        from fundamental_analyzer import FundamentalAnalyzer
        analyzer = FundamentalAnalyzer()
        print("   ✓ 基本面分析器初始化成功")
        
        # 快速功能测试
        result = analyzer._detect_market_type('600519', 'A')
        if result == 'A':
            print("   ✓ 市场类型检测功能正常")
            return True
        else:
            print("   ⚠ 市场类型检测结果异常")
            return False
            
    except Exception as e:
        print(f"   ✗ 基本面分析器测试失败: {e}")
        return False

def test_web_framework():
    """测试Web框架"""
    print("5. 测试Web框架...")
    try:
        import flask
        from flask import Flask
        print("   ✓ Flask导入成功")
        
        import flask_cors
        print("   ✓ Flask-CORS导入成功")
        
        return True
    except ImportError as e:
        print(f"   ✗ Web框架导入失败: {e}")
        return False

def test_environment_config():
    """测试环境配置"""
    print("6. 测试环境配置...")
    
    if not os.path.exists('.env'):
        print("   ⚠ .env文件不存在")
        if os.path.exists('.env.template'):
            print("   提示: 请运行 cp .env.template .env 并配置API密钥")
        return False
    
    # 检查关键环境变量
    api_keys = []
    if os.getenv('OPENAI_API_KEY'):
        api_keys.append('OpenAI')
    if os.getenv('GEMINI_API_KEY'):
        api_keys.append('Gemini')
    
    if api_keys:
        print(f"   ✓ 已配置API密钥: {', '.join(api_keys)}")
        return True
    else:
        print("   ⚠ 未配置AI服务API密钥")
        return False

def test_docker_files():
    """测试Docker文件"""
    print("7. 测试Docker配置文件...")
    
    required_files = [
        'Dockerfile',
        'docker-compose.yml',
        'requirements-prod.txt',
        '.dockerignore'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if not missing_files:
        print("   ✓ 所有Docker配置文件存在")
        return True
    else:
        print(f"   ✗ 缺少文件: {', '.join(missing_files)}")
        return False

def main():
    """主测试函数"""
    print("基本面分析系统 - 快速系统测试")
    print("=" * 50)
    
    tests = [
        ("基本导入", test_basic_imports),
        ("AI库导入", test_ai_imports),
        ("股票数据源", test_stock_data_sources),
        ("基本面分析器", test_fundamental_analyzer),
        ("Web框架", test_web_framework),
        ("环境配置", test_environment_config),
        ("Docker配置", test_docker_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ✗ {test_name}测试异常: {e}")
            results.append((test_name, False))
        print()
    
    # 输出测试总结
    print("=" * 50)
    print("测试总结:")
    
    success_count = 0
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n总体结果: {success_count}/{len(results)} 项测试通过")
    
    if success_count == len(results):
        print("\n🎉 所有测试通过！系统准备就绪。")
        print("\n下一步:")
        print("1. 配置 .env 文件中的API密钥")
        print("2. 运行: ./docker-build.sh deploy")
        print("3. 访问: http://localhost:5000")
        return 0
    elif success_count >= len(results) * 0.8:
        print("\n⚠ 大部分测试通过，系统基本可用。")
        print("请检查失败的测试项目。")
        return 0
    else:
        print("\n❌ 多项测试失败，请检查系统配置。")
        print("\n建议:")
        print("1. 运行: python install_dependencies.py")
        print("2. 检查环境配置")
        print("3. 重新运行测试")
        return 1

if __name__ == "__main__":
    sys.exit(main())