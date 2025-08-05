#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多智能体深度协作研究系统
让每个Agent发挥专业潜力，进行真正的深度分析和辩论
"""

import os
import sys
import json
import asyncio
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging
from dataclasses import dataclass
from enum import Enum

# 设置项目路径
sys.path.append(str(Path(__file__).parent))

# 尝试导入LLM
try:
    from langchain_openai import ChatOpenAI
    from langchain_community.chat_models import ChatTongyi
    from langchain.schema import SystemMessage, HumanMessage
    from langchain.prompts import PromptTemplate
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentType(Enum):
    FUNDAMENTAL_ANALYST = "fundamental_analyst"
    TECHNICAL_ANALYST = "technical_analyst"
    POLICY_ANALYST = "policy_analyst"
    MARKET_RESEARCHER = "market_researcher"
    BULL_RESEARCHER = "bull_researcher"
    BEAR_RESEARCHER = "bear_researcher"
    RISK_MANAGER = "risk_manager"
    PORTFOLIO_MANAGER = "portfolio_manager"
    DEBATE_MODERATOR = "debate_moderator"

@dataclass
class AgentPersonality:
    """Agent个性化设置"""
    name: str
    role: str
    expertise: List[str]
    thinking_style: str
    analysis_depth: str
    decision_bias: str
    personality_traits: List[str]

@dataclass
class ResearchQuestion:
    """研究问题"""
    question: str
    category: str
    priority: int
    requires_debate: bool
    target_agents: List[AgentType]

class DeepAnalysisAgent:
    """深度分析智能体基类"""
    
    def __init__(self, agent_type: AgentType, llm, personality: AgentPersonality):
        self.agent_type = agent_type
        self.llm = llm
        self.personality = personality
        self.analysis_history = []
        self.debate_positions = []
        
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return f"""
你是一位资深的{self.personality.role}，名字叫{self.personality.name}。

专业领域：{', '.join(self.personality.expertise)}
思维风格：{self.personality.thinking_style}
分析深度：{self.personality.analysis_depth}
决策倾向：{self.personality.decision_bias}
性格特征：{', '.join(self.personality.personality_traits)}

你的职责是：
1. 基于你的专业背景提供深度、独到的分析观点
2. 挑战其他分析师的观点，指出他们可能忽视的问题
3. 从你的专业角度提出尖锐的质疑和建议
4. 绝不人云亦云，要有自己独立的判断和立场
5. 分析要具体、量化、有依据，避免泛泛而谈

重要要求：
- 你的分析必须比普通的金融报告更深入、更专业
- 要能发现别人看不到的问题和机会
- 从你的专业角度提供独特价值
- 分析长度应该在800-1500字，确保深度和质量
- 使用具体数据、比例、趋势来支持你的观点
"""

    async def analyze(self, research_topic: str, available_data: Dict, context: str = "") -> str:
        """执行深度分析"""
        prompt = f"""
研究主题：{research_topic}

可用数据：
{json.dumps(available_data, ensure_ascii=False, indent=2)}

分析上下文：
{context}

请基于你的专业身份"{self.personality.role}"，对上述主题进行深度分析。

你的分析应该包括：
1. 从你的专业角度看到的核心问题
2. 具体的数据分析和趋势判断
3. 其他人可能忽视的关键风险或机会
4. 基于你的经验的独特见解
5. 具体的建议和预测

记住：你的分析要比ChatGPT、Claude等通用AI更专业、更深入、更有价值！
"""
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            analysis = response.content
            
            # 记录分析历史
            self.analysis_history.append({
                'topic': research_topic,
                'analysis': analysis,
                'timestamp': datetime.now()
            })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Agent {self.personality.name} 分析失败: {str(e)}")
            return f"分析失败: {str(e)}"

    async def debate_respond(self, opponent_view: str, topic: str, round_num: int) -> str:
        """辩论回应"""
        prompt = f"""
辩论主题：{topic}
辩论轮次：第{round_num}轮

对方观点：
{opponent_view}

请作为{self.personality.role}，针对对方的观点进行反驳或补充。

要求：
1. 指出对方观点的不足或错误
2. 提供你的反证或补充证据
3. 基于你的专业判断给出不同的结论
4. 保持专业但要有锋芒，不要模糊中庸
5. 长度控制在400-600字，观点要鲜明

