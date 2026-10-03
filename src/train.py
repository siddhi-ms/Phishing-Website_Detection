"""Train the ANN, evaluate it and save model + plots.  Run: python src/train.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, precision_score, recall_score)
from tensorflow import keras
from tensorflow.keras import layers

from src.preprocess import ASSETS_DIR, FEATURES, MODEL_DIR, preprocess, save_eda_plots

SEED = 42
EPOCHS = 25
BATCH_SIZE = 32
MODEL_PATH = MODEL_DIR / "phishing_ann.keras"


def build_model(n_features=len(FEATURES)):
    """12 -> Dense(16, relu) -> Dense(8, relu) -> Dense(1, sigmoid)"""
    model = keras.Sequential([
        keras.Input(shape=(n_features,)),
        layers.Dense(16, activation="relu"),
        layers.Dense(8, activation="relu"),
        layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def plot_history(history):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for ax, key, title in zip(axes, ["accuracy", "loss"], ["Accuracy", "Loss"]):
        ax.plot(history.history[key], label="train")
        ax.plot(history.history[f"val_{key}"], label="validation")
        ax.set_title(f"Model {title}")
        ax.set_xlabel("Epoch")
        ax.legend()
    plt.tight_layout()
    plt.savefig(ASSETS_DIR / "training_curves.png", dpi=150)
    plt.close()


def plot_confusion(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Phishing", "Legitimate"], yticklabels=["Phishing", "Legitimate"])
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    plt.savefig(ASSETS_DIR / "confusion_matrix.png", dpi=150, bbox_inches="tight")
    plt.close()


def main():
    np.random.seed(SEED)
    tf.random.set_seed(SEED)
    MODEL_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)

    X_train, X_test, y_train, y_test, data = preprocess()
    save_eda_plots(data)

    model = build_model()
    model.summary()
    history = model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE,
                        validation_split=0.1, verbose=2)
    model.save(MODEL_PATH)
    print(f"Saved model -> {MODEL_PATH.name}")

    y_pred = (model.predict(X_test, verbose=0).ravel() >= 0.5).astype(int)
    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1_score": round(f1_score(y_test, y_pred), 4),
        "train_samples": int(len(y_train)),
        "test_samples": int(len(y_test)),
    }
    print(classification_report(y_test, y_pred, target_names=["Phishing", "Legitimate"]))
    print(metrics)
    (ASSETS_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))
    plot_history(history)
    plot_confusion(y_test, y_pred)
    print("Done. Now run: streamlit run app.py")


if __name__ == "__main__":
    main()
