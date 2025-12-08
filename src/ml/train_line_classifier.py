import os
import re
import joblib
import warnings
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, confusion_matrix, f1_score, precision_recall_fscore_support

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(r"C:\Users\aakas\Documents\workout_project")
LABEL_DATA_PATH = PROJECT_ROOT/ "data_labels" / "lines_for_trainning.csv"
MODELS_DIR = PROJECT_ROOT/ "models"
MODEL_PATH = MODELS_DIR / "line_clf.joblib"
CM_PNG = MODELS_DIR/ "confusion_matrix.png"


# load dataset 
def load_label_data(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Labeled CSV not found at: {path}")
    df = pd.read_csv(path)

    # drop emties in 'label' or 'raw_line'
    if 'raw_line' not in df.columns or 'label' not in df.columns:
        raise ValueError("Label file must contain 'raw_line' and 'label' columns.")
    df = df[["raw_line", "label"]].dropna(subset=["raw_line"])
    df["raw_line"] = df["raw_line"].astype(str).str.strip()
    df["label"] = df["label"].astype(str).str.strip()

    df = df[df["label"] != ""].reset_index(drop=True)
    return df

# confusion matrix
def plot_and_save_confusion(y_true, y_pred, labels, out_path: Path):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    plt.figure(figsize=(max(6, len(labels)*0.8), max(4, len(labels)*0.5)))
    sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.ylabel("True")
    plt.xlabel("Predicted")
    plt.title("Normalized Confusion Matrix")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=200)
    plt.close()

# Pipeline

def build_pipeline(class_weight="balanced"):

    char_vect = TfidfVectorizer(analyzer="char_wb", ngram_range=(2,4), min_df=2)
    word_vect = TfidfVectorizer(analyzer="word", ngram_range=(1,2), token_pattern=r"(?u)\b\w+\b", min_df=2)

    combined = FeatureUnion([("char", char_vect), ("word", word_vect)])

    base_clf = LogisticRegression(solver="liblinear", max_iter=2000, class_weight=class_weight, random_state=42)

    # calibrate probabilities
    calibrated = CalibratedClassifierCV(base_clf, cv=3, method="isotonic")

    pipe = Pipeline([
        ("feats", combined),
        ("clf", calibrated)
    ])
    return pipe

# Train 

def train_and_evaluate(label_csv=LABEL_DATA_PATH, model_out=MODEL_PATH, cm_out=CM_PNG):

    df = load_label_data(label_csv)
    if df.empty:
        raise RuntimeError("No labeled rows found in CSV.")
    
    x = df["raw_line"].values
    y = df["label"].values
    
    # if very few samples per class, to avoid stratify errors
    unique_counts = df["label"].value_counts()

    stratify_arg = y if unique_counts.min() >= 2 else None

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.20, random_state=42, stratify=stratify_arg)

    # Baseline pipeline
    pipe = build_pipeline(class_weight="balanced")

    # Grid search
    param_grid = {
        "clf__estimator__C": [0.5, 1.0, 3.0]
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42) if stratify_arg is not None else 3

    search = GridSearchCV(pipe, param_grid, cv=cv, scoring="f1_macro", n_jobs=-1, verbose=1)

    search.fit(x_train, y_train)

    best_pipe = search.best_estimator_
    print("\nBest params:", best_pipe)

    # Evaluate on test set
    y_pred = best_pipe.predict(x_test)
    print("\n Test Set Evaluation")
    print("Accuracy: {:.4f}".format(best_pipe.score(x_test, y_test)))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, digits=4))

    # Save confussion matrix 
    labels = sorted(df["label"].unique())
    plot_and_save_confusion(y_test, y_pred, labels=labels, out_path=cm_out)
    

    # Save model
    model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipe, str(model_out)) 
    print(f"Successfully saved model to: {model_out}")


    # Save detailed per-class mertrics to CSV
    p, r, f1, support = precision_recall_fscore_support(y_test, y_pred, labels=labels, zero_division=0)
    metrics_df = pd.DataFrame({"label":labels, "precision": p, "recall": r, "f1": f1, "support": support})
    metrics_df.to_csv(model_out.parent / "test_metrics_per_class.csv", index=False)
    print("Saved per-class metrics to:", model_out.parent / "test_metrics_per_class.csv")

    # Calibration info: show mean predicted prob for predicted label for some error analysis

    try:
        proba = best_pipe.predict_proba(x_test)
        avg_confidence = np.mean(np.max(proba, axis=1))
        print(f"Avg predicted confidence on test set: {avg_confidence:.3f}")
    except Exception:
        pass

    return best_pipe, metrics_df

# Inference helper

def predict_lines(lines, model_path=MODEL_PATH, threshold=0.6):

    if not model_path.exists():
        raise FileNotFoundError("Model not found.")
    pipe = joblib.load(model_path)
    preds = pipe.predict(lines)
    probs = pipe.predict_proba(lines)
    out = []
    for line, lab, prob_vec in zip(lines, preds, probs):
        maxp = prob_vec.max()
        out_label = lab if maxp >= threshold else "LOW_CONFIDENCE"
        out.append((line, out_label, float(maxp)))
    
    return out


if __name__== "__main__":
    try:
        best_pipe, metrics_df = train_and_evaluate()
    except Exception as e:
        print("ERROR during training:", str(e))
        raise
