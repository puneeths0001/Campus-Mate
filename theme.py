# theme.py - glassmorphism look: deep indigo background, blurred colour blobs, frosted-glass cards
import html as _html
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
    /* Every place you type or choose becomes frosted glass.
       Step 1: the outer box gets the glass recipe */
    [data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div, [data-testid="stAudioInput"],
    [data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"], [data-testid="stNumberInputContainer"] {
        background: linear-gradient(135deg, rgba(255,255,255,.16), rgba(255,255,255,.05)) !important;
        backdrop-filter: blur(18px) saturate(140%); -webkit-backdrop-filter: blur(18px) saturate(140%);
        border: 1px solid rgba(255,255,255,.28) !important; border-radius: 16px !important;
        box-shadow: 0 8px 24px rgba(5,5,40,.25), inset 0 1px 0 rgba(255,255,255,.3);
        transition: border-color .2s, box-shadow .2s; }
    /* Step 2: every layer inside (and the wrappers around) must be see-through, or the dark colour shows */
    [data-baseweb="base-input"], [data-baseweb="input"] > div, [data-baseweb="textarea"] > div,
    [data-baseweb="input"] input, [data-baseweb="textarea"] textarea, [data-testid="stNumberInput"] button,
    [data-testid="stAudioInput"] div, [data-testid="stAudioInput"] canvas {
        background: transparent !important; background-color: transparent !important; color: #fff !important; }
    /* if Streamlit nests one box inside another, only the outer one draws the glass */
    [data-testid="stTextInputRootElement"] [data-baseweb="input"], [data-testid="stTextAreaRootElement"] [data-baseweb="textarea"] {
        background: transparent !important; border: none !important; box-shadow: none !important; backdrop-filter: none !important; }
    [data-testid="stAudioInput"] span, [data-testid="stAudioInput"] code, [data-testid="stAudioInput"] p {
        background: transparent !important; color: rgba(255,255,255,.8) !important; }
    /* Embedded components (like the location button) paint a solid dark box unless told to match */
    iframe { color-scheme: light; background: transparent !important; }
    [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within, [data-baseweb="select"]:focus-within > div {
        border-color: rgba(255,255,255,.75) !important; box-shadow: 0 0 0 3px rgba(124,156,255,.30), 0 8px 24px rgba(5,5,40,.25); }
    input::placeholder, textarea::placeholder { color: rgba(255,255,255,.45) !important; }
    /* Date picker and dropdown boxes: clear every inner layer, then draw the glass on the outer box only */
    [data-testid="stDateInput"] *, [data-testid="stSelectbox"] *, [data-testid="stMultiSelect"] * {
        background: transparent !important; background-color: transparent !important; }
    [data-testid="stDateInput"] [data-baseweb="input"], [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background: linear-gradient(135deg, rgba(255,255,255,.16), rgba(255,255,255,.05)) !important;
        backdrop-filter: blur(18px) saturate(140%); -webkit-backdrop-filter: blur(18px) saturate(140%);
        border: 1px solid rgba(255,255,255,.28) !important; border-radius: 16px !important;
        box-shadow: 0 8px 24px rgba(5,5,40,.25), inset 0 1px 0 rgba(255,255,255,.3); }
    /* Opened dropdown lists: clear every layer, glass on the outer panel, soft highlight on hover */
    [data-baseweb="popover"] * { background: transparent !important; background-color: transparent !important; color: #fff !important; }
    [data-baseweb="popover"] li:hover, [data-baseweb="popover"] [aria-selected="true"] { background: rgba(255,255,255,.16) !important; border-radius: 10px; }
    /* The calendar and the opened dropdown lists */
    [data-baseweb="popover"] > div { background: rgba(40,33,100,.80) !important; backdrop-filter: blur(22px); -webkit-backdrop-filter: blur(22px);
        border: 1px solid rgba(255,255,255,.25); border-radius: 16px; }
    [data-baseweb="calendar"], [data-baseweb="calendar"] div, [data-baseweb="popover"] ul, [data-baseweb="popover"] li {
        background: transparent !important; color: #fff !important; }
    /* Hide the small "Press Enter to submit form" hint that sits on top of the typing area */
    [data-testid="InputInstructions"], [data-testid="stTextInput"] [class*="InputInstructions"] { display: none !important; }
    /* Boards (bordered containers) and message bars are glass too */
    [data-testid="stVerticalBlockBorderWrapper"] { background: linear-gradient(135deg, rgba(255,255,255,.12), rgba(255,255,255,.04));
        border: 1px solid rgba(255,255,255,.24) !important; border-radius: 24px; backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
        box-shadow: 0 14px 34px rgba(5,5,40,.28), inset 0 1px 0 rgba(255,255,255,.25); }
    [data-testid="stAlert"] { background: rgba(255,255,255,.08) !important; border: 1px solid rgba(255,255,255,.22); border-radius: 18px;
        backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); }
    [data-testid="stAlert"] > div { background: transparent !important; }
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
    /* Frosted-glass tables (drawn with real HTML, so the glass shows through) */
    .gt-wrap { overflow-x: auto; border-radius: 22px; border: 1px solid rgba(255,255,255,.26);
        background: linear-gradient(135deg, rgba(255,255,255,.14), rgba(255,255,255,.04));
        backdrop-filter: blur(18px) saturate(140%); -webkit-backdrop-filter: blur(18px) saturate(140%);
        box-shadow: 0 14px 34px rgba(5,5,40,.28), inset 0 1px 0 rgba(255,255,255,.3); }
    .gt { width: 100%; border-collapse: collapse; color: #fff; font-size: 15px; }
    .gt th { text-align: left; font-weight: 600; color: rgba(255,255,255,.75); padding: 13px 18px;
        background: rgba(255,255,255,.07); border-bottom: 1px solid rgba(255,255,255,.2); }
    .gt td { padding: 12px 18px; border-bottom: 1px solid rgba(255,255,255,.10); }
    .gt tr:last-child td { border-bottom: none; }
    .gt tbody tr:hover td { background: rgba(255,255,255,.08); }
    .gt .r { text-align: right; }
    /* Sidebar menu: frosted-glass pills that slide in, float gently, and giggle when you hover */
    [data-testid="stSidebarNav"] a, a[data-testid="stSidebarNavLink"] {
        background: linear-gradient(135deg, rgba(255,255,255,.16), rgba(255,255,255,.04)) !important;
        border: 1px solid rgba(255,255,255,.22) !important; border-radius: 16px !important; margin: 6px 12px; padding: 4px 6px;
        backdrop-filter: blur(14px) saturate(140%); -webkit-backdrop-filter: blur(14px) saturate(140%);
        box-shadow: 0 6px 16px rgba(5,5,40,.22), inset 0 1px 0 rgba(255,255,255,.28);
        animation: float 4.5s ease-in-out infinite; animation-delay: var(--f, 0s);
        transition: border-color .2s, background .2s; }
    [data-testid="stSidebarNav"] li { animation: slidein .5s ease-out both; animation-delay: var(--d, 0s); }
    [data-testid="stSidebarNav"] li:nth-child(1) { --d: 0.00s; --f: -0.0s; }
    [data-testid="stSidebarNav"] li:nth-child(2) { --d: 0.08s; --f: -0.7s; }
    [data-testid="stSidebarNav"] li:nth-child(3) { --d: 0.16s; --f: -1.4s; }
    [data-testid="stSidebarNav"] li:nth-child(4) { --d: 0.24s; --f: -2.1s; }
    [data-testid="stSidebarNav"] li:nth-child(5) { --d: 0.32s; --f: -2.8s; }
    [data-testid="stSidebarNav"] li:nth-child(6) { --d: 0.40s; --f: -3.5s; }
    [data-testid="stSidebarNav"] li:nth-child(7) { --d: 0.48s; --f: -4.2s; }
    [data-testid="stSidebarNav"] li:nth-child(8) { --d: 0.56s; --f: -4.9s; }
    [data-testid="stSidebarNav"] a:hover, a[data-testid="stSidebarNavLink"]:hover {
        animation: giggle .6s ease-in-out !important; border-color: rgba(255,255,255,.6) !important;
        background: linear-gradient(135deg, rgba(255,255,255,.30), rgba(255,255,255,.10)) !important; }
    [data-testid="stSidebarNav"] a[aria-current="page"], a[data-testid="stSidebarNavLink"][aria-current="page"] {
        background: linear-gradient(135deg, rgba(255,255,255,.38), rgba(255,255,255,.16)) !important; border-color: rgba(255,255,255,.65) !important; }
    @keyframes float { 0%, 100% { transform: translate(0, 0); } 50% { transform: translate(3px, -3px); } }
    @keyframes slidein { from { opacity: 0; transform: translateX(-28px); } to { opacity: 1; transform: translateX(0); } }
    @keyframes giggle {
        0%, 100% { transform: rotate(0) scale(1.03); } 20% { transform: rotate(-2.5deg) scale(1.05); }
        40% { transform: rotate(2.5deg) scale(1.05); } 60% { transform: rotate(-1.5deg) scale(1.04); }
        80% { transform: rotate(1.5deg) scale(1.04); } }
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
    </style>
    """, unsafe_allow_html=True)


def glass_table(df, right=()):
    """Draws a pandas table as a frosted-glass HTML table. 'right' lists the columns to right-align (numbers)."""
    head = "".join(f'<th class="{"r" if c in right else ""}">{_html.escape(str(c))}</th>' for c in df.columns)
    rows = "".join(
        "<tr>" + "".join(f'<td class="{"r" if c in right else ""}">{_html.escape(str(v))}</td>'
                         for c, v in zip(df.columns, row)) + "</tr>"
        for row in df.itertuples(index=False))
    st.markdown(f'<div class="gt-wrap"><table class="gt"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>',
                unsafe_allow_html=True)
