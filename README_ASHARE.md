# A股智能交易代理系统

基于LangGraph和多智能体架构的A股市场智能投资决策系统，专为中国A股市场特色设计。

## 🌟 核心特性

### 🤖 多智能体协作
- **市场分析师**: 技术指标分析和趋势判断
- **基本面分析师**: 财务数据和基本面评估
- **政策分析师**: 政策影响和宏观环境分析
- **多头研究员**: 挖掘投资机会和上涨逻辑
- **空头研究员**: 识别投资风险和下跌逻辑
- **风险管理师**: 综合风险评估和投资决策

### 📊 A股市场专业数据
- **股票数据**: 通过Tushare和AKShare获取实时行情
- **财务数据**: 完整的财务报表和关键指标
- **技术指标**: 专业的技术分析指标计算
- **新闻数据**: 新浪财经、财联社等权威新闻源
- **市场情绪**: 资金流向、投资者情绪分析
- **行业分析**: 行业轮动和板块分析

### 🎯 A股特色功能
- **涨跌停制度**: 考虑10%涨跌停限制
- **T+1交易制度**: 适配A股交易规则
- **政策敏感性**: 重点关注政策影响
- **资金面分析**: 北向资金、融资融券数据
- **中国会计准则**: 基于中国财务报表标准
- **监管环境**: 考虑证监会等监管要求

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd tradingagent

# 安装A股专用依赖
pip install -r requirements_ashare.txt
```

### 2. API密钥配置

创建 `.env` 文件并配置必要的API密钥：

```bash
# Tushare数据源（必需）
TUSHARE_TOKEN=your_tushare_token_here

# 阿里云千问模型（推荐）
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# 或者使用OpenAI（可选）
OPENAI_API_KEY=your_openai_api_key_here

# 新浪财经和财联社（可选，用于新闻获取）
SINA_API_KEY=your_sina_api_key_here
CLS_API_KEY=your_cls_api_key_here
```

#### 获取API密钥指南

**Tushare Token（必需）**:
1. 访问 [Tushare官网](https://tushare.pro/)
2. 注册账号并实名认证
3. 获取免费Token（每日500次调用）
4. 付费用户可获得更高调用频率

**阿里云千问API（推荐）**:
1. 访问 [阿里云DashScope](https://dashscope.aliyun.com/)
2. 开通千问模型服务
3. 获取API Key
4. 支持中文金融分析，效果更佳

### 3. 基本使用

#### 命令行工具

```bash
# 分析单只股票
python ashare_cli.py analyze --symbol 000001.SZ

# 分析多只股票
python ashare_cli.py analyze --symbols 000001.SZ,000002.SZ,600000.SH

# 股票筛选（市值>100亿，PE<30）
python ashare_cli.py screen --market-cap-min 10000000000 --pe-max 30

# 搜索股票
python ashare_cli.py search --query "招商银行"

# 获取股票列表
python ashare_cli.py list --market main  # 主板
python ashare_cli.py list --market gem   # 创业板
python ashare_cli.py list --market sme   # 中小板
```

#### Python脚本

```python
from tradingagents.ashare_trading_graph import AShareTradingGraph
from tradingagents.ashare_config import get_ashare_config

# 创建配置
config = get_ashare_config()

# 自定义配置
config.update({
    "llm": {
        "provider": "dashscope",
        "model": "qwen-max",
        "api_key": "your_dashscope_api_key"
    },
    "debate": {
        "rounds": 3,
        "enable_debate": True
    },
    "risk_management": {
        "max_position_size": 0.1,
        "stop_loss_threshold": 0.08
    }
})

# 创建交易图
trading_graph = AShareTradingGraph(config)

# 分析单只股票
result = trading_graph.analyze_stock("000001.SZ")
print(result)

# 股票筛选
screened_stocks = trading_graph.screen_stocks({
    "market_cap_min": 10000000000,  # 100亿市值
    "pe_ratio_max": 30,             # PE<30
    "volume_ratio_min": 1.2         # 量比>1.2
})

