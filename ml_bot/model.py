import json
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

with open("intent_data.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

texts = [item["text"] for item in data]
labels = [item["intent"] for item in data]

vectorizer = TfidfVectorizer(ngram_range=(1, 2))
X = vectorizer.fit_transform(texts)

model = LogisticRegression(class_weight="balanced")
model.fit(X, labels)

with open("intent_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("intent_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("Model eğitildi ve kaydedildi.")
