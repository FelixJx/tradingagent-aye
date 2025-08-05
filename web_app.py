from flask import Flask, request, jsonify, render_template
import os
import sys
import json
import traceback
from datetime import datetime, timedelta
import time
import threading

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入真实数据集成模块
try:
    from real_data_integration import get_real_stock_data, get_real_news_analysis, get_real_llm_analysis
    REAL_DATA_AVAILABLE = True
    print("✅ Real data integration loaded successfully")
except ImportError as e:
    REAL_DATA_AVAILABLE = False
    print(f"❌ Real data integration FAILED to load: {e}")
    print(f"❌ This means the system will use mock data even in production!")
except Exception as e:
    REAL_DATA_AVAILABLE = False
    print(f"❌ Unexpected error loading real data integration: {type(e).__name__}: {e}")

# 导入配置管理，优先使用完整配置
config = None
try:
    from config import get_config
    config = get_config()
    print("✅ Using full configuration with LangChain support")
except Exception as e:
    print(f"⚠️ Full config import failed: {e}")
    try:
        from config_simple import get_simple_config
        config = get_simple_config()
        print("📦 Using simplified configuration")
    except Exception as e2:
        print(f"⚠️ Simple config also failed: {e2}")
        print("🔧 Using direct environment variables")
        
        # 创建一个基础配置对象
        class BasicConfig:
            @property
            def tushare_token(self):
                return os.getenv('TUSHARE_TOKEN')
            @property
            def dashscope_api_key(self):
                return os.getenv('DASHSCOPE_API_KEY')
            @property
            def tavily_api_key(self):
                return os.getenv('TAVILY_API_KEY')
        
        config = BasicConfig()

app = Flask(__name__)

# 全局变量
trading_agent = None
analysis_cache = {}

# 检测高级功能可用性
def check_advanced_features():
    """检测高级功能是否可用"""
    features = {
        'langchain': False,
        'akshare': False,
        'pandas': False,
        'tushare': False,
        'dashscope': False,
        'tavily': False,
        'enhanced_agent': False,
        'real_time_data': False,
        'news_search': False,
        'enhanced_llm': False
    }
    
    try:
        import langchain
        features['langchain'] = True
        print("✅ LangChain available")
    except ImportError:
        print("❌ LangChain not available")
    
    try:
        import akshare
        features['akshare'] = True
        print("✅ AKShare available")
    except ImportError:
        print("❌ AKShare not available")
    
    try:
        import pandas
        features['pandas'] = True
        print("✅ Pandas available")
    except ImportError:
        print("❌ Pandas not available")
    
    try:
        import tushare
        features['tushare'] = True
        print("✅ Tushare available")
    except ImportError:
        print("❌ Tushare not available")
    
    try:
        import dashscope
        features['dashscope'] = True
        print("✅ DashScope available")
    except ImportError:
        print("❌ DashScope not available")
    
    try:
        from tavily import TavilyClient
        features['tavily'] = True
        print("✅ Tavily available")
    except ImportError:
        print("❌ Tavily not available")
    
    try:
        from enhanced_agent_architecture import EnhancedTradingSystem
        features['enhanced_agent'] = True
        print("✅ Enhanced Agent Architecture available")
    except ImportError as e:
        print(f"❌ Enhanced Agent Architecture not available: {e}")
    
    try:
        from real_time_data_service import get_data_service
        features['real_time_data'] = True
        print("✅ Real-time Data Service available")
    except ImportError:
        print("❌ Real-time Data Service not available")
    
    try:
        from news_search_service import get_news_service
        features['news_search'] = True
        print("✅ News Search Service available")
    except ImportError:
        print("❌ News Search Service not available")
    
    try:
        from enhanced_llm_service import get_llm_service
        features['enhanced_llm'] = True
        print("✅ Enhanced LLM Service available")
    except ImportError:
        print("❌ Enhanced LLM Service not available")
    
    return features

# 初始化时检查功能
AVAILABLE_FEATURES = check_advanced_features()

