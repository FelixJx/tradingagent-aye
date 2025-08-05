#!/bin/bash

echo "=== TradingAgent 阿里云部署脚本 ==="

# 获取服务器信息
read -p "阿里云服务器IP地址: " SERVER_IP
read -p "SSH用户名 (默认root): " SERVER_USER
SERVER_USER=${SERVER_USER:-root}
read -p "SSH端口 (默认22): " SSH_PORT
SSH_PORT=${SSH_PORT:-22}

echo "开始部署到 $SERVER_USER@$SERVER_IP:$SSH_PORT"

# 测试连接
echo "测试服务器连接..."
ssh -o ConnectTimeout=10 $SERVER_USER@$SERVER_IP -p $SSH_PORT "echo '连接成功'" || {
    echo "连接失败，请检查服务器配置"
    exit 1
}

# 打包项目（排除不必要的文件）
echo "打包项目文件..."
tar czf /tmp/tradingagent.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv*' \
    --exclude='cache/*' \
    --exclude='results/*' \
    --exclude='logs/*' \
    --exclude='*.log' \
    .

# 上传到服务器
echo "上传文件到服务器..."
scp -P $SSH_PORT /tmp/tradingagent.tar.gz $SERVER_USER@$SERVER_IP:/tmp/

# 服务器端部署
echo "在服务器上部署..."
ssh $SERVER_USER@$SERVER_IP -p $SSH_PORT << 'REMOTE_SCRIPT'
    # 安装Docker和Docker Compose
    if command -v yum >/dev/null 2>&1; then
        yum update -y
        yum install -y docker docker-compose
    elif command -v apt >/dev/null 2>&1; then
        apt update -y
        apt install -y docker.io docker-compose
    fi
    
    # 启动Docker服务
    systemctl start docker
    systemctl enable docker
    
    # 创建项目目录
    mkdir -p /opt/tradingagent
    cd /opt/tradingagent
    
    # 解压项目文件
    tar -xzf /tmp/tradingagent.tar.gz
    
    # 创建必要目录
    mkdir -p cache results logs
    
    # 设置权限
    chmod +x *.sh
    
    echo "=== 服务器部署完成 ==="
    echo "项目路径: /opt/tradingagent"
    echo "配置文件: /opt/tradingagent/.env"
    echo "启动命令: docker-compose up -d"
REMOTE_SCRIPT

# 清理临时文件
rm -f /tmp/tradingagent.tar.gz

echo "=== 部署完成 ==="
echo "下一步操作:"
echo "1. 登录服务器: ssh $SERVER_USER@$SERVER_IP"
echo "2. 进入目录: cd /opt/tradingagent"
echo "3. 检查配置: cat .env"
echo "4. 启动服务: docker-compose up -d"
echo "5. 查看日志: docker-compose logs -f"
