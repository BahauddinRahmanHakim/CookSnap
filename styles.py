"""
styles.py — CookSnap
Semua CSS dan tema (dark/light) untuk aplikasi.
"""

import streamlit as st


def get_theme_vars(is_light: bool) -> str:
    if is_light:
        return """
    :root {
        --bg-primary:    #faf8f5;
        --bg-secondary:  #f0ede8;
        --bg-card:       #ffffff;
        --bg-card-hover: #f5f3ef;
        --accent-warm:   #d4952e;
        --accent-orange: #c4521e;
        --accent-green:  #4d9650;
        --accent-blue:   #4189bf;
        --text-primary:  #1a1814;
        --text-muted:    #6b6560;
        --text-dim:      #9a948c;
        --border:        #e0dcd5;
        --border-accent: #d4952e30;
        --radius:        14px;
        --radius-sm:     8px;
        --card-shadow:   0 2px 12px rgba(0,0,0,0.06);
        --hero-grad-1:   #f5f0e6;
        --hero-grad-2:   #faf8f5;
        --hero-grad-3:   #f5ede0;
        --hero-glow-1:   rgba(212,149,46,0.08);
        --hero-glow-2:   rgba(196,82,30,0.06);
        --scrollbar-track: #f0ede8;
        --scrollbar-thumb: #d5d0c9;
        --scrollbar-hover: #b0aaa2;
        --alert-success-bg: #e8f5e9;
        --alert-success-text: #2e7d32;
        --alert-success-border: #a5d6a7;
        --alert-info-bg: #e3f2fd;
        --alert-info-text: #1565c0;
        --alert-info-border: #90caf9;
        --alert-warning-bg: #fff3e0;
        --alert-warning-text: #e65100;
        --alert-warning-border: #ffcc80;
        --alert-error-bg: #ffebee;
        --alert-error-text: #c62828;
        --alert-error-border: #ef9a9a;
        --text-on-accent: #000000;
    }
    """
    else:
        return """
    :root {
        --bg-primary:    #0f0e0c;
        --bg-secondary:  #1a1814;
        --bg-card:       #211f1b;
        --bg-card-hover: #2a2720;
        --accent-warm:   #e8a838;
        --accent-orange: #d4622a;
        --accent-green:  #6aaf6a;
        --accent-blue:   #5ba3d9;
        --text-primary:  #f0ece4;
        --text-muted:    #8a8070;
        --text-dim:      #5a5248;
        --border:        #302c26;
        --border-accent: #e8a83830;
        --radius:        14px;
        --radius-sm:     8px;
        --card-shadow:   0 2px 12px rgba(0,0,0,0.25);
        --hero-grad-1:   #1a1408;
        --hero-grad-2:   #0f0e0c;
        --hero-grad-3:   #1a1008;
        --hero-glow-1:   rgba(232,168,56,0.06);
        --hero-glow-2:   rgba(212,98,42,0.05);
        --scrollbar-track: #1a1814;
        --scrollbar-thumb: #302c26;
        --scrollbar-hover: #5a5248;
        --alert-success-bg: rgba(106,175,106,0.15);
        --alert-success-text: #6aaf6a;
        --alert-success-border: rgba(106,175,106,0.35);
        --alert-info-bg: rgba(91,163,217,0.15);
        --alert-info-text: #5ba3d9;
        --alert-info-border: rgba(91,163,217,0.35);
        --alert-warning-bg: rgba(232,168,56,0.15);
        --alert-warning-text: #e8a838;
        --alert-warning-border: rgba(232,168,56,0.35);
        --alert-error-bg: rgba(212,98,42,0.15);
        --alert-error-text: #d4622a;
        --alert-error-border: rgba(212,98,42,0.35);
        --text-on-accent: #ffffff;
    }
    """


COMPONENT_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

.sidebar-brand { padding: 16px 0 24px 0; }
.sidebar-brand-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem; font-weight: 800;
    background: linear-gradient(135deg, var(--accent-warm), var(--accent-orange));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.sidebar-brand-sub {
    font-size: 0.7rem; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px;
}
.sidebar-stats { font-size: 0.72rem; color: var(--text-dim); padding: 8px 0; }
.sidebar-stats strong { color: var(--text-muted); }

#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }

