"""Data loading, cleaning, EDA plots and scaling for the phishing project."""
import sys
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "dataset" / "phishing.csv"
MODEL_DIR = ROOT / "model"
ASSETS_DIR = ROOT / "assets"
SCALER_PATH = MODEL_DIR / "scaler.pkl"

# Exactly the 12 features used by the ANN (a Python list = ordered array of names)
# Columns come from the Kaggle file "Phishing_Legitimate_full.csv" (renamed phishing.csv)
FEATURES = [
    "NumDots",
    "SubdomainLevel",
    "PathLevel",
    "UrlLength",
    "NumDash",
    "AtSymbol",
    "NumNumericChars",
    "NoHttps",
    "IpAddress",
    "NumSensitiveWords",
    "HostnameLength",
    "PctExtHyperlinks",
]
TARGET = "CLASS_LABEL"  # in the CSV: 1 = phishing, 0 = legitimate


def load_data(path=DATA_PATH):
    """Load the CSV (tabular storage) into a DataFrame."""
    path = Path(path)
    if not path.exists():
        sys.exit(f"Dataset not found at {path}. Place the Kaggle 'phishing.csv' there.")
    return pd.read_csv(path)


def check_nulls(df):
    """Print and return the null count per column."""
    nulls = df.isnull().sum()
    print("Null values per column:")
    print(nulls[nulls > 0] if nulls.sum() else "  none")
    return nulls


def prepare_dataframe(df):
    """Keep the 12 features + target.

    CSV label:  CLASS_LABEL 1 = phishing, 0 = legitimate
    Project:    0 = Phishing, 1 = Legitimate   (so sigmoid output = P(Legitimate))
    """
    df = df.copy()
    df.columns = df.columns.str.strip()
    lookup = {c.lower(): c for c in df.columns}  # case-insensitive column matching
    wanted = FEATURES + [TARGET]
    missing = [c for c in wanted if c.lower() not in lookup]
    if missing:
        raise KeyError(f"Missing columns: {missing}\nColumns found in CSV: {list(df.columns)}")

    data = df[[lookup[c.lower()] for c in wanted]].copy()
    data.columns = wanted
    data = data.apply(pd.to_numeric, errors="coerce").dropna()

    labels = set(data[TARGET].unique())
    if not labels <= {0, 1}:
        raise ValueError(f"{TARGET} must contain only 0 and 1, found {sorted(labels)}")
    data[TARGET] = (1 - data[TARGET]).astype(int)  # flip: 1(phishing)->0, 0(legit)->1
    return data


def preprocess(test_size=0.2, seed=42, save_scaler=True):
    """Full preprocessing. Returns scaled X_train, X_test, y_train, y_test and the DataFrame."""
    df = load_data()
    print(f"Loaded dataset: {df.shape[0]} rows x {df.shape[1]} columns")
    check_nulls(df)
    data = prepare_dataframe(df).dropna()

    X, y = data[FEATURES], data[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=y
    )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)  # fit on train only (no leakage)
    X_test_s = scaler.transform(X_test)

    if save_scaler:
        MODEL_DIR.mkdir(exist_ok=True)
        joblib.dump(scaler, SCALER_PATH)
        print(f"Saved scaler -> {SCALER_PATH.name}")
    return X_train_s, X_test_s, y_train.values, y_test.values, data


def save_eda_plots(data):
    """Save class pie chart, correlation heatmap and feature distributions to /assets."""
    ASSETS_DIR.mkdir(exist_ok=True)

    counts = data[TARGET].value_counts().sort_index()
    plt.figure(figsize=(5, 5))
    plt.pie(counts, labels=["Phishing", "Legitimate"], autopct="%1.1f%%",
            colors=["#E63946", "#2A9D8F"], startangle=90)
    plt.title("Class Distribution")
    plt.savefig(ASSETS_DIR / "class_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(10, 8))
    sns.heatmap(data.corr(), annot=True, fmt=".2f", cmap="coolwarm", annot_kws={"size": 7})
    plt.title("Correlation Heatmap")
    plt.savefig(ASSETS_DIR / "correlation_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()

    fig, axes = plt.subplots(4, 3, figsize=(14, 14))
    plot_df = data.assign(Class=data[TARGET].map({0: "Phishing", 1: "Legitimate"}))
    for ax, col in zip(axes.ravel(), FEATURES):
        sns.histplot(data=plot_df, x=col, hue="Class", bins=25, multiple="layer", alpha=0.55,
                     palette={"Phishing": "#E63946", "Legitimate": "#2A9D8F"}, ax=ax)
        ax.set_title(col, fontsize=10)
        ax.set_xlabel("")
    plt.tight_layout()
    plt.savefig(ASSETS_DIR / "feature_distributions.png", dpi=130, bbox_inches="tight")
    plt.close()
    print("Saved EDA plots to /assets")


if __name__ == "__main__":
    *_, frame = preprocess()
    save_eda_plots(frame)
