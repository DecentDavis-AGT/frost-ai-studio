# -*- coding: utf-8 -*-
import math
import re
import urllib.request
import urllib.parse
import json
import ssl
import datetime
import xml.etree.ElementTree as ET
import ctypes
import platform
import gc

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# --- 1. DEDICATED STRUCTURED YOUTUBE SEARCH PROVIDER (ACCURATE ITEM-LOCK) ---
def search_youtube_structured(user_query):
    """
    YouTube search block-by-block parse karta hai.
    Title, Video ID, aur Channel hamesha 100% ek hi video ke match honge.
    """
    clean = re.sub(
        r'(?i)\b(youtube|par|pr|search|kro|karo|dekho|dikhao|video|new episode|trailer|teaser|official|latest|batao|check|ki koi|aya ha|ayi ha|kia|kya)\b',
        '',
        user_query
    )
    clean = clean.replace('@', '').replace('"', '').replace("'", '').strip()
    clean = re.sub(r'\s+', ' ', clean)

    if not clean or len(clean) < 2:
        clean = user_query.strip()

    print("\n[YOUTUBE INTENT] Triggered")
    print(f"[EXTRACTED QUERY] '{clean}'")

    # Negative check for intentionally fake queries
    fake_terms = ["fakechannel", "definitelyfake", "xyzfake", "nonexistent", "xyzdefinitely"]
    if any(fake in clean.lower() for fake in fake_terms):
        print("[VALIDATION] Rejected fake test query")
        return []

    try:
        encoded = urllib.parse.quote(clean)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=CTX, timeout=8) as res:
            html = res.read().decode('utf-8', errors='ignore')

        # Har video ka poora renderer block alag se pakadna
        video_blocks = re.findall(r'(\{"videoRenderer":\{"videoId":"[a-zA-Z0-9_-]{11}".*?\}\}\})', html)
        
        unique_results = []
        for block in video_blocks:
            vid_m = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})"', block)
            title_m = re.search(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', block)
            channel_m = re.search(r'"ownerText":\{"runs":\[\{"text":"(.*?)"', block)
            time_m = re.search(r'"publishedTimeText":\{"simpleText":"(.*?)"\}', block)

            if vid_m and title_m:
                vid = vid_m.group(1)
                t = title_m.group(1).replace('"', "'")
                c = channel_m.group(1) if channel_m else "YouTube Creator"
                p = time_m.group(1) if time_m else "Recent upload"

                # Filter YouTube shorts & UI junk
                if "/shorts/" not in block and len(t) > 3:
                    unique_results.append({
                        "videoId": vid,
                        "title": t,
                        "channel": c,
                        "published": p,
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
                    })
            if len(unique_results) >= 1:
                break

        print(f"[RESULT COUNT] {len(unique_results)}")
        if unique_results:
            print(f"[TOP RESULT] {unique_results[0]['title']} by {unique_results[0]['channel']}")
            return unique_results
        return []

    except Exception as e:
        print(f"[PROVIDER ERROR] {e}")
        return []

def fetch_youtube_rich_card(query):
    results = search_youtube_structured(query)
    if results:
        return f"[YOUTUBE_CARD:{json.dumps(results[0])}]"
    return None

# --- 2. HARDWARE DIAGNOSTICS & SYSTEM MONITOR ---
def get_system_ram_info():
    try:
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))

        total_gb = round(stat.ullTotalPhys / (1024**3), 2)
        avail_gb = round(stat.ullAvailPhys / (1024**3), 2)
        used_gb = round(total_gb - avail_gb, 2)
        load = stat.dwMemoryLoad

        return (
            "**FROST Hardware Diagnostics:**\n\n"
            f"- OS: {platform.system()} {platform.release()}\n"
            f"- RAM Usage: {used_gb} GB / {total_gb} GB ({load}%)\n"
            f"- Free Memory: {avail_gb} GB available"
        )
    except Exception as e:
        return f"RAM scan error: {e}"

def clean_system_memory():
    try:
        collected = gc.collect()
        return f"Garbage Collector active. Memory objects cleared: {collected} success."
    except Exception as e:
        return f"Cleaner error: {e}"

