"""Reusable prediction module: predict_website(features_dict)."""
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import pandas as pd

from src.preprocess import FEATURES, MODEL_DIR, SCALER_PATH

MODEL_PATH = MODEL_DIR / "phishing_ann.keras"

# Hash map (dict): feature -> description, input range, default, and "suspicious" rule.
FEATURE_INFO = {
    "NumDots": {"desc": "Number of '.' in the URL", "min": 0, "max": 30, "default": 2, "step": 1,
                "rule": "> 3", "bad": lambda v: v > 3},
    "SubdomainLevel": {"desc": "Number of sub-domain levels", "min": 0, "max": 15, "default": 1, "step": 1,
                       "rule": ">= 3", "bad": lambda v: v >= 3},
    "PathLevel": {"desc": "Number of '/' levels in the URL path", "min": 0, "max": 30, "default": 2, "step": 1,
                  "rule": "> 5", "bad": lambda v: v > 5},
    "UrlLength": {"desc": "Total characters in the URL", "min": 1, "max": 1000, "default": 40, "step": 1,
                  "rule": "> 75", "bad": lambda v: v > 75},
    "NumDash": {"desc": "Number of '-' in the URL", "min": 0, "max": 50, "default": 0, "step": 1,
                "rule": ">= 3", "bad": lambda v: v >= 3},
    "AtSymbol": {"desc": "'@' present in the URL (1 = yes, 0 = no)", "min": 0, "max": 1, "default": 0, "step": 1,
                 "rule": "= 1", "bad": lambda v: v == 1},
    "NumNumericChars": {"desc": "Number of digits in the URL", "min": 0, "max": 200, "default": 0, "step": 1,
                        "rule": "> 10", "bad": lambda v: v > 10},
    "NoHttps": {"desc": "HTTPS not used (1 = no HTTPS, 0 = HTTPS)", "min": 0, "max": 1, "default": 0, "step": 1,
                "rule": "= 1", "bad": lambda v: v == 1},
    "IpAddress": {"desc": "IP address used as host (1 = yes, 0 = no)", "min": 0, "max": 1, "default": 0, "step": 1,
                  "rule": "= 1", "bad": lambda v: v == 1},
    "NumSensitiveWords": {"desc": "Words like login, secure, bank, account", "min": 0, "max": 10, "default": 0,
                          "step": 1, "rule": ">= 1", "bad": lambda v: v >= 1},
    "HostnameLength": {"desc": "Characters in the host name", "min": 1, "max": 300, "default": 15, "step": 1,
                       "rule": "> 30", "bad": lambda v: v > 30},
    "PctExtHyperlinks": {"desc": "Fraction of links pointing to other domains (0-1)", "min": 0.0, "max": 1.0,
                         "default": 0.1, "step": 0.05, "rule": "> 0.5", "bad": lambda v: v > 0.5},
}

# Ready-made examples for demo / viva
PRESETS = {
    "Legitimate-like": {"NumDots": 2, "SubdomainLevel": 1, "PathLevel": 2, "UrlLength": 40, "NumDash": 0,
                        "AtSymbol": 0, "NumNumericChars": 0, "NoHttps": 0, "IpAddress": 0,
                        "NumSensitiveWords": 0, "HostnameLength": 15, "PctExtHyperlinks": 0.1},
    "Phishing-like": {"NumDots": 5, "SubdomainLevel": 3, "PathLevel": 6, "UrlLength": 110, "NumDash": 4,
                      "AtSymbol": 1, "NumNumericChars": 15, "NoHttps": 1, "IpAddress": 1,
                      "NumSensitiveWords": 2, "HostnameLength": 45, "PctExtHyperlinks": 0.9},
}


def get_risk_level(risk_score):
    """0-30 Low, 31-70 Medium, 71-100 High."""
    score = round(risk_score)
    if score <= 30:
        return "Low"
    if score <= 70:
        return "Medium"
    return "High"


def suspicious_features(features_dict):
    """Return (feature, description, value, rule) for every feature that breaks its rule."""
    return [(n, FEATURE_INFO[n]["desc"], features_dict[n], FEATURE_INFO[n]["rule"])
            for n in FEATURES if FEATURE_INFO[n]["bad"](features_dict[n])]


def recommendation(risk_level):
    return {
        "Low": "Site looks safe, but always check the address bar and avoid sharing secrets unless needed.",
        "Medium": "Be careful. Verify the URL manually and avoid entering passwords or card details.",
        "High": "Do NOT enter any personal data. Leave the site and report it as phishing.",
    }[risk_level]


@lru_cache(maxsize=1)
def _load_artifacts():
    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        raise FileNotFoundError("Model not found. Run `python src/train.py` first.")
    from tensorflow import keras  # imported lazily so the UI loads fast

    return keras.models.load_model(MODEL_PATH), joblib.load(SCALER_PATH)


def predict_website(features_dict):
    """features_dict: {feature_name: number}. Returns prediction, confidence, risk level."""
    missing = [f for f in FEATURES if f not in features_dict]
    if missing:
        raise KeyError(f"Missing features: {missing}")
    model, scaler = _load_artifacts()

    vector = pd.DataFrame([[float(features_dict[f]) for f in FEATURES]], columns=FEATURES)
    p_legit = float(model.predict(scaler.transform(vector), verbose=0)[0][0])
    p_phish = 1.0 - p_legit  # sigmoid output = P(Legitimate)

    risk_score = round(p_phish * 100, 2)
    return {
        "prediction": "Legitimate" if p_legit >= 0.5 else "Phishing",
        "confidence": round(max(p_legit, p_phish) * 100, 2),
        "risk_score": risk_score,
        "risk_level": get_risk_level(risk_score),
    }


if __name__ == "__main__":
    for name, preset in PRESETS.items():
        print(name, "->", predict_website(preset))
