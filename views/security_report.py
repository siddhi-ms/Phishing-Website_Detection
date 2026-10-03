"""Page 3 - Security Report."""
import streamlit as st

from utils.insights import build_checklist, build_recommendations
from utils.state import go
from utils.styles import card, check_item, esc, md, page_header, risk_meter, score_ring, section, verdict_icon


def render():
    page_header("Security Report", "Result of the latest scan.")
    scan = st.session_state.get("scan")
    if not scan:
        md(card("No scan yet", "Analyze a website in the URL Scanner to see its security report here.", "", "blue"))
        st.button("Go to URL Scanner", type="primary", on_click=go, args=("URL Scanner",))
        return

    res, p, feats, sig = scan["result"], scan["parsed"], scan["features"], scan["signals"]
    safe = res["prediction"] == "Legitimate"
    md(f'<div class="pg-verdict {"safe" if safe else "bad"}">{verdict_icon(safe)}'
       f'<div class="pg-verdict-text"><div class="pg-verdict-title">'
       f'{"Legitimate Website" if safe else "Phishing Website Detected"}</div>'
       f'<div class="pg-url">{esc(scan["url"])}</div></div></div>')

    left, mid, right = st.columns([1.2, 1, 1.4])
    with left:
        md(f'<div class="pg-card"><div class="pg-stat-label">Confidence</div>'
           f'<div class="pg-stat-value">{res["confidence"]:.1f}%</div>'
           f'<div class="pg-stat-sub">that this site is {res["prediction"].lower()}</div><br>'
           f'{risk_meter(res["risk_score"], res["risk_level"])}</div>')
    with mid:
        md(f'<div class="pg-card">{score_ring(scan["security_score"])}</div>')
    with right:
        scheme = p["scheme"] + (" (assumed)" if sig["scheme_assumed"] else "")
        rows = [("Protocol", scheme), ("Domain", p["domain"] or "-"), ("Subdomain", p["subdomain"] or "-"),
                ("Path", p["path"] or "/"), ("Query", p["query"] or "-")]
        if p["port"]:
            rows.append(("Port", p["port"]))
        body = "".join(f"<tr><td>{k}</td><td>{esc(v)}</td></tr>" for k, v in rows)
        md(f'<div class="pg-card"><div class="pg-stat-label">URL breakdown</div>'
           f'<table class="pg-table">{body}</table></div>')

    items = build_checklist(feats, sig)
    flagged = sum(i["status"] == "fail" for i in items)
    section("Suspicious feature checklist")
    st.caption(f"{flagged} of {len(items)} checks flagged")
    md('<div class="pg-grid">' + "".join(check_item(i, idx) for idx, i in enumerate(items)) + "</div>")

    section("AI recommendation")
    tips = "".join(f"<li>{esc(t)}</li>" for t in build_recommendations(res, feats, sig))
    accent = {"Low": "green", "Medium": "amber", "High": "red"}[res["risk_level"]]
    md(card(f'{res["risk_level"]} risk', f'<ul class="pg-tips">{tips}</ul>', "", accent))
    st.write("")
    st.button("Scan another website", type="primary", on_click=go, args=("URL Scanner",))
