<p align="center">
  <img src="assets/TauricResearch.png" style="width: 60%; height: auto;">
</p>

<div align="center" style="line-height: 1;">
  <a href="https://arxiv.org/abs/2412.20138" target="_blank"><img alt="arXiv" src="https://img.shields.io/badge/arXiv-2412.20138-B31B1B?logo=arxiv"/></a>
  <a href="https://discord.com/invite/hk9PGKShPK" target="_blank"><img alt="Discord" src="https://img.shields.io/badge/Discord-TradingResearch-7289da?logo=discord&logoColor=white&color=7289da"/></a>
  <a href="./assets/wechat.png" target="_blank"><img alt="WeChat" src="https://img.shields.io/badge/WeChat-TauricResearch-brightgreen?logo=wechat&logoColor=white"/></a>
  <a href="https://x.com/TauricResearch" target="_blank"><img alt="X Follow" src="https://img.shields.io/badge/X-TauricResearch-white?logo=x&logoColor=white"/></a>
  <br>
  <a href="https://github.com/TauricResearch/" target="_blank"><img alt="Community" src="https://img.shields.io/badge/Join_GitHub_Community-TauricResearch-14C290?logo=discourse"/></a>
</div>

<div align="center">
  <!-- Keep these links. Translations will automatically update with the README. -->
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=de">Deutsch</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=es">Español</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=fr">français</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ja">日本語</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ko">한국어</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=pt">Português</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ru">Русский</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=zh">中文</a>
</div>

---

# TradingAgents: Multi-Agents LLM Financial Trading Framework 

> 🎉 **TradingAgents** officially released! We have received numerous inquiries about the work, and we would like to express our thanks for the enthusiasm in our community.
>
> So we decided to fully open-source the framework. Looking forward to building impactful projects with you!

<div align="center">
<a href="https://www.star-history.com/#TauricResearch/TradingAgents&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" />
   <img alt="TradingAgents Star History" src="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" style="width: 80%; height: auto;" />
 </picture>
</a>
</div>

<div align="center">