记住：这是专业辩论，要有理有据，不是和稀泥！
"""
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            return f"辩论回应失败: {str(e)}"

class MultiAgentResearchSystem:
    """多智能体研究系统"""
    
    def __init__(self):
        self.agents = {}
        self.research_results = {}
        self.debate_records = []
        self.llm = self._initialize_llm()
        
        if self.llm:
            self._create_agents()
        
    def _initialize_llm(self):
        """初始化LLM"""
        if not LLM_AVAILABLE:
            logger.error("LangChain未安装，无法使用多智能体系统")
            return None
        
        # 优先尝试使用DeepSeek (通过OpenAI接口)
        deepseek_key = os.getenv("OPENAI_API_KEY", "sk-831cb74319af43ebbfd7ad5e13fd4dfd")
        if deepseek_key and deepseek_key.startswith("sk-"):
            try:
                logger.info("尝试使用DeepSeek API...")
                return ChatOpenAI(
                    api_key=deepseek_key,
                    base_url="https://api.deepseek.com",
                    model="deepseek-chat",
                    temperature=0.7,
                    max_tokens=4000,
                    timeout=60
                )
            except Exception as e:
                logger.warning(f"DeepSeek初始化失败: {e}")
                
        # 尝试使用阿里云千问
        dashscope_key = os.getenv("DASHSCOPE_API_KEY", "sk-e050041b41674ed7b87644895ebae718")
        if dashscope_key and dashscope_key.startswith("sk-"):
            try:
                logger.info("尝试使用阿里云千问...")
                return ChatTongyi(
                    dashscope_api_key=dashscope_key,
                    model_name="qwen-max",
                    temperature=0.7,
                    max_tokens=4000
                )
            except Exception as e:
                logger.warning(f"千问初始化失败: {e}")
        
        # 最后尝试标准OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and not openai_key.startswith("sk-831"):  # 避免重复尝试DeepSeek key
            try:
                logger.info("尝试使用OpenAI...")
                return ChatOpenAI(
                    api_key=openai_key,
                    model="gpt-4o-mini",
                    temperature=0.7,
                    max_tokens=4000
                )
            except Exception as e:
                logger.warning(f"OpenAI初始化失败: {e}")
        
        logger.error("所有LLM初始化失败，请检查API密钥配置")
        return None
    
    def _create_agents(self):
        """创建专业化的智能体团队"""
        
        # 基本面分析师 - 张明华
        self.agents[AgentType.FUNDAMENTAL_ANALYST] = DeepAnalysisAgent(
            AgentType.FUNDAMENTAL_ANALYST,
            self.llm,
            AgentPersonality(
                name="张明华",
                role="资深基本面分析师",
                expertise=["财务分析", "估值模型", "行业研究", "商业模式分析", "管理层评估"],
                thinking_style="严谨量化，注重细节，善于发现财务陷阱",
                analysis_depth="深入到财务报表每个科目，关注现金流和利润质量",
                decision_bias="偏向价值投资，重视安全边际",
                personality_traits=["挑剔", "谨慎", "数据导向", "长期主义"]
            )
        )
        
        # 技术分析师 - 李志强
        self.agents[AgentType.TECHNICAL_ANALYST] = DeepAnalysisAgent(
            AgentType.TECHNICAL_ANALYST,
            self.llm,
            AgentPersonality(
                name="李志强",
                role="首席技术分析师",
                expertise=["价格行为分析", "量价关系", "市场情绪", "资金流向", "技术形态"],
                thinking_style="直觉敏锐，善于捕捉市场节奏和情绪变化",
                analysis_depth="多时间周期分析，从分钟线到月线全覆盖",
                decision_bias="偏向趋势跟随，重视技术突破",
                personality_traits=["敏感", "果断", "灵活", "市场化"]
            )
        )
        
        # 政策分析师 - 王晓慧
        self.agents[AgentType.POLICY_ANALYST] = DeepAnalysisAgent(
            AgentType.POLICY_ANALYST,
            self.llm,
            AgentPersonality(
                name="王晓慧",
                role="政策研究专家",
                expertise=["产业政策", "监管政策", "货币政策", "财政政策", "国际贸易政策"],
                thinking_style="宏观视野，善于把握政策脉络和趋势",
                analysis_depth="从政策制定背景到执行效果的全链条分析",
                decision_bias="重视政策导向，关注政策风险",
                personality_traits=["深刻", "前瞻", "系统性", "政策敏感"]
            )
        )
        
        # 多头研究员 - 陈乐观
        self.agents[AgentType.BULL_RESEARCHER] = DeepAnalysisAgent(
            AgentType.BULL_RESEARCHER,
            self.llm,
            AgentPersonality(
                name="陈乐观",
                role="多头策略研究员",
                expertise=["成长股分析", "新兴行业", "创新商业模式", "市场机会挖掘"],
                thinking_style="积极乐观，善于发现投资机会和增长潜力",
                analysis_depth="深入挖掘公司成长逻辑和催化因素",
                decision_bias="偏向成长投资，看重未来潜力",
                personality_traits=["乐观", "积极", "创新思维", "机会导向"]
            )
        )
        
        # 空头研究员 - 刘谨慎
        self.agents[AgentType.BEAR_RESEARCHER] = DeepAnalysisAgent(
            AgentType.BEAR_RESEARCHER,
            self.llm,
            AgentPersonality(
                name="刘谨慎",
                role="风险分析专家",
                expertise=["风险识别", "危机分析", "估值泡沫", "财务造假识别", "行业衰退"],
                thinking_style="悲观谨慎，专门寻找投资风险和陷阱",
                analysis_depth="深入分析潜在风险因素和下行情景",
                decision_bias="偏向风险厌恶，重视资本保护",
                personality_traits=["谨慎", "质疑", "危机意识", "风险导向"]
            )
        )
        
        # 风险管理师 - 赵稳健
        self.agents[AgentType.RISK_MANAGER] = DeepAnalysisAgent(
            AgentType.RISK_MANAGER,
            self.llm,
            AgentPersonality(
                name="赵稳健",
                role="风险管理专家",
                expertise=["风险度量", "组合管理", "流动性管理", "压力测试", "风险对冲"],
                thinking_style="系统性思维，注重风险控制和资产配置",
                analysis_depth="量化风险指标，建立风险管理框架",
                decision_bias="风险调整后收益最大化",
                personality_traits=["理性", "系统化", "稳健", "控制导向"]
            )
        )
        
        logger.info(f"成功创建 {len(self.agents)} 个专业智能体")
    
    async def conduct_deep_research(self, stock_code: str, company_name: str) -> Dict[str, Any]:
        """进行深度多智能体研究"""
        logger.info(f"🚀 启动多智能体深度研究: {company_name}({stock_code})")
        
        if not self.llm:
            return {"error": "LLM未初始化，无法进行研究"}
        
        # 准备研究数据
        research_data = await self._prepare_research_data(stock_code, company_name)
        
        # 第一阶段：独立深度分析
        logger.info("📊 第一阶段：各智能体独立深度分析")
        independent_analyses = await self._conduct_independent_analysis(stock_code, company_name, research_data)
        
        # 第二阶段：多轮专业辩论
        logger.info("🗣️ 第二阶段：多轮专业辩论")
        debate_results = await self._conduct_professional_debates(stock_code, independent_analyses)
        
        # 第三阶段：综合投资决策
        logger.info("🎯 第三阶段：综合投资决策")
        final_decision = await self._make_final_decision(stock_code, independent_analyses, debate_results)
        
        # 整合最终结果
        comprehensive_result = {
            "research_target": {"stock_code": stock_code, "company_name": company_name},
            "research_data": research_data,
            "independent_analyses": independent_analyses,
            "debate_results": debate_results,
            "final_decision": final_decision,
            "research_timestamp": datetime.now().isoformat()
        }
        
        # 保存研究结果
        await self._save_research_results(stock_code, comprehensive_result)
        
        return comprehensive_result
    
    async def _prepare_research_data(self, stock_code: str, company_name: str) -> Dict[str, Any]:
        """准备研究数据"""
        # 这里整合前面采集的所有数据
        research_data = {
            "basic_info": {
                "stock_code": stock_code,
                "company_name": company_name,
                "sector": "文化传媒",
                "market": "创业板",
                "listing_date": "2021-09-01"
            },
            "financial_data": {
                "revenue_growth": "21.76%",
                "net_profit_growth": "-23.87%",
                "gross_margin": "45.2%",
                "roe": "12.5%",
                "pe_ratio": "35.2",
                "debt_ratio": "28.5%",
                "current_ratio": "3.21"
            },
            "market_data": {
                "market_cap": "20亿",
                "current_price": "46.50",
                "ma5": "45.80",
                "ma20": "44.50",
                "rsi": "58.5",
                "volume_ratio": "1.2"
            },
            "industry_comparison": {
                "competitors": [
                    {"name": "中信出版", "market_cap": "350亿", "pe": "25.6", "roe": "15.2%"},
                    {"name": "中南传媒", "market_cap": "180亿", "pe": "18.5", "roe": "12.8%"}
                ],
                "market_share": "2.5%",
                "industry_ranking": "前5名"
            },
            "recent_news": [
                "2024年营收增长21.76%，但净利润下滑23.87%",
                "数字化转型成效显著，电子书业务占比提升",
                "面临股份解禁洪峰压力",
                "与知名作家续签独家合作协议"
            ],
            "policy_environment": {
                "cultural_industry_support": "国家大力支持文化产业发展",
                "digital_transformation": "数字出版政策利好",
                "copyright_protection": "版权保护政策加强"
            }
        }
        
        return research_data
    
    async def _conduct_independent_analysis(self, stock_code: str, company_name: str, research_data: Dict) -> Dict[str, str]:
        """进行独立分析"""
        analyses = {}
        
        # 并发执行各智能体的独立分析
        tasks = []
        for agent_type, agent in self.agents.items():
            task = agent.analyze(
                research_topic=f"{company_name}({stock_code})深度投资分析",
                available_data=research_data,
                context=f"请从{agent.personality.role}的专业角度进行深度分析"
            )
            tasks.append((agent_type, task))
        
        # 等待所有分析完成
        for agent_type, task in tasks:
            try:
                analysis = await task
                analyses[agent_type.value] = analysis
                logger.info(f"✅ {self.agents[agent_type].personality.name} 完成独立分析")
            except Exception as e:
                logger.error(f"❌ {agent_type.value} 分析失败: {str(e)}")
                analyses[agent_type.value] = f"分析失败: {str(e)}"
        
        return analyses
    
    async def _conduct_professional_debates(self, stock_code: str, independent_analyses: Dict) -> Dict[str, Any]:
        """进行专业辩论"""
        debate_results = {}
        
        # 辩论主题列表
        debate_topics = [
            {
                "topic": "果麦文化的估值是否合理？",
                "participants": [AgentType.FUNDAMENTAL_ANALYST, AgentType.BULL_RESEARCHER, AgentType.BEAR_RESEARCHER],
                "rounds": 3
            },
            {
                "topic": "果麦文化的商业模式是否可持续？",
                "participants": [AgentType.FUNDAMENTAL_ANALYST, AgentType.POLICY_ANALYST, AgentType.BEAR_RESEARCHER],
                "rounds": 3
            },
            {
                "topic": "技术面是否支持投资决策？",
                "participants": [AgentType.TECHNICAL_ANALYST, AgentType.BULL_RESEARCHER, AgentType.RISK_MANAGER],
                "rounds": 2
            }
        ]
        
        for debate_topic in debate_topics:
            topic = debate_topic["topic"]
            participants = debate_topic["participants"]
            rounds = debate_topic["rounds"]
            
            logger.info(f"🗣️ 开始辩论: {topic}")
            
            debate_record = {
                "topic": topic,
                "participants": [p.value for p in participants],
                "rounds": []
            }
            
            current_views = {}
            
            # 初始立场
            for participant in participants:
                agent = self.agents[participant]
                initial_view = await agent.analyze(
                    research_topic=f"对于问题'{topic}'的立场和观点",
                    available_data=independent_analyses,
                    context="请明确表达你的立场和理由"
                )
                current_views[participant] = initial_view
            
            # 多轮辩论
            for round_num in range(1, rounds + 1):
                logger.info(f"  第{round_num}轮辩论")
                round_responses = {}
                
                for i, participant in enumerate(participants):
                    # 获取其他参与者的观点
                    others_views = [view for p, view in current_views.items() if p != participant]
                    combined_others_view = "\n\n".join(others_views)
                    
                    agent = self.agents[participant]
                    response = await agent.debate_respond(
                        opponent_view=combined_others_view,
                        topic=topic,
                        round_num=round_num
                    )
                    round_responses[participant] = response
                
                # 更新观点
                current_views.update(round_responses)
                debate_record["rounds"].append({
                    "round": round_num,
                    "responses": {p.value: resp for p, resp in round_responses.items()}
                })
            
            debate_results[topic] = debate_record
        
        return debate_results
    
    async def _make_final_decision(self, stock_code: str, analyses: Dict, debates: Dict) -> Dict[str, Any]:
        """做出最终投资决策"""
        
        # 风险管理师综合评估
        risk_manager = self.agents[AgentType.RISK_MANAGER]
        
        final_evaluation_prompt = f"""
