# theme.py - glassmorphism look: deep indigo background, blurred colour blobs, frosted-glass cards
import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
    /* Big soft blobs (blue, pink, orange) on a deep indigo base */
    .stApp {
        background:
          radial-gradient(42% 36% at 28% 2%,  rgba(79,134,255,.60), transparent 70%),
          radial-gradient(46% 42% at 0% 100%, rgba(255,79,195,.55), transparent 70%),
          radial-gradient(36% 38% at 100% 92%, rgba(255,155,61,.50), transparent 70%),
          #17133F;
        background-attachment: fixed;
    }
    header[data-testid="stHeader"] { background: transparent; }
    h1, h2, h3 { color: #fff; font-weight: 700; letter-spacing: -0.02em; }

    /* The glass recipe: translucent white + blur + thin bright border + soft shadow */
    .glass, [data-testid="stMetric"], [data-testid="stSidebar"] {
        background: linear-gradient(135deg, rgba(255,255,255,.18), rgba(255,255,255,.05)) !important;
        backdrop-filter: blur(22px) saturate(140%); -webkit-backdrop-filter: blur(22px) saturate(140%);
        border: 1px solid rgba(255,255,255,.26);
    }
    [data-testid="stMetric"] { border-radius: 26px; padding: 18px 22px; box-shadow: 0 18px 40px rgba(5,5,40,.30), inset 0 1px 0 rgba(255,255,255,.3);
        transition: transform .2s, border-color .2s; }
    [data-testid="stMetric"]:hover { transform: translateY(-4px); border-color: rgba(255,255,255,.5); }
    [data-testid="stSidebar"] { border-width: 0 1px 0 0; }

    [data-testid="stSidebarNav"] a { border-radius: 14px; margin: 2px 8px; transition: background .2s; }
    [data-testid="stSidebarNav"] a span { color: rgba(255,255,255,.75) !important; font-weight: 500; }
    [data-testid="stSidebarNav"] a:hover { background: rgba(255,255,255,.10); }
    [data-testid="stSidebarNav"] a[aria-current="page"] { background: rgba(255,255,255,.20); }
    [data-testid="stSidebarNav"] a[aria-current="page"] span { color: #fff !important; }

    /* Inputs and buttons also look like glass */
    /* Every place you type or choose becomes frosted glass */
    [data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div, [data-testid="stAudioInput"] {
        background: linear-gradient(135deg, rgba(255,255,255,.16), rgba(255,255,255,.05)) !important;
        backdrop-filter: blur(18px) saturate(140%); -webkit-backdrop-filter: blur(18px) saturate(140%);
        border: 1px solid rgba(255,255,255,.28) !important; border-radius: 16px !important;
        box-shadow: 0 8px 24px rgba(5,5,40,.25), inset 0 1px 0 rgba(255,255,255,.3);
        transition: border-color .2s, box-shadow .2s; }
    [data-baseweb="base-input"], [data-baseweb="input"] input, [data-baseweb="textarea"] textarea,
    [data-testid="stNumberInput"] button { background: transparent !important; color: #fff !important; }
    [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within, [data-baseweb="select"]:focus-within > div {
        border-color: rgba(255,255,255,.75) !important; box-shadow: 0 0 0 3px rgba(124,156,255,.30), 0 8px 24px rgba(5,5,40,.25); }
    input::placeholder, textarea::placeholder { color: rgba(255,255,255,.45) !important; }
    /* Dropdown lists, forms, expanders and tables */
    [data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] [role="listbox"] {
        background: rgba(40,33,100,.78) !important; backdrop-filter: blur(22px); -webkit-backdrop-filter: blur(22px);
        border: 1px solid rgba(255,255,255,.25); border-radius: 16px; }
    [data-testid="stForm"], [data-testid="stExpander"] {
        background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.22) !important; border-radius: 22px;
        backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); }
    [data-testid="stDataFrame"] { border: 1px solid rgba(255,255,255,.22); border-radius: 18px; overflow: hidden; }
    .stButton > button, [data-testid="stFormSubmitButton"] button {
        border-radius: 999px; color: #fff; font-weight: 600; padding: 8px 22px;
        background: linear-gradient(135deg, rgba(255,255,255,.30), rgba(255,255,255,.10));
        border: 1px solid rgba(255,255,255,.38); backdrop-filter: blur(12px);
        transition: transform .2s, box-shadow .2s; }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-2px); color: #fff; border-color: rgba(255,255,255,.7); box-shadow: 0 10px 28px rgba(124,156,255,.45); }
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
    </style>
    """, unsafe_allow_html=True)
