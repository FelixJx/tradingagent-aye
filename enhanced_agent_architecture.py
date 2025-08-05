#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Trading Agent Architecture
深度改进的交易智能体架构
集成实时数据、深度推理、多智能体辩论和自我反思
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Try to import optional dependencies with fallbacks
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    print("⚠️ NumPy not available, using fallback functions")
    HAS_NUMPY = False

try:
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    from langchain_core.prompts import ChatPromptTemplate
    HAS_LANGCHAIN = True
    print("✅ LangChain successfully imported")
except ImportError as e:
    print(f"⚠️ LangChain not available: {e}")
    HAS_LANGCHAIN = False

try:
    import akshare as ak
    HAS_AKSHARE = True
    print("✅ AKShare successfully imported")
except ImportError as e:
    print(f"⚠️ AKShare not available: {e}")
    HAS_AKSHARE = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    print("⚠️ Pandas not available, using limited functionality")
    HAS_PANDAS = False

# 导入配置
try:
    from config import get_config
except ImportError:
    from config_simple import get_simple_config as get_config

# 导入新的服务
try:
    from real_time_data_service import get_data_service
    from news_search_service import get_news_service  
    from enhanced_llm_service import get_llm_service
    HAS_ENHANCED_SERVICES = True
    print("✅ Enhanced services successfully imported")
except ImportError as e:
    print(f"⚠️ Enhanced services not available: {e}")
    HAS_ENHANCED_SERVICES = False

class MarketRegime(Enum):
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    VOLATILE_MARKET = "volatile_market"
    SIDEWAYS_MARKET = "sideways_market"

