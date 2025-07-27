#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速依赖安装脚本
根据您提供的包列表快速安装所有依赖
"""

import subprocess
import sys
import os

# 您提供的依赖包列表
REQUIRED_PACKAGES = [
    'pandas',
    'scipy', 
    'akshare',
    'tqdm',
    'openai',
    'requests',
    'python-dotenv',
    'flask',
    'loguru',
    'matplotlib',
    'seaborn',
    'ipython',
    'beautifulsoup4',
    'html5lib',
    'lxml',
    'jsonpath',
    'openpyxl',
    'flask-swagger-ui',
    'sqlalchemy',
    'flask-cors',
    'flask-caching',
    'gunicorn',
    'PyYAML',
    'scikit-learn',
    'statsmodels',
    'pytest',
    'tavily-python',
    'supervisor',
    'redis',
    'google',
    'google-genai'
]

def install_package(package):
    """安装单个包"""
    try:
        print(f"📦 安装 {package}...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', package
        ], capture_output=True, text=True, check=True)
        print(f"✅ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 安装失败: {e.stderr}")
        return False

def main():
    """主安装函数"""
    print("🚀 快速依赖安装脚本")
    print("=" * 50)
    
    # 检查虚拟环境
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        print("⚠️  建议在虚拟环境中安装依赖")
        response = input("是否继续? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # 升级pip
    print("\n🔄 升级pip...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        print("✅ pip升级完成")
    except:
        print("⚠️  pip升级失败，继续安装...")
    
    # 安装包
    print(f"\n📦 开始安装 {len(REQUIRED_PACKAGES)} 个依赖包...")
    
    success_count = 0
    failed_packages = []
    
    for i, package in enumerate(REQUIRED_PACKAGES, 1):
        print(f"\n[{i}/{len(REQUIRED_PACKAGES)}]", end=" ")
        if install_package(package):
            success_count += 1
        else:
            failed_packages.append(package)
    
    # 安装结果
    print(f"\n📊 安装结果: {success_count}/{len(REQUIRED_PACKAGES)} 成功")
    
    if failed_packages:
        print(f"\n❌ 安装失败的包: {', '.join(failed_packages)}")
        print("\n💡 可以尝试单独安装失败的包:")
        for pkg in failed_packages:
            print(f"   pip install {pkg}")
    else:
        print("\n🎉 所有依赖包安装完成!")
    
    # 验证安装
    print("\n🔍 验证关键包...")
    critical_packages = ['pandas', 'numpy', 'flask', 'openai', 'akshare']
    
    for pkg in critical_packages:
        try:
            __import__(pkg)
            print(f"✅ {pkg}")
        except ImportError:
            print(f"❌ {pkg}")
    
    print("\n✅ 快速安装完成!")
    print("\n📝 后续步骤:")
    print("1. 运行 python check_dependencies.py 进行完整检查")
    print("2. 运行 python get_codename.py 测试股票查询功能")
    print("3. 运行 python quick_system_test.py 进行系统测试")

if __name__ == '__main__':
    main()