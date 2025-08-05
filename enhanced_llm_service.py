#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced LLM Service
集成阿里云DashScope和多种LLM服务
"""

import os
import asyncio
from typing import Dict, List, Optional, Any, Union
import json
from datetime import datetime

# 阿里云DashScope导入
try:
    import dashscope
    from dashscope import Generation
    HAS_DASHSCOPE = True
    print("✅ DashScope successfully imported")
except ImportError:
    HAS_DASHSCOPE = False
    print("❌ DashScope not available")

# LangChain集成
try:
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    from langchain_core.language_models.base import BaseLanguageModel
    HAS_LANGCHAIN = True
    print("✅ LangChain LLM integration available")
except ImportError:
    HAS_LANGCHAIN = False
    print("❌ LangChain not available")

class EnhancedLLMService:
    """增强的LLM服务"""
    
    def __init__(self, dashscope_api_key: str = None):
        self.dashscope_api_key = dashscope_api_key or os.getenv('DASHSCOPE_API_KEY')
        self.initialize_dashscope()
        
        # 模型配置
        self.models = {
            'qwen-turbo': {
                'provider': 'dashscope',
                'max_tokens': 1500,
                'temperature': 0.7,
                'suitable_for': ['general', 'analysis', 'reasoning']
            },
            'qwen-plus': {
                'provider': 'dashscope', 
                'max_tokens': 6000,
                'temperature': 0.8,
                'suitable_for': ['complex_analysis', 'detailed_report', 'multi_step']
            },
            'qwen-max': {
                'provider': 'dashscope',
                'max_tokens': 8000,
                'temperature': 0.9,
                'suitable_for': ['deep_thinking', 'creative_analysis', 'comprehensive']
            }
        }
    
    def initialize_dashscope(self):
        """初始化DashScope"""
        if HAS_DASHSCOPE and self.dashscope_api_key:
            try:
                dashscope.api_key = self.dashscope_api_key
                print(f"✅ DashScope initialized with key: {self.dashscope_api_key[:10]}...")
            except Exception as e:
                print(f"❌ DashScope initialization failed: {e}")
        else:
            print("⚠️ DashScope API key not available")
    
    async def ainvoke(self, prompt: Union[str, List[Dict]], model: str = 'qwen-turbo', **kwargs) -> str:
        """异步调用LLM"""
        if HAS_DASHSCOPE and self.dashscope_api_key:
            return await self._call_dashscope(prompt, model, **kwargs)
        else:
            return await self._fallback_response(prompt)
    
    async def _call_dashscope(self, prompt: Union[str, List[Dict]], model: str, **kwargs) -> str:
        """调用DashScope API"""
        try:
            # 处理不同格式的输入
            if isinstance(prompt, str):
                messages = [{'role': 'user', 'content': prompt}]
            elif isinstance(prompt, list):
                messages = prompt
            else:
                messages = [{'role': 'user', 'content': str(prompt)}]
            
            # 获取模型配置
            model_config = self.models.get(model, self.models['qwen-turbo'])
            
            # 调用API
            response = Generation.call(
                model=model,
                messages=messages,
                result_format='message',
                max_tokens=kwargs.get('max_tokens', model_config['max_tokens']),
                temperature=kwargs.get('temperature', model_config['temperature']),
                top_p=kwargs.get('top_p', 0.8),
                seed=kwargs.get('seed', 42)
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                print(f"DashScope API error: {response.status_code} - {response.message}")
                return await self._fallback_response(prompt)
                
        except Exception as e:
            print(f"DashScope call error: {e}")
            return await self._fallback_response(prompt)
    
    async def _fallback_response(self, prompt: Union[str, List[Dict]]) -> str:
        """备用响应"""
        await asyncio.sleep(0.1)  # 模拟延迟
        return f"基于传统分析方法的回应（LLM服务暂不可用）: {str(prompt)[:50]}..."
    
    async def multi_step_analysis(self, context: Dict[str, Any], analysis_type: str = 'comprehensive') -> Dict[str, Any]:
        """多步骤分析"""
        results = {
            'analysis_type': analysis_type,
            'timestamp': datetime.now().isoformat(),
            'steps': []
        }
        
        # 定义分析步骤
        steps = self._get_analysis_steps(analysis_type)
        
        for step_name, step_config in steps.items():
            try:
                step_prompt = self._build_step_prompt(step_name, step_config, context, results)
                
                response = await self.ainvoke(
                    step_prompt,
                    model=step_config.get('model', 'qwen-turbo'),
                    temperature=step_config.get('temperature', 0.7)
                )
                
                results['steps'].append({
                    'step': step_name,
                    'input': step_prompt[:200] + "..." if len(step_prompt) > 200 else step_prompt,
                    'output': response,
                    'model': step_config.get('model', 'qwen-turbo'),
                    'timestamp': datetime.now().isoformat()
                })
                
                # 将结果添加到上下文中供后续步骤使用
                context[f'{step_name}_result'] = response
                
            except Exception as e:
                print(f"Analysis step '{step_name}' failed: {e}")
                results['steps'].append({
                    'step': step_name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return results
    
    def _get_analysis_steps(self, analysis_type: str) -> Dict[str, Dict]:
        """获取分析步骤配置"""
        if analysis_type == 'comprehensive':
            return {
                'data_understanding': {
                    'model': 'qwen-turbo',
                    'temperature': 0.5,
                    'focus': '数据理解和预处理'
                },
                'fundamental_analysis': {
                    'model': 'qwen-plus',
                    'temperature': 0.7,
                    'focus': '基本面深度分析'
                },
                'technical_analysis': {
                    'model': 'qwen-turbo',
                    'temperature': 0.6,
                    'focus': '技术面分析'
                },
                'sentiment_analysis': {
                    'model': 'qwen-plus',
                    'temperature': 0.8,
                    'focus': '市场情绪和新闻分析'
                },
                'risk_assessment': {
                    'model': 'qwen-plus',
                    'temperature': 0.5,
                    'focus': '风险评估和控制'
                },
                'final_synthesis': {
                    'model': 'qwen-max',
                    'temperature': 0.9,
                    'focus': '综合决策和建议'
                }
            }
        elif analysis_type == 'quick':
            return {
                'quick_overview': {
                    'model': 'qwen-turbo',
                    'temperature': 0.7,
                    'focus': '快速概览分析'
                },
                'key_points': {
                    'model': 'qwen-turbo',
                    'temperature': 0.6,
                    'focus': '关键要点提取'
                }
            }
        else:
            return self._get_analysis_steps('comprehensive')
    
    def _build_step_prompt(self, step_name: str, step_config: Dict, context: Dict, results: Dict) -> str:
        """构建步骤提示"""
        base_context = f"""
