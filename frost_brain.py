# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import json
import re
import ssl
import random
import time

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# --- 1. LOCAL KNOWLEDGE VAULT ---
INTEL_VAULT = {
    "techno gamerz": (
        "**Techno Gamerz (Ujjwal Chaurasia):**\n\n"
        "- Content: GTA V storyline series, Minecraft survival builds, mobile gaming.\n"
        "- Impact: 40M+ subscribers, pioneer of long-form narrative gaming in South Asia."
    ),
    "carryminati": (
        "**CarryMinati (Ajey Nagar):**\n\n"
        "- Content: Satirical roasts, comedy sketches, diss tracks, gaming streams on CarryisLive."
    ),
    "spacex": (
        "**SpaceX (Space Exploration Technologies Corp.):**\n\n"
        "- Founder: Elon Musk (2002).\n"
        "- Flagship: Falcon 9 reusable booster tech, Starship super-heavy launch system."
    ),
    "quaid-e-azam": (
        "**Quaid-e-Azam Muhammad Ali Jinnah (1876 - 1948):**\n\n"
        "- Pakistan ke founder aur pehle Governor-General.\n"
        "- Slogan: Unity, Faith, Discipline (Ittehad, Yaqeen, Tanzeem)."
    ),
    "elon musk": (
        "**Elon Musk:**\n\n"
        "- Identity: Visionary tech entrepreneur aur engineer.\n"
        "- Current Ventures: CEO of Tesla, Founder of SpaceX, Owner of X (Twitter), Neuralink, aur xAI."
    ),
    "feastables": (
        "**Feastables (MrBeast Brand):**\n\n"
        "- Founder: Jimmy Donaldson (MrBeast).\n"
        "- Key Flavors: Milk Chocolate, Peanut Butter, Deez Nutz, Milk Crunch.\n"
        "- Recipe: Organic cocoa butter, cocoa powder, sugar, aur milk mix karke banta hai."
    ),
    "google": (
        "**Google Overview & History:**\n\n"
        "- Founders: Larry Page aur Sergey Brin ne 1998 me Stanford University ke research project ke taur par shuru kiya.\n"
        "- Core: Shuruat Backrub search algorithm se hui jo web pages ki relevance rank karta tha.\n"
        "- Parent Company: Alphabet Inc."
    )
}

TYPO_MAPPING = {
    "techno gamer": "techno gamerz",
    "technogamerz": "techno gamerz",
    "carry minati": "carryminati",
    "carriminati": "carryminati",
    "space x": "spacex",
    "open ai": "openai",
    "quaid azam": "quaid-e-azam",
    "who ius": "who is",
    "elon mask": "elon musk",
    "feastable": "feastables",
    "festables": "feastables",
    "proboiz": "proboiz 95",
    "darkhero": "darkheroes"
}

def clean_query_text(text):
    low = text.lower().strip()
    for wrong, right in TYPO_MAPPING.items():
        low = re.sub(r'\b' + re.escape(wrong) + r'\b', right, low)
    return low

def clean_for_search(text):
    clean = clean_query_text(text)
    clean = re.sub(r'(?i)\b(who is|what is|tell me about|explain|explore|kon hai|kon ha|kya hai|kya ha|ke bare me|k bare me|about|youtube par search kro|search kro|dekho|batao)\b', '', clean).strip()
    clean = re.sub(r'[^\w\s]', '', clean).strip()
    return clean

# --- 2. LIVE WEB & YOUTUBE INTEL CRAWLER ---
def live_web_search(query):
    low = query.lower().strip()
    skip_phrases = ["intelligent", "tum kitne", "kitnai", "baat kro", "talk in", "attached image", "who are you"]
    if any(p in low for p in skip_phrases) or len(low) < 3:
        return None

    try:
        clean = clean_for_search(query)
        search_term = clean if clean else query
        encoded = urllib.parse.quote(search_term)
        url = "https://html.duckduckgo.com/html/?q=" + encoded
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=CTX, timeout=6) as res:
            html = res.read().decode('utf-8', errors='ignore')
            snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, flags=re.DOTALL)
            if snippets:
                clean_results = []
                junk_phrases = [
                    "#reels", "#actor", "#shorts", "subscribers", "views",
                    "google ki is seva", "subscribe for", "for business inquiry",
                    "enjoy the videos and music", "upload original content",
                    "terms of service", "privacy policy"
                ]
                for s in snippets[:4]:
                    text = re.sub(r'<[^>]+>', '', s).strip()
                    # Unicode cleanup for Windows 7 safety
                    text = re.sub(r'[^\x00-\x7F]+', ' ', text).strip()
                    if len(text) > 20 and not any(junk in text.lower() for junk in junk_phrases):
                        clean_results.append(text)
                if clean_results:
                    return clean_results
    except Exception:
        pass
    return None

def search_wikipedia_direct(clean_query):
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(clean_query)
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=CTX, timeout=5) as res:
            data = json.loads(res.read().decode("utf-8"))
            if data.get("extract"):
                clean_extract = re.sub(r'[^\x00-\x7F]+', ' ', data['extract']).strip()
                return "**Wikipedia Overview (" + str(data.get('title', clean_query)) + "):**\n\n" + clean_extract
    except Exception:
        pass
    return None

