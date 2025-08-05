#!/bin/bash

echo "=== TradingAgent 服务启动脚本 ==="

# 检查Docker是否运行
if ! docker info >/dev/null 2>&1; then
    echo "启动Docker服务..."
    sudo systemctl start docker
fi

# 检查配置文件
if [ ! -f .env ]; then
    echo "错误: 找不到 .env 配置文件"
    echo "请先配置环境变量"
    exit 1
fi

# 创建必要目录
mkdir -p cache results logs

# 构建并启动服务
echo "构建Docker镜像..."
docker-compose build

echo "启动服务..."
docker-compose up -d

echo "检查服务状态..."
docker-compose ps

echo "查看日志 (Ctrl+C 退出):"
docker-compose logs -f
