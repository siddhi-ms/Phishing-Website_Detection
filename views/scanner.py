"""Page 2 - URL Scanner."""
import streamlit as st

from src.predict import predict_website
from utils.feature_extractor import extract_features
from utils.fetcher import FetchError, analyze_live_page
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
    deep = st.session_state.get("deep_scan", False)
    fetch_warning = None

    with st.spinner("Analyzing the website - this may take a few seconds..." if deep else
                     "Extracting URL features and running the neural network..."):
        live_page = None
        if deep:
            try:
                live_page = analyze_live_page(raw)
            except FetchError as exc:
                fetch_warning = str(exc)
            except Exception as exc:  # unexpected failure - degrade gracefully
                fetch_warning = f"Unexpected error while fetching the page: {exc}"
        try:
            features, parsed, signals = extract_features(raw, live_page=live_page)
            result = predict_website(features)
        except FileNotFoundError:
            st.error("The trained model was not found. Run `python src/train.py` first, then try again.")
            return
        except Exception as exc:  # keep the UI alive on any unexpected error
            st.error(f"Could not analyse this URL: {exc}")
            return

    signals["fetch_warning"] = fetch_warning
    save_scan({"url": parsed["url"], "features": features, "parsed": parsed, "signals": signals,
               "result": result, "security_score": security_score(result)})
    go("Security Report")
    st.rerun()


def render():
    page_header("URL Scanner", "Enter a website address. Features are extracted from the URL automatically.")
    st.text_input("Website URL", key="url_input", placeholder="https://example.com", label_visibility="collapsed")
    st.checkbox(
        "Also fetch the live page to check its external links (optional)",
        key="deep_scan", value=False,
        help="Without this, the external-links feature uses a neutral default and only the URL text "
             "is analysed - nothing is downloaded. With this on, the app makes a real network request "
             "to the address and reads its HTML to count links to other domains. Only enable this for "
             "sites you're comfortable having your computer connect to; it is skipped automatically if "
             "the request fails, times out, or the page isn't HTML.")
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
    md(card("External links (optional deep scan)",
            "The model also uses the share of links pointing to other domains. By default a neutral value is "
            "used so nothing is downloaded. Tick the checkbox above to fetch the real page and measure this "
            "properly - useful when you want the most accurate result, but it does mean your computer connects "
            "to that address.",
            "", "blue"))
