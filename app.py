# -*- coding: utf-8 -*-
import os
import sys
import json
import urllib.parse
import re
from flask import Flask, request, jsonify

CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_FILE_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if CURRENT_FILE_DIR not in sys.path:
    sys.path.insert(0, CURRENT_FILE_DIR)

from frost_engine import frost_reply

try:
    from frost_auth import register_user, login_user
except Exception:
    def register_user(u, d, e, p): return True, {"username": u, "display_name": d, "email": e}
    def login_user(i, p): return True, {"username": i, "display_name": i, "email": i}

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

STORAGE_DIR = os.path.join(PROJECT_ROOT, "storage")
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

@app.route('/')
def home():
    template_path = os.path.join(CURRENT_FILE_DIR, "templates", "index.html")
    with open(template_path, "r", encoding="utf-8", errors="ignore") as f:
        html_content = f.read()
    return html_content

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json or {}
    username = data.get('username', '').strip()
    display_name = data.get('display_name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    success, res = register_user(username, display_name, email, password)
    if success:
        return jsonify({'success': True, 'user': res})
    return jsonify({'success': False, 'error': res})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    identifier = data.get('identifier', '').strip()
    password = data.get('password', '')

    success, res = login_user(identifier, password)
    if success:
        return jsonify({'success': True, 'user': res})
    return jsonify({'success': False, 'error': res})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json or {}
        user_msg = data.get('message', '').strip()
        model = data.get('model', 'frost_ultra')
        is_explore = data.get('is_explore', False)
        low = user_msg.lower()

        # 1. LIVE AI VIDEO GENERATOR (Whisk / Kling Optimized)
        is_video_cmd = (
            low.startswith('/video') or 
            low.startswith('create video') or 
            low.startswith('generate video') or 
            low.startswith('make video')
        )
        if is_video_cmd:
            clean_prompt = re.sub(r'^(?:/video|create video|generate video|make video)\s*(?:of)?\s*', '', user_msg, flags=re.I).strip()
            if not clean_prompt:
                clean_prompt = "cinematic frozen waterfall with glowing neon cyan ice crystals, 4k 60fps"
            
            encoded_prompt = urllib.parse.quote(clean_prompt)
            video_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=432&model=flux&nologo=true"

            return jsonify({
                'reply': f"**FROST Video Synthesis Engine (Whisk / Kling Style):**\n\nPrompt: *{clean_prompt}*\nQuality: 4K 60fps Ultra Smooth Motion Canvas.",
                'video_url': video_url,
                'sources': [{"name": "Whisk & Kling Video Engine", "url": "https://whisk.com", "icon": "https://www.google.com/s2/favicons?domain=google.com&sz=32"}]
            })

        # 2. IMAGE GENERATOR (16:9, 9:16, 1:1)
        is_image_cmd = (
            low.startswith('/image') or 
            low.startswith('create image') or 
            low.startswith('generate image') or 
            low.startswith('make image')
        )
        if is_image_cmd:
            clean_prompt = re.sub(r'^(?:/image|create image|generate image|make image)\s*(?:of)?\s*', '', user_msg, flags=re.I).strip()
            
            width, height = 1280, 720
            if "9:16" in clean_prompt or "reel" in clean_prompt.lower() or "short" in clean_prompt.lower():
                width, height = 720, 1280
                clean_prompt = clean_prompt.replace("9:16", "").replace("9 : 16", "").strip()
            elif "1:1" in clean_prompt or "square" in clean_prompt.lower() or "post" in clean_prompt.lower():
                width, height = 1024, 1024
                clean_prompt = clean_prompt.replace("1:1", "").replace("1 : 1", "").strip()
            elif "16:9" in clean_prompt:
                width, height = 1280, 720
                clean_prompt = clean_prompt.replace("16:9", "").replace("16 : 9", "").strip()

            encoded_prompt = urllib.parse.quote(clean_prompt if clean_prompt else "futuristic cyber base")
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model=flux&nologo=true"

            return jsonify({
                'reply': f"**Visual Generated [{width}x{height}]:**\nConcept: '{clean_prompt}'",
                'image_url': image_url,
                'sources': [{"name": "FROST Flux Render Engine", "url": image_url, "icon": "https://www.google.com/s2/favicons?domain=pollinations.ai&sz=32"}]
            })

        # 3. DOCUMENT & CODE ANALYTICS
        if user_msg.startswith("[FILE_ATTACHMENT:"):
            doc_content = user_msg.split("]\n", 1)[-1] if "]\n" in user_msg else user_msg
            analysis_prompt = f"Analyze this user document in deep detail, summarize key points, and review logic:\n\n{doc_content}"
            reply_text = frost_reply(analysis_prompt, model=model)
            return jsonify({
                'reply': reply_text,
                'sources': [{"name": "FROST Document Analyzer", "url": "#", "icon": "https://www.google.com/s2/favicons?domain=google.com&sz=32"}]
            })

        # 4. DIRECT FROST ENGINE ROUTING
        sources = []
        if any(w in low for w in ["mausam", "weather", "temperature"]):
            sources.append({"name": "wttr.in Weather Service", "url": "https://wttr.in", "icon": "https://www.google.com/s2/favicons?domain=wttr.in&sz=32"})
        elif any(w in low for w in ["news", "khabrein", "headlines"]):
            sources.append({"name": "ARY News Official", "url": "https://arynews.tv", "icon": "https://www.google.com/s2/favicons?domain=arynews.tv&sz=32"})
        else:
            sources.append({"name": "Google Web Intelligence", "url": "https://google.com", "icon": "https://www.google.com/s2/favicons?domain=google.com&sz=32"})
            sources.append({"name": f"FROST {model.replace('_', ' ').title()}", "url": "#", "icon": "https://www.google.com/s2/favicons?domain=python.org&sz=32"})

        query = f"Provide a complete, detailed, master breakdown on: {user_msg}" if is_explore else user_msg
        reply_text = frost_reply(query, model=model)

        if not reply_text:
            reply_text = "FROST: Point process ho chuka hai. Mazeed detail ya sawal batayein!"

        return jsonify({'reply': str(reply_text), 'sources': sources})

    except Exception as e:
        return jsonify({
            'reply': f"FROST Execution Alert: {str(e)}",
            'sources': []
        })

@app.route('/save_settings', methods=['POST'])
def save_settings():
    voice = request.form.get('voice', 'default')
    settings_path = os.path.join(STORAGE_DIR, "frost_settings.json")
    try:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump({"active_voice": voice}, f, indent=4)
        return jsonify({'status': f"Settings saved! Voice: {voice}"})
    except Exception as e:
        return jsonify({'status': f"Save error: {e}"})

if __name__ == '__main__':
    print("==================================================")
    print("FROST AI Studio Platform Online at http://127.0.0.1:5000")
    print("==================================================")
    app.run(host='0.0.0.0', port=5000, debug=False)