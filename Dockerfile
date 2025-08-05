# TradingAgent 阿里云部署 Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
COPY requirements_ashare.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_ashare.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p cache results logs

# 设置权限
RUN chmod +x *.py

# 暴露端口（如果有web服务）
EXPOSE 8000

# 设置环境变量
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# 运行命令
CMD ["python", "main.py"]
