# -*- coding: utf-8 -*-
"""
增强版A股数据工具模块
集成新的数据采集agent到现有工具体系
与原有ashare_utils.py兼容，提供更强大的数据获取能力
"""

import os
import logging
from typing import List, Dict, Optional, Annotated
from datetime import datetime, timedelta

from .ashare_utils import *  # 导入原有功能保持兼容性
from ..agents.enhanced_ashare_data_agent import create_enhanced_ashare_data_agent
from ..ashare_config import get_ashare_config

# 尝试导入LLM
try:
    from langchain_openai import ChatOpenAI
    from langchain_community.chat_models import ChatTongyi
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

logger = logging.getLogger(__name__)

# 全局数据采集agent实例
_data_agent = None

def _get_data_agent():
    """获取数据采集agent实例（懒加载）"""
    global _data_agent
    
    if _data_agent is None and LLM_AVAILABLE:
        try:
            # 尝试初始化LLM
            dashscope_key = os.getenv("DASHSCOPE_API_KEY")
            openai_key = os.getenv("OPENAI_API_KEY")
            
            if dashscope_key:
                try:
                    llm = ChatTongyi(
                        dashscope_api_key=dashscope_key,
                        model_name="qwen-turbo",
                        temperature=0.7
                    )
                    logger.info("使用阿里云千问模型初始化数据采集agent")
                except:
                    llm = None
            elif openai_key:
                llm = ChatOpenAI(
                    api_key=openai_key,
                    model="gpt-4o-mini",
                    temperature=0.7
                )
                logger.info("使用OpenAI模型初始化数据采集agent")
            else:
                llm = None
            
            if llm:
                _data_agent = create_enhanced_ashare_data_agent(llm)
                logger.info("增强版数据采集agent初始化成功")
            
        except Exception as e:
            logger.warning(f"数据采集agent初始化失败: {str(e)}")
    
    return _data_agent

def get_enhanced_ashare_company_news(
    stock_code: Annotated[str, "A股股票代码"],
    company_name: Annotated[str, "公司名称"],
    curr_date: Annotated[str, "当前日期，格式：YYYY-MM-DD"],
    lookback_days: Annotated[int, "回看天数"] = 7
) -> str:
    """
    获取增强版A股公司相关新闻
    如果增强agent可用，使用多数据源采集；否则回退到原有方法
    """
    data_agent = _get_data_agent()
    
    if data_agent:
        try:
            logger.info(f"使用增强版数据采集获取 {company_name}({stock_code}) 新闻")
            return data_agent.get_comprehensive_stock_news(stock_code, lookback_days)
        except Exception as e:
            logger.warning(f"增强版新闻采集失败，回退到基础方法: {str(e)}")
    
    # 回退到原有方法
    return get_ashare_company_news(stock_code, company_name, curr_date, lookback_days)

def get_enhanced_ashare_market_news(
    curr_date: Annotated[str, "当前日期，格式：YYYY-MM-DD"],
    lookback_days: Annotated[int, "回看天数"] = 3,
    limit: Annotated[int, "新闻数量限制"] = 20
) -> str:
    """
    获取增强版A股市场整体新闻
    """
    data_agent = _get_data_agent()
    
    if data_agent:
        try:
            logger.info("使用增强版数据采集获取市场新闻")
            return data_agent.get_market_sentiment_analysis("A股市场", lookback_days)
        except Exception as e:
            logger.warning(f"增强版市场新闻采集失败，回退到基础方法: {str(e)}")
    
    # 回退到原有方法
    return get_ashare_market_news(curr_date, lookback_days, limit)

