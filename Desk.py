# Desk.py - Home page ("Desk") of Campus Mate (run with: streamlit run Desk.py)
import streamlit as st
import streamlit.components.v1 as components
import html
import json
from pathlib import Path
import pandas as pd
from datetime import date, datetime
from theme import apply_theme
from when_parse import fmt

st.set_page_config(page_title="Desk | Campus Mate", page_icon="🎓", layout="wide")
apply_theme()

# Hero "window": drifting colour blobs with frosted-glass cards on top. The pass card tilts in 3D with your mouse.
HERO = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body { margin:0; font-family:'Inter',sans-serif; color:#fff; }
.win { position:relative; height:430px; margin:4px; border-radius:22px; overflow:hidden; background:#1B1648;
       border:1px solid rgba(255,255,255,.14); }
.blob { position:absolute; border-radius:50%; filter:blur(60px); animation:drift 12s ease-in-out infinite alternate; }
.b1 { width:340px; height:300px; background:#4F86FF; left:32%; top:-130px; }
.b2 { width:380px; height:340px; background:#FF4FC3; left:-90px; bottom:-150px; animation-delay:-4s; }
.b3 { width:300px; height:280px; background:#FF9B3D; right:-80px; bottom:-120px; animation-delay:-8s; }
@keyframes drift { to { transform:translate(34px,-22px) scale(1.1); } }
.glass { position:absolute; border-radius:26px; border:1px solid rgba(255,255,255,.28); box-sizing:border-box; padding:22px;
         background:linear-gradient(135deg, rgba(255,255,255,.24), rgba(255,255,255,.06));
         backdrop-filter:blur(22px) saturate(140%); -webkit-backdrop-filter:blur(22px) saturate(140%);
         box-shadow:0 20px 50px rgba(5,5,40,.35), inset 0 1px 0 rgba(255,255,255,.35); }
.tilt { transform:perspective(900px); transition:transform .15s ease-out; will-change:transform; }
.pass { left:5%; top:21%; width:40%; height:52%; }
.top { display:flex; justify-content:space-between; font-size:12px; letter-spacing:.14em; color:rgba(255,255,255,.7); }
.logo { font-size:20px; font-weight:700; letter-spacing:-.02em; color:#fff; }
.chip { width:46px; height:34px; border-radius:9px; margin:22px 0 14px; background:linear-gradient(135deg,#f6d88a,#b98a3a); }
.num { font-size:19px; letter-spacing:.22em; font-weight:500; }
.live { left:52%; top:8%; width:43%; height:44%; }
.lbl { font-size:13px; color:rgba(255,255,255,.72); }
.big { font-size:clamp(28px,4.4vw,46px); font-weight:700; letter-spacing:-.03em; margin-top:4px; }
svg { position:absolute; left:22px; right:22px; bottom:16px; width:calc(100% - 44px); height:42%; }
.wave { fill:none; stroke:#fff; stroke-width:3; stroke-linecap:round; stroke-dasharray:700; stroke-dashoffset:700;
        animation:draw 2.4s ease forwards; filter:drop-shadow(0 0 6px rgba(255,255,255,.7)); }
@keyframes draw { to { stroke-dashoffset:0; } }
.list { left:52%; top:58%; width:43%; height:36%; padding:16px 22px; }
.row { display:flex; justify-content:space-between; padding:6px 0; font-size:14px; border-bottom:1px solid rgba(255,255,255,.16); }
.row:last-child { border-bottom:none; }
@media (max-width:700px) {
  .pass { display:none; }
  .live, .list { left:5%; width:90%; }
  .live { top:5%; height:44%; } .list { top:54%; height:41%; }
}
@media (prefers-reduced-motion: reduce) { .blob, .wave { animation:none; stroke-dashoffset:0; } }
</style>
<div class="win" id="win">
  <div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div>
  <div class="glass tilt pass">
    <div class="top"><span class="logo">campus mate</span><span>STUDENT PASS</span></div>
    <div class="chip"></div>
    <div class="num">SAFE · SMART · SAVING</div>
  </div>
  <div class="glass tilt live">
    <div class="lbl">__SPENT_LABEL__</div>
    <div class="big">__SPENT__</div>
    <svg viewBox="0 0 400 100" preserveAspectRatio="none"><path class="wave"
      d="M0 72 C 40 22, 80 22, 120 56 S 200 92, 240 56 S 310 10, 350 34 S 385 40, 400 12"/></svg>
  </div>
  <div class="glass tilt list">
    <div class="lbl" style="margin-bottom:4px">__NOTES_LABEL__</div>
    __ROWS__
  </div>
</div>
<script>
document.querySelectorAll('.tilt').forEach(card => {     // every glass card tilts toward the mouse
  card.addEventListener('mousemove', e => {
    const r = card.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
    card.style.transform = `perspective(900px) rotateY(${x * 16}deg) rotateX(${-y * 16}deg) scale(1.02)`;
  });
  card.addEventListener('mouseleave', () => card.style.transform = 'perspective(900px)');
});
</script>
"""
# Real numbers if the student already used the Expenses or Reminders page in this visit, otherwise sample values
df = st.session_state.get("expenses")
if df is not None and not df.empty:
    month = df[pd.to_datetime(df["Date"]).dt.month == date.today().month]
    spent, spent_label = f"₹{month['Amount'].sum():,.0f}", "Spent this month"
else:
    spent, spent_label = "₹3,450", "Expenses this month (sample)"

notes = [r for r in st.session_state.get("reminders", []) if r.get("Type") != "exam"]
items = sorted(notes, key=lambda r: (r["Due"] is None, r["Due"] or datetime.max))[:4]
if items:
    rows = [(r["Task"], fmt(r["Due"], r.get("HasTime", True)) if r["Due"] else "Note") for r in items]
    notes_label = "Assignments & notes"
else:
    rows = [("Maths assignment", "Fri, 5 pm"), ("Physics lab record", "Mon"),
            ("DBMS exam", "Next week"), ("Library book return", "Sat")]
    notes_label = "Assignments & notes (sample)"
rows_html = "".join(f'<div class="row"><span>{html.escape(a)}</span><span>{html.escape(b)}</span></div>' for a, b in rows)

page = (HERO.replace("__SPENT_LABEL__", spent_label).replace("__SPENT__", spent)
            .replace("__NOTES_LABEL__", notes_label).replace("__ROWS__", rows_html))
components.html(page, height=450)

st.subheader("What Campus Mate does")
st.markdown("""
<style>
.g-card { position:relative; overflow:hidden; border-radius:26px; padding:24px; min-height:170px;
          background:linear-gradient(135deg, rgba(255,255,255,.18), rgba(255,255,255,.05));
          border:1px solid rgba(255,255,255,.26); backdrop-filter:blur(22px) saturate(140%);
          box-shadow:0 18px 40px rgba(5,5,40,.30), inset 0 1px 0 rgba(255,255,255,.3);
          transition:transform .2s ease, border-color .2s ease; margin-bottom:6px; }
.g-card::before { content:""; position:absolute; width:150px; height:150px; right:-50px; top:-50px; border-radius:50%;
          background:var(--c); filter:blur(38px); opacity:.55; }
.g-ico { position:relative; width:48px; height:48px; border-radius:16px; display:grid; place-items:center; font-size:24px;
         background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.3); margin-bottom:14px; }
.g-t { position:relative; color:#fff; font-size:19px; font-weight:700; letter-spacing:-.02em; }
.g-p { position:relative; color:rgba(255,255,255,.75); font-size:14px; line-height:1.5; margin-top:6px; }

/* The "Open" pill sits inside the bottom of each card. Clicking the card itself also works (small script below). */
.g-card { cursor:pointer; padding-bottom:58px; }
[data-testid="stColumn"]:hover .g-card, [data-testid="column"]:hover .g-card { transform:translateY(-4px); border-color:rgba(255,255,255,.55); }
[data-testid="stElementContainer"]:has([data-testid="stPageLink"]), .element-container:has([data-testid="stPageLink"]) {
    margin-top:-54px; margin-left:24px; position:relative; z-index:3; width:fit-content; transition:transform .2s ease; }
[data-testid="stColumn"]:hover [data-testid="stPageLink"], [data-testid="column"]:hover [data-testid="stPageLink"] { transform:translateY(-4px); }
[data-testid="stPageLink"] a { width:fit-content; background:rgba(255,255,255,.16) !important; border:1px solid rgba(255,255,255,.32);
    border-radius:999px; padding:3px 16px; color:#fff !important; }
[data-testid="stPageLink"] a:hover { background:rgba(255,255,255,.30) !important; }
</style>
""", unsafe_allow_html=True)

# Find each page file by its number, so the cards still work if a file is renamed (for example 2_Reminder.py)
PAGES = {p.name.split("_")[0]: f"pages/{p.name}" for p in sorted((Path(__file__).parent / "pages").glob("*.py"))}

CARDS = [   # (page number, icon, title, text, glow colour)
    ("1", "🚨", "Safety SOS", "Say “help” and your parents get your live location.", "#FF4FC3"),
    ("2", "⏰", "Reminders", "Announcements, assignments and exams, typed or spoken.", "#FF9B3D"),
    ("3", "💸", "Expense tracker", "See where your money goes and when you cross your limit.", "#4F86FF"),
    ("4", "🛡️", "Scam detector", "Paste a link, email or offer and get a live risk check.", "#4F86FF"),
    ("5", "📊", "CGPA planner", "Enter your marks and see which subjects pull your SGPA down.", "#FF9B3D"),
    ("6", "🧠", "AI Study Buddy", "Ask doubts, solve problems, and make notes and flowcharts in a chat.", "#FF4FC3"),
]
NAV = {"1": "safety", "2": "remind", "3": "expense", "4": "scam", "5": "cgpa", "6": "study"}   # a word from each menu label
for row in (CARDS[:3], CARDS[3:]):
    cols = st.columns(3)
    for col, (num, icon, title, text, color) in zip(cols, row):
        with col:
            st.markdown(f'<div class="g-card" data-nav="{NAV[num]}" style="--c:{color}"><div class="g-ico">{icon}</div>'
                        f'<div class="g-t">{title}</div><div class="g-p">{text}</div></div>', unsafe_allow_html=True)
            if num in PAGES:
                st.page_link(PAGES[num], label="Open →")   # a button that always works

# Clicking anywhere on a card presses the matching menu link on the left (so the page changes without reloading).
# The script is placed in the browser's own page, so it keeps working after you switch pages.
_CARD_JS = """(function () {
  if (window.__cmCards) return; window.__cmCards = true;
  document.addEventListener('click', function (e) {
    var card = e.target.closest && e.target.closest('.g-card[data-nav]');
    if (!card) return;
    var want = card.getAttribute('data-nav');
    var links = document.querySelectorAll('[data-testid="stSidebarNav"] a, a[data-testid="stSidebarNavLink"]');
    for (var i = 0; i < links.length; i++) {
      if (links[i].textContent.toLowerCase().indexOf(want) > -1) { links[i].click(); break; }
    }
  });
})();"""
components.html("<script>const d = window.parent.document; if (!d.getElementById('cm-cards')) { const s = d.createElement('script'); "
                "s.id = 'cm-cards'; s.textContent = " + json.dumps(_CARD_JS) + "; d.head.appendChild(s); }</script>", height=0)
st.caption("Click a card, or use the menu on the left.")
