# 增强版A股数据采集系统

🚀 **不达目的不罢休的智能数据采集agent** - 为A股交易系统提供全面、高质量的数据支持

## 🌟 系统特色

### 📊 全面的数据源覆盖
- **巨潮信息网** - 官方公告数据源，权威可靠
- **新浪财经** - 实时财经新闻，覆盖面广
- **东方财富网** - 综合金融数据，深度分析
- **中国证券网** - 权威证券资讯，专业解读
- **深交所互动易** - 投资者互动平台，获取第一手信息
- **第一财经** - 专业财经媒体，高质量内容
- **韭研公社** - 投资研究社区，多元观点

### 🧠 智能化特性
- **不达目的不罢休**: 多重重试机制，确保数据获取成功
- **LangChain智能决策**: 基于LLM的智能分析和策略调整
- **GitHub爬虫自动发现**: 自动搜索和集成开源爬虫工具
- **数据质量智能评估**: 自动评估和筛选高质量数据
- **多并发采集**: 支持多任务并发，提高采集效率

### 🗄️ 健全的数据管理
- **结构化存储**: 基于SQLAlchemy的专业数据库设计
- **数据去重**: 智能内容哈希，避免重复数据
- **质量分级**: 五级质量评估体系
- **关键词提取**: 自动提取和标记关键信息
- **数据导出**: 支持Excel等多种格式导出

## 🛠️ 安装和配置

### 环境要求
```bash
Python >= 3.10
```

### 依赖安装
```bash
# 基础依赖
pip install -r requirements_ashare.txt

# 额外数据采集依赖
pip install selenium beautifulsoup4 jieba sqlalchemy openpyxl
```

### 环境变量配置
```bash
# Tushare数据源（推荐）
export TUSHARE_TOKEN="your_tushare_token_here"

# 阿里云千问模型（推荐用于中文分析）
export DASHSCOPE_API_KEY="your_dashscope_api_key_here"

# OpenAI（备选）
export OPENAI_API_KEY="your_openai_api_key_here"
```

## 🚀 快速开始

### 1. 基础使用
```python
from tradingagents.agents.enhanced_ashare_data_agent import create_enhanced_ashare_data_agent
from langchain_openai import ChatOpenAI

# 初始化模型和数据agent
llm = ChatOpenAI(model="gpt-4o-mini")
data_agent = create_enhanced_ashare_data_agent(llm)

# 获取综合新闻
news_report = data_agent.get_comprehensive_stock_news("000001", days_back=7)
print(news_report)
```

### 2. 运行演示程序
```bash
python demo_enhanced_data_collector.py
```

### 3. 集成到现有系统
```python
from tradingagents.ashare_trading_graph import AShareTradingGraph
from tradingagents.ashare_config import get_ashare_config

# 获取增强配置
config = get_ashare_config()

# 创建交易图（自动包含数据采集功能）
trading_graph = AShareTradingGraph(config)

# 现在可以使用增强的数据采集功能
result = trading_graph.analyze_stock("600036")
```

## 🔧 功能详解

### 📰 综合新闻采集
```python
# 从多个数据源获取股票新闻
result = data_agent.get_comprehensive_stock_news(
    stock_code="000001",  # 股票代码
    days_back=7           # 回看天数
)
```

### 📋 公告数据获取
```python
# 获取官方公告信息
result = data_agent.get_stock_announcements(
    stock_code="000001",
    days_back=30
)
```

### 💬 互动问答采集
```python
# 获取投资者互动数据
result = data_agent.get_interactive_qa(
    stock_code="000001",
    days_back=30
)
```

### 📈 市场情绪分析
```python
# 分析市场情绪
result = data_agent.get_market_sentiment_analysis(
    keyword="银行",
    days_back=7
)
```

### 🏭 行业分析
```python
# 获取行业分析报告
result = data_agent.get_industry_analysis(
    industry="科技",
    days_back=14
)
```

### 🔍 数据搜索
```python
# 搜索相关数据
result = data_agent.search_stock_data(
    query="平安银行",
    data_types="news,announcement,interaction"
)
```

### 📊 数据质量报告
```python
# 获取数据质量统计
result = data_agent.get_data_quality_report()
```

### 📤 数据导出
```python
# 导出数据到Excel
result = data_agent.export_data_excel("data_export.xlsx")
```

