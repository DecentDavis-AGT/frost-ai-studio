import os
import sys
import re

# Storage module connect karna
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "storage"))
from frost_storage import safe_load_json, safe_save_json

def clean_token(text):
    return re.sub(r'[\'\"\?\.\,\!\:\;]', '', text).strip().lower()

class FrostMemory:
    def __init__(self):
        self.session_history = []
        self.default_data = {
            "user_name": "Daniyal",
            "bot_name": "FROST AI",
            "preferences": {
                "language": "Roman Urdu / English mix",
                "tone": "Cool Bro"
            },
            "facts": {}
        }
        self.persistent_data = safe_load_json("frost_memory.json", self.default_data)

    def save(self):
        safe_save_json("frost_memory.json", self.persistent_data)

    def add_to_session(self, user_msg, bot_msg):
        self.session_history.append({"user": user_msg, "frost": bot_msg})
        if len(self.session_history) > 12:
            self.session_history.pop(0)

    def get_last_topic(self):
        return self.session_history[-1]["user"] if self.session_history else ""

    def remember_fact(self, key, value, category="general", importance=5):
        k = clean_token(key)
        v = clean_token(value)
        self.persistent_data["facts"][k] = {
            "value": v,
            "category": category,
            "importance": importance
        }
        self.save()
        return f"Main ne permanent storage mein lock kar diya:\n-> [{category.upper()}] {k.title()} = '{v}'"

    def recall_fact(self, query):
        q = clean_token(query)
        stop = {"mera", "meri", "mere", "my", "kya", "hai", "ha", "konsa", "konsi", "batao", "what", "is"}
        q_words = [w for w in q.split() if w not in stop and len(w) > 1]
        if not q_words:
            return None

        best_key = None
        max_overlap = 0

        for k in self.persistent_data.get("facts", {}):
            k_words = k.split()
            matches = sum(1 for w in q_words if w in k_words)
            if matches > max_overlap:
                max_overlap = matches
                best_key = k

        if best_key and max_overlap >= 1:
            data = self.persistent_data["facts"][best_key]
            val = data["value"] if isinstance(data, dict) else data
            return f"Aapka {best_key} '{val}' hai."
        return None