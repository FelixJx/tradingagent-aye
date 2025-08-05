#!/bin/bash

# A股智能交易代理系统安装脚本
# 作者: TradingAgents Team
# 日期: 2024-12-20

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python版本
check_python() {
    print_info "检查Python版本..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3未安装，请先安装Python 3.8+"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))")
    required_version="3.8"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
        print_success "Python版本检查通过: $python_version"
    else
        print_error "Python版本过低: $python_version，需要3.8+"
        exit 1
    fi
}

# 检查pip
check_pip() {
    print_info "检查pip..."
    
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3未安装，请先安装pip"
        exit 1
    fi
    
    print_success "pip检查通过"
}

# 创建虚拟环境
create_venv() {
    print_info "创建Python虚拟环境..."
    
    if [ -d "venv_ashare" ]; then
        print_warning "虚拟环境已存在，跳过创建"
    else
        python3 -m venv venv_ashare
        print_success "虚拟环境创建完成"
    fi
    
    print_info "激活虚拟环境..."
    source venv_ashare/bin/activate
    print_success "虚拟环境激活完成"
}

# 升级pip
upgrade_pip() {
    print_info "升级pip..."
    pip install --upgrade pip
    print_success "pip升级完成"
}

# 安装依赖
install_dependencies() {
    print_info "安装A股专用依赖包..."
    
    if [ ! -f "requirements_ashare.txt" ]; then
        print_error "requirements_ashare.txt文件不存在"
        exit 1
    fi
    
    pip install -r requirements_ashare.txt
    print_success "依赖包安装完成"
}

# 安装TA-Lib（可选）
install_talib() {
    print_info "尝试安装TA-Lib..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            print_info "在macOS上使用Homebrew安装TA-Lib..."
            brew install ta-lib
            pip install TA-Lib
            print_success "TA-Lib安装完成"
        else
            print_warning "未检测到Homebrew，跳过TA-Lib安装"
            print_warning "请手动安装: brew install ta-lib && pip install TA-Lib"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        print_info "在Linux上安装TA-Lib..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y build-essential
            wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
            tar -xzf ta-lib-0.4.0-src.tar.gz
            cd ta-lib/
            ./configure --prefix=/usr
            make
            sudo make install
            cd ..
            rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
            pip install TA-Lib
            print_success "TA-Lib安装完成"
        else
            print_warning "不支持的Linux发行版，跳过TA-Lib安装"
        fi
    else
        print_warning "不支持的操作系统，跳过TA-Lib安装"
    fi
}

# 创建配置文件模板
create_config_template() {
    print_info "创建配置文件模板..."
    
    cat > .env.template << EOF
# A股交易代理系统环境变量配置模板
# 复制此文件为.env并填入真实的API密钥

# =============================================================================
# 必需配置
# =============================================================================

# Tushare数据源API密钥（必需）
# 获取地址: https://tushare.pro/
# 注册并实名认证后可获得免费Token
TUSHARE_TOKEN=your_tushare_token_here

# 阿里云千问模型API密钥（推荐）
# 获取地址: https://dashscope.aliyun.com/
# 支持中文金融分析，效果更佳
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# =============================================================================
# 可选配置
# =============================================================================

# OpenAI API密钥（可选，作为备用LLM）
# OPENAI_API_KEY=your_openai_api_key_here

# 新浪财经API密钥（可选，用于新闻获取）
# SINA_API_KEY=your_sina_api_key_here

# 财联社API密钥（可选，用于新闻获取）
# CLS_API_KEY=your_cls_api_key_here

# =============================================================================
# 系统配置
# =============================================================================

# 日志级别
LOG_LEVEL=INFO

# 数据缓存目录
CACHE_DIR=./cache

# 结果输出目录
OUTPUT_DIR=./results
EOF

    print_success "配置文件模板创建完成: .env.template"
}

# 创建快速启动脚本
create_startup_script() {
    print_info "创建快速启动脚本..."
    
    cat > start_ashare.sh << 'EOF'
#!/bin/bash

# A股交易代理系统快速启动脚本

set -e

# 激活虚拟环境
if [ -d "venv_ashare" ]; then
    source venv_ashare/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "❌ 虚拟环境不存在，请先运行安装脚本"
    exit 1
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "❌ 配置文件.env不存在"
    echo "请复制.env.template为.env并填入API密钥"
    exit 1
fi

# 加载环境变量
source .env

# 检查必需的API密钥
if [ -z "$TUSHARE_TOKEN" ] || [ "$TUSHARE_TOKEN" = "your_tushare_token_here" ]; then
    echo "❌ 请在.env文件中设置TUSHARE_TOKEN"
    exit 1
fi

if [ -z "$DASHSCOPE_API_KEY" ] || [ "$DASHSCOPE_API_KEY" = "your_dashscope_api_key_here" ]; then
    echo "❌ 请在.env文件中设置DASHSCOPE_API_KEY"
    exit 1
fi

echo "🚀 启动A股交易代理系统..."
echo "选择运行模式:"
echo "1. 演示模式 (demo_ashare.py)"
echo "2. 命令行工具 (ashare_cli.py)"
echo "3. 主程序 (ashare_main.py)"
echo "4. 退出"

read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo "🎬 运行演示模式..."
        python demo_ashare.py
        ;;
    2)
        echo "💻 启动命令行工具..."
        python ashare_cli.py --help
        ;;
    3)
        echo "🔧 运行主程序..."
        python ashare_main.py
        ;;
    4)
        echo "👋 退出"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac
EOF

    chmod +x start_ashare.sh
    print_success "快速启动脚本创建完成: start_ashare.sh"
}

# 显示安装后说明
show_post_install_info() {
    print_success "🎉 A股智能交易代理系统安装完成！"
    echo ""
    print_info "接下来的步骤:"
    echo "1. 复制配置文件模板: cp .env.template .env"
    echo "2. 编辑.env文件，填入您的API密钥"
    echo "3. 运行快速启动脚本: ./start_ashare.sh"
    echo ""
    print_info "获取API密钥:"
    echo "• Tushare Token: https://tushare.pro/"
    echo "• 阿里云千问API: https://dashscope.aliyun.com/"
    echo ""
    print_info "文档和帮助:"
    echo "• 详细文档: README_ASHARE.md"
    echo "• 演示脚本: python demo_ashare.py"
    echo "• 命令行工具: python ashare_cli.py --help"
    echo ""
    print_warning "注意: 本系统仅供学习研究使用，不构成投资建议！"
}

# 主函数
main() {
    echo "🚀 A股智能交易代理系统安装程序"
    echo "=================================="
    echo ""
    
    # 检查系统要求
    check_python
    check_pip
    
    # 创建虚拟环境
    create_venv
    
    # 升级pip
    upgrade_pip
    
    # 安装依赖
    install_dependencies
    
    # 安装TA-Lib（可选）
    read -p "是否安装TA-Lib技术指标库？(y/N): " install_talib_choice
    if [[ $install_talib_choice =~ ^[Yy]$ ]]; then
        install_talib
    else
        print_info "跳过TA-Lib安装"
    fi
    
    # 创建配置文件和脚本
    create_config_template
    create_startup_script
    
    # 显示安装后说明
    show_post_install_info
}

# 错误处理
trap 'print_error "安装过程中发生错误，请检查上面的错误信息"' ERR

# 运行主函数
main "$@"