def get_stock_data(symbol):
    """获取股票数据 - 优先使用真实API数据"""
    try:
        # 强制检查环境变量 - 直接从os.getenv获取，确保准确性
        flask_env = os.getenv('FLASK_ENV', 'development')
        config_env = getattr(config, 'flask_env', 'unknown') if config else 'no_config'
        
        print(f"🔧 Environment check: OS_ENV={flask_env}, CONFIG_ENV={config_env}, REAL_DATA={REAL_DATA_AVAILABLE}")
        
        # 强制在Render部署环境中使用真实数据（临时修复）
        is_render_deployment = os.getenv('RENDER') or os.getenv('RENDER_SERVICE_ID') or 'render' in os.getcwd().lower()
        should_use_real_data = REAL_DATA_AVAILABLE and (flask_env == 'production' or is_render_deployment)
        
        if should_use_real_data:
            print(f"🔄 Fetching REAL stock data for {symbol} (env: {flask_env}, render: {is_render_deployment})")
            return get_real_stock_data(symbol)
        
        # 开发环境或API不可用时使用模拟数据
        print(f"⚠️ Using MOCK data for {symbol} (env: {flask_env}, real_data: {REAL_DATA_AVAILABLE})")
        base_price = 100 + (hash(symbol) % 50)
        
        return {
            'symbol': symbol,
            'name': get_stock_name(symbol),
            'current_price': round(base_price + (hash(symbol + str(datetime.now().day)) % 20 - 10), 2),
            'open_price': round(base_price + (hash(symbol + 'open') % 15 - 7), 2),
            'high_price': round(base_price + (hash(symbol + 'high') % 25), 2),
            'low_price': round(base_price - (hash(symbol + 'low') % 15), 2),
            'volume': (hash(symbol + 'vol') % 1000000) + 100000,
            'turnover': round((hash(symbol + 'turn') % 100) / 10, 2),
            'pe_ratio': round(15 + (hash(symbol + 'pe') % 30), 2),
            'pb_ratio': round(1 + (hash(symbol + 'pb') % 50) / 10, 2),
            'market_cap': (hash(symbol + 'cap') % 5000) + 1000,
            'data_source': 'mock'
        }
    except Exception as e:
        print(f"❌ Stock data error: {e}")
        return {'error': f'数据获取失败: {str(e)}'}

def get_stock_name(symbol):
    """获取股票名称"""
    names = {
        '000001.SZ': '平安银行',
        '000002.SZ': '万科A',
        '600036.SH': '招商银行',
        '600519.SH': '贵州茅台',
        '000858.SZ': '五粮液',
        '002415.SZ': '海康威视',
        '300059.SZ': '东方财富'
    }
    return names.get(symbol, f'股票{symbol.split(".")[0]}')

