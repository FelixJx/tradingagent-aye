from flask import Flask, request, jsonify, render_template
import os
import sys
from datetime import datetime
import traceback

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# 全局变量存储trading agent
trading_agent = None

@app.route('/')
def home():
    # 如果请求接受HTML，返回网页界面
    if 'text/html' in request.headers.get('Accept', ''):
        return render_template('index.html')
    
    # 否则返回JSON API信息
    return jsonify({
        "status": "TradingAgent Web Service",
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "message": "TradingAgent API is running!",
        "endpoints": {
            "/analyze": "POST - Analyze stock symbol",
            "/health": "GET - Health check",
            "/dashboard": "GET - Web dashboard"
        }
    })

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/api/info')
def api_info():
    return jsonify({
        "status": "TradingAgent Web Service",
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "message": "TradingAgent API is running!",
        "endpoints": {
            "/analyze": "POST - Analyze stock symbol",
            "/health": "GET - Health check",
            "/dashboard": "GET - Web dashboard"
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Service is running",
        "uptime": "Service operational"
    })

@app.route('/analyze', methods=['POST'])
def analyze_stock():
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        symbol = data.get('symbol', 'NVDA')
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # 模拟详细的股票分析结果
        analysis_result = {
            "symbol": symbol.upper(),
            "date": date,
            "analysis": {
                "recommendation": "BUY" if hash(symbol) % 3 == 0 else "HOLD" if hash(symbol) % 3 == 1 else "SELL",
                "price_target": round(150 + (hash(symbol) % 100), 2),
                "confidence": round(0.7 + (hash(symbol) % 30) / 100, 2),
                "risk_level": ["Low", "Medium", "High"][hash(symbol) % 3]
            },
            "technical_indicators": {
                "rsi": round(30 + (hash(symbol) % 40), 2),
                "moving_average_50": round(140 + (hash(symbol) % 50), 2),
                "moving_average_200": round(130 + (hash(symbol) % 60), 2),
                "volume_trend": ["Increasing", "Stable", "Decreasing"][hash(symbol) % 3]
            },
            "market_sentiment": {
                "bullish_signals": hash(symbol + date) % 5 + 1,
                "bearish_signals": hash(date + symbol) % 4 + 1,
                "neutral_signals": 3
            },
            "timestamp": datetime.now().isoformat(),
            "processing_time_ms": round((hash(symbol) % 500) + 100, 2)
        }
        
        return jsonify(analysis_result)
            
    except Exception as e:
        return jsonify({
            "error": f"Analysis failed: {str(e)}",
            "symbol": data.get('symbol', 'Unknown') if data else 'Unknown',
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    # 获取Render提供的端口
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting TradingAgent Flask app on port {port}")
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=port, debug=False)
