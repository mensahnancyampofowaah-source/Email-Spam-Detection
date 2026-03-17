"""
Train a spam detection model using the SMS Spam Collection dataset.
Saves the trained model and vectorizer to disk using pickle.
"""

import re
import pickle
import urllib.request
import zipfile
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix
)

# ── NLTK stopwords (bundled fallback if download fails) ─────────────────────
STOPWORDS = {
    "a","about","above","after","again","against","all","am","an","and",
    "any","are","aren't","as","at","be","because","been","before","being",
    "below","between","both","but","by","can't","cannot","could","couldn't",
    "did","didn't","do","does","doesn't","doing","don't","down","during",
    "each","few","for","from","further","get","got","had","hadn't","has",
    "hasn't","have","haven't","having","he","he'd","he'll","he's","her",
    "here","here's","hers","herself","him","himself","his","how","how's",
    "i","i'd","i'll","i'm","i've","if","in","into","is","isn't","it",
    "it's","its","itself","let's","me","more","most","mustn't","my",
    "myself","no","nor","not","of","off","on","once","only","or","other",
    "ought","our","ours","ourselves","out","over","own","same","shan't",
    "she","she'd","she'll","she's","should","shouldn't","so","some","such",
    "than","that","that's","the","their","theirs","them","themselves","then",
    "there","there's","these","they","they'd","they'll","they're","they've",
    "this","those","through","to","too","under","until","up","very","was",
    "wasn't","we","we'd","we'll","we're","we've","were","weren't","what",
    "what's","when","when's","where","where's","which","while","who","who's",
    "whom","why","why's","will","with","won't","would","wouldn't","you",
    "you'd","you'll","you're","you've","your","yours","yourself","yourselves",
}


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " url ", text)      # URLs
    text = re.sub(r"\d+", " num ", text)                  # numbers
    text = re.sub(r"[^\w\s]", " ", text)                  # punctuation
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    return " ".join(tokens)


def load_dataset() -> pd.DataFrame:
    """Download the SMS Spam Collection dataset and return a DataFrame."""
    url = (
        "https://archive.ics.uci.edu/ml/machine-learning-databases/"
        "00228/smsspamcollection.zip"
    )
    zip_path = "/tmp/smsspam.zip"
    tsv_path = "/tmp/SMSSpamCollection"

    if not os.path.exists(tsv_path):
        print("Downloading SMS Spam Collection dataset …")
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall("/tmp/")

    df = pd.read_csv(
        tsv_path, sep="\t", header=None, names=["label", "message"],
        encoding="latin-1"
    )
    df["label"] = df["label"].map({"ham": 0, "spam": 1})
    return df


def main():
    os.makedirs("models", exist_ok=True)

    # 1. Load data
    df = load_dataset()
    print(f"Dataset loaded: {len(df)} rows  |  spam={df['label'].sum()}  ham={(df['label']==0).sum()}")

    # 2. Clean text
    df["clean"] = df["message"].apply(clean_text)

    # 3. Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        df["clean"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    # 4. TF-IDF vectorisation
    vectorizer = TfidfVectorizer(max_features=8000, ngram_range=(1, 2), sublinear_tf=True)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec  = vectorizer.transform(X_test)

    # 5. Train Naive Bayes
    model = MultinomialNB(alpha=0.1)
    model.fit(X_train_vec, y_train)

    # 6. Evaluate
    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy : {acc*100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Ham", "Spam"]))

    # 7. Persist
    with open("models/spam_model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("models/tfidf_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open("models/accuracy.txt", "w") as f:
        f.write(f"{acc:.4f}")

    print("\n✓ Model saved to models/spam_model.pkl")
    print("✓ Vectorizer saved to models/tfidf_vectorizer.pkl")
    return acc


if __name__ == "__main__":
    main()