🚀 [TradingAgents](#tradingagents-framework) | ⚡ [Installation & CLI](#installation-and-cli) | 🎬 [Demo](https://www.youtube.com/watch?v=90gr5lwjIho) | 📦 [Package Usage](#tradingagents-package) | 🤝 [Contributing](#contributing) | 📄 [Citation](#citation)

</div>

## TradingAgents Framework

TradingAgents is a multi-agent trading framework that mirrors the dynamics of real-world trading firms. By deploying specialized LLM-powered agents: from fundamental analysts, sentiment experts, and technical analysts, to trader, risk management team, the platform collaboratively evaluates market conditions and informs trading decisions. Moreover, these agents engage in dynamic discussions to pinpoint the optimal strategy.

<p align="center">
  <img src="assets/schema.png" style="width: 100%; height: auto;">
</p>

> TradingAgents framework is designed for research purposes. Trading performance may vary based on many factors, including the chosen backbone language models, model temperature, trading periods, the quality of data, and other non-deterministic factors. [It is not intended as financial, investment, or trading advice.](https://tauric.ai/disclaimer/)

Our framework decomposes complex trading tasks into specialized roles. This ensures the system achieves a robust, scalable approach to market analysis and decision-making.

### Analyst Team
- Fundamentals Analyst: Evaluates company financials and performance metrics, identifying intrinsic values and potential red flags.
- Sentiment Analyst: Analyzes social media and public sentiment using sentiment scoring algorithms to gauge short-term market mood.
- News Analyst: Monitors global news and macroeconomic indicators, interpreting the impact of events on market conditions.
- Technical Analyst: Utilizes technical indicators (like MACD and RSI) to detect trading patterns and forecast price movements.

<p align="center">
  <img src="assets/analyst.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

### Researcher Team
- Comprises both bullish and bearish researchers who critically assess the insights provided by the Analyst Team. Through structured debates, they balance potential gains against inherent risks.

<p align="center">
  <img src="assets/researcher.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### Trader Agent
- Composes reports from the analysts and researchers to make informed trading decisions. It determines the timing and magnitude of trades based on comprehensive market insights.

<p align="center">
  <img src="assets/trader.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### Risk Management and Portfolio Manager
- Continuously evaluates portfolio risk by assessing market volatility, liquidity, and other risk factors. The risk management team evaluates and adjusts trading strategies, providing assessment reports to the Portfolio Manager for final decision.
- The Portfolio Manager approves/rejects the transaction proposal. If approved, the order will be sent to the simulated exchange and executed.

<p align="center">
  <img src="assets/risk.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

## Installation and CLI

### Installation

Clone TradingAgents:
```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

Create a virtual environment in any of your favorite environment managers:
```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### Required APIs

You will also need the FinnHub API for financial data. All of our code is implemented with the free tier.
```bash
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY
```

You will need the OpenAI API for all the agents.
```bash
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY
```

## A股智能交易代理系统 (Chinese A-Share Intelligent Trading Agents)

🎉 **全新A股专用版本发布！** 基于中国A股市场特色，我们开发了专门的多智能体交易系统，涵盖A股市场所有股票的智能分析和选股功能。

### 🌟 A股专用特性

- **🤖 六大专业智能体**: 市场分析师、基本面分析师、政策分析师、多头研究员、空头研究员、风险管理师
- **📊 全面数据覆盖**: 通过Tushare和AKShare获取A股全市场数据
- **🏛️ 政策敏感分析**: 专门针对A股政策市特色的政策影响分析
- **🎯 A股特色适配**: 涨跌停制度、T+1交易、北向资金、中国会计准则
- **🧠 千问模型优化**: 使用阿里云千问模型，更好理解中文金融语境

### 🚀 快速开始A股系统

#### 安装A股专用依赖
```bash
# 安装A股专用依赖包
pip install -r requirements_ashare.txt
```

#### 配置API密钥
```bash
# Tushare数据源（必需）
export TUSHARE_TOKEN="your_tushare_token_here"

# 阿里云千问模型（推荐）
export DASHSCOPE_API_KEY="your_dashscope_api_key_here"
```

#### 命令行快速使用
```bash
# 分析单只A股
python ashare_cli.py analyze --symbol 000001.SZ

# A股选股筛选
python ashare_cli.py screen --market-cap-min 10000000000 --pe-max 30

# 搜索A股股票
python ashare_cli.py search --query "招商银行"
```

#### Python代码使用
```python
from tradingagents.ashare_trading_graph import AShareTradingGraph
from tradingagents.ashare_config import get_ashare_config

# 创建A股专用配置
config = get_ashare_config()
config.update({
    "llm": {
        "provider": "dashscope",
        "model": "qwen-max",
        "api_key": "your_dashscope_api_key"
    },
    "data_sources": {
        "tushare_token": "your_tushare_token"
    }
})

# 初始化A股交易图
trading_graph = AShareTradingGraph(config)

# 分析招商银行
result = trading_graph.analyze_stock("600036.SH")
print(result)

# A股选股
screened_stocks = trading_graph.screen_stocks({
    "market_cap_min": 10000000000,  # 100亿市值以上
    "pe_ratio_max": 30,             # PE小于30
    "roe_min": 0.1                  # ROE大于10%
})

# 批量分析
batch_results = trading_graph.batch_analyze(screened_stocks[:5])
```

### 📋 A股智能体架构

#### 分析师团队
- **市场分析师**: 专注A股技术指标分析，考虑涨跌停、量比等A股特色指标
- **基本面分析师**: 基于中国会计准则的财务分析，关注ROE、负债率、现金流
- **政策分析师**: 专门分析政策对A股的影响，包括货币政策、产业政策、监管政策

#### 研究员团队
- **多头研究员**: 挖掘A股投资机会，关注政策催化、业绩拐点、估值修复
- **空头研究员**: 识别A股投资风险，关注商誉减值、关联交易、流动性风险

#### 风险管理
- **风险管理师**: 综合评估投资风险，考虑A股特有的系统性风险和政策风险

### 🎯 A股选股功能

支持多维度股票筛选：

```python
# 价值股筛选
value_criteria = {
    "pe_ratio_max": 15,        # 低估值
    "pb_ratio_max": 2,         # 低市净率
    "roe_min": 0.15,           # 高ROE
    "debt_ratio_max": 0.5      # 低负债
}

# 成长股筛选
growth_criteria = {
    "revenue_growth_min": 0.2,  # 营收增长20%+
    "profit_growth_min": 0.3,   # 利润增长30%+
    "market_cap_min": 5000000000  # 50亿市值以上
}

# 政策受益股筛选
policy_criteria = {
    "industries": ["新能源", "半导体", "生物医药"],
    "exclude_st": True,
    "volume_ratio_min": 1.2
}
```

### 📊 详细文档

完整的A股系统使用指南请参考：[A股系统README](README_ASHARE.md)

---

## 原版美股系统配置 (Original US Stock System)

### 数据源配置 (Data Source Configuration)

#### FinnHub API配置
```bash
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY
```

#### OpenAI API配置
```bash
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY
```

### 新闻数据源配置 (News Data Sources)

#### 财联社新闻数据
可以通过GitHub获取财联社的新闻数据：
```bash
# 克隆财联社新闻爬虫项目
git clone https://github.com/your-repo/cailianshe-news-crawler.git
```

#### 新浪财经新闻数据
新浪财经新闻数据获取：
```bash
# 克隆新浪财经新闻爬虫项目
git clone https://github.com/your-repo/sina-finance-news-crawler.git
```

#### 集成新闻数据到TradingAgents
```python
# 在dataflows/interface.py中添加中文新闻获取函数
def get_cailianshe_news(stock_code, current_date, lookback_days=7):
    """
    获取财联社相关股票新闻
    """
    # 实现财联社新闻获取逻辑
    pass

def get_sina_finance_news(stock_code, current_date, lookback_days=7):
    """
    获取新浪财经相关股票新闻
    """
    # 实现新浪财经新闻获取逻辑
    pass
```

### A股使用示例 (A-Share Usage Example)

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
import tushare as ts
import akshare as ak

# 设置数据源
ts.set_token('b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065')

# A股配置
config = DEFAULT_CONFIG.copy()
config.update({
    "llm_provider": "dashscope",
    "deep_think_llm": "qwen-max",
    "quick_think_llm": "qwen-turbo",
    "max_debate_rounds": 3,
    "online_tools": True,
    "market_region": "china",
    "data_sources": {
        "tushare": True,
        "akshare": True,
        "cailianshe": True,
        "sina_finance": True
    }
})

# 初始化交易智能体
ta = TradingAgentsGraph(debug=True, config=config)

# 分析热门A股
stocks_to_analyze = [
    "000001",  # 平安银行
    "000002",  # 万科A
    "600036",  # 招商银行
    "600519",  # 贵州茅台
    "000858"   # 五粮液
]

for stock in stocks_to_analyze:
    print(f"\n分析股票: {stock}")
    _, decision = ta.propagate(stock, "2024-12-20")
    print(f"决策结果: {decision}")
    
    # 记忆和反思
    ta.reflect_and_remember(stock, decision)
```

### 注意事项 (Important Notes)

1. **合规性**: 请确保遵守中国证监会相关法规，本工具仅供研究和学习使用
2. **数据质量**: Tushare提供更专业的数据，AKShare数据免费但可能存在延迟
3. **交易时间**: A股交易时间为工作日09:30-15:00，请注意时区设置
4. **模型选择**: 千问模型对中文金融术语理解更好，推荐用于A股分析
5. **风险提示**: 本工具不构成投资建议，投资有风险，入市需谨慎

### CLI Usage

You can also try out the CLI directly by running:
```bash
python -m cli.main
```
You will see a screen where you can select your desired tickers, date, LLMs, research depth, etc.

<p align="center">
  <img src="assets/cli/cli_init.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

An interface will appear showing results as they load, letting you track the agent's progress as it runs.

<p align="center">
  <img src="assets/cli/cli_news.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

<p align="center">
  <img src="assets/cli/cli_transaction.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

## TradingAgents Package

### Implementation Details

We built TradingAgents with LangGraph to ensure flexibility and modularity. We utilize `o1-preview` and `gpt-4o` as our deep thinking and fast thinking LLMs for our experiments. However, for testing purposes, we recommend you use `o4-mini` and `gpt-4.1-mini` to save on costs as our framework makes **lots of** API calls.

### Python Usage

To use TradingAgents inside your code, you can import the `tradingagents` module and initialize a `TradingAgentsGraph()` object. The `.propagate()` function will return a decision. You can run `main.py`, here's also a quick example:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())

# forward propagate
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

You can also adjust the default configuration to set your own choice of LLMs, debate rounds, etc.

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4.1-nano"  # Use a different model
config["quick_think_llm"] = "gpt-4.1-nano"  # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds
config["online_tools"] = True # Use online tools or cached data

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

> For `online_tools`, we recommend enabling them for experimentation, as they provide access to real-time data. The agents' offline tools rely on cached data from our **Tauric TradingDB**, a curated dataset we use for backtesting. We're currently in the process of refining this dataset, and we plan to release it soon alongside our upcoming projects. Stay tuned!

You can view the full list of configurations in `tradingagents/default_config.py`.

## Contributing

We welcome contributions from the community! Whether it's fixing a bug, improving documentation, or suggesting a new feature, your input helps make this project better. If you are interested in this line of research, please consider joining our open-source financial AI research community [Tauric Research](https://tauric.ai/).

## Citation

Please reference our work if you find *TradingAgents* provides you with some help :)

```
@misc{xiao2025tradingagentsmultiagentsllmfinancial,
      title={TradingAgents: Multi-Agents LLM Financial Trading Framework}, 
      author={Yijia Xiao and Edward Sun and Di Luo and Wei Wang},
      year={2025},
      eprint={2412.20138},
      archivePrefix={arXiv},
      primaryClass={q-fin.TR},
      url={https://arxiv.org/abs/2412.20138}, 
}
```
