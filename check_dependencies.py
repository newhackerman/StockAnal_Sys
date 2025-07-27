#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的依赖检查脚本
"""

import sys
import importlib

def check_package(package_name, import_name=None):
    """检查单个包是否可用"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False

def main():
    """主检查函数"""
    print("检查关键依赖包...")
    
    # 关键依赖列表
    dependencies = [
        # 核心数据处理
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('scipy', 'scipy'),
        ('requests', 'requests'),
        
        # AI服务
        ('openai', 'openai'),
        ('google-genai', 'google.generativeai'),
        
        # 股票数据
        ('akshare', 'akshare'),
        
        # Web框架
        ('flask', 'flask'),
        ('flask-cors', 'flask_cors'),
        ('flask-swagger-ui', 'flask_swagger_ui'),
        
        # 数据库
        ('sqlalchemy', 'sqlalchemy'),
        
        # 数据解析
        ('beautifulsoup4', 'bs4'),
        ('lxml', 'lxml'),
        ('html5lib', 'html5lib'),
        
        # 工具库
        ('openpyxl', 'openpyxl'),
        ('tqdm', 'tqdm'),
        ('jsonpath', 'jsonpath'),
        ('python-dotenv', 'dotenv'),
        ('PyYAML', 'yaml'),
        
        # 日志
        ('loguru', 'loguru'),
        
        # 缓存
        ('redis', 'redis'),
        
        # 图表
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
        
        # 调试
        ('ipython', 'IPython'),
        
        # 机器学习
        ('scikit-learn', 'sklearn'),
        ('statsmodels', 'statsmodels'),
        
        # 测试
        ('pytest', 'pytest'),
        
        # 部署
        ('gunicorn', 'gunicorn'),
        
        # AI搜索
        ('tavily-python', 'tavily'),
        
        # Google API
        ('google', 'google')
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for package_name, import_name in dependencies:
        if check_package(package_name, import_name):
            print(f"✓ {package_name}")
            success_count += 1
        else:
            print(f"✗ {package_name}")
    
    print(f"\n结果: {success_count}/{total_count} 依赖包可用")
    
    # 计算成功率
    success_rate = (success_count / total_count) * 100
    
    if success_count >= int(total_count * 0.8):  # 至少80%的包可用
        print(f"✓ 依赖检查通过 ({success_rate:.1f}%)，可以继续部署")
        return 0
    else:
        print(f"✗ 依赖检查失败 ({success_rate:.1f}%)，请安装缺失的包")
        print("\n安装方法:")
        print("1. 运行: python install_dependencies.py")
        print("2. 或手动安装: pip install -r requirements.txt")
        print("3. Windows用户可运行: setup_env.bat")
        return 1

if __name__ == "__main__":
    sys.exit(main())