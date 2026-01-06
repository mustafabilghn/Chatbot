import pickle
import random
import os
import re
import json
from ml_bot.intent_responses import INTENT_RESPONSES
from difflib import get_close_matches

BASE_DIR = os.path.dirname(__file__)

MODEL_PATH = os.path.join(BASE_DIR, "intent_model.pkl")
VEC_PATH = os.path.join(BASE_DIR, "intent_vectorizer.pkl")
KB_PATH = os.path.join(BASE_DIR, "../knowledge_base.json")


def load_resources():
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        with open(VEC_PATH, "rb") as f:
            vectorizer = pickle.load(f)
        with open(KB_PATH, "r", encoding="utf-8") as f:
            kb_data = json.load(f)
        return model, vectorizer, kb_data
    except FileNotFoundError:
        print("HATA: Model veya veritabanı dosyaları bulunamadı!")
        return None, None, {"questions": []}


model, vectorizer, knowledge_base = load_resources()


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("ı", "i").replace("ğ", "g").replace("ü", "u")
    text = text.replace("ş", "s").replace("ö", "o").replace("ç", "c")
    text = re.sub(r"[^\w\s]", "", text)
    return text


def solve_math(text: str):
    clean_text = text.lower().replace("arti", "+").replace("eksi", "-")
    clean_text = re.sub(r"[^0-9+\-*/.]", "", clean_text)
    if not re.search(r"\d", clean_text) or not re.search(r"[+\-*/]", clean_text):
        return None
    try:
        return str(eval(clean_text))
    except:
        return None


def get_kb_answer(normalized_input):
    questions = [normalize(q["question"]) for q in knowledge_base["questions"]]
    matches = get_close_matches(normalized_input, questions, n=1, cutoff=0.6)

    if matches:
        match_question = matches[0]
        for q in knowledge_base["questions"]:
            if normalize(q["question"]) == match_question:
                return q["answer"]
    return None


def get_response(user_input: str):
    normalized_input = normalize(user_input)

    math_result = solve_math(user_input)
    if math_result:
        return math_result

    kb_answer = get_kb_answer(normalized_input)
    if kb_answer:
        return kb_answer

    if model and vectorizer:
        X = vectorizer.transform([normalized_input])
        probs = model.predict_proba(X)[0]
        max_prob = max(probs)
        intent = model.predict(X)[0]

        print(f"Tahmin: {intent} | Güven: {max_prob:.2f}")

        if max_prob > 0.25:
            if intent in INTENT_RESPONSES:
                return random.choice(INTENT_RESPONSES[intent])

    return None
