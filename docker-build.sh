#!/bin/bash

# Docker构建和部署脚本
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 检查环境变量
check_env() {
    log_info "检查环境变量..."
    
    if [ ! -f ".env" ]; then
        log_warn ".env文件不存在，从模板创建..."
        cp .env.template .env
        log_warn "请编辑 .env 文件并填入正确的API密钥"
    fi
    
    # 检查必要的环境变量
    source .env
    
    if [ -z "$OPENAI_API_KEY" ] && [ -z "$GEMINI_API_KEY" ]; then
        log_error "请在 .env 文件中配置至少一个AI服务的API密钥"
        exit 1
    fi
    
    log_info "环境变量检查完成"
}

# 检查Docker环境
check_docker() {
    log_info "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    # 检查Docker是否运行
    if ! docker info &> /dev/null; then
        log_error "Docker服务未运行，请启动Docker"
        exit 1
    fi
    
    log_info "Docker环境检查通过"
}

# 构建镜像
build_image() {
    log_info "构建Docker镜像..."
    
    # 清理旧的构建缓存
    docker builder prune -f
    
    # 构建生产镜像
    docker-compose build --no-cache --parallel
    
    # 检查构建结果
    if [ $? -eq 0 ]; then
        log_info "镜像构建成功"
    else
        log_error "镜像构建失败"
        exit 1
    fi
}

# 构建开发镜像
build_dev_image() {
    log_info "构建开发环境镜像..."
    
    docker-compose -f docker-compose.dev.yml build --no-cache
    
    if [ $? -eq 0 ]; then
        log_info "开发镜像构建成功"
    else
        log_error "开发镜像构建失败"
        exit 1
    fi
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # 启动测试容器
    docker-compose -f docker-compose.dev.yml up -d redis-dev
    
    # 运行测试
    docker run --rm \
        --network analyzer-dev-network \
        -v $(pwd):/app \
        -w /app \
        fundamental-analyzer-dev:latest \
        python -m pytest tests/ -v
    
    # 清理测试环境
    docker-compose -f docker-compose.dev.yml down
    
    log_info "测试完成"
}

# 启动生产环境
start_production() {
    log_info "启动生产环境..."
    
    # 创建必要的目录
    mkdir -p logs data cache
    
    # 启动服务
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 15
    
    # 健康检查
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        log_info "生产环境启动成功"
        log_info "应用地址: http://localhost:5000"
    else
        log_error "生产环境启动失败"
        docker-compose logs
        exit 1
    fi
}

# 启动开发环境
start_development() {
    log_info "启动开发环境..."
    
    # 创建必要的目录
    mkdir -p logs data cache
    
    # 启动开发服务
    docker-compose -f docker-compose.dev.yml up -d
    
    # 等待服务启动
    log_info "等待开发环境启动..."
    sleep 10
    
    log_info "开发环境启动成功"
    log_info "应用地址: http://localhost:5000"
    log_info "调试端口: 5678"
    log_info "Redis端口: 6380"
}

# 停止所有服务
stop_all() {
    log_info "停止所有服务..."
    
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    
    log_info "所有服务已停止"
}

# 清理资源
cleanup() {
    log_info "清理Docker资源..."
    
    # 停止所有容器
    stop_all
    
    # 删除未使用的镜像
    docker image prune -f
    
    # 删除未使用的卷
    docker volume prune -f
    
    # 删除未使用的网络
    docker network prune -f
    
    log_info "清理完成"
}

# 查看日志
view_logs() {
    local service=${1:-fundamental-analyzer}
    log_info "查看 $service 服务日志..."
    docker-compose logs -f $service
}

# 进入容器
enter_container() {
    local service=${1:-fundamental-analyzer}
    log_info "进入 $service 容器..."
    docker-compose exec $service bash
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backup_${timestamp}"
    
    mkdir -p "${backup_dir}"
    
    # 备份数据目录
    if [ -d "data" ]; then
        cp -r data "${backup_dir}/"
    fi
    
    # 备份日志
    if [ -d "logs" ]; then
        cp -r logs "${backup_dir}/"
    fi
    
    # 备份配置
    cp .env "${backup_dir}/"
    cp docker-compose.yml "${backup_dir}/"
    
    # 创建压缩包
    tar -czf "${backup_dir}.tar.gz" "${backup_dir}"
    rm -rf "${backup_dir}"
    
    log_info "数据备份完成: ${backup_dir}.tar.gz"
}

# 显示帮助信息
show_help() {
    echo "基本面分析系统 Docker 构建和部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  check-env     - 检查环境变量配置"
    echo "  build         - 构建生产环境镜像"
    echo "  build-dev     - 构建开发环境镜像"
    echo "  test          - 运行测试"
    echo "  start         - 启动生产环境"
    echo "  start-dev     - 启动开发环境"
    echo "  stop          - 停止所有服务"
    echo "  logs [服务名]  - 查看服务日志"
    echo "  shell [服务名] - 进入容器shell"
    echo "  backup        - 备份数据"
    echo "  cleanup       - 清理Docker资源"
    echo "  deploy        - 完整部署流程"
    echo "  help          - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 deploy              # 完整部署"
    echo "  $0 start-dev           # 启动开发环境"
    echo "  $0 logs redis          # 查看Redis日志"
    echo "  $0 shell               # 进入主应用容器"
}

# 完整部署流程
deploy() {
    log_info "开始完整部署流程..."
    
    check_docker
    check_env
    build_image
    start_production
    
    log_info "部署完成！"
    log_info "应用地址: http://localhost:5000"
}

# 主函数
main() {
    case "$1" in
        "check-env")
            check_env
            ;;
        "build")
            check_docker
            build_image
            ;;
        "build-dev")
            check_docker
            build_dev_image
            ;;
        "test")
            check_docker
            run_tests
            ;;
        "start")
            check_docker
            check_env
            start_production
            ;;
        "start-dev")
            check_docker
            check_env
            start_development
            ;;
        "stop")
            stop_all
            ;;
        "logs")
            view_logs $2
            ;;
        "shell")
            enter_container $2
            ;;
        "backup")
            backup_data
            ;;
        "cleanup")
            cleanup
            ;;
        "deploy")
            deploy
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        "")
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"