[data-testid="collapsedControl"] {
    color: var(--accent-warm) !important; background: var(--bg-card) !important;
    border: 1px solid var(--border) !important; border-radius: 8px !important;
    top: 12px !important; left: 12px !important;
    width: 40px !important; height: 40px !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4) !important;
    transition: all 0.2s ease !important; z-index: 999 !important;
}
[data-testid="collapsedControl"]:hover {
    background: var(--accent-warm) !important; color: var(--text-on-accent) !important;
    border-color: var(--accent-warm) !important; transform: scale(1.05) !important;
}
[data-testid="collapsedControl"] svg { fill: var(--accent-warm) !important; width: 20px !important; height: 20px !important; }
[data-testid="collapsedControl"]:hover svg { fill: var(--text-on-accent) !important; }

/* HERO */
.hero-section {
    background: linear-gradient(135deg, var(--hero-grad-1) 0%, var(--hero-grad-2) 50%, var(--hero-grad-3) 100%);
    border: 1px solid var(--border); border-radius: 24px;
    padding: 72px 48px 56px; text-align: center;
    position: relative; overflow: hidden; margin-bottom: 48px;
}
.hero-section::before {
    content: ''; position: absolute;
    top: -100px; left: -100px; right: -100px; bottom: -100px;
    background: radial-gradient(ellipse at 30% 50%, var(--hero-glow-1) 0%, transparent 60%),
                radial-gradient(ellipse at 70% 50%, var(--hero-glow-2) 0%, transparent 60%);
    pointer-events: none;
    animation: heroGlow 6s ease-in-out infinite alternate;
}
@keyframes heroGlow { 0% { opacity: 0.6; transform: scale(1); } 100% { opacity: 1; transform: scale(1.05); } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes shimmer { 0% { background-position: -200% center; } 100% { background-position: 200% center; } }

.hero-logo {
    font-family: 'Playfair Display', serif; font-size: 4.5rem; font-weight: 800;
    background: linear-gradient(135deg, var(--accent-warm) 0%, var(--accent-orange) 40%, var(--accent-warm) 80%, #f0d48a 100%);
    background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1; margin-bottom: 16px;
    animation: fadeInUp 0.8s ease-out, shimmer 4s linear infinite;
}
.hero-tagline {
    font-size: 1.3rem; color: var(--text-muted); font-weight: 300;
    max-width: 580px; margin: 0 auto 14px; line-height: 1.65;
    animation: fadeInUp 0.8s ease-out 0.15s both;
}
.hero-sub {
    font-size: 0.82rem; color: var(--text-dim); letter-spacing: 0.08em;
    text-transform: uppercase; margin-bottom: 40px;
    animation: fadeInUp 0.8s ease-out 0.3s both;
}
.hero-stats {
    display: flex; justify-content: center; gap: 56px; margin-bottom: 44px;
    animation: fadeInUp 0.8s ease-out 0.45s both;
}
.hero-stat-num {
    font-family: 'Playfair Display', serif; font-size: 2.4rem; font-weight: 800;
    background: linear-gradient(135deg, var(--accent-warm), var(--accent-orange));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-stat-label { font-size: 0.72rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(232,168,56,0.1); border: 1px solid rgba(232,168,56,0.3);
    color: var(--accent-warm); font-size: 0.75rem; font-weight: 600;
    padding: 6px 16px; border-radius: 20px; margin: 4px;
    letter-spacing: 0.04em; transition: all 0.2s ease;
}
.hero-badge:hover { background: rgba(232,168,56,0.2); transform: translateY(-1px); }

/* QUICK SEARCH */
.quick-search-wrap {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 20px; padding: 32px 36px;
    margin: -20px auto 48px; max-width: 750px;
    position: relative; box-shadow: var(--card-shadow);
    animation: fadeInUp 0.8s ease-out 0.6s both;
}
.quick-search-wrap::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--accent-warm), var(--accent-orange), var(--accent-warm));
    border-radius: 20px 20px 0 0;
}
.quick-search-label { font-family: 'Playfair Display', serif; font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.quick-search-hint { font-size: 0.78rem; color: var(--text-muted); margin-bottom: 16px; }

/* FEATURE CARDS */
.feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 48px; }
.feature-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 32px 26px;
    position: relative; overflow: hidden; transition: all 0.3s ease; box-shadow: var(--card-shadow);
}
.feature-card:hover { border-color: rgba(232,168,56,0.4); transform: translateY(-4px); box-shadow: 0 16px 48px rgba(0,0,0,0.15); }
.feature-card::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--accent-warm), var(--accent-orange));
    transform: scaleX(0); transition: transform 0.3s ease;
}
.feature-card:hover::after { transform: scaleX(1); }
.feature-icon { font-size: 2.4rem; margin-bottom: 16px; display: block; }
.feature-title { font-family: 'Playfair Display', serif; font-size: 1.08rem; font-weight: 700; color: var(--text-primary); margin-bottom: 10px; }
.feature-desc { font-size: 0.82rem; color: var(--text-muted); line-height: 1.7; }

