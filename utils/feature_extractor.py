"""Turn a URL string into the SAME 12 features the ANN was trained on."""
from src.predict import FEATURE_INFO
from src.preprocess import FEATURES
from utils.parser import normalize_url, parse_url

# Same idea as the dataset's "sensitive words" feature
SENSITIVE_WORDS = ("secure", "account", "webscr", "login", "ebayisapi", "signin", "banking", "confirm")

# Hash set: O(1) membership test for URL shortening services
SHORTENERS = {
    "bit.ly", "goo.gl", "tinyurl.com", "t.co", "ow.ly", "is.gd", "buff.ly", "adf.ly", "bit.do",
    "cutt.ly", "rebrand.ly", "shorturl.at", "tiny.cc", "rb.gy", "t.ly", "lnkd.in", "s.id", "v.gd",
}

# Needs the page's HTML (external links) -> not scraped; the existing default value is used.
NOT_EXTRACTED = ["PctExtHyperlinks"]


def extract_features(raw_url):
    """Return (features_dict, parsed_url, signals). features_dict has the 12 model inputs."""
    url, scheme_assumed = normalize_url(raw_url)
    p = parse_url(url)
    low = url.lower()

    features = {
        "NumDots": url.count("."),
        "SubdomainLevel": len(p["subdomain"].split(".")) if p["subdomain"] else 0,
        "PathLevel": p["path"].count("/"),
        "UrlLength": len(url),
        "NumDash": url.count("-"),
        "AtSymbol": int("@" in url),
        "NumNumericChars": sum(ch.isdigit() for ch in url),
        "NoHttps": int(p["scheme"] != "https"),
        "IpAddress": int(p["is_ip"]),
        "NumSensitiveWords": sum(low.count(w) for w in SENSITIVE_WORDS),
        "HostnameLength": len(p["hostname"]),
        "PctExtHyperlinks": FEATURE_INFO["PctExtHyperlinks"]["default"],
    }
    features = {name: features[name] for name in FEATURES}  # keep the training order

    signals = {
        "scheme_assumed": scheme_assumed,
        "shortener": p["hostname"] in SHORTENERS or p["domain"] in SHORTENERS,
        "not_extracted": NOT_EXTRACTED,
    }
    return features, p, signals
