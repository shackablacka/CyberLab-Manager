import ssl
import urllib.error
import urllib.request

NAME = "HTTP Method Tester"
DESCRIPTION = "Check which HTTP methods a lab server permits."
ALLOWED_ROLES = ["admin", "instructor"]

METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"]
DANGEROUS = {"PUT", "DELETE", "TRACE"}


def run(username, role):
    url = input("Target URL: ").strip()
    if not url:
        return
    if not url.startswith("http"):
        url = "http://" + url

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print(f"[*] Testing methods against {url}...")
    for method in METHODS:
        try:
            req = urllib.request.Request(
                url, method=method, headers={"User-Agent": "CyberLab/1.0"}
            )
            with urllib.request.urlopen(req, timeout=4, context=ctx) as resp:
                code = resp.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception:
            code = "ERR"

        flag = "  <-- potentially dangerous" if (
            method in DANGEROUS and code not in (405, 501, "ERR")
        ) else ""
        print(f"  {method:<8} -> {code}{flag}")
