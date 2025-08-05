#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading Agent Startup Script
处理依赖和环境初始化
"""

import os
import sys

# 确保Python路径正确
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('PYTHONPATH', current_dir)

# 尝试导入可选依赖
def install_optional_dependencies():
    """尝试安装可选依赖"""
    optional_packages = [
        'langchain==0.2.0',
        'langchain-core==0.2.0', 
        'langchain-community==0.2.0',
        'pydantic==2.7.4',
        'aiohttp==3.9.5',
        'stockstats==0.6.2'
    ]
    
    print("🔧 检查可选依赖...")
    for package in optional_packages:
        try:
            pkg_name = package.split('==')[0]
            __import__(pkg_name)
            print(f"✅ {pkg_name} already available")
        except ImportError:
            print(f"⚠️ {pkg_name} not available - 运行基础功能")

def main():
    """主启动函数"""
    print("🚀 Trading Agent 启动中...")
    print(f"📁 工作目录: {current_dir}")
    print(f"🐍 Python版本: {sys.version}")
    
    # 检查可选依赖
    install_optional_dependencies()
    
    # 导入并启动应用
    try:
        from web_app import app
        
        # 获取端口
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        print(f"🌐 启动Web服务 {host}:{port}")
        print("📊 数据源: Tushare + AKShare + Tavily")
        print("🤖 AI引擎: DashScope + OpenAI")
        print("⚡ 多智能体系统就绪")
        
        # 启动应用
        app.run(host=host, port=port, debug=False)
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()