# 📦 依赖包安装指南

## 🎯 快速开始

### Windows用户 (推荐)
```batch
# 1. 运行自动安装脚本
setup_env.bat

# 2. 启动系统
start_system.bat
```

### 所有平台
```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. 安装依赖
python install_dependencies.py
# 或
python quick_install.py
```

## 📋 依赖包列表

根据您的需求，以下是完整的依赖包列表：

### 核心依赖 (必需)
```
pandas                  # 数据处理
scipy                   # 科学计算  
akshare                 # 股票数据
tqdm                    # 进度条
openai                  # OpenAI API
requests                # HTTP请求
python-dotenv           # 环境变量
flask                   # Web框架
loguru                  # 日志记录
```

### 数据处理和可视化
```
matplotlib              # 基础图表
seaborn                 # 统计图表
openpyxl                # Excel处理
beautifulsoup4          # HTML解析
html5lib                # HTML5解析
lxml                    # XML解析
jsonpath                # JSON查询
```

### Web和API
```
flask-swagger-ui        # API文档
flask-cors              # 跨域支持
flask-caching           # 缓存
sqlalchemy              # 数据库ORM
```

### 开发和调试
```
ipython                 # 交互式Python
pytest                  # 测试框架
```

### 机器学习和统计
```
scikit-learn            # 机器学习
statsmodels             # 统计模型
```

### 部署和运维
```
gunicorn                # WSGI服务器
supervisor              # 进程管理
redis                   # 缓存数据库
PyYAML                  # YAML配置
```

### AI增强功能
```
google-genai            # Google AI
tavily-python           # AI搜索
google                  # Google API基础
```

## 🛠️ 安装方法

### 方法1: 一键安装脚本 (推荐)
```bash
python install_dependencies.py
```
- 自动检测环境
- 选择开发/生产模式
- 包含错误处理和验证

### 方法2: 快速安装
```bash
python quick_install.py
```
- 基于您提供的包列表
- 逐个安装并显示进度
- 适合快速部署

### 方法3: 传统pip安装
```bash
# 开发环境 (完整功能)
pip install -r requirements.txt

# 生产环境 (精简版)
pip install -r requirements-prod.txt
```

### 方法4: 手动安装核心包
```bash
pip install pandas scipy akshare tqdm openai requests python-dotenv flask loguru matplotlib seaborn ipython beautifulsoup4 html5lib lxml jsonpath openpyxl flask-swagger-ui sqlalchemy flask-cors flask-caching gunicorn PyYAML scikit-learn statsmodels pytest tavily-python supervisor redis google google-genai
```

## ✅ 验证安装

### 1. 运行依赖检查
```bash
python check_dependencies.py
```

### 2. 测试核心功能
```bash
python get_codename.py
python demo_get_codename.py
```

### 3. 系统完整测试
```bash
python quick_system_test.py
```

## 🔧 故障排除

### 常见问题及解决方案

#### 1. 包安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple [包名]
```

#### 2. 权限问题
```bash
# 使用用户安装
pip install --user [包名]

# 或使用虚拟环境 (推荐)
python -m venv .venv
```

#### 3. 编译错误 (Windows)
- 安装 Microsoft Visual C++ Build Tools
- 或使用预编译的wheel包

#### 4. 网络问题
```bash
# 设置代理
pip install --proxy http://proxy:port [包名]

# 增加超时时间
pip install --timeout 1000 [包名]
```

## 📊 安装验证结果

当前系统依赖检查结果：
```
✅ 核心功能包: 24/30 (80%) - 通过
✅ 数据处理: pandas, numpy, scipy ✓
✅ AI服务: openai ✓, google-genai (需安装)
✅ Web框架: flask, flask-cors ✓
✅ 数据源: akshare ✓
✅ 工具库: tqdm, loguru, matplotlib ✓
```

## 🚀 部署建议

### 开发环境
```bash
# 完整安装
pip install -r requirements.txt
python check_dependencies.py
```

### 生产环境
```bash
# 精简安装
pip install -r requirements-prod.txt
python check_dependencies.py
```

### Docker部署
```dockerfile
FROM python:3.9-slim
COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt
```

## 📝 后续步骤

1. **环境配置**: 复制 `.env.template` 到 `.env` 并配置API密钥
2. **数据初始化**: 运行 `python get_codename.py` 初始化股票数据
3. **系统测试**: 运行 `python quick_system_test.py` 验证功能
4. **启动服务**: 运行 `python app.py` 启动Web服务

## 💡 优化建议

1. **使用虚拟环境**: 避免包冲突
2. **定期更新**: 保持依赖包最新
3. **缓存优化**: 使用pip缓存加速安装
4. **分层部署**: 按需安装功能模块

---

🎉 **安装完成后，您的基本面分析系统将具备完整的AI增强功能！**