def get_enhanced_ashare_policy_news(
    curr_date: Annotated[str, "当前日期，格式：YYYY-MM-DD"],
    lookback_days: Annotated[int, "回看天数"] = 7
) -> str:
    """
    获取增强版A股相关政策新闻
    """
    data_agent = _get_data_agent()
    
    if data_agent:
        try:
            logger.info("使用增强版数据采集获取政策新闻")
            return data_agent.get_market_sentiment_analysis("证监会 政策", lookback_days)
        except Exception as e:
            logger.warning(f"增强版政策新闻采集失败，回退到基础方法: {str(e)}")
    
    # 回退到原有方法
    return get_ashare_policy_news(curr_date, lookback_days)

def get_ashare_stock_announcements(
    stock_code: Annotated[str, "A股股票代码"],
    curr_date: Annotated[str, "当前日期，格式：YYYY-MM-DD"],
    lookback_days: Annotated[int, "回看天数"] = 30
) -> str:
    """
    获取A股股票公告（新增功能）
    """
    data_agent = _get_data_agent()
    
    if data_agent:
        try:
            logger.info(f"获取 {stock_code} 的公告数据")
            return data_agent.get_stock_announcements(stock_code, lookback_days)
        except Exception as e:
            logger.error(f"获取股票公告失败: {str(e)}")
            return f"获取股票 {stock_code} 公告数据失败: {str(e)}"
    else:
        return f"增强版数据采集不可用，无法获取 {stock_code} 的公告数据"

def get_ashare_interactive_qa(
    stock_code: Annotated[str, "A股股票代码"],
    curr_date: Annotated[str, "当前日期，格式：YYYY-MM-DD"],
    lookback_days: Annotated[int, "回看天数"] = 30
) -> str:
    """
    获取A股投资者互动问答（新增功能）
    """
    data_agent = _get_data_agent()
    
    if data_agent:
        try:
            logger.info(f"获取 {stock_code} 的互动问答数据")
            return data_agent.get_interactive_qa(stock_code, lookback_days)
        except Exception as e:
            logger.error(f"获取互动问答失败: {str(e)}")
            return f"获取股票 {stock_code} 互动问答失败: {str(e)}"
    else:
        return f"增强版数据采集不可用，无法获取 {stock_code} 的互动问答"

def get_enhanced_ashare_industry_analysis(
    industry: Annotated[str, "行业名称"],
    curr_date: Annotated[str, "当前日期，格式：YYYY-MM-DD"],
    lookback_days: Annotated[int, "回看天数"] = 14
) -> str:
    """
    获取增强版A股行业分析
    """
    data_agent = _get_data_agent()
    
    if data_agent:
        try:
            logger.info(f"获取 {industry} 行业分析")
            return data_agent.get_industry_analysis(industry, lookback_days)
        except Exception as e:
            logger.warning(f"增强版行业分析失败，回退到基础方法: {str(e)}")
    
    # 回退到原有方法
    return get_ashare_industry_analysis("000001")  # 使用示例股票代码

def search_ashare_comprehensive_data(
    keyword: Annotated[str, "搜索关键词"],
    data_types: Annotated[str, "数据类型"] = "news,announcement,interaction",
    limit: Annotated[int, "结果数量限制"] = 50
) -> str:
    """
    综合搜索A股相关数据（新增功能）
    """
    data_agent = _get_data_agent()
    
    if data_agent:
        try:
            logger.info(f"综合搜索: {keyword}")
            return data_agent.search_stock_data(keyword, data_types)
        except Exception as e:
            logger.error(f"综合搜索失败: {str(e)}")
            return f"搜索 '{keyword}' 失败: {str(e)}"
    else:
        return f"增强版数据采集不可用，无法搜索 '{keyword}'"

def get_ashare_data_quality_report() -> str:
    """
    获取A股数据质量报告（新增功能）
    """
    data_agent = _get_data_agent()
    
    if data_agent:
        try:
            logger.info("生成数据质量报告")
            return data_agent.get_data_quality_report()
        except Exception as e:
            logger.error(f"生成数据质量报告失败: {str(e)}")
            return f"生成数据质量报告失败: {str(e)}"
    else:
        return "增强版数据采集不可用，无法生成数据质量报告"

