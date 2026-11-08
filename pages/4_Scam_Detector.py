# pages/4_Scam_Detector.py - rule checks + LIVE link checks (real destination, certificate, domain age, VirusTotal)
import re
from urllib.parse import urlparse
import streamlit as st
from theme import apply_theme
from scam_rules import analyze, analyze_url, registered_domain
from link_check import follow, domain_age_days, virustotal

st.set_page_config(page_title="Scam Detector | Campus Mate", page_icon="🛡️", layout="wide")
apply_theme()
st.title("🛡️ Scam detector")
st.write("Paste a link, an email or an internship or scholarship offer.")

def vt_key():
    try:
        return st.secrets["VIRUSTOTAL_API_KEY"]
    except Exception:
        return st.sidebar.text_input("VirusTotal API key (for live checks)", type="password", key="vt_key")

text = st.text_area("Paste here", height=200,
                    placeholder="Congratulations! You are selected. Pay a registration fee at http://...")

if st.button("Check now") and text.strip():
    score, level, reasons = analyze(text)               # step 1: warning-sign rules on the text and links
    urls = re.findall(r"(?:https?://|www\.)[^\s<>\"']+", text)[:3]
    key, extra, threat = vt_key(), 0, False
    cards = []

    for u in urls:                                       # step 2: live checks on each link
        url = u if u.startswith("http") else "http://" + u
        lines = []
        with st.spinner(f"Checking {url} ..."):
            trace = follow(url)
            final = trace.get("final", url)
            host = (urlparse(final).hostname or "").lower()

            if trace.get("error"):
                lines.append(f"🌐 {trace['error']}")
                extra += 10
                reasons.append("The link could not be opened, which is common for dead or fake pages.")
            else:
                lines.append(f"🔗 Real destination: **{host}**" + (f" (after {len(trace['chain']) - 1} redirect(s))" if len(trace["chain"]) > 1 else ""))
                if registered_domain(host) != registered_domain(urlparse(url).hostname or ""):
                    extra += 10
                    reasons.append(f"The link hides where it goes. It really leads to {host}.")
                    reasons += [why for _, why in analyze_url(final)]   # check the real destination with the rules too
            if not trace["ssl_ok"]:
                lines.append("🔒 Certificate: **invalid**")
                extra += 25
                reasons.append("The website's security certificate is invalid.")
            elif url.startswith("https") or (final or "").startswith("https"):
                lines.append("🔒 Certificate: valid")

            age = domain_age_days(host) if host else None
            if age is None:
                lines.append("📅 Domain age: unknown")
            else:
                lines.append(f"📅 Domain age: **{age} days**")
                if age < 30:
                    extra += 25
                    reasons.append(f"The domain was created only {age} days ago. Scam sites are usually brand new.")
                elif age < 180:
                    extra += 10
                    reasons.append(f"The domain is less than 6 months old ({age} days).")

            if key:
                vt = virustotal(final if not trace.get("error") else url, key)
                if vt.get("error"):
                    lines.append(f"🧪 VirusTotal: {vt['error']}")
                elif vt.get("submitted"):
                    lines.append("🧪 VirusTotal: first time seen. It was sent for scanning, so check again in a minute.")
                else:
                    bad = vt["malicious"]
                    lines.append(f"🧪 VirusTotal: **{bad}** malicious and {vt['suspicious']} suspicious out of {vt['total']} security engines")
                    if bad:
                        threat = True
                        extra += min(80, 40 + 10 * bad)
                        reasons.append(f"{bad} security engines on VirusTotal flag this link as dangerous.")
                    elif vt["suspicious"]:
                        extra += 15
                        reasons.append("Some security engines on VirusTotal find this link suspicious.")
            else:
                lines.append("🧪 VirusTotal: add a key in the sidebar to turn this check on.")
        cards.append((url, lines))

    score = min(100, score + extra)
    if threat:
        score = max(score, 70)
    level = "Low risk" if score < 25 else "Medium risk" if score < 55 else "High risk"

    c1, c2 = st.columns(2)
    c1.metric("Risk score", f"{score} / 100")
    c2.metric("Verdict", "Known threat" if threat else level)
    st.progress(score / 100)
    if threat or score >= 55:
        st.error("Do not click, reply or pay. Show it to a teacher or your college placement cell.")
    elif score >= 25:
        st.warning("Be careful. Check the sender on the official website before doing anything.")
    else:
        st.success("No known threats and no strong warning signs found. That is not proof the link is safe.")

    for url, lines in cards:
        with st.container(border=True):
            st.write(f"**Live check: {url}**")
            for line in lines:
                st.write(line)
    if reasons:
        st.subheader("Why")
        for r in dict.fromkeys(reasons):
            st.write("• " + r)
st.caption("No tool can prove a link is 100% safe. This checks live signals and known-threat lists, and shows you the evidence.")