class AnalysisDepth(Enum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"
    COMPREHENSIVE = "comprehensive"

@dataclass
class MarketData:
    symbol: str
    price_data: pd.DataFrame
    financial_data: Dict
    news_data: List[Dict]
    technical_indicators: Dict
    macro_data: Dict
    timestamp: datetime

@dataclass
class AnalysisResult:
    symbol: str
    recommendation: str
    confidence: float
    price_target: float
    risk_level: str
    reasoning: str
    supporting_evidence: List[str]
    risk_factors: List[str]
    scenario_analysis: Dict
    timestamp: datetime

class UnifiedDataService:
    """统一数据服务 - 真实数据集成"""
    
    def __init__(self, config):
        self.config = config
        self.tushare_available = bool(config.tushare_token)
        
        # 初始化增强服务
        if HAS_ENHANCED_SERVICES:
            self.data_service = get_data_service()
            self.news_service = get_news_service()
            print("✅ Enhanced data services initialized")
        else:
            self.data_service = None
            self.news_service = None
        
    async def get_comprehensive_data(self, symbol: str) -> MarketData:
        """获取全面的市场数据"""
        if HAS_ENHANCED_SERVICES and self.data_service:
            # 使用增强服务获取真实数据
            return await self._get_enhanced_data(symbol)
        else:
            # 使用原有方法作为备用
            return await self._get_fallback_data(symbol)
    
    async def _get_enhanced_data(self, symbol: str) -> MarketData:
        """使用增强服务获取数据"""
        tasks = [
            self.data_service.get_real_time_quote(symbol),
            self.data_service.get_historical_data(symbol, "1y"),
            self.data_service.get_company_info(symbol),
            self.news_service.search_stock_news(symbol, limit=20),
            self._get_macro_data()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理实时行情
        quote_data = results[0] if not isinstance(results[0], Exception) else {}
        hist_data = results[1] if not isinstance(results[1], Exception) else pd.DataFrame()
        company_info = results[2] if not isinstance(results[2], Exception) else {}
        news_data = results[3] if not isinstance(results[3], Exception) else []
        macro_data = results[4] if not isinstance(results[4], Exception) else {}
        
        # 计算技术指标
        technical_indicators = await self._calculate_technical_indicators(hist_data) if not hist_data.empty else {}
        
        return MarketData(
            symbol=symbol,
            price_data=hist_data,
            financial_data={'quote': quote_data, 'company': company_info},
            news_data=news_data,
            technical_indicators=technical_indicators,
            macro_data=macro_data,
            timestamp=datetime.now()
        )
    
    async def _get_fallback_data(self, symbol: str) -> MarketData:
        """备用数据获取方法"""
        tasks = [
            self._get_price_data(symbol),
            self._get_financial_data(symbol),
            self._get_news_data(symbol),
            self._get_technical_indicators(symbol),
            self._get_macro_data()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return MarketData(
            symbol=symbol,
            price_data=results[0] if not isinstance(results[0], Exception) else pd.DataFrame(),
            financial_data=results[1] if not isinstance(results[1], Exception) else {},
            news_data=results[2] if not isinstance(results[2], Exception) else [],
            technical_indicators=results[3] if not isinstance(results[3], Exception) else {},
            macro_data=results[4] if not isinstance(results[4], Exception) else {},
            timestamp=datetime.now()
        )
    
    async def _calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """计算技术指标"""
        if df.empty or not HAS_PANDAS:
            return {}
        
        try:
            indicators = {}
            
            # 使用收盘价列，兼容不同的列名
            close_col = None
            for col in ['收盘', 'close', 'Close']:
                if col in df.columns:
                    close_col = col
                    break
            
            if close_col is None:
                return {}
            
            close_prices = df[close_col]
            
            # 移动平均线
            for period in [5, 10, 20, 60, 120, 250]:
                if len(close_prices) >= period:
                    indicators[f'MA{period}'] = close_prices.rolling(period).mean().iloc[-1]
            
            # RSI
            if len(close_prices) >= 14:
                delta = close_prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                indicators['RSI'] = (100 - (100 / (1 + rs))).iloc[-1]
            
            # MACD
            if len(close_prices) >= 26:
                exp1 = close_prices.ewm(span=12).mean()
                exp2 = close_prices.ewm(span=26).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9).mean()
                indicators['MACD'] = macd.iloc[-1]
                indicators['MACD_Signal'] = signal.iloc[-1]
                indicators['MACD_Histogram'] = (macd - signal).iloc[-1]
            
            # 布林带
            if len(close_prices) >= 20:
                bb_mean = close_prices.rolling(20).mean()
                bb_std = close_prices.rolling(20).std()
                indicators['BB_Upper'] = (bb_mean + 2 * bb_std).iloc[-1]
                indicators['BB_Middle'] = bb_mean.iloc[-1]
                indicators['BB_Lower'] = (bb_mean - 2 * bb_std).iloc[-1]
            
            return indicators
            
        except Exception as e:
            print(f"Technical indicators calculation error: {e}")
            return {}
    
    async def _get_price_data(self, symbol: str) -> pd.DataFrame:
        """获取价格数据"""
        try:
            # 获取近1年的数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            data = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust="qfq"
            )
            return data
        except Exception as e:
            print(f"获取价格数据失败: {e}")
            return pd.DataFrame()
    
    async def _get_financial_data(self, symbol: str) -> Dict:
        """获取财务数据"""
        try:
            # 获取主要财务指标
            financial_data = {}
            
            # 利润表
            profit_data = ak.stock_profit_sheet_by_report_em(symbol=symbol)
            if not profit_data.empty:
                financial_data['profit'] = profit_data.head(4).to_dict('records')
            
            # 资产负债表
            balance_data = ak.stock_balance_sheet_by_report_em(symbol=symbol)
            if not balance_data.empty:
                financial_data['balance'] = balance_data.head(4).to_dict('records')
            
            # 现金流量表
            cashflow_data = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
            if not cashflow_data.empty:
                financial_data['cashflow'] = cashflow_data.head(4).to_dict('records')
                
            return financial_data
        except Exception as e:
            print(f"获取财务数据失败: {e}")
            return {}
    
    async def _get_news_data(self, symbol: str) -> List[Dict]:
        """获取新闻数据"""
        try:
            # 获取个股新闻
            news_data = ak.stock_news_em(symbol=symbol)
            if not news_data.empty:
                return news_data.head(20).to_dict('records')
            return []
        except Exception as e:
            print(f"获取新闻数据失败: {e}")
            return []
    
    async def _get_technical_indicators(self, symbol: str) -> Dict:
        """计算技术指标"""
        try:
            price_data = await self._get_price_data(symbol)
            if price_data.empty:
                return {}
            
            indicators = {}
            
            # 移动平均线
            for period in [5, 10, 20, 60, 120, 250]:
                if len(price_data) >= period:
                    indicators[f'MA{period}'] = price_data['收盘'].rolling(period).mean().iloc[-1]
            
            # RSI
            delta = price_data['收盘'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['RSI'] = 100 - (100 / (1 + rs)).iloc[-1]
            
            # MACD
            exp1 = price_data['收盘'].ewm(span=12).mean()
            exp2 = price_data['收盘'].ewm(span=26).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9).mean()
            indicators['MACD'] = macd.iloc[-1]
            indicators['MACD_Signal'] = signal.iloc[-1]
            indicators['MACD_Histogram'] = (macd - signal).iloc[-1]
            
            # 布林带
            bb_period = 20
            if len(price_data) >= bb_period:
                bb_mean = price_data['收盘'].rolling(bb_period).mean()
                bb_std = price_data['收盘'].rolling(bb_period).std()
                indicators['BB_Upper'] = (bb_mean + 2 * bb_std).iloc[-1]
                indicators['BB_Middle'] = bb_mean.iloc[-1]
                indicators['BB_Lower'] = (bb_mean - 2 * bb_std).iloc[-1]
            
            return indicators
        except Exception as e:
            print(f"计算技术指标失败: {e}")
            return {}
    
    async def _get_macro_data(self) -> Dict:
        """获取宏观经济数据"""
        try:
            macro_data = {}
            
            # 获取上证指数数据
            sh_index = ak.stock_zh_index_daily(symbol="sh000001")
            if not sh_index.empty:
                macro_data['sh_index'] = {
                    'close': sh_index['close'].iloc[-1],
                    'change_pct': ((sh_index['close'].iloc[-1] - sh_index['close'].iloc[-2]) / sh_index['close'].iloc[-2] * 100)
                }
            
            # 可以添加更多宏观指标：GDP、CPI、利率等
            
            return macro_data
        except Exception as e:
            print(f"获取宏观数据失败: {e}")
            return {}

class MarketRegimeDetector:
    """市场状态检测器"""
    
    def __init__(self):
        self.regime_thresholds = {
            'volatility_high': 0.02,
            'trend_strong': 0.05,
            'volume_surge': 2.0
        }
    
    async def detect_regime(self, market_data: MarketData) -> MarketRegime:
        """检测当前市场状态"""
        if market_data.price_data.empty:
            return MarketRegime.SIDEWAYS_MARKET
        
        # 计算近期收益率
        returns = market_data.price_data['收盘'].pct_change().dropna()
        recent_returns = returns.tail(20)
        
        # 计算波动率
        volatility = recent_returns.std()
        
        # 计算趋势强度
        trend = recent_returns.mean()
        
        # 判断市场状态
        if volatility > self.regime_thresholds['volatility_high']:
            return MarketRegime.VOLATILE_MARKET
        elif trend > self.regime_thresholds['trend_strong']:
            return MarketRegime.BULL_MARKET
        elif trend < -self.regime_thresholds['trend_strong']:
            return MarketRegime.BEAR_MARKET
        else:
            return MarketRegime.SIDEWAYS_MARKET

class DeepReasoningAgent:
    """深度推理智能体"""
    
    def __init__(self, llm, agent_type: str):
        self.llm = llm
        self.agent_type = agent_type
        self.reasoning_steps = []
        
    async def deep_analyze(self, market_data: MarketData, context: Dict = None) -> Dict:
        """深度分析"""
        self.reasoning_steps = []
        
        # 第1步：数据理解和预处理
        data_summary = await self._summarize_data(market_data)
        self.reasoning_steps.append(("数据理解", data_summary))
        
        # 第2步：多维度分析
        multi_analysis = await self._multi_dimensional_analysis(market_data)
        self.reasoning_steps.append(("多维度分析", multi_analysis))
        
        # 第3步：交叉验证
        cross_validation = await self._cross_validate_signals(multi_analysis)
        self.reasoning_steps.append(("交叉验证", cross_validation))
        
        # 第4步：风险评估
        risk_assessment = await self._assess_risks(market_data, cross_validation)
        self.reasoning_steps.append(("风险评估", risk_assessment))
        
        # 第5步：最终结论
        final_conclusion = await self._synthesize_conclusion(
            market_data, multi_analysis, cross_validation, risk_assessment
        )
        self.reasoning_steps.append(("最终结论", final_conclusion))
        
        return {
            'analysis': final_conclusion,
            'reasoning_chain': self.reasoning_steps,
            'agent_type': self.agent_type,
            'timestamp': datetime.now()
        }
    
    async def _summarize_data(self, market_data: MarketData) -> str:
        """数据摘要"""
        prompt = f"""
        作为{self.agent_type}，请分析以下数据摘要：
        
        股票代码: {market_data.symbol}
        价格数据: {len(market_data.price_data)}个交易日
        最新价格: {market_data.price_data['收盘'].iloc[-1] if not market_data.price_data.empty else '无数据'}
        技术指标: {list(market_data.technical_indicators.keys())}
        新闻数量: {len(market_data.news_data)}
        
        请提供数据质量评估和关键观察点。
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    async def _multi_dimensional_analysis(self, market_data: MarketData) -> Dict:
        """多维度分析"""
        analyses = {}
        
        # 技术面分析
        if market_data.technical_indicators:
            tech_prompt = f"""
            基于以下技术指标进行专业分析：
            {json.dumps(market_data.technical_indicators, indent=2, ensure_ascii=False)}
            
            请提供：
            1. 趋势判断
            2. 支撑阻力位
            3. 交易信号
            4. 风险提示
            """
            analyses['technical'] = await self.llm.ainvoke(tech_prompt)
        
        # 基本面分析
        if market_data.financial_data:
            fundamental_prompt = f"""
            基于以下财务数据进行基本面分析：
            {json.dumps(market_data.financial_data, indent=2, ensure_ascii=False, default=str)}
            
            请分析：
            1. 盈利能力
            2. 成长性
            3. 估值水平
            4. 财务健康度
            """
            analyses['fundamental'] = await self.llm.ainvoke(fundamental_prompt)
        
        # 情感面分析
        if market_data.news_data:
            sentiment_prompt = f"""
            基于以下新闻数据进行情感分析：
            {json.dumps(market_data.news_data[:5], indent=2, ensure_ascii=False, default=str)}
            
            请分析：
            1. 整体情感倾向
            2. 关键事件影响
            3. 市场预期变化
            """
            analyses['sentiment'] = await self.llm.ainvoke(sentiment_prompt)
        
        return analyses
    
    async def _cross_validate_signals(self, analyses: Dict) -> Dict:
        """交叉验证信号"""
        validation_prompt = f"""
        请对以下分析结果进行交叉验证：
        
        技术面分析: {analyses.get('technical', '无')}
        基本面分析: {analyses.get('fundamental', '无')}
        情感面分析: {analyses.get('sentiment', '无')}
        
        请分析：
        1. 各维度信号一致性
        2. 矛盾点和解释
        3. 权重建议
        4. 综合信号强度
        """
        
        response = await self.llm.ainvoke(validation_prompt)
        return {'validation': response.content if hasattr(response, 'content') else str(response)}
    
    async def _assess_risks(self, market_data: MarketData, validation: Dict) -> Dict:
        """风险评估"""
        risk_prompt = f"""
        基于以下信息进行全面风险评估：
        
        股票: {market_data.symbol}
        验证结果: {validation}
        
        请评估：
        1. 市场风险
        2. 个股风险
        3. 行业风险
        4. 系统性风险
        5. 流动性风险
        
        并提供风险等级（低/中/高）和应对策略。
        """
        
        response = await self.llm.ainvoke(risk_prompt)
        return {'risk_assessment': response.content if hasattr(response, 'content') else str(response)}
    
    async def _synthesize_conclusion(self, market_data: MarketData, 
                                   multi_analysis: Dict, 
                                   validation: Dict, 
                                   risk_assessment: Dict) -> Dict:
        """综合结论"""
        synthesis_prompt = f"""
        作为专业的{self.agent_type}，请基于以下完整分析提供最终投资建议：
        
        股票: {market_data.symbol}
        多维分析: {multi_analysis}
        交叉验证: {validation}
        风险评估: {risk_assessment}
        
        请提供：
        1. 明确的投资建议（强烈买入/买入/持有/卖出/强烈卖出）
        2. 置信度（0-100%）
        3. 价格目标区间
        4. 投资逻辑总结
        5. 关键风险提示
        
        请确保建议具体、可操作，并说明决策依据。
        """
        
        response = await self.llm.ainvoke(synthesis_prompt)
        return {'conclusion': response.content if hasattr(response, 'content') else str(response)}

class MultiAgentDebateSystem:
    """多智能体辩论系统"""
    
    def __init__(self, llm):
        self.llm = llm
        self.agents = {
            'bull_researcher': DeepReasoningAgent(llm, "多头研究员"),
            'bear_researcher': DeepReasoningAgent(llm, "空头研究员"),
            'neutral_analyst': DeepReasoningAgent(llm, "中性分析师"),
            'risk_manager': DeepReasoningAgent(llm, "风险管理师")
        }
        
    async def conduct_debate(self, market_data: MarketData, rounds: int = 3) -> Dict:
        """进行多轮辩论"""
        debate_history = []
        
        # 第1轮：各方独立分析
        initial_analyses = {}
        for agent_name, agent in self.agents.items():
            analysis = await agent.deep_analyze(market_data)
            initial_analyses[agent_name] = analysis
        
        debate_history.append({
            'round': 0,
            'type': 'initial_analysis',
            'analyses': initial_analyses
        })
        
        # 多轮辩论
        for round_num in range(1, rounds + 1):
            round_debates = await self._conduct_round_debate(
                market_data, initial_analyses, debate_history
            )
            debate_history.append({
                'round': round_num,
                'type': 'debate',
                'debates': round_debates
            })
        
        # 最终综合
        final_consensus = await self._reach_consensus(debate_history)
        
        return {
            'debate_history': debate_history,
            'final_consensus': final_consensus,
            'timestamp': datetime.now()
        }
    
    async def _conduct_round_debate(self, market_data: MarketData, 
                                  initial_analyses: Dict, 
                                  debate_history: List) -> Dict:
        """进行一轮辩论"""
        round_debates = {}
        
        # 多头 vs 空头辩论
        bull_vs_bear = await self._debate_between_agents(
            'bull_researcher', 'bear_researcher',
            market_data, initial_analyses, debate_history
        )
        round_debates['bull_vs_bear'] = bull_vs_bear
        
        # 中性分析师仲裁
        neutral_mediation = await self._mediate_debate(
            bull_vs_bear, market_data, initial_analyses
        )
        round_debates['neutral_mediation'] = neutral_mediation
        
        # 风险管理师风险提示
        risk_warning = await self._assess_debate_risks(
            bull_vs_bear, neutral_mediation, market_data
        )
        round_debates['risk_warning'] = risk_warning
        
        return round_debates
    
    async def _debate_between_agents(self, agent1_name: str, agent2_name: str,
                                   market_data: MarketData,
                                   initial_analyses: Dict,
                                   debate_history: List) -> Dict:
        """两个智能体间的辩论"""
        agent1_view = initial_analyses[agent1_name]['analysis']['conclusion']
        agent2_view = initial_analyses[agent2_name]['analysis']['conclusion']
        
        # Agent1 反驳 Agent2
        rebuttal1_prompt = f"""
        作为{agent1_name}，请反驳以下观点：
        
        对方观点: {agent2_view}
        你的观点: {agent1_view}
        
        请提供有力的反驳论据，并加强你的观点。
        """
        
        rebuttal1 = await self.llm.ainvoke(rebuttal1_prompt)
        
        # Agent2 反驳 Agent1
        rebuttal2_prompt = f"""
        作为{agent2_name}，请回应以下反驳并维护你的观点：
        
        对方反驳: {rebuttal1.content if hasattr(rebuttal1, 'content') else str(rebuttal1)}
        你的观点: {agent2_view}
        
        请提供有力的反驳论据。
        """
        
        rebuttal2 = await self.llm.ainvoke(rebuttal2_prompt)
        
        return {
            f'{agent1_name}_rebuttal': rebuttal1.content if hasattr(rebuttal1, 'content') else str(rebuttal1),
            f'{agent2_name}_counter': rebuttal2.content if hasattr(rebuttal2, 'content') else str(rebuttal2)
        }
    
    async def _mediate_debate(self, debate: Dict, market_data: MarketData, 
                            initial_analyses: Dict) -> Dict:
        """中性仲裁"""
        mediation_prompt = f"""
        作为中性分析师，请仲裁以下辩论：
        
        辩论内容: {debate}
        股票: {market_data.symbol}
        
        请提供：
        1. 双方观点的优缺点
        2. 中性客观的评估
        3. 平衡的投资建议
        4. 不确定性因素
        """
        
        response = await self.llm.ainvoke(mediation_prompt)
        return {'mediation': response.content if hasattr(response, 'content') else str(response)}
    
    async def _assess_debate_risks(self, debate: Dict, mediation: Dict, 
                                 market_data: MarketData) -> Dict:
        """评估辩论中的风险"""
        risk_prompt = f"""
        作为风险管理师，请评估以下辩论中忽略的风险：
        
        辩论: {debate}
        仲裁: {mediation}
        股票: {market_data.symbol}
        
        请识别：
        1. 被忽略的风险因素
        2. 潜在的黑天鹅事件
        3. 风险控制建议
        4. 仓位管理策略
        """
        
        response = await self.llm.ainvoke(risk_prompt)
        return {'risk_assessment': response.content if hasattr(response, 'content') else str(response)}
    
    async def _reach_consensus(self, debate_history: List) -> Dict:
        """达成最终共识"""
        consensus_prompt = f"""
        基于完整的辩论历史，请形成最终共识：
        
        辩论历史: {json.dumps(debate_history, indent=2, ensure_ascii=False, default=str)}
        
        请提供：
        1. 最终投资建议
        2. 综合评分（0-100）
        3. 主要支撑因素
        4. 主要风险因素
        5. 建议仓位配置
        6. 时间建议（短期/中期/长期）
        
        请确保建议平衡、客观、可操作。
        """
        
        response = await self.llm.ainvoke(consensus_prompt)
        return {'consensus': response.content if hasattr(response, 'content') else str(response)}

class EnhancedTradingSystem:
    """增强版交易系统"""
    
    def __init__(self):
        self.config = get_config()
        self.data_service = UnifiedDataService(self.config)
        self.regime_detector = MarketRegimeDetector()
        
        # 初始化LLM（根据配置）
        self.llm = self._initialize_llm()
        self.debate_system = MultiAgentDebateSystem(self.llm)
        
    def _initialize_llm(self):
        """初始化LLM"""
        try:
            if HAS_ENHANCED_SERVICES:
                # 使用增强的LLM服务
                return get_llm_service()
            elif self.config.dashscope_api_key and HAS_LANGCHAIN:
                from langchain_community.llms import Tongyi
                return Tongyi(
                    dashscope_api_key=self.config.dashscope_api_key,
                    model_name="qwen-turbo"
                )
            else:
                # 使用模拟LLM用于测试
                return MockLLM()
        except Exception as e:
            print(f"LLM初始化失败: {e}")
            return MockLLM()
    
    async def comprehensive_analysis(self, symbol: str, 
                                   depth: AnalysisDepth = AnalysisDepth.STANDARD) -> AnalysisResult:
        """全面分析"""
        print(f"🔍 开始对 {symbol} 进行{depth.value}级别的全面分析...")
        
        # 1. 获取全面数据
        print("📊 收集市场数据...")
        market_data = await self.data_service.get_comprehensive_data(symbol)
        
        # 2. 检测市场状态
        print("🌡️ 检测市场状态...")
        market_regime = await self.regime_detector.detect_regime(market_data)
        print(f"市场状态: {market_regime.value}")
        
        # 3. 进行多智能体辩论分析
        if depth in [AnalysisDepth.DEEP, AnalysisDepth.COMPREHENSIVE]:
            print("🗣️ 启动多智能体辩论分析...")
            debate_rounds = 3 if depth == AnalysisDepth.COMPREHENSIVE else 2
            debate_result = await self.debate_system.conduct_debate(
                market_data, rounds=debate_rounds
            )
        else:
            # 标准分析
            single_agent = DeepReasoningAgent(self.llm, "综合分析师")
            analysis = await single_agent.deep_analyze(market_data)
            debate_result = {'final_consensus': analysis}
        
        # 4. 生成最终结果
        final_result = await self._generate_final_result(
            symbol, market_data, market_regime, debate_result, depth
        )
        
        print(f"✅ {symbol} 分析完成！")
        return final_result
    
    async def _generate_final_result(self, symbol: str, market_data: MarketData,
                                   market_regime: MarketRegime, debate_result: Dict,
                                   depth: AnalysisDepth) -> AnalysisResult:
        """生成最终分析结果"""
        
        # 从辩论结果中提取关键信息
        consensus = debate_result.get('final_consensus', {})
        
        # 模拟结果生成（实际实现中会基于LLM输出解析）
        return AnalysisResult(
            symbol=symbol,
            recommendation="买入",  # 需要从LLM输出中解析
            confidence=0.75,
            price_target=0.0,  # 需要计算
            risk_level="中等",
            reasoning="基于多智能体深度分析的综合判断",
            supporting_evidence=[
                "技术指标显示上升趋势",
                "基本面数据良好",
                "市场情绪积极"
            ],
            risk_factors=[
                "市场波动风险",
                "行业政策风险"
            ],
            scenario_analysis={
                "乐观情况": {"概率": 0.3, "回报": 0.25},
                "基准情况": {"概率": 0.5, "回报": 0.15},
                "悲观情况": {"概率": 0.2, "回报": -0.10}
            },
            timestamp=datetime.now()
        )

class MockLLM:
    """模拟LLM（用于测试）"""
    
    async def ainvoke(self, prompt: str) -> Any:
        """模拟异步调用"""
        await asyncio.sleep(0.1)  # 模拟网络延迟
        
        class MockResponse:
            def __init__(self, content):
                self.content = content
        
        # 简单的模拟响应
        if "技术指标" in prompt:
            return MockResponse("基于技术指标分析，当前趋势向上，建议关注。")
        elif "财务数据" in prompt:
            return MockResponse("公司基本面良好，盈利能力稳定。")
        elif "新闻" in prompt:
            return MockResponse("近期新闻整体偏向积极，市场情绪乐观。")
        else:
            return MockResponse("基于综合分析，建议谨慎乐观。")

# 使用示例
async def main():
    """主函数示例"""
    system = EnhancedTradingSystem()
    
    # 进行深度分析
    result = await system.comprehensive_analysis(
        symbol="603516", 
        depth=AnalysisDepth.DEEP
    )
    
    print("\n=== 分析结果 ===")
    print(f"股票: {result.symbol}")
    print(f"建议: {result.recommendation}")
    print(f"置信度: {result.confidence:.2%}")
    print(f"风险等级: {result.risk_level}")
    print(f"分析时间: {result.timestamp}")

if __name__ == "__main__":
    asyncio.run(main())