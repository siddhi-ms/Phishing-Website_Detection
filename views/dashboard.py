"""Page 1 - Dashboard."""
import streamlit as st

from utils import data
from utils.state import go
from utils.styles import card, esc, grid, md, section, stat_card


def render():
    stats = data.dataset_stats()
    metrics = data.load_metrics()
    ready = data.model_ready()

    md("""<div class="pg-hero"><span class="pg-pill">AI-POWERED THREAT DETECTION</span>
    <h1>PhishGuard AI</h1>
    <p>Paste a website address and our Artificial Neural Network checks it for phishing signals in seconds,
    then explains the result with a risk meter, a security score and clear advice.</p></div>""")
    st.button("Scan Website", type="primary", key="hero_scan", on_click=go, args=("URL Scanner",))

    section("Model overview")
    size = f"{stats['rows']:,}" if stats else "-"
    size_sub = (f"{stats['phishing']:,} phishing, {stats['legit']:,} legitimate" if stats
                else "dataset/phishing.csv not found")
    acc = f"{metrics['accuracy'] * 100:.1f}%" if metrics else "-"
    acc_sub = "on the 20% test split" if metrics else "run src/train.py to see"
    md(grid([
        stat_card("", "Model", "ANN", "12 - 16 - 8 - 1 - ReLU / Sigmoid", "blue"),
        stat_card("", "Input features", "12", "URL and host characteristics", "green"),
        stat_card("", "Dataset size", size, size_sub, "purple"),
        stat_card("", "Test accuracy", acc, acc_sub, "amber"),
    ]))
    if not ready:
        md(card("Model not trained yet",
                "Run <span class='pg-code'>python src/train.py</span> once to create the model and scaler. "
                "Scanning needs <span class='pg-code'>phishing_ann.keras</span> and <span class='pg-code'>scaler.pkl</span>.",
                "", "amber"))

    section("How it works")
    md(grid([
        card("1. Enter a URL", "Type or paste any website address into the scanner.", "", "blue"),
        card("2. Extract features", "String analysis reads length, dots, dashes, '@', IP host, sub-domains, HTTPS and more.", "", "green"),
        card("3. ANN prediction", "The saved scaler and neural network output phishing probability.", "", "purple"),
        card("4. Security report", "Verdict, confidence, risk level, security score and recommendations.", "", "red"),
    ]))

    history = st.session_state.get("history", [])
    if history:
        section("Recent scans")
        rows = "".join(
            f'<tr><td>{esc(h["url"][:70])}</td><td>{esc(h["prediction"])}</td><td>{esc(h["risk_level"])}</td><td>{h["score"]}/100</td></tr>'
            for h in history[:5])
        md(f'<div class="pg-card"><table class="pg-table"><tr><td style="font-family:inherit">URL</td>'
           f'<td style="font-family:inherit">Result</td><td style="font-family:inherit">Risk</td>'
           f'<td style="font-family:inherit">Score</td></tr>{rows}</table></div>')
