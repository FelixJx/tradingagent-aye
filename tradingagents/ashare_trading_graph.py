# -*- coding: utf-8 -*-
"""
A股交易代理图
整合所有A股智能体，实现A股市场的智能投资决策
"""

import os
from typing import Dict, List, Optional, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from datetime import datetime, timedelta
import json

# 导入A股智能体
from .agents.analysts.ashare_market_analyst import create_ashare_market_analyst
from .agents.analysts.ashare_fundamental_analyst import create_ashare_fundamental_analyst
from .agents.analysts.ashare_policy_analyst import create_ashare_policy_analyst
from .agents.researchers.ashare_bull_researcher import create_ashare_bull_researcher
from .agents.researchers.ashare_bear_researcher import create_ashare_bear_researcher
from .agents.ashare_risk_manager import create_ashare_risk_manager

# 导入配置
from .ashare_config import get_ashare_config, validate_ashare_config, DASHSCOPE_CONFIG

# 导入数据接口
from .dataflows.ashare_utils import (
    get_ashare_stock_list, get_ashare_stock_data, get_ashare_financial_data,
    get_ashare_technical_indicators, get_ashare_market_sentiment,
    get_ashare_industry_analysis, search_ashare_stocks
)
from .dataflows.ashare_news_utils import (
    get_ashare_company_news, get_ashare_market_news,
    get_ashare_policy_news, get_ashare_industry_news
)

class AShareTradingState:
    """
    A股交易状态管理
    """
    def __init__(self):
        self.messages: List = []
        self.stock_symbol: str = ""
        self.stock_name: str = ""
        self.analysis_date: str = datetime.now().strftime("%Y-%m-%d")
        self.market_data: Dict = {}
        self.financial_data: Dict = {}
        self.technical_data: Dict = {}
        self.news_data: Dict = {}
        self.sentiment_data: Dict = {}
        self.analyst_reports: Dict = {}
        self.researcher_reports: Dict = {}
        self.risk_assessment: Dict = {}
        self.final_decision: Dict = {}
        self.debate_round: int = 0
        self.max_debate_rounds: int = 3