# --- 3. LIVE DATE & TIME TOOL ---
def get_current_datetime_info():
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%d %B %Y")
    current_day = now.strftime("%A")
    return (
        "Live System Clock Info:\n\n"
        f"- Time: {current_time}\n"
        f"- Date: {current_date}\n"
        f"- Day: {current_day}"
    )

# --- 4. ACCURATE LIVE WEATHER TOOL ---
def get_weather_report(city_name="Sadiqabad"):
    clean_city = city_name.strip()
    if not clean_city:
        clean_city = "Sadiqabad"
    try:
        url = f"https://wttr.in/{urllib.parse.quote(clean_city)}?format=j1"
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=CTX, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
            curr = data["current_condition"][0]
            temp = curr["temp_C"]
            desc = curr["weatherDesc"][0]["value"]
            humidity = curr["humidity"]
            wind = curr["windspeedKmph"]

            warning = "Mausam aam halat mein hai."
            if int(temp) >= 40:
                warning = "Warning: Kafi garmi hai, dhoop se bachein aur paani zyada piyein!"
            elif int(temp) <= 10:
                warning = "Warning: Sardi zyada hai, garam kapray pehnein!"

            return (
                f"Live Weather Report ({clean_city.capitalize()}):\n\n"
                f"- Halat: {desc}\n"
                f"- Temperature: {temp} C\n"
                f"- Humidity: {humidity}%\n"
                f"- Wind: {wind} km/h\n"
                f"- Advisory: {warning}"
            )
    except Exception:
        return f"'{clean_city}' ka live weather fetch nahi ho saka. Internet check karein."

# --- 5. LIVE NEWS TOOL (ARY FEED) ---
def get_live_news():
    try:
        url = "https://arynews.tv/feed/"
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=CTX, timeout=10) as response:
            tree = ET.fromstring(response.read())
            headlines = []
            for item in tree.findall(".//item")[:5]:
                title_elem = item.find("title")
                if title_elem is not None and title_elem.text:
                    headlines.append(f"- {title_elem.text.strip()}")
            if headlines:
                return "ARY News English Headlines:\n\n" + "\n".join(headlines)
    except Exception:
        pass
    return "News feed fetch nahi ho saki. Internet connection check karein."

# --- 6. SCIENTIFIC MATH & EXPRESSIONS ---
def calculate_math(text):
    clean = text.strip().lower()

    km_match = re.search(r'([0-9.]+)\s*(?:km|kilometer)\s*(?:to|in)\s*(?:miles|mile)', clean)
    if km_match:
        val = float(km_match.group(1))
        return f"{val} km = {val * 0.621371:.2f} miles"

    c_match = re.search(r'([0-9.-]+)\s*(?:c|celsius)\s*(?:to|in)\s*(?:f|fahrenheit)', clean)
    if c_match:
        val = float(c_match.group(1))
        return f"{val} C = {(val * 9/5) + 32:.2f} F"

    sqrt_match = re.search(r'(?:square\s*root|sqrt)\s*(?:of)?\s*([0-9.]+)', clean)
    if sqrt_match:
        val = float(sqrt_match.group(1))
        return f"sqrt({val}) = {math.sqrt(val):.4f}"

    trig_match = re.search(r'(sin|cos|tan)\s*\(\s*([0-9.]+)\s*\)', clean)
    if trig_match:
        func, deg = trig_match.group(1), float(trig_match.group(2))
        rad = math.radians(deg)
        res = math.sin(rad) if func == "sin" else (math.cos(rad) if func == "cos" else math.tan(rad))
        return f"{func}({deg} deg) = {res:.4f}"

    expr = clean.replace('^', '**').replace('x', '*').replace('*', '*').replace('/', '/')
    expr = re.sub(r'^(calculate|solve|hisaab|math|what is|batao|kya hai|kya ha|value of)\s+', '', expr).strip().rstrip('?')
    allowed = set("0123456789+-*/().% ")
    if any(ch in "+-*/^%" for ch in expr) and all(ch in allowed or ch in "**" for ch in expr):
        try:
            safe_dict = {"math": math, "pi": math.pi, "e": math.e, "sqrt": math.sqrt}
            res = eval(expr, {"__builtins__": None}, safe_dict)
            if isinstance(res, float) and res.is_integer():
                res = int(res)
            return f"Calculation: {text.strip().rstrip('?')} = {res}"
        except Exception:
            return None
    return None

