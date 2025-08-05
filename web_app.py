from flask import Flask, request, jsonify
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
    return jsonify({
        "status": "TradingAgent Web Service",
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "message": "TradingAgent API is running!",
        "endpoints": {
            "/analyze": "POST - Analyze stock symbol",
            "/health": "GET - Health check"
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Service is running"
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
        
        # 模拟分析结果
        return jsonify({
            "symbol": symbol,
            "date": date,
            "analysis": "Stock analysis completed",
            "recommendation": "Hold",
            "confidence": 0.85,
            "timestamp": datetime.now().isoformat()
        })
            
    except Exception as e:
        return jsonify({
            "error": f"Analysis failed: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    # 获取Render提供的端口
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask app on port {port}")
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=port, debug=False)