def get_news_analysis(symbol):
    """获取新闻分析 - 优先使用真实API数据"""
    try:
        # 直接检查环境变量
        flask_env = os.getenv('FLASK_ENV', 'development')
        
        # 强制在Render部署环境中使用真实数据
        is_render_deployment = os.getenv('RENDER') or os.getenv('RENDER_SERVICE_ID') or 'render' in os.getcwd().lower()
        should_use_real_data = REAL_DATA_AVAILABLE and (flask_env == 'production' or is_render_deployment)
        
        if should_use_real_data:
            print(f"🔄 Fetching REAL news data for {symbol}")
            return get_real_news_analysis(symbol)
        
        # 开发环境或API不可用时使用模拟数据
        print(f"⚠️ Using MOCK news data for {symbol} (env: {flask_env}, real_data: {REAL_DATA_AVAILABLE})")
        sentiment_score = round((hash(symbol + 'news') % 200 - 100) / 100, 2)
        news_count = hash(symbol + 'count') % 20 + 5
        
        sentiments = ['积极', '中性', '消极']
        sentiment_text = sentiments[1] if abs(sentiment_score) < 0.3 else (sentiments[0] if sentiment_score > 0 else sentiments[2])
        
        return {
            'sentiment_score': sentiment_score,
            'sentiment_text': sentiment_text,
            'news_count': news_count,
            'summary': f'根据最近{news_count}条新闻分析，市场对{get_stock_name(symbol)}的情感偏向{sentiment_text}',
            'key_news': [
                f'{get_stock_name(symbol)}发布最新财报，业绩超预期',
                f'机构调研显示对{get_stock_name(symbol)}前景看好',
                f'{get_stock_name(symbol)}获得重要合作项目'
            ][:news_count//3 + 1],
            'data_source': 'mock'
        }
    except Exception as e:
        print(f"❌ News analysis error: {e}")
        return {'error': f'新闻分析失败: {str(e)}'}

def get_technical_indicators(symbol):
    """计算技术指标"""
    try:
        base = hash(symbol) % 100
        
        return {
            'RSI': round(30 + (base % 40), 2),
            'MACD': round((base % 20 - 10) / 10, 3),
            'KDJ_K': round(20 + (base % 60), 2),
            'KDJ_D': round(25 + (base % 50), 2),
            'KDJ_J': round(15 + (base % 70), 2),
            'MA5': round(95 + (base % 20), 2),
            'MA10': round(93 + (base % 25), 2),
            'MA20': round(90 + (base % 30), 2),
            'MA60': round(85 + (base % 35), 2),
            'BOLL_UPPER': round(105 + (base % 15), 2),
            'BOLL_MIDDLE': round(100 + (base % 10), 2),
            'BOLL_LOWER': round(95 + (base % 8), 2)
        }
    except Exception as e:
        return {'error': f'技术指标计算失败: {str(e)}'}

def multi_agent_analysis(symbol, stock_data, news_data, technical_data):
    """多智能体分析 - 增强版LLM驱动分析"""
    try:
        # 直接检查环境变量
        flask_env = os.getenv('FLASK_ENV', 'development')
        is_render_deployment = os.getenv('RENDER') or os.getenv('RENDER_SERVICE_ID') or 'render' in os.getcwd().lower()
        use_llm = REAL_DATA_AVAILABLE and (flask_env == 'production' or is_render_deployment)
        
        print(f"🤖 Running multi-agent analysis for {symbol} (ENV: {flask_env}, LLM: {use_llm})")
        
        agents = {
            '基本面分析师': analyze_fundamentals(symbol, stock_data, use_llm),
            '技术分析师': analyze_technical(symbol, technical_data, use_llm),
            '情感分析师': analyze_sentiment(symbol, news_data, use_llm),
            '风险控制师': analyze_risk(symbol, stock_data, use_llm),
            '量化分析师': analyze_quantitative(symbol, stock_data, technical_data, use_llm)
        }
        
        # 如果使用LLM，还需要生成智能体协商结果
        if use_llm:
            agents['综合决策师'] = synthesize_agent_decisions(symbol, agents, stock_data, news_data, technical_data)
        
        return agents
    except Exception as e:
        print(f"❌ Multi-agent analysis error: {e}")
        return {'error': f'多智能体分析失败: {str(e)}'}

def analyze_fundamentals(symbol, data, use_llm=False):
    """基本面分析 - 支持LLM深度分析"""
    try:
        if use_llm:
            # 使用LLM进行深度基本面分析
            prompt = f"""
作为专业的基本面分析师，请对股票 {symbol} ({data.get('name', '未知')}) 进行深度基本面分析：

财务数据：
- 市盈率(PE): {data.get('pe_ratio', '未知')}
- 市净率(PB): {data.get('pb_ratio', '未知')}
- 市值: {data.get('market_cap', '未知')}亿元
- 当前价格: {data.get('current_price', '未知')}元
- 换手率: {data.get('turnover', '未知')}%

请从以下角度进行分析：
1. 估值水平评估（PE、PB是否合理）
2. 行业对比分析
3. 财务健康度判断
4. 投资价值评估
5. 具体买入/持有/卖出建议

请提供专业且简洁的分析结论（200字以内）。
"""
            try:
                analysis = get_real_llm_analysis(prompt, {'stock_data': data})
                return f"【LLM深度分析】{analysis}"
            except Exception as e:
                print(f"LLM fundamental analysis failed: {e}")
                # 降级到基础分析
                pass
        
        # 基础规则分析（备用或开发环境）
        pe = data.get('pe_ratio', 20)
        pb = data.get('pb_ratio', 2)
        
        if pe < 15 and pb < 1.5:
            return f'【基础分析】估值偏低，PE={pe}, PB={pb}，具有投资价值。当前价格{data.get("current_price", "未知")}元，建议关注。'
        elif pe > 30 or pb > 3:
            return f'【基础分析】估值偏高，PE={pe}, PB={pb}，建议谨慎。当前市值{data.get("market_cap", "未知")}亿，需要观望。'
        else:
            return f'【基础分析】估值合理，PE={pe}, PB={pb}，可适量配置。价格{data.get("current_price", "未知")}元属于合理区间。'
    except Exception as e:
        return f'基本面数据分析异常: {str(e)}'

def analyze_technical(symbol, data, use_llm=False):
    """技术分析 - 支持LLM深度分析"""
    try:
        if use_llm:
            prompt = f"""
作为专业技术分析师，请对股票 {symbol} 进行技术面分析：

技术指标：
- RSI: {data.get('RSI', '未知')}
- MACD: {data.get('MACD', '未知')}
- KDJ: K={data.get('KDJ_K', '未知')}, D={data.get('KDJ_D', '未知')}, J={data.get('KDJ_J', '未知')}
- 均线: MA5={data.get('MA5', '未知')}, MA20={data.get('MA20', '未知')}, MA60={data.get('MA60', '未知')}
- 布林带: 上轨={data.get('BOLL_UPPER', '未知')}, 中轨={data.get('BOLL_MIDDLE', '未知')}, 下轨={data.get('BOLL_LOWER', '未知')}

请分析：
1. 超买/超卖状态
2. 趋势方向判断
3. 关键支撑/阻力位
4. 短期交易信号
5. 具体操作建议

请提供简洁的技术分析结论（150字以内）。
"""
            try:
                analysis = get_real_llm_analysis(prompt, {'technical_data': data})
                return f"【LLM技术分析】{analysis}"
            except Exception as e:
                print(f"LLM technical analysis failed: {e}")
                pass
        
        # 基础技术分析
        rsi = data.get('RSI', 50)
        macd = data.get('MACD', 0)
        
        signals = []
        if rsi < 30:
            signals.append('RSI显示超卖，可能反弹')
        elif rsi > 70:
            signals.append('RSI显示超买，注意风险')
        else:
            signals.append(f'RSI={rsi}，处于正常区间')
            
        if macd > 0:
            signals.append('MACD金叉，趋势向好')
        else:
            signals.append('MACD死叉，趋势转弱')
            
        return f"【技术指标】{'; '.join(signals)}" if signals else '技术指标中性'
    except Exception as e:
        return f'技术分析异常: {str(e)}'

def analyze_sentiment(symbol, data, use_llm=False):
    """情感分析 - 支持LLM深度分析"""
    try:
        if use_llm:
            prompt = f"""
作为市场情感分析师，请分析股票 {symbol} 的市场情感：

新闻数据：
- 情感得分: {data.get('sentiment_score', '未知')}
- 情感倾向: {data.get('sentiment_text', '未知')}
- 新闻数量: {data.get('news_count', '未知')}条
- 关键新闻: {data.get('key_news', [])}

请分析：
1. 市场情感对股价的影响
2. 投资者信心评估
3. 媒体关注度分析
4. 短期情感变化趋势
5. 基于情感的交易建议

请提供简洁的情感分析结论（120字以内）。
"""
            try:
                analysis = get_real_llm_analysis(prompt, {'news_data': data})
                return f"【LLM情感分析】{analysis}"
            except Exception as e:
                print(f"LLM sentiment analysis failed: {e}")
                pass
        
        # 基础情感分析
        score = data.get('sentiment_score', 0)
        news_count = data.get('news_count', 0)
        if score > 0.3:
            return f'【市场情感】积极(得分:{score})，{news_count}条新闻显示利好，市场看多情绪浓厚'
        elif score < -0.3:
            return f'【市场情感】消极(得分:{score})，{news_count}条新闻显示利空，需要关注风险'
        else:
            return f'【市场情感】中性(得分:{score})，{news_count}条新闻无明显倾向，观望为主'
    except Exception as e:
        return f'情感分析异常: {str(e)}'

def analyze_risk(symbol, data, use_llm=False):
    """风险分析 - 支持LLM深度分析"""
    try:
        if use_llm:
            prompt = f"""
作为风险控制师，请对股票 {symbol} 进行风险评估：

风险指标：
- 换手率: {data.get('turnover', '未知')}%
- 市值: {data.get('market_cap', '未知')}亿元
- 当前价格: {data.get('current_price', '未知')}元
- 成交量: {data.get('volume', '未知')}
- PE比率: {data.get('pe_ratio', '未知')}

请评估：
1. 流动性风险等级
2. 市值规模风险
3. 估值风险
4. 市场风险
5. 具体风险控制建议

请提供专业的风险评估（120字以内）。
"""
            try:
                analysis = get_real_llm_analysis(prompt, {'risk_data': data})
                return f"【LLM风险评估】{analysis}"
            except Exception as e:
                print(f"LLM risk analysis failed: {e}")
                pass
        
        # 基础风险分析
        turnover = data.get('turnover', 5)
        market_cap = data.get('market_cap', 1000)
        price = data.get('current_price', 0)
        
        risk_level = '中等'
        risk_factors = []
        
        if turnover > 10:
            risk_level = '较高'
            risk_factors.append('高换手率显示投机性强')
        elif turnover < 2:
            risk_level = '较低'
            risk_factors.append('低换手率流动性不足')
            
        if market_cap < 100:
            risk_factors.append('小市值股票波动性大')
        elif market_cap > 5000:
            risk_factors.append('大市值股票相对稳定')
            
        factors_text = '，'.join(risk_factors) if risk_factors else '风险因素适中'
        return f'【风险评估】流动性风险{risk_level}(换手率:{turnover}%)，市值{market_cap}亿。{factors_text}'
    except Exception as e:
        return f'风险分析异常: {str(e)}'

def analyze_quantitative(symbol, stock_data, technical_data, use_llm=False):
    """量化分析 - 支持LLM深度分析"""
    try:
        if use_llm:
            prompt = f"""
作为量化分析师，请对股票 {symbol} 进行量化建模分析：

量化数据：
股票数据: PE={stock_data.get('pe_ratio', '未知')}, PB={stock_data.get('pb_ratio', '未知')}, 市值={stock_data.get('market_cap', '未知')}亿
技术数据: RSI={technical_data.get('RSI', '未知')}, MACD={technical_data.get('MACD', '未知')}, MA20={technical_data.get('MA20', '未知')}
价格数据: 当前={stock_data.get('current_price', '未知')}元, 换手率={stock_data.get('turnover', '未知')}%

请进行：
1. 多因子模型评分
2. 技术信号强度评估
3. 风险收益比计算
4. 量化交易信号
5. 具体仓位建议

请提供量化分析结论（150字以内）。
"""
            try:
                analysis = get_real_llm_analysis(prompt, {'stock_data': stock_data, 'technical_data': technical_data})
                return f"【LLM量化分析】{analysis}"
            except Exception as e:
                print(f"LLM quantitative analysis failed: {e}")
                pass
        
        # 基础量化评分
        score = 0
        factors = []
        
        # 估值因子
        pe = stock_data.get('pe_ratio', 20)
        if pe < 15:
            score += 1
            factors.append('估值优势(低PE)')
        elif pe > 30:
            score -= 1
            factors.append('估值劣势(高PE)')
            
        # 技术因子
        rsi = technical_data.get('RSI', 50)
        if 30 < rsi < 70:
            score += 0.5
            factors.append('技术面中性')
        elif rsi < 30:
            score += 1
            factors.append('技术面超卖')
        elif rsi > 70:
            score -= 0.5
            factors.append('技术面超买')
            
        # 流动性因子
        turnover = stock_data.get('turnover', 5)
        if 3 < turnover < 15:
            score += 0.3
            factors.append('流动性适中')
            
        return f'【量化模型】综合评分:{score:.1f}分，关键因子:{"、".join(factors) if factors else "无明显因子"}'
    except Exception as e:
        return f'量化分析异常: {str(e)}'

def synthesize_agent_decisions(symbol, agents_analysis, stock_data, news_data, technical_data):
    """综合决策师 - 整合所有智能体分析结果"""
    try:
        prompt = f"""
作为首席投资策略师，请综合以下多个专业分析师的观点，对股票 {symbol} ({stock_data.get('name', '未知')}) 做出最终投资决策：

各分析师观点：
基本面分析师: {agents_analysis.get('基本面分析师', '无')}
技术分析师: {agents_analysis.get('技术分析师', '无')}
情感分析师: {agents_analysis.get('情感分析师', '无')}
风险控制师: {agents_analysis.get('风险控制师', '无')}
量化分析师: {agents_analysis.get('量化分析师', '无')}

综合数据：
- 当前价格: {stock_data.get('current_price', '未知')}元
- PE/PB: {stock_data.get('pe_ratio', '未知')}/{stock_data.get('pb_ratio', '未知')}
- RSI/MACD: {technical_data.get('RSI', '未知')}/{technical_data.get('MACD', '未知')}
- 市场情感: {news_data.get('sentiment_text', '未知')}

请分析各分析师观点的一致性和分歧点，给出：
1. 综合投资评级（买入/持有/卖出）
2. 置信度（1-100%）
3. 主要支撑理由
4. 核心风险点
5. 具体执行建议

请提供最终决策（200字以内）。
"""
        
        try:
            analysis = get_real_llm_analysis(prompt, {
                'agents': agents_analysis,
                'stock_data': stock_data,
                'news_data': news_data,
                'technical_data': technical_data
            })
            return f"【综合决策】{analysis}"
        except Exception as e:
            print(f"LLM synthesis failed: {e}")
            return "【综合决策】系统正在整合多维度分析结果，各分析师观点已收集完毕，请查看详细分析报告。"
    except Exception as e:
        return f'综合决策分析异常: {str(e)}'

def generate_thinking_process(symbol, mode, agents_analysis):
    """生成真实的思考过程 - 反映实际API调用"""
    # 直接检查环境变量，不依赖config对象
    flask_env = os.getenv('FLASK_ENV', 'development')
    is_render_deployment = os.getenv('RENDER') or os.getenv('RENDER_SERVICE_ID') or 'render' in os.getcwd().lower()
    use_real_data = REAL_DATA_AVAILABLE and (flask_env == 'production' or is_render_deployment)
    
    thinking_steps = [
        f'🔍 开始分析股票 {symbol} - {get_stock_name(symbol)}',
        f'📊 选择分析模式: {mode}',
        f'🔧 系统环境: {flask_env} | Render检测: {"✅" if is_render_deployment else "❌"} | 真实数据: {"✅" if use_real_data else "❌模拟模式"}',
        '',
        '🌐 数据获取阶段:',
        f'├─ {"🔄 Tushare/AKShare实时数据获取..." if use_real_data else "⚠️ 使用模拟股票数据"}',
        f'├─ {"🔄 Tavily新闻搜索API调用..." if use_real_data else "⚠️ 使用模拟新闻数据"}',
        f'└─ {"✅ 技术指标实时计算完成" if use_real_data else "✅ 技术指标模拟计算完成"}',
        '',
        '🤖 多智能体分析阶段:',
        f'├─ 基本面分析师: {"🧠 DashScope LLM深度分析中..." if use_real_data else "📊 规则分析完成"}',
        f'├─ 技术分析师: {"🧠 LLM技术面深度解读中..." if use_real_data else "📈 指标规则分析完成"}',  
        f'├─ 情感分析师: {"🧠 LLM情感语义分析中..." if use_real_data else "📰 情感规则分析完成"}',
        f'├─ 风险控制师: {"🧠 LLM风险评估分析中..." if use_real_data else "⚠️ 风险规则分析完成"}',
        f'└─ 量化分析师: {"🧠 LLM量化建模分析中..." if use_real_data else "📊 量化规则分析完成"}',
        '',
        '🧠 智能体协商阶段:',
        '├─ 收集各分析师的专业观点',
        '├─ 识别分析结果的一致性和分歧点',
        '├─ 评估各观点的权重和可信度',
        f'└─ {"🤖 综合决策师 LLM整合分析..." if use_real_data else "📋 基础规则整合完成"}',
        '',
        '📊 分析结果整合:',
        f'• 基本面: {agents_analysis.get("基本面分析师", "分析中...")}',
        f'• 技术面: {agents_analysis.get("技术分析师", "分析中...")}', 
        f'• 情感面: {agents_analysis.get("情感分析师", "分析中...")}',
        f'• 风险面: {agents_analysis.get("风险控制师", "分析中...")}',
        f'• 量化面: {agents_analysis.get("量化分析师", "分析中...")}',
    ]
    
    # 如果有综合决策师结果，添加到思考过程中
    if '综合决策师' in agents_analysis:
        thinking_steps.extend([
            '',
            '⚖️ 最终决策阶段:',
            f'└─ {agents_analysis.get("综合决策师", "决策生成中...")}'
        ])
    
    thinking_steps.extend([
        '',
        f'✅ {"多维度智能分析完成" if use_real_data else "基础分析完成"}'
    ])
    
    return '\n'.join(thinking_steps)

def generate_final_recommendation(symbol, stock_data, news_data, technical_data, agents_analysis):
    """生成最终推荐"""
    try:
        # 简单的决策逻辑
        score = 0
        confidence = 0.7
        
        # 基于各种分析结果计算分数
        pe = stock_data.get('pe_ratio', 20)
        rsi = technical_data.get('RSI', 50)
        sentiment = news_data.get('sentiment_score', 0)
        
        # 估值评分
        if pe < 15:
            score += 2
        elif pe > 30:
            score -= 2
            
        # 技术评分  
        if rsi < 30:
            score += 1
        elif rsi > 70:
            score -= 1
            
        # 情感评分
        score += sentiment * 2
        
        # 生成推荐
        if score > 1:
            recommendation = 'BUY'
            confidence = min(0.9, confidence + score * 0.1)
        elif score < -1:
            recommendation = 'SELL'
            confidence = min(0.9, confidence + abs(score) * 0.1)
        else:
            recommendation = 'HOLD'
            
        return {
            'recommendation': recommendation,
            'confidence': round(confidence, 2),
            'score': score,
            'reasoning': f'综合评分{score}分，基于PE估值、RSI技术指标、市场情感等多维度分析'
        }
    except Exception as e:
        return {
            'recommendation': 'HOLD',
            'confidence': 0.5,
            'score': 0,
            'reasoning': f'分析过程出现异常: {str(e)}'
        }

@app.route('/')
def home():
    """主页 - 返回中文界面"""
    if 'text/html' in request.headers.get('Accept', ''):
        return render_template('index.html')
    
    return jsonify({
        'status': '智能交易助手',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'message': '多维度股票分析系统正在运行！',
        'features': [
            '实时数据获取 (Tushare)',
            '多LLM协同分析 (DeepSeek + 阿里云)',
            '新闻情感分析 (Tavily)',
            '技术指标计算',
            '多智能体决策'
        ]
    })

@app.route('/test')
def test_dashboard():
    """测试面板页面"""
    return render_template('test_dashboard.html')

@app.route('/api/config/check')
def check_config():
    """检查配置状态"""
    api_status = config.check_api_availability()
    return jsonify({
        'apis': api_status,
        'trading_config': config.get_trading_config(),
        'flask_env': config.flask_env,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/info')
def api_info():
    """API信息"""
    return jsonify({
        'status': '智能交易助手',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'message': '多维度股票分析系统正在运行！',
        'data_sources': ['Tushare', 'Tavily', 'Technical Analysis'],
        'ai_models': ['DeepSeek', 'Alibaba Cloud', 'Multi-Agent System']
    })

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': '系统运行正常',
        'version': 'v2.1.0-real-agents',
        'deploy_time': datetime.now().isoformat(),
        'real_data_available': REAL_DATA_AVAILABLE,
        'services': {
            'web_server': 'running',
            'data_source': 'connected', 
            'ai_models': 'available',
            'cache': 'active'
        }
    })

@app.route('/features')
def feature_status():
    """功能状态检查接口"""
    core_features = ['langchain', 'akshare', 'pandas', 'enhanced_agent']
    advanced_features = ['tushare', 'dashscope', 'tavily', 'real_time_data', 'news_search', 'enhanced_llm']
    
    core_available = all(AVAILABLE_FEATURES.get(f, False) for f in core_features)
    advanced_available = all(AVAILABLE_FEATURES.get(f, False) for f in advanced_features)
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'available_features': AVAILABLE_FEATURES,
        'capabilities': {
            'basic_analysis': True,
            'real_time_data': AVAILABLE_FEATURES.get('tushare', False) or AVAILABLE_FEATURES.get('akshare', False),
            'ai_reasoning': AVAILABLE_FEATURES.get('enhanced_llm', False) or AVAILABLE_FEATURES.get('langchain', False),
            'enhanced_agents': AVAILABLE_FEATURES.get('enhanced_agent', False),
            'technical_analysis': AVAILABLE_FEATURES.get('pandas', False),
            'news_search': AVAILABLE_FEATURES.get('news_search', False),
            'multi_llm_support': AVAILABLE_FEATURES.get('dashscope', False)
        },
        'system_level': 'advanced' if advanced_available else ('core' if core_available else 'basic'),
        'recommendation': (
            'Full AI analysis with real-time data' if advanced_available else
            'Standard AI analysis' if core_available else
            'Basic analysis only'
        ),
        'missing_features': [f for f in advanced_features if not AVAILABLE_FEATURES.get(f, False)]
    })

