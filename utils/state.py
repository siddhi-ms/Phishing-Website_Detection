"""Session state and navigation helpers."""
import streamlit as st

PAGES = ["Dashboard", "URL Scanner", "Security Report", "Analytics", "About"]


def init_state():
    st.session_state.setdefault("page", "Dashboard")
    st.session_state.setdefault("scan", None)     # last scan result (dict)
    st.session_state.setdefault("history", [])    # list of past scans
    st.session_state.setdefault("url_input", "")


def go(page):
    st.session_state["page"] = page


def set_example(url):
    st.session_state["url_input"] = url


def save_scan(scan):
    st.session_state["scan"] = scan
    st.session_state["history"].insert(0, {
        "url": scan["url"], "prediction": scan["result"]["prediction"],
        "risk_level": scan["result"]["risk_level"], "score": scan["security_score"],
    })
    del st.session_state["history"][8:]
