# -*- coding: utf-8 -*-
import os
import sys
import datetime
import gc
import platform
import ctypes
import re
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from frost_brain import ask_ai_brain

# Safe Import with Fallback
try:
    from frost_tools import (
        calculate_math,
        get_weather_report,
        get_live_news,
        get_current_datetime_info,
        generate_code_solution,
        generate_design_blueprint,
        generate_video_ai_prompt,
        search_youtube_structured,
        fetch_youtube_rich_card,
        get_system_ram_info,
        clean_system_memory
    )
except ImportError:
    try:
        from frost_tools import (
            calculate_math,
            get_weather_report,
            get_live_news,
            get_current_datetime_info,
            generate_code_solution,
            generate_design_blueprint,
            generate_video_ai_prompt
        )
    except Exception:
        pass
    def search_youtube_structured(q): return []
    def fetch_youtube_rich_card(q): return None
    def get_system_ram_info(): return "Hardware diagnostics standby."
    def clean_system_memory(): return "Memory optimization standby."

DEFAULT_MODE = "serious"
try:
    from frost_config import DEFAULT_MODE
except Exception:
    pass

try:
    from frost_memory import FrostMemory
    memory = FrostMemory()
except Exception:
    class DummyMemory:
        def __init__(self):
            self.persistent_data = {}
        def remember_fact(self, k, v):
            self.persistent_data[k.lower()] = v
            return f"Fact yaad kar liya: {k} = {v}"
        def recall_fact(self, q):
            for k, v in self.persistent_data.items():
                if k in q.lower():
                    return v
            return None
        def add_to_session(self, u, b):
            pass
    memory = DummyMemory()

try:
    from frost_voice import speak, toggle_voice
except Exception:
    def speak(text): pass
    def toggle_voice(status=None): return "Voice engine standby."

current_mode = DEFAULT_MODE

def set_mode(mode_name):
    global current_mode
    if mode_name in ["serious", "funny"]:
        current_mode = mode_name
        if mode_name == "funny":
            return "Mode switched to FUNNY (WAMUUUU)! Full energetic mode enabled."
        return "Mode switched to SERIOUS. Focused studio analytical mode ready."
    return "Invalid mode selected."

def extract_key_val(raw):
    txt = raw.strip()
    txt = re.sub(r'(?i)\b(remember that|remember|yaad rakho|save fact)\b', '', txt).strip()
    txt = re.sub(r'^(?i)(mera|meri|mere|my)\s+', '', txt).strip()

    eq_m = re.search(r'(.+?)\s*(?:=|is|hai|ha)\s*(.+)', txt, flags=re.IGNORECASE)
    if eq_m:
        return eq_m.group(1).strip(), eq_m.group(2).strip().rstrip('.!')

    parts = txt.split()
    if len(parts) >= 2:
        return " ".join(parts[:-1]), parts[-1].rstrip('.!')
    return txt, txt

def match_memory_fact(query):
    low = query.lower()
    normalized = low.replace('sunhect', 'subject').replace('sunject', 'subject')
    normalized = normalized.replace('fav ', 'favorite ').replace('favourite ', 'favorite ')

    data = getattr(memory, 'persistent_data', {})
    for stored_key, stored_val in data.items():
        k_norm = str(stored_key).lower().replace('fav ', 'favorite ').replace('favourite ', 'favorite ')
        words = [w for w in k_norm.split() if len(w) > 2]
        if all(w in normalized for w in words) or k_norm in normalized:
            return f"Aapka record mil gaya:\n-> {stored_key} = {stored_val}"

    if hasattr(memory, 'recall_fact'):
        rec = memory.recall_fact(normalized)
        if rec:
            return f"Aapka record mil gaya:\n-> {rec}"
    return None