# 批量分析
batch_results = trading_graph.batch_analyze(screened_stocks[:5])
```

## 📋 详细功能

### 股票分析流程

1. **数据收集**: 获取股票基本信息、历史价格、财务数据
2. **技术分析**: 计算技术指标，判断趋势和支撑阻力
3. **基本面分析**: 评估财务健康度、盈利能力、成长性
4. **政策分析**: 分析政策影响和宏观环境
5. **多空辩论**: 多头和空头观点对抗，全面评估
6. **风险管理**: 综合评估，给出投资建议和风险控制

### 股票筛选条件

```python
screen_criteria = {
    # 市值条件
    "market_cap_min": 5000000000,    # 最小市值50亿
    "market_cap_max": 100000000000,  # 最大市值1000亿
    
    # 估值条件
    "pe_ratio_min": 5,               # 最小PE
    "pe_ratio_max": 50,              # 最大PE
    "pb_ratio_max": 5,               # 最大PB
    
    # 财务条件
    "roe_min": 0.1,                  # 最小ROE 10%
    "debt_ratio_max": 0.6,           # 最大负债率60%
    "revenue_growth_min": 0.05,      # 最小营收增长5%
    
    # 技术条件
    "volume_ratio_min": 1.0,         # 最小量比
    "price_change_min": -0.05,       # 最小涨跌幅-5%
    "price_change_max": 0.1,         # 最大涨跌幅10%
    
    # 行业和板块
    "industries": ["银行", "保险", "证券"],  # 指定行业
    "exclude_st": True,              # 排除ST股票
    "exclude_suspended": True,       # 排除停牌股票
}
```

### 配置选项

```python
config = {
    # LLM配置
    "llm": {
        "provider": "dashscope",      # dashscope/openai
        "model": "qwen-max",          # 模型名称
        "temperature": 0.1,           # 温度参数
        "max_tokens": 4000            # 最大token数
    },
    
    # 数据源配置
    "data_sources": {
        "tushare_token": "your_token",
        "enable_akshare": True,
        "enable_sina_news": True,
        "enable_cls_news": True
    },
    
    # 分析配置
    "analysis": {
        "lookback_days": 30,          # 回看天数
        "technical_indicators": [      # 技术指标
            "SMA", "EMA", "RSI", "MACD", "BOLL"
        ],
        "fundamental_metrics": [       # 基本面指标
            "PE", "PB", "ROE", "ROA", "DEBT_RATIO"
        ]
    },
    
    # 辩论配置
    "debate": {
        "enable_debate": True,
        "rounds": 2,                  # 辩论轮数
        "max_agents_per_round": 3
    },
    
    # 风险管理
    "risk_management": {
        "max_position_size": 0.1,     # 最大仓位10%
        "stop_loss_threshold": 0.08,  # 止损阈值8%
        "risk_free_rate": 0.03        # 无风险利率3%
    }
}
```

## 🔧 高级用法

### 自定义智能体

```python
from tradingagents.agents.base_agent import BaseAgent

class CustomAnalyst(BaseAgent):
    def __init__(self, config):
        super().__init__(config)
        self.name = "自定义分析师"
        self.role = "专注于特定分析领域"
    
    def analyze(self, stock_data):
        # 自定义分析逻辑
        return analysis_result

# 集成到交易图中
trading_graph.add_agent("custom_analyst", CustomAnalyst(config))
```

### 批量处理和调度

```python
import schedule
import time

def daily_analysis():
    """每日定时分析"""
    # 获取关注股票列表
    watchlist = ["000001.SZ", "000002.SZ", "600000.SH"]
    
    # 批量分析
    results = trading_graph.batch_analyze(watchlist)
    
    # 保存结果
    trading_graph.save_results(results, "daily_analysis.json")
    
    # 发送报告（可选）
    # send_report(results)

# 设置定时任务
schedule.every().day.at("09:00").do(daily_analysis)
schedule.every().day.at("15:30").do(daily_analysis)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 结果导出和可视化

```python
# 导出分析结果
trading_graph.export_results(results, format="excel", filename="analysis_report.xlsx")
trading_graph.export_results(results, format="pdf", filename="analysis_report.pdf")

# 生成图表
trading_graph.plot_analysis("000001.SZ", save_path="charts/")
```

## 📊 输出示例

### 股票分析报告

```
=== 招商银行(600036.SH) 投资分析报告 ===

📈 技术分析
- 当前价格: ¥42.50 (+1.2%)
- 趋势: 上升趋势，突破20日均线
- 支撑位: ¥41.00, ¥39.50
- 阻力位: ¥44.00, ¥46.00
- RSI: 65 (偏强)
- MACD: 金叉信号

💰 基本面分析
- 市值: 1.2万亿
- PE: 5.8倍 (低估值)
- PB: 0.9倍 (破净)
- ROE: 13.2% (优秀)
- 资产质量: AAA级

🏛️ 政策影响
- 央行降准利好银行股
- 房地产政策边际放松
- 金融监管趋于稳定

🎯 投资建议
- 评级: 买入
- 目标价: ¥48.00
- 止损价: ¥39.00
- 建议仓位: 8%
- 投资期限: 6-12个月

⚠️ 风险提示
- 经济下行压力
- 信贷风险上升
- 利率环境变化
```

## 🛠️ 故障排除

### 常见问题

**Q: Tushare调用频率限制**
A: 升级Tushare账户或使用缓存机制减少API调用

**Q: 千问模型调用失败**
A: 检查API密钥和网络连接，确保账户余额充足

**Q: 股票代码格式错误**
A: 使用正确格式：深交所用.SZ后缀，上交所用.SH后缀

**Q: 数据获取失败**
A: 检查网络连接和数据源API状态

### 日志配置

```python
import logging

# 启用详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ashare_trading.log'),
        logging.StreamHandler()
    ]
)
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## ⚠️ 免责声明

本系统仅供学习和研究使用，不构成投资建议。投资有风险，入市需谨慎。使用本系统进行投资决策的风险由用户自行承担。

## 📞 联系我们

- 项目主页: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 邮箱: [contact@example.com]

---

**祝您投资顺利！** 🚀📈