/* HOW IT WORKS */
.how-step { display: flex; align-items: flex-start; gap: 20px; padding: 20px 0; border-bottom: 1px solid var(--border); }
.how-step:last-child { border-bottom: none; }
.how-num {
    flex-shrink: 0; width: 40px; height: 40px;
    background: linear-gradient(135deg, var(--accent-warm), var(--accent-orange));
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem; font-weight: 800; color: var(--text-on-accent);
}
.how-title { font-weight: 600; font-size: 0.95rem; color: var(--text-primary); margin-bottom: 4px; }
.how-desc { font-size: 0.8rem; color: var(--text-muted); line-height: 1.6; }

/* DIVIDER */
.divider-section { text-align: center; margin: 48px 0 36px; position: relative; }
.divider-section::before { content: ''; position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: var(--border); }
.divider-label {
    display: inline-block; background: var(--bg-primary); padding: 0 24px;
    font-size: 0.78rem; color: var(--text-dim); text-transform: uppercase;
    letter-spacing: 0.14em; position: relative; font-weight: 500;
}

/* METRIC CARDS */
.metric-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }
.metric-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 16px 20px;
    position: relative; overflow: hidden; box-shadow: var(--card-shadow);
}
.metric-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--accent-warm), var(--accent-orange));
}
.metric-value { font-size: 1.8rem; font-weight: 700; color: var(--accent-warm); font-family: 'Playfair Display', serif; }
.metric-label { font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px; }

/* RECIPE CARD */
.recipe-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 20px; margin-bottom: 14px;
    transition: all 0.25s ease; cursor: pointer; position: relative; box-shadow: var(--card-shadow);
}
.recipe-card:hover {
    border-color: var(--accent-warm); background: var(--bg-card-hover);
    transform: translateY(-2px); box-shadow: 0 8px 32px rgba(232, 168, 56, 0.12);
}
.recipe-rank {
    position: absolute; top: 16px; right: 16px;
    background: linear-gradient(135deg, var(--accent-warm), var(--accent-orange));
    color: var(--text-on-accent); font-size: 0.65rem; font-weight: 700;
    padding: 3px 10px; border-radius: 20px; letter-spacing: 0.06em;
}
.recipe-title {
    font-family: 'Playfair Display', serif; font-size: 1.15rem; font-weight: 700;
    color: var(--text-primary); margin-bottom: 6px; padding-right: 80px; line-height: 1.35;
}
.recipe-meta { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 10px; }
.meta-chip {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.72rem; color: var(--text-muted); background: var(--bg-secondary);
    padding: 3px 10px; border-radius: 20px; border: 1px solid var(--border);
}
.match-bar-wrap { margin-top: 10px; }
.match-label { font-size: 0.7rem; color: var(--text-muted); margin-bottom: 4px; display: flex; justify-content: space-between; }
.match-bar-bg { height: 5px; background: var(--bg-secondary); border-radius: 10px; overflow: hidden; }
.match-bar-fill { height: 100%; border-radius: 10px; background: linear-gradient(90deg, var(--accent-green), var(--accent-warm)); transition: width 0.6s ease; }
.ingredient-pills { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px; }
.ing-pill-have { font-size: 0.68rem; padding: 2px 8px; border-radius: 20px; background: rgba(106, 175, 106, 0.15); border: 1px solid rgba(106, 175, 106, 0.4); color: var(--accent-green); }
.ing-pill-miss { font-size: 0.68rem; padding: 2px 8px; border-radius: 20px; background: rgba(212, 98, 42, 0.1); border: 1px solid var(--accent-orange); color: var(--accent-orange); }