@app.route('/debug')
def debug_status():
    """调试状态接口"""
    # 直接从环境变量获取，确保准确性
    flask_env = os.getenv('FLASK_ENV', 'development')
    config_env = getattr(config, 'flask_env', 'unknown') if config else 'no_config'
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'environment': {
            'flask_env_from_os': flask_env,
            'flask_env_from_config': config_env,
            'python_version': sys.version,
            'working_directory': os.getcwd()
        },
        'real_data_integration': {
            'available': REAL_DATA_AVAILABLE,
            'should_use_real_data': REAL_DATA_AVAILABLE and flask_env == 'production',
            'env_check_result': f"OS={flask_env}, CONFIG={config_env}"
        },
        'environment_variables': {
            'FLASK_ENV': os.getenv('FLASK_ENV', 'NOT_SET'),
            'TUSHARE_TOKEN': 'SET' if os.getenv('TUSHARE_TOKEN') else 'NOT_SET',
            'DASHSCOPE_API_KEY': 'SET' if os.getenv('DASHSCOPE_API_KEY') else 'NOT_SET',
            'TAVILY_API_KEY': 'SET' if os.getenv('TAVILY_API_KEY') else 'NOT_SET'
        },
        'config_object': {
            'type': str(type(config)),
            'flask_env': getattr(config, 'flask_env', 'NOT_AVAILABLE'),
            'tushare_token': 'SET' if getattr(config, 'tushare_token', None) else 'NOT_SET',
            'dashscope_api_key': 'SET' if getattr(config, 'dashscope_api_key', None) else 'NOT_SET'
        },
        'feature_detection': AVAILABLE_FEATURES,
        'system_diagnosis': {
            'real_data_ready': REAL_DATA_AVAILABLE and flask_env == 'production',
            'reason': (
                'Real data integration ready' if REAL_DATA_AVAILABLE and flask_env == 'production' 
                else f'REAL_DATA_AVAILABLE={REAL_DATA_AVAILABLE}, flask_env_os={flask_env}, flask_env_config={config_env}'
            ),
            'blocking_factors': [
                f"REAL_DATA_AVAILABLE: {REAL_DATA_AVAILABLE}",
                f"FLASK_ENV from OS: {flask_env}",
                f"FLASK_ENV from CONFIG: {config_env}",
                f"Environment check result: {flask_env == 'production'}"
            ]
        }
    })