# --- MASTER ROUTER & PERSONALITY ENGINE ---
def frost_reply(message, model="frost_ultra"):
    global current_mode
    if not message:
        return "Hello Daniyal! FROST AI Studio bilkul ready hai."

    msg = str(message).strip()
    low = msg.lower()
    clean = re.sub(r'[^\w\s]', '', low).strip()

    # 1. VOICE TOGGLE
    if clean in ["voice on", "aawaz on", "sound on"]:
        return toggle_voice(True)
    elif clean in ["voice off", "aawaz band", "sound off", "mute"]:
        return toggle_voice(False)

    # 2. PERSONALITY SWITCH
    if clean in ["mode funny", "wamuuuu", "masti mode"]:
        return set_mode("funny")
    elif clean in ["mode serious", "serious mode"]:
        return set_mode("serious")

    # 3. CREATOR IDENTITY
    if any(k in low for k in ["i am daniyal", "main daniyal", "my owner", "i am your owner", "i create you", "i created you", "who made you"]):
        return "Welcome, Daniyal! You are my creator and lead architect. FROST Studio is ready for your commands."

    # 4. CHILL & CASUAL GREETINGS
    if any(k in low for k in ["thank", "shukriya", "thanks", "thx"]):
        if current_mode == "funny":
            return "Arre bhai doston mein thank you kaisa! Bas enjoy karo."
        return "Anytime bhai! Hamesha aapke sath hoon, enjoy karo."

    casual_greetings = [
        "hi", "hii", "hiii", "hello", "hey", "salam", "assalam", "kaisa ho", "kaise ho",
        "kai ho", "kaai ho", "kasay ho", "kasai ho", "frost", "yoo", "yo", "hello frost",
        "hii frost", "hi frost", "kya haal hai", "how are you", "chill", "kya scene hai",
        "main agya", "main aa gaya", "main aagya"
    ]
    if clean in casual_greetings or any(clean == g for g in ["hi", "hello", "hey", "hii", "main agya"]):
        if current_mode == "funny":
            return "Arey welcome back Daniyal bhai! Sab mast chal raha hai. Aaj kya dekhna ya build karna hai?"
        return "Welcome back Daniyal bhai. Sab ready hai. Kahiye kya explore karein?"

    # 5. SCIENTIFIC MATH (Priority Check)
    math_calc = calculate_math(msg)
    if math_calc:
        return math_calc

    # 6. HARDWARE DIAGNOSTICS & RAM
    if any(w in clean for w in ["clean ram", "boost ram", "free ram", "ram clean", "clean memory"]):
        return f"**FROST Deep Memory Optimizer:**\n{clean_system_memory()}"
    elif any(w in clean for w in ["system ram", "pc ram", "check ram", "ram usage", "ram status"]):
        return get_system_ram_info()

    # 7. DATE & TIME
    if any(w in clean for w in ["time kya", "waqt kya", "current time", "what time", "aaj konsa din", "aaj kya date"]):
        return get_current_datetime_info()

    # 8. ACCURATE WEATHER (Handles Sadiqabad, Rahim Yar Khan, etc.)
    if any(w in clean for w in ["weather", "mausam", "temperature", "temp"]):
        city = "Sadiqabad"
        if "rahim" in clean or "ryk" in clean:
            city = "Rahim Yar Khan"
        else:
            words = clean.split()
            for idx, w in enumerate(words):
                if w in ["of", "in", "ka", "ki"] and idx + 1 < len(words):
                    city = words[idx + 1].capitalize()
                    break
        return get_weather_report(city)

    # 9. LIVE NEWS
    if clean in ["news", "khabrein", "headlines", "latest news"]:
        return get_live_news()

    # 10. CANVA / DESIGN BLUEPRINTS
    if any(w in low for w in ["canva", "banner", "logo", "thumbnail design", "size kya", "ratio kya"]):
        design_res = generate_design_blueprint(msg)
        if design_res:
            return design_res

    # 11. VIDEO PROMPTS
    if any(w in low for w in ["kling", "whisk", "video prompt", "animate image"]):
        return generate_video_ai_prompt(msg)

    # 12. DEDICATED YOUTUBE SEARCH & DISCOVERY INTENT
    # Sirf tabhi chale jab query waqai YouTube video/channel ke liye ho (coding/queries ko bypass karega)
    yt_explicit = ["youtube", "video", "episode", "trailer", "teaser", "proboiz", "darkheroes", "dark heroes", "junkeyy"]
    is_code_request = any(c in low for c in ["code", "java", "python", "html", "css", "javascript", "program", "function"])
    is_yt_intent = (any(w in low for w in yt_explicit) or "@" in msg or any(w in low for w in ["dekhao", "dikhao", "chalao", "play"])) and not is_code_request
    
    if is_yt_intent and not low.startswith('/image') and not low.startswith('/video'):
        yt_results = search_youtube_structured(msg)
        if yt_results:
            top = yt_results[0]
            card_payload = json.dumps(top)
            
            tone_prefix = "Mil gayi bhai! Video ye rahi:" if current_mode == "funny" else "Haan bhai, YouTube par verified matching video mil gayi:"
            
            return (
                f"{tone_prefix}\n\n"
                f"- **Title:** {top['title']}\n"
                f"- **Channel:** {top['channel']}\n"
                f"- **Upload Time:** {top['published']}\n\n"
                f"[YOUTUBE_CARD:{card_payload}]"
            )
        else:
            print("[FALLBACK] No verified YouTube result found.")
            return "YouTube par is topic ya channel ki koi verified matching video nahi mili. Main guess nahi karunga."

    # 13. DIRECT CODE GENERATION (Quick Templates)
    if any(w in low for w in ["code dedo", "give me code", "html code", "python code", "css code", "write code", "banai kai liye"]):
        code_res = generate_code_solution(msg)
        if code_res:
            return code_res

    # 14. MEMORY FACTS
    if any(k in low for k in ["remember that", "remember", "yaad rakho", "save fact"]):
        topic, val = extract_key_val(msg)
        return memory.remember_fact(topic, val)

    is_memory_read = (
        any(low.startswith(p) for p in ["what is my", "whats my", "what's my", "tell me my", "mera ", "meri ", "mere ", "my "]) or
        ("my" in low.split() and any(w in low for w in ["favorite", "favourite", "fav", "name", "subject", "hobby"]))
    )
    if is_memory_read:
        mem_ans = match_memory_fact(msg)
        if mem_ans:
            return mem_ans
        return "Mujhe yeh fact aapki memory mein nahi mila."

    # 15. AI ENGINE FALLBACK & REASONING (Handles Java, Complex Coding, Knowledge & Chat)
    ans = ask_ai_brain(msg, mode=current_mode, model=model)
    if not ans or str(ans).strip().lower() == "none":
        ans = "Main samajh gaya bhai, batao is par aage kya task perform karna hai?"

    return str(ans)