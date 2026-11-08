# link_check.py - LIVE checks on a link: where it really goes, certificate, domain age, VirusTotal
import base64, ipaddress, socket
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
import requests
import urllib3
from scam_rules import registered_domain

urllib3.disable_warnings()   # we sometimes connect to broken-certificate sites on purpose, only to read the headers
HEADERS = {"User-Agent": "Mozilla/5.0 (Campus Mate link checker)"}

def is_public(url):
    """Safety guard: never let our server open private or internal addresses."""
    host = urlparse(url).hostname
    if not host:
        return False
    try:
        for info in socket.getaddrinfo(host, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return False
    except Exception:
        return False
    return True

def follow(url, max_hops=6):
    """Follows redirects by hand (so every step is checked) and reports the real destination.
    Only headers are read; the page itself is never downloaded."""
    chain, cur, ssl_ok = [url], url, True
    for _ in range(max_hops):
        if not is_public(cur):
            return {"chain": chain, "ssl_ok": ssl_ok,
                    "error": "Could not reach this address. The site may not exist, or it is not a public website."}
        try:
            r = requests.get(cur, headers=HEADERS, timeout=8, allow_redirects=False, stream=True)
        except requests.exceptions.SSLError:
            ssl_ok = False                                   # certificate is invalid or fake
            try:
                r = requests.get(cur, headers=HEADERS, timeout=8, allow_redirects=False, stream=True, verify=False)
            except requests.RequestException as e:
                return {"chain": chain, "ssl_ok": False, "error": f"Could not open the link ({type(e).__name__})"}
        except requests.RequestException as e:
            return {"chain": chain, "ssl_ok": ssl_ok, "error": f"Could not open the link ({type(e).__name__})"}
        status, loc = r.status_code, r.headers.get("Location")
        r.close()
        if status in (301, 302, 303, 307, 308) and loc:
            cur = urljoin(cur, loc)
            chain.append(cur)
            continue
        return {"chain": chain, "final": cur, "status": status, "ssl_ok": ssl_ok}
    return {"chain": chain, "final": cur, "ssl_ok": ssl_ok, "error": "Too many redirects"}

def domain_age_days(host):
    """How old the domain is, from the public RDAP registry. None if it cannot be found."""
    try:
        r = requests.get(f"https://rdap.org/domain/{registered_domain(host)}", headers=HEADERS, timeout=8)
        if r.status_code != 200:
            return None
        for ev in r.json().get("events", []):
            if ev.get("eventAction") == "registration":
                made = datetime.fromisoformat(ev["eventDate"].replace("Z", "+00:00"))
                return (datetime.now(timezone.utc) - made).days
    except Exception:
        pass
    return None

def virustotal(url, key):
    """Asks VirusTotal how many security engines flag this link."""
    uid = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
    head = {"x-apikey": key}
    try:
        r = requests.get(f"https://www.virustotal.com/api/v3/urls/{uid}", headers=head, timeout=15)
        if r.status_code == 404:        # never scanned before: send it for scanning
            requests.post("https://www.virustotal.com/api/v3/urls", headers=head, data={"url": url}, timeout=15)
            return {"submitted": True}
        if r.status_code == 401:
            return {"error": "VirusTotal did not accept the key."}
        if r.status_code == 429:
            return {"error": "VirusTotal limit reached (free plan: 4 checks a minute). Wait a minute and try again."}
        if r.status_code != 200:
            return {"error": f"VirusTotal error {r.status_code}"}
        stats = r.json()["data"]["attributes"]["last_analysis_stats"]
        return {"malicious": stats.get("malicious", 0), "suspicious": stats.get("suspicious", 0), "total": sum(stats.values())}
    except Exception as e:
        return {"error": f"Could not reach VirusTotal ({type(e).__name__})"}
