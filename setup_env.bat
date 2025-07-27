@echo off
chcp 65001 >nul
echo 🚀 基本面分析系统 - 环境设置脚本
echo ================================================

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python已安装
python --version

:: 创建虚拟环境
echo.
echo 🔄 创建虚拟环境...
if exist .venv (
    echo ⚠️  虚拟环境已存在，是否重新创建？
    set /p recreate="输入 y 重新创建，其他键跳过: "
    if /i "!recreate!"=="y" (
        echo 🗑️  删除现有虚拟环境...
        rmdir /s /q .venv
        python -m venv .venv
        echo ✅ 虚拟环境重新创建完成
    ) else (
        echo ⏭️  跳过虚拟环境创建
    )
) else (
    python -m venv .venv
    echo ✅ 虚拟环境创建完成
)

:: 激活虚拟环境
echo.
echo 🔄 激活虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活

:: 升级pip
echo.
echo 🔄 升级pip...
python -m pip install --upgrade pip
echo ✅ pip升级完成

:: 选择安装类型
echo.
echo 📦 选择安装类型:
echo 1. 开发环境 (包含所有依赖)
echo 2. 生产环境 (精简依赖)
set /p install_type="请选择 (1/2, 默认1): "

if "%install_type%"=="2" (
    set requirements_file=requirements-prod.txt
    echo 🔄 安装生产环境依赖...
) else (
    set requirements_file=requirements.txt
    echo 🔄 安装开发环境依赖...
)

:: 安装依赖
python -m pip install -r %requirements_file%
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成

:: 验证安装
echo.
echo 🔍 验证关键包安装...
python -c "
import sys
packages = ['pandas', 'numpy', 'requests', 'scipy', 'openai', 'akshare', 'flask']
failed = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError:
        print(f'❌ {pkg}')
        failed.append(pkg)
if failed:
    print(f'\\n⚠️  安装失败的包: {failed}')
    sys.exit(1)
else:
    print('\\n🎉 关键包验证通过!')
"

if errorlevel 1 (
    echo ❌ 部分包安装失败，请检查错误信息
    pause
    exit /b 1
)

:: 创建启动脚本
echo.
echo 📝 创建启动脚本...
echo @echo off > start_system.bat
echo chcp 65001 ^>nul >> start_system.bat
echo call .venv\Scripts\activate.bat >> start_system.bat
echo echo 🎯 基本面分析系统已启动 >> start_system.bat
echo echo 虚拟环境: %%VIRTUAL_ENV%% >> start_system.bat
echo echo. >> start_system.bat
echo echo 💡 可用命令: >> start_system.bat
echo echo   python app.py                    - 启动Web服务 >> start_system.bat
echo echo   python get_codename.py           - 测试股票代码查询 >> start_system.bat
echo echo   python check_dependencies.py     - 检查依赖 >> start_system.bat
echo echo   python quick_system_test.py      - 系统测试 >> start_system.bat
echo echo. >> start_system.bat
echo cmd /k >> start_system.bat
echo ✅ 启动脚本创建完成: start_system.bat

echo.
echo 🎉 环境设置完成！
echo.
echo 📝 后续步骤:
echo   1. 双击 start_system.bat 启动系统
echo   2. 或手动激活: .venv\Scripts\activate.bat
echo   3. 运行测试: python check_dependencies.py
echo.
pause