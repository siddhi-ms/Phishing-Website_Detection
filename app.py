"""PhishGuard AI - multi-page Streamlit website.  Run: streamlit run app.py"""
import streamlit as st

st.set_page_config(page_title="PhishGuard AI", page_icon=None, layout="wide", initial_sidebar_state="expanded")

from utils.state import PAGES, go, init_state  # noqa: E402
from utils.styles import inject_css, md  # noqa: E402
from views import about, analytics, dashboard, scanner, security_report  # noqa: E402

ROUTES = {
    "Dashboard": dashboard.render,
    "URL Scanner": scanner.render,
    "Security Report": security_report.render,
    "Analytics": analytics.render,
    "About": about.render,
}

inject_css()
init_state()

with st.sidebar:
    md('<div class="pg-logo"><div class="pg-logo-mark">PG</div><div><div class="pg-logo-name">PhishGuard AI</div>'
       '<div class="pg-logo-tag">Phishing Website Detection</div></div></div>')
    for name in PAGES:
        st.button(name, key=f"nav_{name}", on_click=go, args=(name,),
                  type="primary" if st.session_state["page"] == name else "secondary")
    md('<div class="pg-side-foot">Model: ANN (12 - 16 - 8 - 1)<br>Input: 12 URL features<br>Framework: TensorFlow + Streamlit</div>')

ROUTES[st.session_state["page"]]()