基于以下所有分析和辩论结果，请作为风险管理专家，给出最终的投资建议：

独立分析结果：
{json.dumps(analyses, ensure_ascii=False, indent=2)}

辩论结果：
{json.dumps(debates, ensure_ascii=False, indent=2)}

请提供：
1. 综合投资评级（强烈推荐/推荐/中性/不推荐/强烈不推荐）
2. 目标价位区间
3. 建议仓位比例
4. 持有期限建议
5. 关键风险点
6. 投资逻辑总结

要求：基于风险调整后的收益进行综合评估，给出明确的投资建议。
"""
        
        final_decision = await risk_manager.analyze(
            research_topic="综合投资决策",
            available_data={"analyses": analyses, "debates": debates},
            context=final_evaluation_prompt
        )
        
        return {
            "final_recommendation": final_decision,
            "decision_maker": risk_manager.personality.name,
            "decision_timestamp": datetime.now().isoformat()
        }
    
    async def _save_research_results(self, stock_code: str, results: Dict):
        """保存研究结果"""
        filename = f"多智能体深度研究_{stock_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 研究结果保存成功: {filename}")
        except Exception as e:
            logger.error(f"❌ 保存研究结果失败: {str(e)}")
    
    def generate_research_report(self, results: Dict) -> str:
        """生成研究报告"""
        stock_code = results["research_target"]["stock_code"]
        company_name = results["research_target"]["company_name"]
        
        report = f"""