def export_ashare_data(
    output_path: Annotated[str, "导出文件路径"] = None
) -> str:
    """
    导出A股数据（新增功能）
    """
    data_agent = _get_data_agent()
    
    if data_agent:
        try:
            if not output_path:
                output_path = f"ashare_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            logger.info(f"导出数据到: {output_path}")
            return data_agent.export_data_excel(output_path)
        except Exception as e:
            logger.error(f"数据导出失败: {str(e)}")
            return f"数据导出失败: {str(e)}"
    else:
        return "增强版数据采集不可用，无法导出数据"

# 更新工具映射，保持向后兼容
ENHANCED_TOOLS_MAP = {
    # 增强版工具（优先使用）
    "get_comprehensive_stock_news": get_enhanced_ashare_company_news,
    "get_stock_announcements": get_ashare_stock_announcements,
    "get_interactive_qa": get_ashare_interactive_qa,
    "get_market_sentiment_analysis": get_enhanced_ashare_market_news,
    "get_industry_analysis": get_enhanced_ashare_industry_analysis,
    "search_stock_data": search_ashare_comprehensive_data,
    "get_data_quality_report": get_ashare_data_quality_report,
    "export_data": export_ashare_data,
    
    # 原有工具（保持兼容）
    "get_ashare_stock_data": get_ashare_stock_data,
    "get_ashare_financial_data": get_ashare_financial_data,
    "get_ashare_technical_indicators": get_ashare_technical_indicators,
    "get_ashare_market_sentiment": get_ashare_market_sentiment,
    "get_ashare_industry_analysis": get_ashare_industry_analysis,
    "get_ashare_company_news": get_enhanced_ashare_company_news,  # 使用增强版
    "get_ashare_market_news": get_enhanced_ashare_market_news,    # 使用增强版
    "get_ashare_policy_news": get_enhanced_ashare_policy_news,    # 使用增强版
    "search_ashare_stocks": search_ashare_stocks
}

def get_available_tools() -> List[str]:
    """获取所有可用工具列表"""
    return list(ENHANCED_TOOLS_MAP.keys())

def call_tool(tool_name: str, **kwargs) -> str:
    """调用工具的统一接口"""
    if tool_name in ENHANCED_TOOLS_MAP:
        try:
            return ENHANCED_TOOLS_MAP[tool_name](**kwargs)
        except Exception as e:
            logger.error(f"调用工具 {tool_name} 失败: {str(e)}")
            return f"调用工具 {tool_name} 失败: {str(e)}"
    else:
        return f"未知工具: {tool_name}"

def is_enhanced_mode_available() -> bool:
    """检查增强模式是否可用"""
    return _get_data_agent() is not None

def get_system_status() -> Dict[str, any]:
    """获取系统状态"""
    data_agent = _get_data_agent()
    
    status = {
        "enhanced_mode": data_agent is not None,
        "llm_available": LLM_AVAILABLE,
        "available_tools": len(ENHANCED_TOOLS_MAP),
        "data_sources": []
    }
    
    if data_agent:
        try:
            config = get_ashare_config()
            enabled_sources = [
                name for name, config in config.get("data_sources", {}).items()
                if config.get("enabled", False)
            ]
            status["data_sources"] = enabled_sources
        except:
            pass
    
    return status

# 导出所有功能
__all__ = [
    # 增强版新功能
    "get_enhanced_ashare_company_news",
    "get_enhanced_ashare_market_news", 
    "get_enhanced_ashare_policy_news",
    "get_ashare_stock_announcements",
    "get_ashare_interactive_qa",
    "get_enhanced_ashare_industry_analysis",
    "search_ashare_comprehensive_data",
    "get_ashare_data_quality_report",
    "export_ashare_data",
    
    # 工具管理
    "get_available_tools",
    "call_tool",
    "is_enhanced_mode_available",
    "get_system_status",
    "ENHANCED_TOOLS_MAP",
    
    # 原有功能（通过import *继承）
]