#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖包安装脚本
用于在创建.venv后快速安装所有必需的依赖包
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command_list, description):
    """执行命令并处理错误"""
    print(f"
🔄 {description}...")
    try:
        if isinstance(command_list, str):
            command_list = command_list.split()
        
        result = subprocess.run(command_list, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败:")
        print(f"错误信息: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def check_virtual_env():
    """检查是否在虚拟环境中"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 检测到虚拟环境")
        return True
    else:
        print("⚠️  未检测到虚拟环境，建议在虚拟环境中安装依赖")
        response = input("是否继续安装? (y/N): ")
        return response.lower() == 'y'

def upgrade_pip():
    """升级pip"""
    return run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        "升级pip"
    )

def install_requirements(env_type="dev"):
    """安装依赖包"""
    if env_type == "prod":
        requirements_file = "requirements-prod.txt"
        description = "安装生产环境依赖"
    else:
        requirements_file = "requirements.txt"
        description = "安装开发环境依赖"
    
    if not Path(requirements_file).exists():
        print(f"❌ 找不到 {requirements_file} 文件")
        return False
    
    return run_command(
        [sys.executable, "-m", "pip", "install", "-r", requirements_file],
        description
    )

def verify_installation():
    """验证关键包是否安装成功"""
    critical_packages = [
        'pandas', 'numpy', 'requests', 'scipy',
        'openai', 'google.generativeai', 'akshare',
        'flask', 'sqlalchemy', 'beautifulsoup4',
        'tqdm', 'matplotlib', 'seaborn', 'loguru'
    ]
    
    print("\n🔍 验证关键包安装状态:")
    failed_packages = []
    
    for package in critical_packages:
        try:
            if package == 'google.generativeai':
                import google.generativeai
            else:
                __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️  以下包安装失败: {', '.join(failed_packages)}")
        return False
    else:
        print("\n🎉 所有关键包安装成功!")
        return True

def create_requirements_check_script():
    """创建依赖检查脚本"""
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖包检查脚本
检查所有必需的依赖包是否正确安装
"""

import importlib
import sys

# 关键依赖包列表
REQUIRED_PACKAGES = {
    'pandas': '数据处理',
    'numpy': '数值计算',
    'requests': 'HTTP请求',
    'scipy': '科学计算',
    'openai': 'OpenAI API',
    'google.generativeai': 'Google AI API',
    'akshare': '股票数据',
    'flask': 'Web框架',
    'sqlalchemy': '数据库ORM',
    'beautifulsoup4': 'HTML解析',
    'tqdm': '进度条',
    'matplotlib': '图表绘制',
    'seaborn': '统计图表',
    'loguru': '日志记录',
    'redis': '缓存',
    'pytest': '测试框架',
    'scikit-learn': '机器学习',
    'statsmodels': '统计模型',
    'tavily': 'AI搜索'
}

def check_package(package_name, description):
    """检查单个包"""
    try:
        if package_name == 'google.generativeai':
            import google.generativeai
        elif package_name == 'beautifulsoup4':
            import bs4
        elif package_name == 'scikit-learn':
            import sklearn
        else:
            importlib.import_module(package_name)
        return True, None
    except ImportError as e:
        return False, str(e)

def main():
    print("🔍 检查依赖包安装状态\\n")
    
    success_count = 0
    total_count = len(REQUIRED_PACKAGES)
    failed_packages = []
    
    for package, description in REQUIRED_PACKAGES.items():
        success, error = check_package(package, description)
        if success:
            print(f"✅ {package:<20} - {description}")
            success_count += 1
        else:
            print(f"❌ {package:<20} - {description} (错误: {error})")
            failed_packages.append(package)
    
    print(f"\\n📊 安装状态: {success_count}/{total_count} 成功")
    
    if failed_packages:
        print(f"\\n⚠️  需要安装的包: {', '.join(failed_packages)}")
        print("\\n💡 安装命令:")
        print(f"   pip install {' '.join(failed_packages)}")
        return False
    else:
        print("\\n🎉 所有依赖包安装完成!")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
'''
    
    with open('check_dependencies.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    print("✅ 已创建依赖检查脚本: check_dependencies.py")

def main():
    """主函数"""
    print("🚀 基本面分析系统 - 依赖包安装脚本")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查虚拟环境
    if not check_virtual_env():
        sys.exit(1)
    
    # 选择安装类型
    print("\n📦 选择安装类型:")
    print("1. 开发环境 (包含所有依赖)")
    print("2. 生产环境 (精简依赖)")
    
    choice = input("请选择 (1/2, 默认1): ").strip()
    env_type = "prod" if choice == "2" else "dev"
    
    # 升级pip
    if not upgrade_pip():
        print("⚠️  pip升级失败，继续安装...")
    
    # 安装依赖
    if not install_requirements(env_type):
        print("❌ 依赖安装失败")
        sys.exit(1)
    
    # 验证安装
    if verify_installation():
        print("\n🎉 依赖包安装完成!")
        
        # 创建检查脚本
        create_requirements_check_script()
        
        print("\n📝 后续步骤:")
        print("1. 运行 python check_dependencies.py 验证安装")
        print("2. 运行 python quick_system_test.py 进行系统测试")
        print("3. 开始使用基本面分析系统")
        
    else:
        print("\n⚠️  部分依赖安装可能有问题，请检查上述错误信息")
        sys.exit(1)

if __name__ == '__main__':
    main()