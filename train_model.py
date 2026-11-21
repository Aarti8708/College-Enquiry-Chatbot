
import json
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Load training data
with open("intents.json", "r", encoding="utf-8") as file:
    data = json.load(file)

questions = []
labels = []

# Prepare questions and labels
for intent in data["intents"]:
    for pattern in intent["patterns"]:
        questions.append(pattern)
        labels.append(intent["tag"])

# Create ML pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", LogisticRegression(max_iter=1000))
])

# Train the model
model.fit(questions, labels)

# Save trained model
with open("chatbot_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("Machine Learning model trained successfully!")
print("Total training questions:", len(questions))
print("Total intents:", len(set(labels)))
