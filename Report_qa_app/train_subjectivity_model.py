"""train_subjectivity_model.py
Trains a simple model to detect subjective vs objective sentences.

Usage:
  - To use built-in toy examples: `python train_subjectivity_model.py`
  - To train from a CSV with columns `text,label`: `python train_subjectivity_model.py --csv data.csv`

The script saves `models/subjectivity.joblib` (vectorizer, model).
"""

import argparse
import csv
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib


def load_csv(path: str) -> Tuple[List[str], List[int]]:
    texts: List[str] = []
    labels: List[int] = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if 'text' not in reader.fieldnames or 'label' not in reader.fieldnames:
            raise ValueError('CSV must contain `text` and `label` columns')
        for r in reader:
            texts.append(r['text'])
            labels.append(int(r['label']))
    return texts, labels


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', help='Optional CSV path with columns text,label')
    parser.add_argument('--out', default='models/subjectivity.joblib')
    args = parser.parse_args()

    # --- STEP 1: training data ---
    if args.csv:
        texts, labels = load_csv(args.csv)
    else:
        subjective = [
            "We believe the results are excellent",
            "I think this method is the best",
            "It is clear that the system performed wonderfully",
            "Obviously, this approach is superior",
            "Our great team achieved outstanding outcomes",
            "Unfortunately",
            "It seems",
            "It is our understanding",
        ]

        objective = [
            "Tests were conducted at 30 degrees Celsius",
            "Measurements were recorded using a digital meter",
            "The sample failed after 12 hours of exposure",
            "Data were collected from three independent trials",
            "The procedure followed ISO 31000 standards",
        ]

        texts = subjective + objective
        labels = [1] * len(subjective) + [0] * len(objective)

    # --- STEP 2: train simple model ---
    vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 2))
    X = vectorizer.fit_transform(texts)
    model = LogisticRegression(max_iter=1000)
    model.fit(X, labels)

    # --- STEP 3: save model & vectorizer ---
    joblib.dump((vectorizer, model), args.out)

    print(f"✅ Model saved to {args.out}")


if __name__ == '__main__':
    main()