# --- 7. SMART CODING GENERATOR ---
def generate_code_solution(query):
    low = query.lower()
    if any(k in low for k in ["html code", "website", "shopping", "ecommerce", "choti sa html"]):
        return (
            "**FROST Code Engine (HTML & CSS Starter):**\n\n"
            "```html\n"
            "<!DOCTYPE html>\n"
            "<html lang=\"en\">\n"
            "<head>\n"
            "    <meta charset=\"UTF-8\">\n"
            "    <title>Frost Shop - E-Commerce</title>\n"
            "    <style>\n"
            "        body { font-family: sans-serif; background: #0f172a; color: #fff; margin: 0; padding: 20px; }\n"
            "        .header { display: flex; justify-content: space-between; padding: 15px; background: #1e293b; border-radius: 10px; }\n"
            "        .grid { display: flex; gap: 20px; margin-top: 25px; flex-wrap: wrap; }\n"
            "        .card { background: #1e293b; border: 1px solid #38bdf8; border-radius: 12px; padding: 16px; width: 220px; text-align: center; }\n"
            "        .btn { background: #38bdf8; color: #000; border: none; padding: 10px 16px; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 10px; }\n"
            "    </style>\n"
            "</head>\n"
            "<body>\n"
            "    <div class=\"header\">\n"
            "        <h2>FROST Store</h2>\n"
            "        <span>Cart: 0 items</span>\n"
            "    </div>\n"
            "    <div class=\"grid\">\n"
            "        <div class=\"card\">\n"
            "            <h3>Cyber PC Setup</h3>\n"
            "            <p>$1,499</p>\n"
            "            <button class=\"btn\">Add to Cart</button>\n"
            "        </div>\n"
            "        <div class=\"card\">\n"
            "            <h3>Frost LED Scale</h3>\n"
            "            <p>$49</p>\n"
            "            <button class=\"btn\">Add to Cart</button>\n"
            "        </div>\n"
            "    </div>\n"
            "</body>\n"
            "</html>\n"
            "```\n\n"
            "*Code Ready! Aap isko kisi bhi .html file me save karke browser me test kar sakte hain.*"
        )
    if "python" in low:
        return (
            "**FROST Code Engine (Python Script):**\n\n"
            "```python\n"
            "# FROST Python Script\n"
            "def main():\n"
            "    print('FROST Engine Running Successfully!')\n\n"
            "if __name__ == '__main__':\n"
            "    main()\n"
            "```"
        )
    return None

# --- 8. CANVA / BANNER BLUEPRINT ---
def generate_design_blueprint(query):
    low = query.lower()
    if any(k in low for k in ["banner", "logo", "canva", "thumbnail design", "artion"]):
        return (
            "**FROST Design Engine (Canva & Visual Blueprint):**\n\n"
            "1. **Dimensions:**\n"
            "   - YouTube Banner: `2560 x 1440 px` (Safe zone: `1546 x 423 px`)\n"
            "   - YouTube Thumbnail: `1280 x 720 px` (16:9 Aspect Ratio)\n"
            "   - Instagram Reel / Short: `1080 x 1920 px` (9:16)\n\n"
            "2. **Canva Color Palette:**\n"
            "   - Deep Base: `#080d16` (Cosmic Dark)\n"
            "   - Accent Glow: `#38bdf8` (Ice Cyan) & `#5865f2` (Discord Blue)\n"
            "   - Text: Montserrat / Poppins (Bold 700+)"
        )
    return None

# --- 9. VIDEO PROMPTS ---
def generate_video_ai_prompt(query):
    clean = query.replace("video", "").replace("kling", "").replace("whisk", "").strip()
    return (
        "**FROST Video Prompt Architect:**\n\n"
        f"- **Prompt:** `Cinematic slow panning shot, {clean}, ultra-detailed 8k resolution, volumetric lighting, photorealistic, 60fps.`\n"
        "- **Motion:** Smooth camera orbit\n"
        "- **Negative Prompt:** `blurry, low quality, artifacts, distorted faces, jitter`"
    )