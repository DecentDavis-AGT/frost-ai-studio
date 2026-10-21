# -*- coding: utf-8 -*-
import os
import sys
from flask import Flask, request, jsonify

# Path setup taake frost_engine aur frost_tools direct mil sakein
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from frost_engine import frost_reply
from frost_tools import get_weather_report, get_live_news
try:
    from frost_engine import get_system_ram_info
except Exception:
    def get_system_ram_info(): return "RAM diagnostics standby."

app = Flask(__name__)

# Basic CORS headers taake web dashboard bina rukawat request bhej sake
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "engine": "FROST Python Core"})

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.json or {}
        msg = data.get('message', '').strip()
        model = data.get('model', 'frost_ultra')
        
        # Original Python FROST Brain call
        reply_text = frost_reply(msg, model=model)
        
        return jsonify({
            "status": "success",
            "reply": str(reply_text)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "reply": f"FROST Engine Error: {str(e)}"
        }), 500

@app.route('/api/weather', methods=['GET'])
def weather():
    city = request.args.get('city', 'Sadiqabad')
    return jsonify({"report": get_weather_report(city)})

@app.route('/api/news', methods=['GET'])
def news():
    return jsonify({"news": get_live_news()})

@app.route('/api/system', methods=['GET'])
def system_info():
    return jsonify({"diagnostics": get_system_ram_info()})

if __name__ == '__main__':
    print("==================================================")
    print("FROST Python Flask Bridge LIVE on Port 8000")
    print("Connected to Google AI Studio Web Dashboard")
    print("==================================================")
    app.run(host='127.0.0.1', port=8000, debug=False)