# --- 3. DYNAMIC MULTI-MODEL FALLBACK AI ENGINE ---
def ask_online_ai_multi_angle(prompt_text, mode="serious", selected_model="frost_ultra"):
    model_tags = ["openai", "claude", "mistral", "deepseek"]
    random_seed = int(time.time()) + random.randint(100, 9999)

    system_instruction = (
        "You are FROST AI Master Studio, an authentic intelligent assistant created by Daniyal Mohsin. "
        "Mode: " + str(mode) + ". Give deep, helpful, and natural answers in Roman Urdu or English. "
        "Never dump raw internet search text, video scripts, or channel descriptions. "
        "Answer the user query directly with facts, logic, and friendly tone. "
        "Query: " + str(prompt_text)
    )

    for tag in model_tags:
        try:
            url = "https://text.pollinations.ai/" + urllib.parse.quote(system_instruction) + "?model=" + tag + "&seed=" + str(random_seed)
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, context=CTX, timeout=10) as res:
                ans = res.read().decode("utf-8").strip()
                ans_clean = re.sub(r'[^\x00-\x7F]+', ' ', ans).strip()
                if ans_clean and len(ans_clean) > 8:
                    return ans_clean
        except Exception:
            continue
    return None

# --- 4. RESEARCH SYNTHESIZER (AI UNDERSTANDS INTERNET) ---
def synthesize_findings(user_query, raw_findings, mode="serious"):
    """Search snippets ko filter aur understand karke natural Roman Urdu jawab banata hai"""
    if not raw_findings:
        return None

    if isinstance(raw_findings, list):
        evidence_text = "\n".join("- " + str(item) for item in raw_findings)
    else:
        evidence_text = str(raw_findings)

    synthesis_prompt = (
        "User sawal: " + str(user_query) + "\n\n"
        "Internet aur YouTube se mili taza findings:\n" + str(evidence_text) + "\n\n"
        "Hidayat: In findings ko parh kar user ko Roman Urdu mein natural, mukhtasar aur clear jawab do. "
        "Video ka intro, outro ya promotion lines bilkul repeat mat karo. "
        "Agar confirmed update ya episode release date nahi mili toh saaf batao ke official confirm nahi hua."
    )
    
    synthesized = ask_online_ai_multi_angle(synthesis_prompt, mode=mode)
    if synthesized and len(synthesized) > 15:
        return synthesized
    return None

# --- MASTER BRAIN ---
def ask_ai_brain(prompt, mode="serious", model="frost_ultra"):
    raw = prompt.strip()
    if not raw:
        return "Main sun raha hoon, poochiye kya analyze karna hai?"

    low = raw.lower()

    # 1. Direct Self-Awareness / Identity
    if any(q in low for q in ["kitnai intelligent", "kitne intelligent", "how smart", "how intelligent"]):
        return (
            "Main FROST AI Studio hoon! Main real-time code analysis, hardware monitoring (RAM diagnostics), "
            "visual rendering (16:9 thumbnails, 9:16 reels), Google web search, aur deep logical calculations "
            "perform karne ke liye optimized hoon. Aapka next task kya hai?"
        )

    # 2. Language switch trigger
    if any(q in low for q in ["english main baat", "speak english", "talk in english", "english me baat"]):
        return "Understood. Switching primary response tone to clear, professional English. What would you like to explore or build next, Daniyal?"

    # 3. Check Local Knowledge Vault
    for key, text in INTEL_VAULT.items():
        if key in low and len(key) > 3:
            return text

    # 4. Smart Research Trigger (DarkHeroes, YouTube series, Releases, News)
    needs_search = any(k in low for k in [
        "darkheroes", "dark heroes", "proboiz", "junkeyy", "frozen",
        "kab a rahi", "kab aayegi", "release date", "new episode",
        "trailer", "teaser", "latest", "season 4", "season 3", "search", "youtube"
    ])
    
    if needs_search:
        web_res = live_web_search(raw)
        if web_res:
            synthesized = synthesize_findings(raw, web_res, mode=mode)
            if synthesized:
                return synthesized

    # 5. Online Multi-Model AI Reasoning First
    ai_res = ask_online_ai_multi_angle(raw, mode=mode, selected_model=model)
    if ai_res and len(ai_res.strip()) > 8:
        return ai_res

    # 6. Secondary Live Web Crawl with Synthesis
    web_res = live_web_search(raw)
    if web_res:
        synthesized = synthesize_findings(raw, web_res, mode=mode)
        if synthesized:
            return synthesized

    # 7. Wikipedia Fallback
    clean_topic = clean_for_search(raw)
    wiki_res = search_wikipedia_direct(clean_topic)
    if wiki_res:
        return wiki_res

    # 8. Natural Fallback
    return "Bhai is topic par abhi koi confirmed live update nahi mili. Aap directly channel ya exact topic ka naam batayein taake main mazeed deep scan kar sakoon!"