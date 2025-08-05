# -*- coding: utf-8 -*-
"""
A股市场专用配置文件
包含阿里云千问模型配置和A股数据源配置
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

# A股专用默认配置
ASHARE_DEFAULT_CONFIG = {
    # 项目目录配置
    "project_root": str(PROJECT_ROOT),
    "results_dir": str(RESULTS_DIR),
    "data_dir": str(DATA_DIR),
    
    # 阿里云千问模型配置
    "llm_provider": "dashscope",  # 阿里云千问
    "deep_think_llm": "qwen-max",  # 深度思考模型
    "quick_think_llm": "qwen-turbo",  # 快速思考模型
    "llm_backend_url": None,  # 使用官方API
    
    # A股数据源配置（增强版）
    "data_sources": {
        "tushare": {
            "enabled": True,
            "token": os.getenv("TUSHARE_TOKEN", ""),  # 从环境变量获取
            "pro_api": "http://api.tushare.pro"
        },
        "akshare": {
            "enabled": True,
            "requires_token": False  # AKShare无需token
        },
        "sina_finance": {
            "enabled": True,
            "base_url": "https://finance.sina.com.cn"
        },
        "cls_news": {
            "enabled": True,
            "base_url": "https://www.cls.cn"
        },
        # 新增数据源
        "juchao_info": {
            "enabled": True,
            "base_url": "http://www.cninfo.com.cn",
            "description": "巨潮信息网 - 官方公告数据源"
        },
        "eastmoney": {
            "enabled": True,
            "base_url": "https://www.eastmoney.com",
            "api_base": "https://push2.eastmoney.com/api",
            "description": "东方财富网 - 综合财经数据"
        },
        "cns_news": {
            "enabled": True,
            "base_url": "https://www.cs.com.cn",
            "description": "中国证券网 - 权威证券新闻"
        },
        "szse_interact": {
            "enabled": True,
            "base_url": "http://irm.cninfo.com.cn",
            "description": "深交所互动易 - 投资者互动平台"
        },
        "yicai": {
            "enabled": True,
            "base_url": "https://www.yicai.com",
            "description": "第一财经 - 专业财经媒体"
        },
        "jiuyan": {
            "enabled": True,
            "base_url": "https://www.jiuyangongshe.com",
            "description": "韭研公社 - 投资研究社区"
        }
    },
    
    # A股市场特色配置
    "market_config": {
        "market_type": "ashare",
        "trading_hours": {
            "morning": {"start": "09:30", "end": "11:30"},
            "afternoon": {"start": "13:00", "end": "15:00"}
        },
        "price_limit": 0.10,  # 10%涨跌停限制
        "t_plus_1": True,  # T+1交易制度
        "currency": "CNY",
        "timezone": "Asia/Shanghai"
    },
    
    # 辩论和讨论配置
    "max_debate_rounds": 3,
    "max_discussion_rounds": 2,
    
    # A股专用智能体配置（增强版）
    "agents": {
        "analysts": {
            "market_analyst": "ashare_market_analyst",
            "fundamental_analyst": "ashare_fundamental_analyst", 
            "policy_analyst": "ashare_policy_analyst"
        },
        "researchers": {
            "bull_researcher": "ashare_bull_researcher",
            "bear_researcher": "ashare_bear_researcher"
        },
        "risk_manager": "ashare_risk_manager",
        # 新增数据采集智能体
        "data_collector": "enhanced_ashare_data_agent"
    },
    
    # 工具配置（增强版）
    "online_tools": True,
    "tools": {
        # 原有基础工具
        "stock_data": "get_ashare_stock_data",
        "financial_data": "get_ashare_financial_data",
        "technical_indicators": "get_ashare_technical_indicators",
        "market_sentiment": "get_ashare_market_sentiment",
        "industry_analysis": "get_ashare_industry_analysis",
        "company_news": "get_ashare_company_news",
        "market_news": "get_ashare_market_news",
        "policy_news": "get_ashare_policy_news",
        
        # 新增增强数据采集工具
        "comprehensive_stock_news": "get_comprehensive_stock_news",
        "stock_announcements": "get_stock_announcements",
        "interactive_qa": "get_interactive_qa",
        "market_sentiment_analysis": "get_market_sentiment_analysis",
        "industry_analysis_enhanced": "get_industry_analysis",
        "search_stock_data": "search_stock_data",
        "data_quality_report": "get_data_quality_report"
    },
    
    # 数据采集配置
    "data_collection": {
        "enabled": True,
        "max_concurrent_tasks": 5,
        "retry_count": 5,
        "timeout": 30,
        "auto_quality_check": True,
        "github_crawler_search": True,
        "storage_path": "ashare_comprehensive_data.db"
    },
    
    # 数据缓存配置
    "cache_config": {
        "enabled": True,
        "cache_dir": str(DATA_DIR / "cache"),
        "cache_duration": 3600,  # 1小时缓存
        "max_cache_size": "1GB"
    },
    
    # 风险管理配置
    "risk_management": {
        "max_position_size": 0.20,  # 单只股票最大仓位20%
        "max_sector_exposure": 0.40,  # 单个行业最大敞口40%
        "stop_loss_threshold": 0.10,  # 10%止损
        "profit_taking_threshold": 0.30,  # 30%止盈
        "max_drawdown": 0.15,  # 最大回撤15%
        "var_confidence": 0.95,  # VaR置信度95%
    },
    
    # A股股票池配置
    "stock_universe": {
        "include_st": False,  # 是否包含ST股票
        "include_suspended": False,  # 是否包含停牌股票
        "min_market_cap": 1000000000,  # 最小市值10亿
        "min_daily_volume": 10000000,  # 最小日成交额1000万
        "exchanges": ["SSE", "SZSE"],  # 上交所、深交所
        "boards": ["main", "sme", "gem", "star"]  # 主板、中小板、创业板、科创板
    },
    
    # 分析配置
    "analysis_config": {
        "lookback_days": 252,  # 回看252个交易日（1年）
        "technical_indicators": [
            "MA5", "MA10", "MA20", "MA60", "MA120", "MA250",
            "MACD", "RSI", "KDJ", "BOLL", "SAR", "CCI"
        ],
        "fundamental_metrics": [
            "PE", "PB", "PS", "ROE", "ROA", "ROIC",
            "debt_ratio", "current_ratio", "quick_ratio"
        ],
        "news_sources": ["sina", "cls", "eastmoney"],
        "sentiment_analysis": True
    }
}

# 阿里云千问模型配置
DASHSCOPE_CONFIG = {
    "api_key": os.getenv("DASHSCOPE_API_KEY", ""),
    "models": {
        "qwen-max": {
            "name": "qwen-max",
            "description": "千问最强模型，适合复杂分析",
            "max_tokens": 8192,
            "temperature": 0.7
        },
        "qwen-turbo": {
            "name": "qwen-turbo",
            "description": "千问快速模型，适合简单任务", 
            "max_tokens": 8192,
            "temperature": 0.7
        },
        "qwen-plus": {
            "name": "qwen-plus",
            "description": "千问增强模型，平衡性能和速度",
            "max_tokens": 8192,
            "temperature": 0.7
        }
    },
    "default_model": "qwen-turbo",
    "base_url": "https://dashscope.aliyuncs.com/api/v1"
}

# Tushare配置
TUSHARE_CONFIG = {
    "token": os.getenv("TUSHARE_TOKEN", ""),
    "pro_api": "http://api.tushare.pro",
    "timeout": 30,
    "retry_count": 3,
    "rate_limit": {
        "calls_per_minute": 200,  # 根据Tushare权限调整
        "points_per_minute": 2000
    }
}

# AKShare配置
AKSHARE_CONFIG = {
    "timeout": 30,
    "retry_count": 3,
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
}

# 新闻数据源配置
NEWS_CONFIG = {
    "sina_finance": {
        "base_url": "https://finance.sina.com.cn",
        "api_endpoints": {
            "stock_news": "/api/openapi.php/StockNewsService.getStockNews",
            "market_news": "/api/openapi.php/NewsService.getNews"
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://finance.sina.com.cn"
        }
    },
    "cls_news": {
        "base_url": "https://www.cls.cn",
        "api_endpoints": {
            "telegraph": "/api/telegraph",
            "depth": "/api/depth"
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.cls.cn"
        }
    }
}

def get_ashare_config():
    """
    获取A股配置
    
    Returns:
        dict: A股配置字典
    """
    config = ASHARE_DEFAULT_CONFIG.copy()
    
    # 检查必要的环境变量
    if not config["data_sources"]["tushare"]["token"]:
        print("警告: 未设置TUSHARE_TOKEN环境变量，Tushare功能将不可用")
        config["data_sources"]["tushare"]["enabled"] = False
    
    if not DASHSCOPE_CONFIG["api_key"]:
        print("警告: 未设置DASHSCOPE_API_KEY环境变量，将使用默认LLM配置")
        config["llm_provider"] = "openai"  # 回退到OpenAI
    
    return config

def validate_ashare_config(config):
    """
    验证A股配置的有效性
    
    Args:
        config (dict): 配置字典
        
    Returns:
        bool: 配置是否有效
    """
    required_keys = [
        "llm_provider", "deep_think_llm", "quick_think_llm",
        "data_sources", "market_config", "agents"
    ]
    
    for key in required_keys:
        if key not in config:
            print(f"错误: 缺少必要配置项 {key}")
            return False
    
    # 验证数据源配置
    if config["data_sources"]["tushare"]["enabled"]:
        if not config["data_sources"]["tushare"]["token"]:
            print("错误: Tushare已启用但未提供token")
            return False
    
    # 验证LLM配置
    if config["llm_provider"] == "dashscope":
        if not DASHSCOPE_CONFIG["api_key"]:
            print("错误: 选择了DashScope但未提供API密钥")
            return False
    
    return True

# 导出配置
__all__ = [
    "ASHARE_DEFAULT_CONFIG",
    "DASHSCOPE_CONFIG", 
    "TUSHARE_CONFIG",
    "AKSHARE_CONFIG",
    "NEWS_CONFIG",
    "get_ashare_config",
    "validate_ashare_config"
]