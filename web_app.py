from flask import Flask, request, jsonify
import os
import sys
from datetime import datetime
import traceback

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.default_config import DEFAULT_CONFIG
except ImportError as e:
    print(f"Import error: {e}")
    TradingAgentsGraph = None
    DEFAULT_CONFIG = {}

app = Flask(__name__)

# 全局变量存储trading agent
trading_agent = None

def init_trading_agent():
    """初始化TradingAgent"""
    global trading_agent
    try:
        if TradingAgentsGraph is None:
            return False, "TradingAgentsGraph not available"
            
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "google" 
        config["backend_url"] = "https://generativelanguage.googleapis.com/v1"
        config["deep_think_llm"] = "gemini-2.0-flash"
        config["quick_think_llm"] = "gemini-2.0-flash"
        config["max_debate_rounds"] = 1
        config["online_tools"] = True
        
        trading_agent = TradingAgentsGraph(debug=True, config=config)
        return True, "TradingAgent initialized successfully"
    except Exception as e:
        return False, f"Failed to initialize: {str(e)}"

@app.route('/')
def home():
    return jsonify({
        "status": "TradingAgent Web Service",
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "/analyze": "POST - Analyze stock symbol",
            "/health": "GET - Health check"
        }
    })

@app.route('/health')
def health():
    global trading_agent
    agent_status = "initialized" if trading_agent else "not_initialized"
    return jsonify({
        "status": "healthy",
        "agent_status": agent_status,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/analyze', methods=['POST'])
def analyze_stock():
    global trading_agent
    
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        symbol = data.get('symbol')
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        if not symbol:
            return jsonify({"error": "Symbol is required"}), 400
        
        # 初始化agent（如果还没有）
        if trading_agent is None:
            success, message = init_trading_agent()
            if not success:
                return jsonify({"error": f"Agent initialization failed: {message}"}), 500
        
        # 执行分析
        try:
            result, decision = trading_agent.propagate(symbol, date)
            return jsonify({
                "symbol": symbol,
                "date": date,
                "result": str(result),
                "decision": str(decision),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                "error": f"Analysis failed: {str(e)}",
                "symbol": symbol,
                "date": date
            }), 500
            
    except Exception as e:
        return jsonify({
            "error": f"Request processing failed: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

@app.route('/init', methods=['POST'])
def initialize_agent():
    success, message = init_trading_agent()
    return jsonify({
        "success": success,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # 初始化trading agent
    init_success, init_message = init_trading_agent()
    print(f"Initialization: {init_message}")
    
    # 启动Flask应用
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