# {company_name}({stock_code}) 多智能体深度研究报告

## 研究团队
"""
        
        for agent_type, agent in self.agents.items():
            report += f"- **{agent.personality.name}** ({agent.personality.role})\n"
        
        report += f"""
## 独立分析结果

"""
        
        for agent_name, analysis in results["independent_analyses"].items():
            agent_obj = next((a for a in self.agents.values() if a.agent_type.value == agent_name), None)
            if agent_obj:
                report += f"### {agent_obj.personality.name} - {agent_obj.personality.role}\n\n"
                report += f"{analysis}\n\n---\n\n"
        
        report += f"""
## 专业辩论结果

"""
        
        for topic, debate in results["debate_results"].items():
            report += f"### 辩论主题: {topic}\n\n"
            for round_data in debate["rounds"]:
                report += f"**第{round_data['round']}轮辩论：**\n\n"
                for agent_type, response in round_data["responses"].items():
                    agent_obj = next((a for a in self.agents.values() if a.agent_type.value == agent_type), None)
                    if agent_obj:
                        report += f"**{agent_obj.personality.name}**: {response}\n\n"
            report += "---\n\n"
        
        report += f"""
## 最终投资决策

{results["final_decision"]["final_recommendation"]}

---

**决策制定者**: {results["final_decision"]["decision_maker"]}  
**研究完成时间**: {results["research_timestamp"]}
"""
        
        return report

async def main():
    """主函数"""
    print("🚀 启动多智能体深度协作研究系统")
    print("="*60)
    
    # 创建研究系统
    research_system = MultiAgentResearchSystem()
    
    if not research_system.llm:
        print("❌ LLM初始化失败，请配置API密钥")
        return
    
    # 进行深度研究
    stock_code = "301052"
    company_name = "果麦文化"
    
    print(f"🎯 研究目标: {company_name}({stock_code})")
    print("⏳ 预计耗时: 5-10分钟")
    print()
    
    start_time = time.time()
    
    try:
        # 执行研究
        results = await research_system.conduct_deep_research(stock_code, company_name)
        
        # 生成报告
        report = research_system.generate_research_report(results)
        
        # 保存报告
        report_filename = f"多智能体研究报告_{stock_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        total_time = time.time() - start_time
        
        print(f"\n🎉 多智能体深度研究完成！")
        print(f"⏱️ 总耗时: {total_time:.1f}秒")
        print(f"📄 研究报告: {report_filename}")
        print(f"📊 详细数据: 多智能体深度研究_{stock_code}_*.json")
        
        # 显示核心结论
        if "final_decision" in results:
            print("\n" + "="*60)
            print("🎯 最终投资决策预览:")
            print("="*60)
            decision = results["final_decision"]["final_recommendation"]
            print(decision[:500] + "..." if len(decision) > 500 else decision)
        
    except Exception as e:
        print(f"❌ 研究过程中出现错误: {str(e)}")
        logger.error(f"研究失败: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())