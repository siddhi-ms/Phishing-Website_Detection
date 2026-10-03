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


def extract_features(raw_url, live_page=None):
    """Return (features_dict, parsed_url, signals). features_dict has the 12 model inputs.

    live_page: optional (pct_external, external_count, total_links, final_url) from
    utils.fetcher.analyze_live_page(). When given, PctExtHyperlinks uses the real
    value measured on the fetched page instead of the neutral default.
    """
    url, scheme_assumed = normalize_url(raw_url)
    p = parse_url(url)
    low = url.lower()

    if live_page is not None:
        pct_ext, ext_count, total_links, _ = live_page
        not_extracted = []
    else:
        pct_ext = FEATURE_INFO["PctExtHyperlinks"]["default"]
        ext_count = total_links = None
        not_extracted = NOT_EXTRACTED

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
        "PctExtHyperlinks": pct_ext,
    }
    features = {name: features[name] for name in FEATURES}  # keep the training order

    signals = {
        "scheme_assumed": scheme_assumed,
        "shortener": p["hostname"] in SHORTENERS or p["domain"] in SHORTENERS,
        "not_extracted": not_extracted,
        "live_page": live_page is not None,
        "external_links": ext_count,
        "total_links": total_links,
    }
    return features, p, signals