/* RECIPE IMAGE */
.recipe-image-placeholder { width: 100%; display: flex; align-items: center; justify-content: center; background: var(--bg-secondary); border-radius: var(--radius); border: 1px solid var(--border); margin-bottom: 16px; font-size: 4rem; }

/* SECTION TITLE */
.section-title { font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.section-sub { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 20px; }

/* STEP CARD */
.step-card { display: flex; gap: 16px; padding: 14px 0; border-bottom: 1px solid var(--border); }
.step-num {
    flex-shrink: 0; width: 32px; height: 32px;
    background: linear-gradient(135deg, var(--accent-warm), var(--accent-orange));
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 700; color: var(--text-on-accent);
}
.step-text { font-size: 0.88rem; line-height: 1.65; color: var(--text-primary); padding-top: 5px; }

/* NUTRITION BARS */
.nut-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.nut-label { font-size: 0.75rem; color: var(--text-muted); width: 60px; text-align: right; }
.nut-bar-bg { flex: 1; height: 8px; background: var(--bg-secondary); border-radius: 10px; overflow: hidden; }
.nut-bar-fill { height: 100%; border-radius: 10px; }
.nut-val { font-size: 0.72rem; color: var(--text-muted); width: 50px; }

/* CHAT */
.chat-bubble-user {
    background: linear-gradient(135deg, var(--accent-warm), var(--accent-orange));
    color: #000; padding: 10px 16px; border-radius: 18px 18px 4px 18px;
    margin-bottom: 10px; font-size: 0.88rem; max-width: 75%; margin-left: auto; font-weight: 500;
}
.chat-bubble-ai {
    background: var(--bg-card); border: 1px solid var(--border); color: var(--text-primary);
    padding: 10px 16px; border-radius: 18px 18px 18px 4px;
    margin-bottom: 10px; font-size: 0.88rem; max-width: 80%; line-height: 1.6;
}
.chat-name { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; font-weight: 600; }

/* INPUTS */
.stTextInput input, .stTextArea textarea {
    background: var(--bg-card) !important; border: 1px solid var(--border) !important;
    color: var(--text-primary) !important; border-radius: var(--radius-sm) !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: var(--text-muted) !important; opacity: 1 !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--accent-warm) !important; box-shadow: 0 0 0 2px var(--border-accent) !important; }
.stTextInput label, .stTextArea label, .stSelectbox label, .stSlider label, .stNumberInput label { color: var(--text-primary) !important; font-weight: 600 !important; font-size: 0.85rem !important; }

/* SELECTBOX */
[data-baseweb="select"] { background: var(--bg-card) !important; }
[data-baseweb="select"] > div { background: var(--bg-card) !important; border-color: var(--border) !important; border-radius: var(--radius-sm) !important; }
[data-baseweb="select"] input,
[data-baseweb="select"] [role="combobox"],
[data-baseweb="select"] [role="button"],
.stSelectbox select,
.stSelectbox option {
    color: var(--text-primary) !important;
    caret-color: var(--accent-warm) !important;
}
[data-baseweb="select"] * { color: var(--text-primary) !important; }
[data-baseweb="menu"] { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-sm) !important; box-shadow: var(--card-shadow) !important; }
[data-baseweb="option"] { background: var(--bg-card) !important; color: var(--text-primary) !important; font-size: 0.85rem !important; }
[data-baseweb="option"]:hover, [data-baseweb="option"][aria-selected="true"] { background: var(--bg-secondary) !important; color: var(--accent-warm) !important; }

/* SLIDER */
.stSlider [data-baseweb="slider"] [role="slider"] { background: var(--accent-warm) !important; }
.stSlider [data-baseweb="slider"] [data-baseweb="slider-fill"] { background: var(--accent-warm) !important; }

/* BUTTONS */
.stButton button, .stFormSubmitButton button {
    background: linear-gradient(135deg, var(--accent-warm), var(--accent-orange)) !important;
    color: #000 !important; font-weight: 600 !important; border: none !important;
    border-radius: var(--radius-sm) !important; padding: 10px 24px !important;
    font-size: 0.88rem !important; letter-spacing: 0.03em !important; transition: all 0.2s !important;
}
.stButton button:hover, .stFormSubmitButton button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }

