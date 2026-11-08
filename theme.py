# theme.py - dark, modern look shared by every page (Inter font, #17171D tiles, violet + mint accents)
import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
    .stApp { background: #0B0B0F; }
    h1, h2, h3 { color: #fff; font-weight: 700; letter-spacing: -0.02em; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #0F0F14; border-right: 1px solid rgba(255,255,255,.08); }
    [data-testid="stSidebarNav"]::before {
        content: "CM"; display: grid; place-items: center; width: 44px; height: 44px; margin: 18px 16px 8px;
        border-radius: 14px; background: linear-gradient(135deg, #7C5CFF, #3DDC97); color: #0B0B0F; font-weight: 700;
    }
    [data-testid="stSidebarNav"] a { border-radius: 12px; margin: 2px 8px; transition: background .2s; }
    [data-testid="stSidebarNav"] a span { color: #9A9AA5 !important; font-weight: 500; }
    [data-testid="stSidebarNav"] a:hover { background: rgba(255,255,255,.05); }
    [data-testid="stSidebarNav"] a[aria-current="page"] { background: rgba(124,92,255,.18); }
    [data-testid="stSidebarNav"] a[aria-current="page"] span { color: #fff !important; }

    /* Tiles: metrics use the same style as the bento tiles */
    [data-testid="stMetric"] {
        background: #17171D; border: 1px solid rgba(255,255,255,.08); border-radius: 24px; padding: 18px 22px;
        transition: transform .2s, border-color .2s;
    }
    [data-testid="stMetric"]:hover { transform: translateY(-4px); border-color: rgba(255,255,255,.22); }

    /* Buttons */
    .stButton > button, [data-testid="stFormSubmitButton"] button {
        border-radius: 12px; border: 1px solid rgba(255,255,255,.12); color: #fff; font-weight: 600;
        background: #7C5CFF; padding: 8px 20px; transition: transform .2s, box-shadow .2s;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-2px); box-shadow: 0 8px 24px rgba(124,92,255,.45); color: #fff; border-color: rgba(255,255,255,.3);
    }
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
    </style>
    """, unsafe_allow_html=True)
