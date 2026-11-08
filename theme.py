# theme.py - the "glassy clay" look shared by every page
import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@500;700;800&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Nunito', sans-serif; }
    .stApp { background: linear-gradient(135deg, #F3ECFF 0%, #FBE9F5 55%, #E8F0FF 100%); }
    h1, h2, h3 { font-weight: 800; color: #2B2350; }

    /* Sidebar: purple gradient panel with white rounded links */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #8F72FF, #6A4FE0); border-radius: 0 28px 28px 0; }
    [data-testid="stSidebarNav"]::before {
        content: "CM"; display: grid; place-items: center; width: 74px; height: 74px; margin: 18px auto 8px;
        border-radius: 50%; background: linear-gradient(135deg, #B9A5FF, #7C5CFC); color: #fff;
        font-weight: 800; font-size: 26px; border: 3px solid rgba(255,255,255,.7);
        box-shadow: 0 8px 18px rgba(60,30,160,.35); animation: bob 3s ease-in-out infinite;
    }
    [data-testid="stSidebarNav"] a { border-radius: 14px; margin: 3px 8px; transition: transform .2s; }
    [data-testid="stSidebarNav"] a span { color: #fff !important; font-weight: 700; }
    [data-testid="stSidebarNav"] a:hover { transform: translateX(6px) rotate(-1deg); background: rgba(255,255,255,.18); }
    [data-testid="stSidebarNav"] a[aria-current="page"] { background: #fff; }
    [data-testid="stSidebarNav"] a[aria-current="page"] span { color: #5B3FD0 !important; }

    /* Glass + clay cards */
    [data-testid="stMetric"], .cm-card {
        background: rgba(255,255,255,.65); backdrop-filter: blur(10px);
        border: 1.5px solid rgba(255,255,255,.9); border-radius: 24px; padding: 16px 20px;
        box-shadow: 0 12px 28px rgba(124,92,252,.16), inset 0 2px 6px rgba(255,255,255,.9);
    }
    .cm-card { height: 100%; transition: transform .2s; }
    .cm-card:hover { animation: giggle .6s ease-in-out; }
    .cm-card .ico { width: 54px; height: 54px; border-radius: 18px; display: grid; place-items: center;
        font-size: 28px; background: rgba(255,255,255,.8); margin-bottom: 10px;
        box-shadow: 0 6px 14px rgba(0,0,0,.08), inset 0 2px 4px #fff; animation: bob 3.4s ease-in-out infinite; }
    .cm-card h3 { margin: 0 0 4px; font-size: 20px; }
    .cm-card p  { margin: 0; color: #4b4375; }

    /* Pill buttons */
    .stButton > button, [data-testid="stFormSubmitButton"] button {
        border-radius: 999px; border: none; color: #fff; font-weight: 800; padding: 8px 22px;
        background: linear-gradient(135deg, #9B7FFF, #6A4FE0); box-shadow: 0 8px 18px rgba(106,79,224,.35);
        transition: transform .15s;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover { transform: scale(1.06) rotate(-1deg); color: #fff; }

    @keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
    @keyframes giggle {
        0%,100% { transform: rotate(0) scale(1.03); } 20% { transform: rotate(-2.5deg) scale(1.05); }
        40% { transform: rotate(2.5deg) scale(1.05); } 60% { transform: rotate(-1.5deg) scale(1.04); }
        80% { transform: rotate(1.5deg) scale(1.04); }
    }
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
    </style>
    """, unsafe_allow_html=True)