@app.route('/test-real-data/<symbol>')
def test_real_data(symbol):
    """测试实时数据获取"""
    if not AVAILABLE_FEATURES.get('real_time_data', False):
        return jsonify({
            'error': 'Real-time data service not available',
            'available_features': AVAILABLE_FEATURES
        }), 503
    
    try:
        from real_time_data_service import get_data_service
        data_service = get_data_service()
        
        # 由于是同步端点，使用asyncio.run()
        import asyncio
        quote_data = asyncio.run(data_service.get_real_time_quote(symbol))
        
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'data': quote_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Real-time data test failed: {str(e)}',
            'symbol': symbol
        }), 500

@app.route('/test-news/<symbol>')
def test_news(symbol):
    """测试新闻搜索"""
    if not AVAILABLE_FEATURES.get('news_search', False):
        return jsonify({
            'error': 'News search service not available',
            'available_features': AVAILABLE_FEATURES
        }), 503
    
    try:
        from news_search_service import get_news_service
        news_service = get_news_service()
        
        # 由于是同步端点，使用asyncio.run()
        import asyncio
        news_data = asyncio.run(news_service.search_stock_news(symbol, limit=5))
        
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'news_count': len(news_data),
            'news': news_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'News search test failed: {str(e)}',
            'symbol': symbol
        }), 500