股票分析任务 - {step_config['focus']}

股票信息:
- 代码: {context.get('symbol', 'N/A')}  
- 名称: {context.get('company_name', 'N/A')}
- 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        if step_name == 'data_understanding':
            return base_context + f"""
请分析以下数据的质量和关键信息:

实时行情数据:
{json.dumps(context.get('quote_data', {}), indent=2, ensure_ascii=False, default=str)}

历史数据摘要:
- 数据期间: {context.get('hist_period', 'N/A')}
- 数据条数: {context.get('hist_count', 'N/A')}

请评估:
1. 数据的完整性和可靠性
2. 关键价格和成交量信息
3. 需要重点关注的数据点
4. 数据质量评分（1-10分）
"""
        
        elif step_name == 'fundamental_analysis':
            return base_context + f"""
基于以下信息进行基本面分析:

公司基本信息:
{json.dumps(context.get('company_info', {}), indent=2, ensure_ascii=False, default=str)}

财务指标:
{json.dumps(context.get('financial_metrics', {}), indent=2, ensure_ascii=False, default=str)}

请分析:
1. 公司盈利能力和成长性
2. 估值水平（PE、PB等）
3. 财务健康状况
4. 行业地位和竞争优势
5. 基本面评分（1-100分）和投资建议
"""
        
        elif step_name == 'technical_analysis':
            return base_context + f"""
基于以下技术指标进行技术面分析:

技术指标:
{json.dumps(context.get('technical_indicators', {}), indent=2, ensure_ascii=False, default=str)}

价格走势:
{json.dumps(context.get('price_trend', {}), indent=2, ensure_ascii=False, default=str)}

请分析:
1. 当前趋势方向和强度
2. 支撑和阻力位
3. 买卖信号识别
4. 技术面健康度
5. 技术面评分（1-100分）和操作建议
"""
        
        elif step_name == 'sentiment_analysis':
            return base_context + f"""
基于以下新闻和市场信息进行情绪分析:

相关新闻:
{json.dumps(context.get('news_data', [])[:5], indent=2, ensure_ascii=False, default=str)}

市场情绪数据:
{json.dumps(context.get('sentiment_data', {}), indent=2, ensure_ascii=False, default=str)}

请分析:
1. 整体市场情绪倾向
2. 重要新闻事件影响
3. 投资者关注度和预期
4. 情绪面风险和机会
5. 情绪面评分（1-100分）
"""
        
        elif step_name == 'risk_assessment':
            return base_context + f"""
基于前期分析结果进行风险评估:

数据分析结果: {context.get('data_understanding_result', 'N/A')}
基本面分析: {context.get('fundamental_analysis_result', 'N/A')}
技术面分析: {context.get('technical_analysis_result', 'N/A')}
情绪面分析: {context.get('sentiment_analysis_result', 'N/A')}

请评估:
1. 主要风险因素识别
2. 风险等级评定（低/中/高）
3. 风险控制建议
4. 仓位管理策略
5. 止损和止盈建议
"""
        
        elif step_name == 'final_synthesis':
            return base_context + f"""
基于完整分析链进行最终综合决策:

完整分析历史:
{json.dumps([step['output'] for step in results.get('steps', [])], indent=2, ensure_ascii=False, default=str)}

请提供:
1. 综合投资建议（强烈买入/买入/持有/卖出/强烈卖出）
2. 目标价格区间
3. 投资逻辑总结（3-5个核心要点）
4. 风险提示和注意事项
5. 建议持有期限
6. 整体信心度（1-100%）

请确保建议具体、可操作，并基于前面的分析结果。
"""
        
        else:
            return base_context + f"请对 {context.get('symbol', 'N/A')} 进行 {step_config['focus']} 分析。"

# 全局实例
_llm_service = None

def get_llm_service() -> EnhancedLLMService:
    """获取LLM服务实例"""
    global _llm_service
    if _llm_service is None:
        _llm_service = EnhancedLLMService()
    return _llm_service

# 测试函数
async def test_llm_service():
    """测试LLM服务"""
    service = get_llm_service()
    
    print("=== 测试基础LLM调用 ===")
    response = await service.ainvoke("请简要分析一下当前A股市场的整体情况", model='qwen-turbo')
    print(f"响应: {response}")
    
    print("\n=== 测试多步骤分析 ===")
    context = {
        'symbol': '600036',
        'company_name': '招商银行',
        'quote_data': {'current_price': 37.5, 'change_pct': 2.1},
        'news_data': [{'title': '招商银行发布三季报', 'content': '业绩超预期'}]
    }
    
    analysis = await service.multi_step_analysis(context, 'quick')
    print(f"分析步骤数: {len(analysis['steps'])}")
    for step in analysis['steps']:
        print(f"步骤: {step['step']} - 输出长度: {len(step.get('output', ''))}")

if __name__ == "__main__":
    asyncio.run(test_llm_service())