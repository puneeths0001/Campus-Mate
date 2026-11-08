# scam_rules.py - rule-based scam checker. Each rule adds risk points and a reason.
import re
from urllib.parse import urlparse

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly", "rb.gy", "shorturl.at"}
RISKY_TLDS = {"xyz", "top", "click", "tk", "ml", "ga", "cf", "gq", "work", "zip", "icu", "buzz", "rest"}
BRANDS = {"paytm": ["paytm.com"], "phonepe": ["phonepe.com"], "sbi": ["sbi.co.in", "onlinesbi.sbi"],
          "hdfc": ["hdfcbank.com"], "icici": ["icicibank.com"], "google": ["google.com"],
          "amazon": ["amazon.in", "amazon.com"], "linkedin": ["linkedin.com"],
          "microsoft": ["microsoft.com"], "instagram": ["instagram.com"], "whatsapp": ["whatsapp.com"]}

TEXT_RULES = [  # (pattern, points, reason)
    (r"(registration|processing|security|training|kit|admission|joining|application)\s*(fee|fees|deposit|charges?)", 30,
     "Asks you to pay a fee. Real internships and scholarships do not charge you."),
    (r"\brefundable\b", 10, "Mentions a 'refundable' payment, a common scam hook."),
    (r"no interview|without interview|direct selection|guaranteed (job|placement|selection|internship)", 20,
     "Promises selection without an interview."),
    (r"urgent|immediately|last chance|limited seats|act now|within 24 hours|expires today", 10,
     "Uses pressure and urgency words."),
    (r"\botp\b|password|\bcvv\b|aadhaar|pan card|bank details|card number|\bupi pin\b", 25,
     "Asks for sensitive details (OTP, password, bank or ID details)."),
    (r"congratulations.*(selected|won)|lottery|prize|winner", 15, "Looks like a 'you won / you are selected' lure."),
    (r"verify your account|account (is )?(suspended|blocked)|\bkyc\b", 20, "Threatens account blocking to make you click."),
    (r"work from home.*earn|earn\s*(rs\.?|₹)?\s*\d+.*(per|a) (day|hour|week)", 15, "Promises easy high earnings."),
    (r"whatsapp|telegram", 8, "Pushes you to chat on WhatsApp or Telegram."),
]
FREE_MAIL = ("gmail.com", "yahoo.com", "outlook.com", "hotmail.com")

def registered_domain(host):
    p = host.split(".")
    if len(p) >= 3 and len(p[-1]) == 2 and p[-2] in {"co", "com", "org", "gov", "ac", "edu", "nic"}:
        return ".".join(p[-3:])
    return ".".join(p[-2:])

def analyze_url(url):
    out = []
    u = urlparse(url if "://" in url else "http://" + url)
    host = (u.hostname or "").lower()
    reg = registered_domain(host)
    if u.scheme == "http": out.append((10, f"{host}: not using secure HTTPS."))
    if re.fullmatch(r"[\d.]+", host): out.append((30, f"{host}: uses a raw IP address instead of a name."))
    if "@" in u.netloc: out.append((25, f"{host}: has an '@' in the link, which hides the real site."))
    if "xn--" in host: out.append((25, f"{host}: uses look-alike (punycode) characters."))
    if host.count("-") >= 3: out.append((10, f"{host}: has many hyphens."))
    if len(host.split(".")) >= 5: out.append((10, f"{host}: has too many sub-domains."))
    if reg in SHORTENERS: out.append((15, f"{reg}: a short link hides the real destination."))
    if host.rsplit(".", 1)[-1] in RISKY_TLDS: out.append((15, f"{host}: ends with a TLD often used in scams."))
    if re.search(r"\.(exe|apk|scr|zip)$", u.path.lower()): out.append((20, "The link downloads a program file."))
    for brand, official in BRANDS.items():
        if brand in re.split(r"[^a-z0-9]+", host) and reg not in official:
            out.append((35, f"{host}: pretends to be {brand} but is not its real site."))
    if len(url) > 100: out.append((5, "The link is unusually long."))
    return out

def analyze(text):
    """Returns (score 0-100, level, list of reasons)."""
    reasons = []
    for url in re.findall(r"(?:https?://|www\.)[^\s<>\"']+", text):
        reasons += analyze_url(url)
    low = text.lower()
    for pattern, pts, why in TEXT_RULES:
        if re.search(pattern, low): reasons.append((pts, why))
    for mail in re.findall(r"[\w.+-]+@([\w.-]+\.\w+)", low):
        if mail in FREE_MAIL and re.search(r"intern|hiring|recruit|\bhr\b|scholarship|offer", low):
            reasons.append((12, f"A hiring or scholarship message from a free email ({mail}), not a company domain."))
    score = min(100, sum(p for p, _ in reasons))
    level = "Low risk" if score < 25 else "Medium risk" if score < 55 else "High risk"
    return score, level, [r for _, r in reasons]
