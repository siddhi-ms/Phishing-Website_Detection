"""Page 2 - URL Scanner."""
import streamlit as st

from src.predict import predict_website
from utils.feature_extractor import extract_features
from utils.insights import security_score
from utils.parser import validate_url
from utils.state import go, save_scan, set_example
from utils.styles import card, grid, md, page_header, section

EXAMPLES = [
    ("Safe-looking", "https://www.wikipedia.org"),
    ("Suspicious", "http://secure-login.account-verify.example-bank.com/signin/confirm"),
    ("IP + '@'", "http://192.168.10.5/login@secure/account"),
]


def analyze():
    raw = st.session_state.get("url_input", "")
    error = validate_url(raw)
    if error:
        st.error(error)
        return
    with st.spinner("Extracting URL features and running the neural network..."):
        try:
            features, parsed, signals = extract_features(raw)
            result = predict_website(features)
        except FileNotFoundError:
            st.error("The trained model was not found. Run `python src/train.py` first, then try again.")
            return
        except Exception as exc:  # keep the UI alive on any unexpected error
            st.error(f"Could not analyse this URL: {exc}")
            return
    save_scan({"url": parsed["url"], "features": features, "parsed": parsed, "signals": signals,
               "result": result, "security_score": security_score(result)})
    go("Security Report")
    st.rerun()


def render():
    page_header("URL Scanner", "Enter a website address. Features are extracted from the URL automatically.")
    st.text_input("Website URL", key="url_input", placeholder="https://example.com", label_visibility="collapsed")
    if st.button("Analyze Website", type="primary", key="analyze_btn"):
        analyze()
    st.caption("Tip: include http:// or https://. If you leave it out, http:// is assumed.")

    section("Try an example")
    cols = st.columns(len(EXAMPLES))
    for col, (label, url) in zip(cols, EXAMPLES):
        col.button(label, key=f"ex_{label}", on_click=set_example, args=(url,))

    section("What is checked")
    md(grid([
        card("IP address", "Is the host a raw IP instead of a domain name?", "", "red"),
        card("URL length and host length", "Very long addresses can hide the real domain.", "", "blue"),
        card("'@' symbol", "Text before '@' can disguise the true destination.", "", "amber"),
        card("Shortening service", "bit.ly, tinyurl and similar hide where a link goes.", "", "purple"),
        card("Hyphens and digits", "Fake brand domains often use many '-' and numbers.", "", "green"),
        card("Sub-domains and dots", "Deep sub-domain chains imitate trusted names.", "", "blue"),
        card("HTTPS and sensitive words", "No encryption, or words like login/secure/account.", "", "red"),
        card("Path depth", "Number of '/' levels after the domain.", "", "amber"),
    ]))
    md(card("Not scanned: external links",
            "The model also uses the share of links pointing to other domains. That needs the page's HTML, "
            "and this project does not fetch pages, so a neutral default value is used for that one feature.",
            "", "blue"))
