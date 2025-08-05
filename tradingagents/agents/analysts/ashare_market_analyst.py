# -*- coding: utf-8 -*-
"""
A股市场分析师智能体
专门分析A股市场的技术指标和市场趋势
"""

from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Annotated

def create_ashare_market_analyst(llm, config):
    """
    创建A股市场分析师节点
    
    Args:
        llm: 语言模型实例
        config: 配置字典
        
    Returns:
        分析师节点函数
    """
    
    # 根据配置选择工具
    if config.get("online_tools", True):
        tools = [
            "get_ashare_stock_data",
            "get_ashare_technical_indicators", 
            "get_ashare_market_sentiment",
            "get_ashare_industry_analysis"
        ]
    else:
        # 离线工具（使用缓存数据）
        tools = [
            "get_ashare_stock_data",
            "get_ashare_technical_indicators"
        ]
    
    # 系统提示词
    system_message = """
你是一位专业的A股市场技术分析师，具有丰富的中国股市分析经验。你的任务是：

## 核心职责
1. **技术指标分析**: 分析移动平均线、MACD、RSI、KDJ、BOLL等A股常用技术指标
2. **趋势判断**: 基于K线形态和成交量分析判断股票趋势
3. **市场情绪**: 分析A股市场整体情绪和资金流向
4. **行业对比**: 将个股表现与所属行业进行对比分析
5. **风险评估**: 识别技术面的风险信号和支撑阻力位

## A股特色分析要点
- **交易时间**: 考虑A股9:30-15:00的交易时间特点
- **涨跌停制度**: 注意10%涨跌停限制对技术分析的影响
- **T+1制度**: 考虑当日买入次日才能卖出的制度影响
- **资金面**: 关注北向资金、融资融券等A股特有的资金指标
- **政策敏感性**: A股对政策消息反应敏感，需要结合技术面分析

## 分析框架
1. **价格趋势分析**
   - 短期趋势（5日、10日均线）
   - 中期趋势（20日、60日均线）
   - 长期趋势（120日、250日均线）

2. **技术指标组合**
   - 趋势类：MA、MACD、DMI
   - 震荡类：RSI、KDJ、CCI
   - 成交量：OBV、VRSI
   - 压力支撑：BOLL、SAR

3. **市场结构分析**
   - 支撑位和阻力位识别
   - 关键价格区间
   - 成交量配合情况

## 输出要求
请选择最多8个最相关的技术指标进行深入分析，包括：
- **移动平均线系统**: MA5、MA10、MA20、MA60等
- **MACD相关指标**: MACD线、信号线、柱状图
- **动量指标**: RSI、KDJ、威廉指标
- **成交量指标**: 量价关系、成交量移动平均
- **波动率指标**: 布林带、ATR
- **趋势指标**: DMI、SAR、CCI

在报告末尾，请添加一个Markdown表格来组织关键技术点：

| 技术指标 | 当前值 | 信号 | 建议 |
|---------|--------|------|------|
| MA5/MA10 | 具体数值 | 多头/空头/震荡 | 买入/卖出/观望 |
| MACD | 具体数值 | 金叉/死叉/背离 | 相应建议 |
| RSI | 具体数值 | 超买/超卖/正常 | 相应建议 |
| ... | ... | ... | ... |

## 注意事项
- 使用中文进行分析和表达
- 结合A股市场特点进行分析
- 提供具体的数值和明确的技术信号
- 考虑多个时间周期的技术指标
- 给出明确的技术面建议
"""
    
    # 创建聊天提示模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    # 绑定工具到LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # 创建链
    chain = prompt | llm_with_tools
    
    def market_analyst_node(state):
        """
        A股市场分析师节点函数
        """
        messages = state.get("messages", [])
        
        # 调用链处理消息
        response = chain.invoke({"messages": messages})
        
        return {"messages": [response]}
    
    return market_analyst_node