## 🎯 核心架构

### 数据采集Agent
```
DataCollectorAgent
├── 任务队列管理
├── 多重重试机制
├── GitHub爬虫集成
└── LLM智能决策
```

### 数据存储系统
```
DataStorageManager
├── SQLAlchemy ORM
├── 数据质量评估
├── 智能去重
└── 关键词提取
```

### 爬虫工厂
```
CrawlerFactory
├── JuchaoInfoCrawler (巨潮信息网)
├── EnhancedSinaCrawler (新浪财经)
├── EastMoneyCrawler (东方财富)
├── CNSCrawler (中国证券网)
├── SZSEInteractiveCrawler (深交所互动易)
├── YicaiCrawler (第一财经)
└── JiuyanCrawler (韭研公社)
```

## 📊 数据质量体系

### 五级质量评估
- **优秀 (Excellent)**: 90-100分，完整准确的高质量数据
- **良好 (Good)**: 75-89分，质量较好，可直接使用
- **一般 (Average)**: 60-74分，基本可用，可能需要清洗
- **较差 (Poor)**: 40-59分，质量较差，需要谨慎使用
- **无效 (Invalid)**: 0-39分，无效数据，自动过滤

### 质量评估维度
- 字段完整性检查
- 内容质量分析
- 时间合理性验证
- 垃圾内容识别
- 格式规范检查

## 🔄 重试机制

### 多层重试策略
1. **内置爬虫重试**: 使用内置爬虫首次尝试
2. **GitHub爬虫备用**: 自动搜索相关开源爬虫
3. **LLM智能分析**: 基于错误分析调整策略
4. **指数退避**: 避免过于频繁的请求
5. **最终兜底**: 记录失败任务供后续处理

### 智能决策
- 错误类型分析
- 策略动态调整
- 数据源切换建议
- 参数优化推荐

## 📈 性能优化

### 并发控制
- 最大并发任务数: 5个
- 请求间隔控制: 随机1-3秒
- 连接池管理: 复用HTTP连接
- 内存占用监控: 防止内存泄漏

### 缓存策略
- 数据库级缓存: SQLite优化配置
- 内存缓存: 热点数据快速访问
- 磁盘缓存: 大数据临时存储
- 过期机制: 自动清理旧数据

## 🛡️ 风险控制

### 反爬措施应对
- 随机User-Agent
- 代理IP支持
- 请求频率控制
- 错误重试限制

### 数据安全
- 敏感信息过滤
- 数据加密存储
- 访问权限控制
- 审计日志记录

## 📋 配置说明

### 数据源配置
```python
"data_sources": {
    "juchao_info": {
        "enabled": True,
        "base_url": "http://www.cninfo.com.cn"
    },
    "sina_finance": {
        "enabled": True,
        "base_url": "https://finance.sina.com.cn"
    }
    # ... 更多数据源
}
```

### 采集配置
```python
"data_collection": {
    "enabled": True,
    "max_concurrent_tasks": 5,
    "retry_count": 5,
    "timeout": 30,
    "auto_quality_check": True,
    "github_crawler_search": True
}
```

## 🐛 常见问题

### Q: 数据采集失败怎么办？
A: 系统具有强大的重试机制，会自动尝试多种方法。检查网络连接和API配置。

### Q: 如何提高数据质量？
A: 配置Tushare等专业数据源，启用自动质量检查，定期清理低质量数据。

### Q: 支持自定义数据源吗？
A: 支持，可以继承DataSourceCrawler基类实现自定义爬虫。

### Q: 数据存储在哪里？
A: 默认存储在SQLite数据库中，可配置其他数据库。

## 🤝 贡献指南

欢迎贡献代码和改进建议！

### 添加新数据源
1. 继承`DataSourceCrawler`基类
2. 实现`crawl`方法
3. 注册到`CrawlerFactory`
4. 添加配置项

### 改进数据质量
1. 优化验证规则
2. 增强清洗算法
3. 改进关键词提取
4. 完善质量评估

## 📄 许可证

本项目基于原TradingAgents项目的许可证。

## 🙏 致谢

感谢TauricResearch团队的开源贡献，以及所有数据源提供商。

---

**🎯 让我们一起建立最全面的A股数据库！**