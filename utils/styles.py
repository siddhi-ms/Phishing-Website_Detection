"""Dark cybersecurity theme (CSS) and small HTML component helpers."""
import html as _html
import re

import streamlit as st

ACCENT = {"blue": "#3B82F6", "green": "#10B981", "red": "#EF4444", "amber": "#F59E0B", "purple": "#8B5CF6"}
LEVEL_COLOR = {"Low": "green", "Medium": "amber", "High": "red"}

CSS = """
<style>
:root{--bg:#0B1220;--panel:#111C31;--panel2:#0F1A2E;--border:#1F2D4A;--text:#E5EDF7;--muted:#8CA0BC;
--blue:#3B82F6;--green:#10B981;--red:#EF4444;--amber:#F59E0B;}
.stApp{background:radial-gradient(1100px 480px at 85% -8%,rgba(59,130,246,.14),transparent 60%),
radial-gradient(900px 420px at -5% 105%,rgba(16,185,129,.09),transparent 60%),#0B1220;color:var(--text);}
[data-testid="stHeader"]{background:transparent;}
#MainMenu,footer{visibility:hidden;}
.block-container{padding-top:2rem;padding-bottom:3rem;max-width:1150px;}
h1,h2,h3,h4,p,li,label,span{color:var(--text);}
[data-testid="stSidebar"]{background:var(--panel2);border-right:1px solid var(--border);}
[data-testid="stSidebar"] .block-container{padding-top:1rem;}

/* buttons */
.stButton>button{border-radius:12px;border:1px solid var(--border);background:var(--panel);color:var(--text);
padding:.6rem 1rem;font-weight:600;transition:all .2s ease;}
.stButton>button:hover{border-color:var(--blue);transform:translateY(-2px);box-shadow:0 6px 18px rgba(59,130,246,.25);color:#fff;}
.stButton>button[kind="primary"],.stButton>button[data-testid="stBaseButton-primary"]{
background:linear-gradient(90deg,#2563EB,#10B981);border:none;color:#fff;}
[data-testid="stSidebar"] .stButton>button{width:100%;justify-content:flex-start;text-align:left;background:transparent;border:1px solid transparent;}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(59,130,246,.12);border-color:var(--border);transform:none;box-shadow:none;}
[data-testid="stSidebar"] .stButton>button[kind="primary"],
[data-testid="stSidebar"] .stButton>button[data-testid="stBaseButton-primary"]{
background:linear-gradient(90deg,rgba(37,99,235,.35),rgba(16,185,129,.25));border:1px solid #2B4A86;}

/* inputs */
.stTextInput input{font-size:1.15rem;padding:.95rem 1.1rem;border-radius:14px;background:var(--panel2);
border:1px solid var(--border);color:var(--text);}
.stTextInput input:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(59,130,246,.25);}
[data-testid="stImage"] img{border-radius:12px;background:#fff;}

/* components */
.pg-logo{display:flex;align-items:center;gap:.7rem;padding:.4rem .4rem 1rem .4rem;}
.pg-logo-mark{width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;
font-size:15px;font-weight:800;letter-spacing:.02em;color:#fff;background:linear-gradient(135deg,#2563EB,#10B981);box-shadow:0 4px 16px rgba(37,99,235,.4);}
.pg-logo-name{font-size:1.2rem;font-weight:800;color:#fff;line-height:1.1;}
.pg-logo-tag{font-size:.72rem;color:var(--muted);}
.pg-side-foot{margin-top:1.5rem;padding:.8rem;border:1px solid var(--border);border-radius:12px;font-size:.78rem;color:var(--muted);}
.pg-hero{position:relative;overflow:hidden;background:linear-gradient(135deg,#0F1F3D 0%,#111C31 55%,#0E2A2A 100%);
border:1px solid var(--border);border-radius:22px;padding:2.6rem 2.2rem;margin-bottom:1rem;}
.pg-hero:after{content:"";position:absolute;right:-60px;top:-60px;width:260px;height:260px;border-radius:50%;
background:radial-gradient(circle,rgba(59,130,246,.35),transparent 70%);}
.pg-pill{display:inline-block;padding:.25rem .7rem;border-radius:999px;font-size:.75rem;font-weight:700;letter-spacing:.04em;
background:rgba(16,185,129,.15);color:#34D399;border:1px solid rgba(16,185,129,.4);}
.pg-hero h1{font-size:2.8rem;font-weight:800;margin:.7rem 0 .4rem 0;line-height:1.1;
background:linear-gradient(90deg,#60A5FA,#34D399);-webkit-background-clip:text;background-clip:text;color:transparent!important;}
.pg-hero p{color:var(--muted);font-size:1.05rem;max-width:640px;margin:0;}
.pg-head{margin-bottom:1.2rem;}
.pg-head h1{font-size:2rem;font-weight:800;margin:0;}
.pg-head p{color:var(--muted);margin:.2rem 0 0 0;}
.pg-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem;margin:1rem 0;}
.pg-card{background:var(--panel);border:1px solid var(--border);border-radius:16px;padding:1.15rem 1.25rem;
transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease;height:100%;box-sizing:border-box;}
.pg-card:hover{transform:translateY(-4px);border-color:var(--accent,#3B82F6);box-shadow:0 10px 28px rgba(0,0,0,.4);}
.pg-card-icon{font-size:1.5rem;margin-bottom:.3rem;}
.pg-card-icon:empty{display:none;}
.pg-card-title{font-weight:700;font-size:1.05rem;color:#fff;margin-bottom:.3rem;}
.pg-card-body{color:var(--muted);font-size:.93rem;line-height:1.5;}
.pg-stat-label{color:var(--muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;}
.pg-stat-value{font-size:1.9rem;font-weight:800;color:var(--accent,#fff);margin:.1rem 0;}
.pg-stat-sub{color:var(--muted);font-size:.82rem;}
.pg-section{font-size:1.25rem;font-weight:700;margin:1.6rem 0 .2rem 0;color:#fff;}
.pg-verdict{border-radius:18px;padding:1.4rem 1.6rem;border:1px solid;margin-bottom:1rem;}
.pg-verdict.safe{background:rgba(16,185,129,.10);border-color:rgba(16,185,129,.55);}
.pg-verdict.bad{background:rgba(239,68,68,.10);border-color:rgba(239,68,68,.55);}
.pg-verdict-title{font-size:1.8rem;font-weight:800;}
.pg-verdict.safe .pg-verdict-title{color:#34D399;}
.pg-verdict.bad .pg-verdict-title{color:#F87171;}
.pg-url{font-family:Consolas,monospace;color:var(--muted);word-break:break-all;font-size:.9rem;margin-top:.3rem;}
.pg-meter{background:linear-gradient(90deg,#10B981 0%,#F59E0B 50%,#EF4444 100%);border-radius:10px;height:18px;position:relative;margin:1rem 0 .3rem 0;}
.pg-meter-pin{position:absolute;top:-7px;width:12px;height:32px;background:#fff;border:2px solid #0B1220;border-radius:5px;}
.pg-meter-scale{display:flex;justify-content:space-between;color:var(--muted);font-size:.75rem;}
.pg-ring{width:150px;height:150px;border-radius:50%;margin:.3rem auto;display:flex;align-items:center;justify-content:center;
background:conic-gradient(var(--c) calc(var(--p)*1%),#1F2D4A 0);}
.pg-ring-in{width:118px;height:118px;border-radius:50%;background:var(--panel);display:flex;flex-direction:column;align-items:center;justify-content:center;}
.pg-ring-num{font-size:2.2rem;font-weight:800;line-height:1;color:var(--c);}
.pg-ring-sub{font-size:.75rem;color:var(--muted);}
.pg-check{display:flex;gap:.8rem;align-items:flex-start;background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:.8rem 1rem;transition:all .2s;}
.pg-check:hover{border-color:#2B4A86;transform:translateY(-2px);}
.pg-check-ico{flex:0 0 28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.9rem;}
.pg-check.pass .pg-check-ico{background:rgba(16,185,129,.18);color:#34D399;}
.pg-check.fail .pg-check-ico{background:rgba(239,68,68,.18);color:#F87171;}
.pg-check.info .pg-check-ico{background:rgba(59,130,246,.18);color:#60A5FA;}
.pg-check-label{font-weight:700;color:#fff;font-size:.95rem;}
.pg-check-detail{color:var(--muted);font-size:.85rem;}
.pg-tag{display:inline-block;margin-left:.4rem;padding:.05rem .45rem;border-radius:999px;font-size:.65rem;font-weight:700;background:#1F2D4A;color:#9DB2D3;}
.pg-table{width:100%;border-collapse:collapse;font-size:.92rem;}
.pg-table td{padding:.5rem .3rem;border-bottom:1px solid var(--border);vertical-align:top;}
.pg-table td:first-child{color:var(--muted);width:34%;}
.pg-table td:last-child{font-family:Consolas,monospace;color:#E5EDF7;word-break:break-all;}
.pg-tips{margin:0;padding-left:1.1rem;color:var(--muted);line-height:1.7;}
.pg-tips li{color:#C9D6EA;}
.pg-flow{display:flex;flex-wrap:wrap;align-items:center;gap:.5rem;margin:.8rem 0;}
.pg-node{padding:.7rem 1rem;border-radius:12px;font-weight:700;text-align:center;color:#fff;font-size:.9rem;}
.pg-arrow{color:var(--muted);font-size:1.3rem;}
.pg-code{font-family:Consolas,monospace;background:#0B1220;border:1px solid var(--border);border-radius:6px;padding:0 .35rem;color:#7DD3FC;font-size:.85rem;}
@media (max-width:700px){.pg-hero{padding:1.6rem 1.2rem;}.pg-hero h1{font-size:2rem;}.pg-head h1{font-size:1.6rem;}}

@keyframes pgPop{0%{transform:scale(0) rotate(-15deg);opacity:0;}60%{transform:scale(1.18) rotate(4deg);opacity:1;}100%{transform:scale(1) rotate(0);}}
.pg-check-ico{animation:pgPop .45s cubic-bezier(.34,1.56,.64,1) both;}
.pg-verdict{display:flex;align-items:center;gap:1.1rem;}
.pg-verdict-text{flex:1;}
.pg-verdict-icon{flex:0 0 auto;overflow:visible;}
.pg-verdict-icon circle,.pg-verdict-icon path{stroke:var(--c);stroke-width:4;stroke-linecap:round;stroke-linejoin:round;fill:none;}
.pg-draw{stroke-dashoffset:0;animation:pgDraw .6s ease-out both;}
.pg-draw-ring{stroke-dasharray:175;stroke-dashoffset:175;animation:pgDraw .7s ease-out both;}
.pg-draw-mark{stroke-dasharray:60;stroke-dashoffset:60;animation:pgDraw .45s ease-out .5s both;}
@keyframes pgDraw{to{stroke-dashoffset:0;}}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def esc(value):
    return _html.escape(str(value), quote=True)


def md(markup):
    """Render trusted HTML. Newlines/indent are removed so Markdown never turns it into a code block."""
    flat = re.sub(r">\s*\n\s*<", "><", markup.strip())
    flat = re.sub(r"\s*\n\s*", " ", flat)
    st.markdown(flat, unsafe_allow_html=True)


def page_header(title, subtitle):
    md(f'<div class="pg-head"><h1>{esc(title)}</h1><p>{esc(subtitle)}</p></div>')


def section(title):
    md(f'<div class="pg-section">{esc(title)}</div>')


def card(title, body, icon="", accent="blue"):
    return (f'<div class="pg-card" style="--accent:{ACCENT[accent]}"><div class="pg-card-icon">{icon}</div>'
            f'<div class="pg-card-title">{title}</div><div class="pg-card-body">{body}</div></div>')


def stat_card(icon, label, value, sub="", accent="blue"):
    return (f'<div class="pg-card" style="--accent:{ACCENT[accent]}"><div class="pg-card-icon">{icon}</div>'
            f'<div class="pg-stat-label">{label}</div><div class="pg-stat-value">{value}</div>'
            f'<div class="pg-stat-sub">{sub}</div></div>')


def grid(items):
    return '<div class="pg-grid">' + "".join(items) + "</div>"


def risk_meter(score, level):
    color = ACCENT[LEVEL_COLOR[level]]
    pos = max(1, min(97, score))
    return (f'<div class="pg-stat-label">Risk meter</div>'
            f'<div class="pg-meter"><div class="pg-meter-pin" style="left:calc({pos}% - 6px)"></div></div>'
            f'<div class="pg-meter-scale"><span>0 Low</span><span>50 Medium</span><span>100 High</span></div>'
            f'<div style="margin-top:.6rem;font-size:1.4rem;font-weight:800;color:{color}">{level} risk '
            f'<span style="color:#8CA0BC;font-size:.95rem;font-weight:600">({score:.1f} / 100)</span></div>')


def score_ring(score):
    color = ACCENT["green"] if score >= 70 else ACCENT["amber"] if score >= 40 else ACCENT["red"]
    return (f'<div class="pg-ring" style="--p:{score};--c:{color}"><div class="pg-ring-in">'
            f'<div class="pg-ring-num">{score}</div><div class="pg-ring-sub">/ 100</div></div></div>'
            f'<div style="text-align:center" class="pg-stat-label">Security score</div>')


def check_item(item, index=0):
    icon = {"pass": "\u2714", "fail": "\u2716", "info": "i"}[item["status"]]
    tag = f'<span class="pg-tag">{esc(item["tag"])}</span>' if item["tag"] else ""
    delay = f'style="animation-delay:{index * 0.06:.2f}s"'
    return (f'<div class="pg-check {item["status"]}"><div class="pg-check-ico" {delay}>{icon}</div><div>'
            f'<div class="pg-check-label">{esc(item["label"])}{tag}</div>'
            f'<div class="pg-check-detail">{esc(item["detail"])}</div></div></div>')


def verdict_icon(safe):
    """Small animated tick / cross drawn as SVG (circle + mark 'draws in')."""
    color = ACCENT["green"] if safe else ACCENT["red"]
    mark = ('<path class="pg-draw pg-draw-mark" d="M18 33 L28 43 L46 21"/>' if safe else
            '<path class="pg-draw pg-draw-mark" d="M21 21 L43 43"/>'
            '<path class="pg-draw pg-draw-mark" d="M43 21 L21 43"/>')
    return (f'<svg class="pg-verdict-icon" viewBox="0 0 64 64" width="56" height="56" style="--c:{color}">'
            f'<circle class="pg-draw pg-draw-ring" cx="32" cy="32" r="27"/>{mark}</svg>')
