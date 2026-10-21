# -*- coding: utf-8 -*-
import os
import sys
from flask import Flask, request, jsonify

# Base path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from frost_engine import frost_reply

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data = request.json or {}
        user_message = data.get('message', '').strip()
        model = data.get('model', 'frost_ultra')
        
        # Call your original Python FROST Engine
        reply = frost_reply(user_message, model=model)
        
        return jsonify({
            'status': 'success',
            'reply': str(reply)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'reply': f"FROST Engine Error: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("==================================================")
    print("FROST Python Bridge API Online on Port 8000!")
    print("Connecting Google AI Studio Dashboard to Local Brain")
    print("==================================================")
    app.run(host='127.0.0.1', port=8000, debug=False)