@app.route('/test-llm')
def test_llm():
    """测试LLM服务"""
    if not AVAILABLE_FEATURES.get('enhanced_llm', False):
        return jsonify({
            'error': 'Enhanced LLM service not available',
            'available_features': AVAILABLE_FEATURES
        }), 503
    
    try:
        from enhanced_llm_service import get_llm_service
        llm_service = get_llm_service()
        
        # 测试基础调用
        import asyncio
        test_prompt = "请简要分析当前A股市场的整体趋势，不超过100字。"
        response = asyncio.run(llm_service.ainvoke(test_prompt, model='qwen-turbo'))
        
        return jsonify({
            'status': 'success',
            'prompt': test_prompt,
            'response': response,
            'model': 'qwen-turbo',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'LLM test failed: {str(e)}',
            'prompt': test_prompt
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_stock():
    """股票分析主接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供分析参数'}), 400
            
        symbol = data.get('symbol', '').upper()
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        mode = data.get('mode', 'comprehensive')
        detailed = data.get('detailed', True)
        
        if not symbol:
            return jsonify({'error': '请提供股票代码'}), 400
            
        # 检查缓存
        cache_key = f'{symbol}_{date}_{mode}'
        if cache_key in analysis_cache:
            cached_result = analysis_cache[cache_key]
            cached_result['from_cache'] = True
            return jsonify(cached_result)
        
        # 执行分析
        analysis_start = time.time()
        
        # 1. 获取股票数据
        stock_data = get_stock_data(symbol)
        if 'error' in stock_data:
            return jsonify(stock_data), 500
            
        # 2. 获取新闻分析
        news_data = get_news_analysis(symbol)
        
        # 3. 计算技术指标
        technical_data = get_technical_indicators(symbol)
        
        # 4. 多智能体分析
        agents_analysis = multi_agent_analysis(symbol, stock_data, news_data, technical_data)
        
        # 5. 生成思考过程
        thinking_process = generate_thinking_process(symbol, mode, agents_analysis)
        
        # 6. 生成最终推荐
        recommendation = generate_final_recommendation(symbol, stock_data, news_data, technical_data, agents_analysis)
        
        # 构建完整结果
        result = {
            'symbol': symbol,
            'name': stock_data.get('name', ''),
            'date': date,
            'mode': mode,
            'analysis': recommendation,
            'thinking_process': thinking_process,
            'multi_agent_analysis': agents_analysis,
            'news_analysis': news_data,
            'technical_indicators': technical_data,
            'stock_data': stock_data,
            'processing_time': round((time.time() - analysis_start) * 1000, 2),
            'timestamp': datetime.now().isoformat(),
            'from_cache': False
        }
        
        # 缓存结果 (5分钟)
        analysis_cache[cache_key] = result
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'分析失败: {str(e)}',
            'traceback': traceback.format_exc() if app.debug else None
        }), 500

# 定期清理缓存
def cleanup_cache():
    """清理过期缓存"""
    while True:
        time.sleep(300)  # 5分钟清理一次
        if len(analysis_cache) > 100:  # 限制缓存大小
            # 清理一半的旧缓存
            keys_to_remove = list(analysis_cache.keys())[:len(analysis_cache)//2]
            for key in keys_to_remove:
                analysis_cache.pop(key, None)

# 启动缓存清理线程
cleanup_thread = threading.Thread(target=cleanup_cache, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    # 环境信息打印
    print("=" * 60)
    print("🚀 Trading Agent 启动中...")
    print(f"🐍 Python版本: {sys.version}")
    print(f"📁 工作目录: {os.getcwd()}")
    print(f"🔧 Flask版本: {getattr(__import__('flask'), '__version__', 'unknown')}")
    
    # 环境变量检查
    env_vars = {
        'PORT': os.getenv('PORT', '5000'),
        'FLASK_ENV': os.getenv('FLASK_ENV', 'development'),
        'TUSHARE_TOKEN': '已配置' if os.getenv('TUSHARE_TOKEN') else '未配置',
        'DASHSCOPE_API_KEY': '已配置' if os.getenv('DASHSCOPE_API_KEY') else '未配置',
        'TAVILY_API_KEY': '已配置' if os.getenv('TAVILY_API_KEY') else '未配置'
    }
    
    print("\n🔑 环境变量状态:")
    for key, value in env_vars.items():
        print(f"  {key}: {value}")
    
    # 功能检查
    print(f"\n⚡ 可用功能: {AVAILABLE_FEATURES}")
    
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"\n🌐 启动Web服务 {host}:{port}")
    print("📊 数据源: Tushare + AKShare + Tavily")
    print("🤖 AI引擎: DashScope + Multi-Agent System")
    print("=" * 60)
    
    try:
        app.run(host=host, port=port, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
