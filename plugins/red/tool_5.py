import ssl
import urllib.request

NAME = "HTTP Header Auditor"
DESCRIPTION = "Inspect web response headers for missing security controls."
ALLOWED_ROLES = ["admin", "instructor"]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]


def run(username, role):
    url = input("Target URL: ").strip()
    if not url:
        return
    if not url.startswith("http"):
        url = "http://" + url

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CyberLab/1.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            headers = resp.info()
            print("\n--- Response Headers ---")
            for k, v in headers.items():
                print(f"  {k}: {v}")
            print("\n--- Security Analysis ---")
            for sec in SECURITY_HEADERS:
                mark = "[+]" if sec in headers else "[-]"
                state = "PRESENT" if sec in headers else "MISSING"
                print(f"  {mark} {sec:<30} {state}")
    except Exception as e:
        print(f"[!] Request failed: {e}")
