#!/bin/bash

echo "=== TradingAgent 部署检查脚本 ==="

echo "1. 检查Docker服务..."
if docker info >/dev/null 2>&1; then
    echo "✓ Docker 运行正常"
else
    echo "✗ Docker 未运行"
fi

echo "2. 检查容器状态..."
docker-compose ps

echo "3. 检查环境变量..."
if [ -f .env ]; then
    echo "✓ 配置文件存在"
    echo "已配置的API密钥:"
    grep -E "(TUSHARE_TOKEN|DASHSCOPE_API_KEY)" .env | head -2
else
    echo "✗ 配置文件不存在"
fi

echo "4. 检查日志文件..."
if [ -d logs ]; then
    echo "✓ 日志目录存在"
    ls -la logs/
else
    echo "! 日志目录不存在"
fi

echo "5. 测试应用连接..."
if curl -f http://localhost:8000 >/dev/null 2>&1; then
    echo "✓ 应用响应正常"
else
    echo "! 应用未响应 (这可能是正常的，如果应用不提供HTTP服务)"
fi

echo "6. 显示实时日志 (按Ctrl+C退出):"
docker-compose logs -f --tail=50