class AShareTradingGraph:
    """
    A股交易代理图主类
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化A股交易代理图
        
        Args:
            config: 配置字典，如果为None则使用默认A股配置
        """
        # 使用A股专用配置
        self.config = config if config else get_ashare_config()
        
        # 验证配置
        if not validate_ashare_config(self.config):
            raise ValueError("A股配置验证失败")
        
        # 初始化LLM
        self.llm = self._init_llm()
        
        # 创建智能体
        self.agents = self._create_agents()
        
        # 构建图
        self.graph = self._build_graph()
        
        print("A股交易代理图初始化完成")
    
    def _init_llm(self):
        """
        初始化语言模型
        """
        provider = self.config.get("llm_provider", "openai")
        
        if provider == "dashscope":
            # 使用阿里云千问
            try:
                from langchain_community.llms import Tongyi
                return Tongyi(
                    dashscope_api_key=DASHSCOPE_CONFIG["api_key"],
                    model_name=self.config.get("quick_think_llm", "qwen-turbo"),
                    temperature=0.7
                )
            except ImportError:
                print("警告: 无法导入Tongyi，回退到OpenAI")
                provider = "openai"
        
        if provider == "openai":
            # 使用OpenAI
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=self.config.get("quick_think_llm", "gpt-3.5-turbo"),
                temperature=0.7
            )
        
        raise ValueError(f"不支持的LLM提供商: {provider}")
    
    def _create_agents(self):
        """
        创建所有智能体
        """
        agents = {}
        
        # 创建分析师团队
        agents["market_analyst"] = create_ashare_market_analyst(self.llm, self.config)
        agents["fundamental_analyst"] = create_ashare_fundamental_analyst(self.llm, self.config)
        agents["policy_analyst"] = create_ashare_policy_analyst(self.llm, self.config)
        
        # 创建研究员团队
        agents["bull_researcher"] = create_ashare_bull_researcher(self.llm, self.config)
        agents["bear_researcher"] = create_ashare_bear_researcher(self.llm, self.config)
        
        # 创建风险管理
        agents["risk_manager"] = create_ashare_risk_manager(self.llm, self.config)
        
        return agents
    
    def _build_graph(self):
        """
        构建交易决策图
        """
        # 创建状态图
        workflow = StateGraph(AShareTradingState)
        
        # 添加节点
        workflow.add_node("data_collection", self._data_collection_node)
        workflow.add_node("market_analysis", self._market_analysis_node)
        workflow.add_node("fundamental_analysis", self._fundamental_analysis_node)
        workflow.add_node("policy_analysis", self._policy_analysis_node)
        workflow.add_node("bull_research", self._bull_research_node)
        workflow.add_node("bear_research", self._bear_research_node)
        workflow.add_node("debate", self._debate_node)
        workflow.add_node("risk_management", self._risk_management_node)
        workflow.add_node("final_decision", self._final_decision_node)
        
        # 设置入口点
        workflow.set_entry_point("data_collection")
        
        # 添加边
        workflow.add_edge("data_collection", "market_analysis")
        workflow.add_edge("market_analysis", "fundamental_analysis")
        workflow.add_edge("fundamental_analysis", "policy_analysis")
        workflow.add_edge("policy_analysis", "bull_research")
        workflow.add_edge("bull_research", "bear_research")
        workflow.add_edge("bear_research", "debate")
        
        # 辩论循环逻辑
        workflow.add_conditional_edges(
            "debate",
            self._should_continue_debate,
            {
                "continue": "bull_research",
                "end": "risk_management"
            }
        )
        
        workflow.add_edge("risk_management", "final_decision")
        workflow.add_edge("final_decision", END)
        
        return workflow.compile()
    
    def _data_collection_node(self, state: AShareTradingState):
        """
        数据收集节点
        """
        print(f"正在收集 {state.stock_symbol} 的数据...")
        
        try:
            # 获取股票基本信息
            if state.stock_symbol:
                # 获取市场数据
                state.market_data = get_ashare_stock_data(
                    state.stock_symbol, 
                    days=self.config["analysis_config"]["lookback_days"]
                )
                
                # 获取财务数据
                state.financial_data = get_ashare_financial_data(state.stock_symbol)
                
                # 获取技术指标
                state.technical_data = get_ashare_technical_indicators(state.stock_symbol)
                
                # 获取市场情绪
                state.sentiment_data = get_ashare_market_sentiment(state.stock_symbol)
                
                # 获取新闻数据
                state.news_data = {
                    "company_news": get_ashare_company_news(state.stock_symbol, days=7),
                    "market_news": get_ashare_market_news(days=7),
                    "policy_news": get_ashare_policy_news(days=7)
                }
                
                print(f"数据收集完成: {state.stock_symbol}")
            
        except Exception as e:
            print(f"数据收集失败: {e}")
            state.messages.append(SystemMessage(content=f"数据收集失败: {e}"))
        
        return state
    
    def _market_analysis_node(self, state: AShareTradingState):
        """
        市场分析节点
        """
        print("正在进行市场技术分析...")
        
        # 构建分析消息
        analysis_prompt = f"""
请对股票 {state.stock_symbol} ({state.stock_name}) 进行全面的技术分析。

市场数据概况:
{json.dumps(state.market_data, ensure_ascii=False, indent=2)}

技术指标数据:
{json.dumps(state.technical_data, ensure_ascii=False, indent=2)}

请重点分析:
1. 价格趋势和关键技术位
2. 技术指标信号
3. 成交量分析
4. 支撑阻力位
5. 短中长期技术展望
"""
        
        messages = [HumanMessage(content=analysis_prompt)]
        result = self.agents["market_analyst"]({"messages": messages})
        
        state.analyst_reports["market_analysis"] = result["messages"][-1].content
        state.messages.extend(result["messages"])
        
        print("市场技术分析完成")
        return state
    
    def _fundamental_analysis_node(self, state: AShareTradingState):
        """
        基本面分析节点
        """
        print("正在进行基本面分析...")
        
        analysis_prompt = f"""
请对股票 {state.stock_symbol} ({state.stock_name}) 进行全面的基本面分析。

财务数据:
{json.dumps(state.financial_data, ensure_ascii=False, indent=2)}

公司新闻:
{state.news_data.get('company_news', '暂无')}

请重点分析:
1. 财务健康状况
2. 盈利能力和成长性
3. 估值水平
4. 行业地位和竞争优势
5. 财务风险评估
"""
        
        messages = [HumanMessage(content=analysis_prompt)]
        result = self.agents["fundamental_analyst"]({"messages": messages})
        
        state.analyst_reports["fundamental_analysis"] = result["messages"][-1].content
        state.messages.extend(result["messages"])
        
        print("基本面分析完成")
        return state
    
    def _policy_analysis_node(self, state: AShareTradingState):
        """
        政策分析节点
        """
        print("正在进行政策影响分析...")
        
        analysis_prompt = f"""
请分析当前政策环境对股票 {state.stock_symbol} ({state.stock_name}) 的影响。

政策新闻:
{state.news_data.get('policy_news', '暂无')}

市场新闻:
{state.news_data.get('market_news', '暂无')}

请重点分析:
1. 相关政策对公司的直接影响
2. 行业政策的影响
3. 宏观政策的传导效应
4. 政策风险和机遇
5. 政策催化剂分析
"""
        
        messages = [HumanMessage(content=analysis_prompt)]
        result = self.agents["policy_analyst"]({"messages": messages})
        
        state.analyst_reports["policy_analysis"] = result["messages"][-1].content
        state.messages.extend(result["messages"])
        
        print("政策影响分析完成")
        return state
    
    def _bull_research_node(self, state: AShareTradingState):
        """
        多头研究节点
        """
        print("正在进行多头投资逻辑分析...")
        
        # 整合所有分析报告
        all_analysis = "\n\n".join([
            f"## {key}\n{value}" for key, value in state.analyst_reports.items()
        ])
        
        research_prompt = f"""
基于以下分析报告，请为股票 {state.stock_symbol} ({state.stock_name}) 构建多头投资逻辑。

{all_analysis}

市场情绪数据:
{json.dumps(state.sentiment_data, ensure_ascii=False, indent=2)}

请重点阐述:
1. 核心投资亮点
2. 上涨催化剂
3. 估值优势
4. 成长潜力
5. 投资建议和目标价

如果存在空头观点，请有效反驳。
"""
        
        messages = [HumanMessage(content=research_prompt)]
        result = self.agents["bull_researcher"]({"messages": messages})
        
        state.researcher_reports["bull_research"] = result["messages"][-1].content
        state.messages.extend(result["messages"])
        
        print("多头投资逻辑分析完成")
        return state
    
    def _bear_research_node(self, state: AShareTradingState):
        """
        空头研究节点
        """
        print("正在进行空头风险分析...")
        
        # 整合所有分析报告
        all_analysis = "\n\n".join([
            f"## {key}\n{value}" for key, value in state.analyst_reports.items()
        ])
        
        research_prompt = f"""
基于以下分析报告，请为股票 {state.stock_symbol} ({state.stock_name}) 进行风险分析和空头逻辑构建。

{all_analysis}

多头观点:
{state.researcher_reports.get('bull_research', '')}

请重点分析:
1. 主要风险因素
2. 估值风险
3. 基本面风险
4. 政策风险
5. 技术面风险

请理性质疑多头观点，提出反驳意见。
"""
        
        messages = [HumanMessage(content=research_prompt)]
        result = self.agents["bear_researcher"]({"messages": messages})
        
        state.researcher_reports["bear_research"] = result["messages"][-1].content
        state.messages.extend(result["messages"])
        
        print("空头风险分析完成")
        return state
    
    def _debate_node(self, state: AShareTradingState):
        """
        辩论节点
        """
        state.debate_round += 1
        print(f"正在进行第 {state.debate_round} 轮辩论...")
        
        # 这里可以实现多头和空头的辩论逻辑
        # 简化实现，直接进入风险管理
        
        return state
    
    def _should_continue_debate(self, state: AShareTradingState):
        """
        判断是否继续辩论
        """
        if state.debate_round < state.max_debate_rounds:
            return "continue"
        else:
            return "end"
    
    def _risk_management_node(self, state: AShareTradingState):
        """
        风险管理节点
        """
        print("正在进行风险管理评估...")
        
        # 整合所有报告
        all_reports = {
            **state.analyst_reports,
            **state.researcher_reports
        }
        
        reports_summary = "\n\n".join([
            f"## {key}\n{value}" for key, value in all_reports.items()
        ])
        
        risk_prompt = f"""
作为风险管理专家，请基于以下所有分析报告，对股票 {state.stock_symbol} ({state.stock_name}) 做出最终投资决策。

{reports_summary}

请提供:
1. 综合风险评估
2. 明确的投资建议（买入/卖出/持有/观望）
3. 建议仓位
4. 止损位和目标价
5. 风险控制措施
6. 投资逻辑总结

请使用风险管理决策表格式输出最终评分和决策。
"""
        
        messages = [HumanMessage(content=risk_prompt)]
        result = self.agents["risk_manager"]({"messages": messages})
        
        state.risk_assessment = result["messages"][-1].content
        state.messages.extend(result["messages"])
        
        print("风险管理评估完成")
        return state
    
    def _final_decision_node(self, state: AShareTradingState):
        """
        最终决策节点
        """
        print("生成最终投资决策报告...")
        
        # 生成最终决策报告
        final_report = {
            "stock_symbol": state.stock_symbol,
            "stock_name": state.stock_name,
            "analysis_date": state.analysis_date,
            "analyst_reports": state.analyst_reports,
            "researcher_reports": state.researcher_reports,
            "risk_assessment": state.risk_assessment,
            "recommendation": "基于风险管理评估的最终建议"
        }
        
        state.final_decision = final_report
        
        print("最终投资决策报告生成完成")
        return state
    
    def analyze_stock(self, stock_symbol: str, stock_name: str = "") -> Dict:
        """
        分析单只股票
        
        Args:
            stock_symbol: 股票代码
            stock_name: 股票名称（可选）
            
        Returns:
            分析结果字典
        """
        print(f"开始分析A股股票: {stock_symbol} {stock_name}")
        
        # 初始化状态
        initial_state = AShareTradingState()
        initial_state.stock_symbol = stock_symbol
        initial_state.stock_name = stock_name
        initial_state.max_debate_rounds = self.config.get("max_debate_rounds", 3)
        
        # 运行图
        try:
            final_state = self.graph.invoke(initial_state)
            return final_state.final_decision
        except Exception as e:
            print(f"分析过程中出现错误: {e}")
            return {"error": str(e)}
    
    def screen_stocks(self, criteria: Dict = None) -> List[Dict]:
        """
        股票筛选
        
        Args:
            criteria: 筛选条件
            
        Returns:
            筛选结果列表
        """
        print("开始A股股票筛选...")
        
        try:
            # 获取股票列表
            stock_list = get_ashare_stock_list()
            
            # 应用筛选条件
            if criteria:
                # 这里可以实现复杂的筛选逻辑
                pass
            
            # 返回筛选结果
            return stock_list[:100]  # 限制返回数量
            
        except Exception as e:
            print(f"股票筛选失败: {e}")
            return []
    
    def batch_analyze(self, stock_list: List[str], max_stocks: int = 10) -> List[Dict]:
        """
        批量分析股票
        
        Args:
            stock_list: 股票代码列表
            max_stocks: 最大分析数量
            
        Returns:
            批量分析结果
        """
        print(f"开始批量分析 {len(stock_list[:max_stocks])} 只股票...")
        
        results = []
        for i, stock_symbol in enumerate(stock_list[:max_stocks]):
            print(f"正在分析第 {i+1}/{min(len(stock_list), max_stocks)} 只股票: {stock_symbol}")
            
            try:
                result = self.analyze_stock(stock_symbol)
                results.append(result)
            except Exception as e:
                print(f"分析 {stock_symbol} 时出错: {e}")
                results.append({"stock_symbol": stock_symbol, "error": str(e)})
        
        print("批量分析完成")
        return results

# 便捷函数
def create_ashare_trading_graph(config: Optional[Dict] = None) -> AShareTradingGraph:
    """
    创建A股交易代理图实例
    
    Args:
        config: 可选配置
        
    Returns:
        AShareTradingGraph实例
    """
    return AShareTradingGraph(config)

# 导出
__all__ = [
    "AShareTradingGraph",
    "AShareTradingState", 
    "create_ashare_trading_graph"
]