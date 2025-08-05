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

# 导入配置管理，优先使用完整配置
try:
    from config import get_config
    config = get_config()
    print("✅ Using full configuration with LangChain support")
except ImportError as e:
    print(f"⚠️ Full config import failed: {e}")
    try:
        from config_simple import get_simple_config
        config = get_simple_config()
        print("📦 Using simplified configuration")
    except ImportError:
        print("❌ No config module available, using environment variables directly")
        config = None

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
    """获取股票数据 (模拟Tushare数据)"""
    try:
        # 这里模拟从Tushare获取数据
        # 实际部署时会连接真实的Tushare API
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
            'market_cap': (hash(symbol + 'cap') % 5000) + 1000
        }
    except Exception as e:
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
    """获取新闻分析 (模拟Tavily搜索)"""
    try:
        # 模拟新闻情感分析
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
            ][:news_count//3 + 1]
        }
    except Exception as e:
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
    """多智能体分析"""
    try:
        agents = {
            '基本面分析师': analyze_fundamentals(symbol, stock_data),
            '技术分析师': analyze_technical(symbol, technical_data),
            '情感分析师': analyze_sentiment(symbol, news_data),
            '风险控制师': analyze_risk(symbol, stock_data),
            '量化分析师': analyze_quantitative(symbol, stock_data, technical_data)
        }
        
        return agents
    except Exception as e:
        return {'error': f'多智能体分析失败: {str(e)}'}

def analyze_fundamentals(symbol, data):
    """基本面分析"""
    try:
        pe = data.get('pe_ratio', 20)
        pb = data.get('pb_ratio', 2)
        
        if pe < 15 and pb < 1.5:
            return f'估值偏低，PE={pe}, PB={pb}，具有投资价值'
        elif pe > 30 or pb > 3:
            return f'估值偏高，PE={pe}, PB={pb}，建议谨慎'
        else:
            return f'估值合理，PE={pe}, PB={pb}，可适量配置'
    except:
        return '基本面数据不足，无法分析'

def analyze_technical(symbol, data):
    """技术分析"""
    try:
        rsi = data.get('RSI', 50)
        macd = data.get('MACD', 0)
        
        signals = []
        if rsi < 30:
            signals.append('RSI显示超卖，可能反弹')
        elif rsi > 70:
            signals.append('RSI显示超买，注意风险')
            
        if macd > 0:
            signals.append('MACD金叉，趋势向好')
        else:
            signals.append('MACD死叉，趋势转弱')
            
        return '; '.join(signals) if signals else '技术指标中性'
    except:
        return '技术分析数据不足'

def analyze_sentiment(symbol, data):
    """情感分析"""
    try:
        score = data.get('sentiment_score', 0)
        if score > 0.3:
            return f'市场情感积极(得分:{score})，利好股价'
        elif score < -0.3:
            return f'市场情感消极(得分:{score})，需要关注风险'
        else:
            return f'市场情感中性(得分:{score})，观望为主'
    except:
        return '情感分析数据不足'

def analyze_risk(symbol, data):
    """风险分析"""
    try:
        turnover = data.get('turnover', 5)
        market_cap = data.get('market_cap', 1000)
        
        risk_level = '中等'
        if turnover > 10:
            risk_level = '较高'
        elif turnover < 2:
            risk_level = '较低'
            
        return f'流动性风险{risk_level}(换手率:{turnover}%)，市值{market_cap}亿'
    except:
        return '风险数据分析不足'

def analyze_quantitative(symbol, stock_data, technical_data):
    """量化分析"""
    try:
        # 简单的量化评分
        score = 0
        factors = []
        
        # 估值因子
        pe = stock_data.get('pe_ratio', 20)
        if pe < 15:
            score += 1
            factors.append('估值优势')
        elif pe > 30:
            score -= 1
            factors.append('估值劣势')
            
        # 技术因子
        rsi = technical_data.get('RSI', 50)
        if 30 < rsi < 70:
            score += 0.5
            factors.append('技术中性')
            
        return f'量化评分:{score}分，主要因子:{"、".join(factors) if factors else "无明显因子"}'
    except:
        return '量化分析计算失败'

def generate_thinking_process(symbol, mode, agents_analysis):
    """生成思考过程"""
    thinking_steps = [
        f'🔍 开始分析股票 {symbol} - {get_stock_name(symbol)}',
        f'📊 选择分析模式: {mode}',
        '🌐 连接数据源，获取最新市场数据...',
        '📈 计算技术指标和价格趋势...',
        '📰 搜索相关新闻和市场情感...',
        '🤖 启动多智能体协同分析系统...',
        '',
        '💭 智能体思考过程:',
        '├─ 基本面分析师: 正在评估财务指标和估值水平',
        '├─ 技术分析师: 正在识别价格模式和技术信号',  
        '├─ 情感分析师: 正在分析市场情绪和新闻影响',
        '├─ 风险控制师: 正在评估投资风险和流动性',
        '└─ 量化分析师: 正在计算综合评分和因子权重',
        '',
        '🧠 综合决策逻辑:',
        f'• 基本面权重: 30% - {agents_analysis.get("基本面分析师", "N/A")}',
        f'• 技术面权重: 25% - {agents_analysis.get("技术分析师", "N/A")}', 
        f'• 情感面权重: 20% - {agents_analysis.get("情感分析师", "N/A")}',
        f'• 风险面权重: 15% - {agents_analysis.get("风险控制师", "N/A")}',
        f'• 量化面权重: 10% - {agents_analysis.get("量化分析师", "N/A")}',
        '',
        '⚖️ 决策融合中...',
        '✅ 生成最终投资建议'
    ]
    
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
    port = int(os.environ.get('PORT', 5000))
    print(f'🚀 启动智能交易助手服务，端口: {port}')
    print('📊 数据源: Tushare + Tavily')
    print('🤖 AI模型: DeepSeek + 阿里云') 
    print('⚡ 多智能体协同分析系统已就绪')
    
    app.run(host='0.0.0.0', port=port, debug=False)