[data-baseweb="tag"] { background-color: rgba(232,168,56,0.2) !important; border: 1px solid var(--accent-warm) !important; color: var(--accent-warm) !important; }

.stTabs [data-baseweb="tab-list"] { background: var(--bg-secondary) !important; border-radius: var(--radius) !important; gap: 4px; padding: 4px; border-bottom: none !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--text-muted) !important; border-radius: var(--radius-sm) !important; font-size: 0.82rem !important; font-weight: 500 !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, var(--accent-warm), var(--accent-orange)) !important; color: #000 !important; }

.stSpinner > div { border-top-color: var(--accent-warm) !important; }
[data-testid="stExpander"] { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; }
hr { border-color: var(--border) !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--scrollbar-track); }
::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--scrollbar-hover); }

/* TOP RECIPE HOME */
.top-recipe-home {
    background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 18px 20px; margin-bottom: 12px; transition: all 0.25s ease;
    position: relative; overflow: hidden; box-shadow: var(--card-shadow);
}
.top-recipe-home:hover { border-color: rgba(232,168,56,0.4); transform: translateY(-2px); box-shadow: 0 8px 28px rgba(232,168,56,0.1); }
.top-recipe-home .tr-rank {
    position: absolute; top: 0; left: 0;
    background: linear-gradient(135deg, var(--accent-warm), var(--accent-orange));
    color: var(--text-on-accent); font-size: 0.62rem; font-weight: 800;
    padding: 4px 12px; border-radius: 0 0 10px 0; letter-spacing: 0.05em;
}
.top-recipe-home .tr-emoji { font-size: 2.2rem; margin-bottom: 6px; display: block; margin-top: 8px; }
.top-recipe-home .tr-title { font-family: 'Playfair Display', serif; font-size: 0.95rem; font-weight: 700; color: var(--text-primary); line-height: 1.3; margin-bottom: 8px; }
.top-recipe-home .tr-loves { display: inline-flex; align-items: center; gap: 4px; font-size: 0.7rem; color: var(--accent-warm); font-weight: 600; }

/* CATEGORY CARD */
.cat-card {
    background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 24px 16px; text-align: center; transition: all 0.3s ease;
    cursor: pointer; box-shadow: var(--card-shadow);
}
.cat-card:hover { border-color: rgba(232,168,56,0.5); transform: translateY(-4px); box-shadow: 0 12px 36px rgba(232,168,56,0.1); }
.cat-card .cat-emoji { font-size: 2.8rem; margin-bottom: 10px; display: block; }
.cat-card .cat-name { font-size: 0.92rem; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.cat-card .cat-count { font-size: 0.72rem; color: var(--text-muted); }

/* THEME TOGGLE */
.theme-toggle-wrap { display: flex; align-items: center; gap: 10px; padding: 8px 12px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; margin-bottom: 16px; }

.substitution-warning { color: var(--accent-orange); font-size: 0.88rem; margin-bottom: 16px; }
.substitution-warning strong { color: var(--accent-orange); font-weight: 700; }

/* STREAMLIT ALERTS */
[data-testid="stAlert"] { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-sm) !important; color: var(--text-primary) !important; }
[data-testid="stSuccess"] { background: var(--alert-success-bg) !important; border-color: var(--alert-success-border) !important; color: var(--alert-success-text) !important; }
[data-testid="stInfo"] { background: var(--alert-info-bg) !important; border-color: var(--alert-info-border) !important; color: var(--alert-info-text) !important; }
[data-testid="stWarning"] { background: var(--alert-warning-bg) !important; border-color: var(--alert-warning-border) !important; color: var(--alert-warning-text) !important; }
[data-testid="stError"] { background: var(--alert-error-bg) !important; border-color: var(--alert-error-border) !important; color: var(--alert-error-text) !important; }
"""


def inject_css(is_light: bool):
    """Inject semua CSS ke halaman Streamlit."""
    theme_vars = get_theme_vars(is_light)
    st.markdown(
        f"<style>\n{theme_vars}\n{COMPONENT_CSS}\n</style>",
        unsafe_allow_html=True,
    )
