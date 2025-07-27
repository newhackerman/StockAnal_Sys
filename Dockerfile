# 多阶段构建的基本面分析系统 Dockerfile
FROM python:3.11-slim as builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    pkg-config \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 升级pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 复制依赖文件
COPY requirements-prod.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements-prod.txt

# 生产环境镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TZ=Asia/Shanghai

# AI服务环境变量
ENV OPENAI_API_KEY=""
ENV OPENAI_API_URL="https://api.openai.com/v1"
ENV OPENAI_API_MODEL="gpt-4o"
ENV GEMINI_API_KEY=""
ENV API_PROVIDER="openai"

# 应用配置环境变量
ENV FLASK_ENV=production
ENV PORT=5000

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libxml2 \
    libxslt1.1 \
    libffi8 \
    libfreetype6 \
    libjpeg62-turbo \
    libpng16-16 \
    curl \
    tzdata \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 设置时区
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 设置工作目录
WORKDIR /app

# 从builder阶段复制Python包
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY fundamental_analyzer.py .
COPY fundamental_config.py .
COPY web_server.py .
COPY stock_analyzer.py .
COPY stock_qa.py .
COPY ai_client.py .
COPY scenario_predictor.py .
COPY industry_analyzer.py .
COPY capital_flow_analyzer.py .
COPY risk_monitor.py .
COPY index_industry_analyzer.py .
COPY news_fetcher.py .
COPY database.py .
COPY us_stock_service.py .
COPY templates/ templates/
COPY static/ static/

# 复制环境配置文件
COPY .env-example .env

# 创建必要的目录
RUN mkdir -p logs data cache

# 设置权限
RUN chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# 暴露端口
EXPOSE ${PORT}

# 启动命令
CMD ["python", "web_server.py"]