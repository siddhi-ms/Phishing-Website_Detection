"""Turn features + prediction into a security score, checklist and recommendations."""
from src.predict import FEATURE_INFO, recommendation
from src.preprocess import FEATURES

# feature -> (label, text when OK, text when suspicious)   [hash map]
CHECK_TEXT = {
    "IpAddress": ("IP address as host", lambda v: "Uses a normal domain name", lambda v: "Host is a raw IP address"),
    "UrlLength": ("URL length", lambda v: f"{v} characters - normal", lambda v: f"{v} characters - unusually long"),
    "AtSymbol": ("'@' symbol", lambda v: "Not present", lambda v: "Present - can hide the real destination"),
    "NumDash": ("Hyphens in URL", lambda v: f"{v} found - normal", lambda v: f"{v} found - often used in fake brand names"),
    "SubdomainLevel": ("Sub-domains", lambda v: f"{v} level(s) - normal", lambda v: f"{v} levels - unusually deep"),
    "NumDots": ("Dots in URL", lambda v: f"{v} - normal", lambda v: f"{v} - too many"),
    "PathLevel": ("Path depth", lambda v: f"{v} level(s) - normal", lambda v: f"{v} levels - very deep"),
    "NoHttps": ("HTTPS encryption", lambda v: "HTTPS is used", lambda v: "No HTTPS - connection not encrypted"),
    "NumNumericChars": ("Digits in URL", lambda v: f"{v} - normal", lambda v: f"{v} - many digits"),
    "NumSensitiveWords": ("Sensitive words", lambda v: "None (login, secure, account...)", lambda v: f"{v} found (login, secure, account...)"),
    "HostnameLength": ("Host name length", lambda v: f"{v} characters - normal", lambda v: f"{v} characters - unusually long"),
}


def security_score(result):
    """Security score /100 = model's probability that the site is legitimate."""
    return max(0, min(100, round(100 - result["risk_score"])))


def build_checklist(features, signals):
    """List of {label, detail, status: pass|fail|info, tag}."""
    items = []
    for name in FEATURES:
        value = features[name]
        if name in signals["not_extracted"]:
            items.append({"label": "External links", "status": "info", "tag": "not scanned",
                          "detail": "Needs page content (not fetched) - neutral default used"})
            continue
        label, ok_text, bad_text = CHECK_TEXT[name]
        bad = FEATURE_INFO[name]["bad"](value)
        items.append({"label": label, "status": "fail" if bad else "pass", "tag": "",
                      "detail": bad_text(value) if bad else ok_text(value)})
    items.append({"label": "URL shortening service", "status": "fail" if signals["shortener"] else "pass",
                  "tag": "extra check",
                  "detail": "Shortened link hides the destination" if signals["shortener"] else "Not a known shortener"})
    return items


def build_recommendations(result, features, signals):
    tips = [recommendation(result["risk_level"])]
    if features["IpAddress"]:
        tips.append("The site is reached through a raw IP address. Real services use domain names.")
    if features["AtSymbol"]:
        tips.append("The '@' symbol can make a link look like it goes to a trusted site while it does not.")
    if signals["shortener"]:
        tips.append("Expand the shortened link with a preview tool before opening it.")
    if features["NoHttps"]:
        tips.append("There is no HTTPS, so anything you type can be read in transit. Never enter passwords or card details.")
    if features["NumSensitiveWords"]:
        tips.append("Words like login/secure/account are used to look trustworthy. Open the official site by typing its address yourself.")
    if features["SubdomainLevel"] >= 3 or features["NumDash"] >= 3:
        tips.append("Many sub-domains or hyphens are common in look-alike domains. Check the real domain (the part before the ending).")
    if features["UrlLength"] > 75:
        tips.append("Very long URLs can hide the real domain. Read the address bar carefully.")
    tips.append("This scan reads only the URL text. It does not open the page, so page-content signals are not covered.")
    return tips
