"""Read-only data helpers for the UI (dataset stats, metrics, feature importance)."""
import json

import numpy as np
import pandas as pd
import streamlit as st

from src.predict import MODEL_PATH
from src.preprocess import ASSETS_DIR, DATA_PATH, FEATURES, SCALER_PATH, TARGET


def model_ready():
    return MODEL_PATH.exists() and SCALER_PATH.exists()


def load_metrics():
    path = ASSETS_DIR / "metrics.json"
    return json.loads(path.read_text()) if path.exists() else None


@st.cache_data(show_spinner=False)
def dataset_stats():
    """Rows and class counts from the CSV (CLASS_LABEL: 1 = phishing, 0 = legitimate)."""
    if not DATA_PATH.exists():
        return None
    try:
        col = pd.read_csv(DATA_PATH, usecols=lambda c: c.strip().lower() == TARGET.lower()).iloc[:, 0]
    except Exception:
        return None
    return {"rows": int(len(col)), "phishing": int((col == 1).sum()), "legit": int((col == 0).sum())}


def permutation_importance(predict_fn, X, y, names, repeats=5, seed=42):
    """Accuracy drop when one feature column is shuffled (bigger drop = more important)."""
    rng = np.random.default_rng(seed)
    base = float((predict_fn(X) == y).mean())
    rows = []
    for j, name in enumerate(names):
        drops = []
        for _ in range(repeats):
            Xp = X.copy()
            rng.shuffle(Xp[:, j])
            drops.append(base - float((predict_fn(Xp) == y).mean()))
        rows.append((name, float(np.mean(drops))))
    return pd.DataFrame(rows, columns=["feature", "importance"]).sort_values("importance", ascending=False)


@st.cache_data(show_spinner=False)
def feature_importance(model_mtime):
    """Permutation importance of the EXISTING model on the held-out 20% test split."""
    from sklearn.model_selection import train_test_split

    from src.predict import _load_artifacts
    from src.preprocess import load_data, prepare_dataframe

    data = prepare_dataframe(load_data())
    X, y = data[FEATURES], data[TARGET]
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model, scaler = _load_artifacts()          # saved model + saved scaler (nothing is retrained)
    Xs = scaler.transform(X_test)
    predict = lambda arr: (model.predict(arr, verbose=0, batch_size=4096).ravel() >= 0.5).astype(int)
    return permutation_importance(predict, Xs, y_test.values, FEATURES)
