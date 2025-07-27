# Docker部署指南

## 概述

本指南介绍如何使用Docker部署基本面分析系统，包括AI服务集成（OpenAI和Gemini）。

## 前置要求

### 系统要求
- Docker >= 20.10
- Docker Compose >= 2.0
- 至少4GB可用内存
- 至少10GB可用磁盘空间

### API密钥要求
- OpenAI API密钥 (推荐)
- Google Gemini API密钥 (可选)
- 至少需要配置一个AI服务

## 快速开始

### 1. 环境配置

```bash
# 复制环境变量模板
cp .env.template .env

# 编辑环境变量文件
nano .env
```

必须配置的环境变量：
```bash
# 至少配置一个AI服务
OPENAI_API_KEY=your_openai_api_key_here
# 或者
GEMINI_API_KEY=your_gemini_api_key_here

# 选择主要的AI提供商
API_PROVIDER=openai  # 或 gemini
```

### 2. 构建和部署

```bash
# 使用部署脚本（推荐）
./docker-build.sh deploy

# 或者手动部署
docker-compose build
docker-compose up -d
```

### 3. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 健康检查
curl http://localhost:5000/health

# 查看日志
docker-compose logs -f
```

## 详细部署步骤

### 1. 依赖检查

```bash
# 测试AI依赖
python test_ai_dependencies.py

# 安装Python依赖（如果需要本地测试）
python install_dependencies.py
```

### 2. 环境变量配置

编辑 `.env` 文件，配置以下关键变量：

```bash
# AI服务配置
OPENAI_API_KEY=sk-...
OPENAI_API_URL=https://api.openai.com/v1
OPENAI_API_MODEL=gpt-4o

GEMINI_API_KEY=AI...
API_PROVIDER=openai

# 数据库配置
USE_DATABASE=true
DATABASE_URL=sqlite:///./data/stock_analysis.db

# Redis配置
REDIS_URL=redis://redis:6379/0

# 应用配置
PORT=5000
DEBUG=false
```

### 3. 构建镜像

```bash
# 构建生产镜像
./docker-build.sh build

# 或者使用docker-compose
docker-compose build --no-cache
```

### 4. 启动服务

```bash
# 启动生产环境
./docker-build.sh start

# 或者使用docker-compose
docker-compose up -d
```

## 开发环境部署

### 启动开发环境

```bash
# 使用开发脚本
./dev-deploy.sh start

# 或者使用docker-compose
docker-compose -f docker-compose.dev.yml up -d
```

### 开发环境特性

- 代码热重载
- 调试端口开放 (5678)
- 开发工具集成
- 详细日志输出

### 开发工具

```bash
# 进入开发容器
./dev-deploy.sh shell

# 运行测试
./dev-deploy.sh test

# 代码格式化
./dev-deploy.sh format

# 代码检查
./dev-deploy.sh lint
```

## 服务管理

### 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 重启服务
docker-compose restart [service_name]

# 停止服务
docker-compose down

# 更新服务
docker-compose pull
docker-compose up -d
```

### 数据管理

```bash
# 备份数据
./docker-build.sh backup

# 查看数据卷
docker volume ls

# 清理未使用的资源
docker system prune -f
```

## 服务架构

### 容器服务

1. **fundamental-analyzer** - 主应用服务
   - 端口: 5000
   - 包含: Web服务、AI客户端、数据分析

2. **redis** - 缓存服务
   - 端口: 6379
   - 用途: 数据缓存、会话存储

3. **nginx** - 反向代理（可选）
   - 端口: 80, 443
   - 用途: 负载均衡、SSL终止

### 数据卷

- `./logs` - 应用日志
- `./data` - 数据库文件
- `./cache` - 缓存文件

### 网络

- `analyzer-network` - 内部服务通信网络

## 配置说明

### AI服务配置

```bash
# OpenAI配置
OPENAI_API_KEY=sk-...           # API密钥
OPENAI_API_URL=https://...      # API端点
OPENAI_API_MODEL=gpt-4o         # 模型名称

# Gemini配置
GEMINI_API_KEY=AI...            # API密钥

# 提供商选择
API_PROVIDER=openai             # openai 或 gemini
```

### 数据库配置

```bash
# SQLite（默认）
DATABASE_URL=sqlite:///./data/stock_analysis.db

# PostgreSQL（可选）
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# MySQL（可选）
DATABASE_URL=mysql://user:pass@host:3306/dbname
```

### 缓存配置

```bash
# Redis配置
REDIS_URL=redis://redis:6379/0

# 缓存开关
ENABLE_CACHE=true
```

## 监控和日志

### 健康检查

```bash
# 应用健康检查
curl http://localhost:5000/health

# 服务状态检查
docker-compose ps
```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs -f fundamental-analyzer

# 查看实时日志
tail -f logs/app.log
```

### 性能监控

```bash
# 容器资源使用
docker stats

# 系统资源使用
docker system df
```

## 故障排除

### 常见问题

1. **AI API连接失败**
   ```bash
   # 检查API密钥配置
   docker-compose exec fundamental-analyzer env | grep API_KEY
   
   # 测试网络连接
   docker-compose exec fundamental-analyzer curl -I https://api.openai.com
   ```

2. **数据库连接问题**
   ```bash
   # 检查数据目录权限
   ls -la data/
   
   # 重新创建数据库
   docker-compose exec fundamental-analyzer python -c "from database import init_db; init_db()"
   ```

3. **Redis连接问题**
   ```bash
   # 检查Redis服务
   docker-compose exec redis redis-cli ping
   
   # 重启Redis
   docker-compose restart redis
   ```

4. **端口冲突**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep :5000
   
   # 修改端口配置
   # 编辑 docker-compose.yml 中的端口映射
   ```

### 调试模式

```bash
# 启用调试模式
export DEBUG=true
docker-compose up -d

# 查看详细日志
docker-compose logs -f --tail=100
```

### 重置环境

```bash
# 完全重置
docker-compose down -v
docker system prune -f
rm -rf data/ logs/ cache/
./docker-build.sh deploy
```

## 生产环境优化

### 性能优化

1. **资源限制**
   ```yaml
   # docker-compose.yml
   services:
     fundamental-analyzer:
       deploy:
         resources:
           limits:
             memory: 2G
             cpus: '1.0'
   ```

2. **缓存优化**
   ```bash
   # 增加Redis内存
   REDIS_MAXMEMORY=512mb
   ```

3. **并发优化**
   ```bash
   # 使用Gunicorn
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "web_server:app"]
   ```

### 安全配置

1. **网络安全**
   ```yaml
   # 限制网络访问
   networks:
     analyzer-network:
       internal: true
   ```

2. **密钥管理**
   ```bash
   # 使用Docker secrets
   docker secret create openai_key openai_key.txt
   ```

3. **SSL配置**
   ```bash
   # 配置HTTPS
   # 编辑 nginx.conf 启用SSL
   ```

## 更新和维护

### 应用更新

```bash
# 拉取最新代码
git pull

# 重新构建和部署
./docker-build.sh deploy
```

### 依赖更新

```bash
# 更新Python依赖
pip-compile requirements.in

# 重新构建镜像
docker-compose build --no-cache
```

### 数据备份

```bash
# 自动备份
./docker-build.sh backup

# 定期备份（crontab）
0 2 * * * /path/to/docker-build.sh backup
```

## 支持和帮助

### 获取帮助

```bash
# 查看部署脚本帮助
./docker-build.sh help

# 查看开发脚本帮助
./dev-deploy.sh
```

### 日志分析

```bash
# 错误日志过滤
docker-compose logs | grep ERROR

# 性能日志分析
docker-compose logs | grep -E "(slow|timeout|memory)"
```

### 社区支持

- GitHub Issues: 报告问题和功能请求
- 文档: 查看详细技术文档
- 示例: 参考配置示例