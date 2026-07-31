import urllib.error
import urllib.parse
import urllib.request

NAME = "Reflected XSS Probe"
DESCRIPTION = "Check if input reflects unescaped in a lab page."
ALLOWED_ROLES = ["admin", "instructor"]

MARKER = "clm7x9probe"
PAYLOADS = [
    MARKER,
    f"<{MARKER}>",
    f"\"><{MARKER}>",
    f"<script>/*{MARKER}*/</script>",
]


def run(username, role):
    print("[!] LAB USE ONLY — authorized targets only.")
    url = input("URL with parameter (e.g. http://lab/search.php?q=test): ").strip()
    if not url or "=" not in url:
        print("[!] URL must contain a query parameter.")
        return

    base, _ = url.rsplit("=", 1)
    for payload in PAYLOADS:
        test = base + "=" + urllib.parse.quote(payload)
        try:
            req = urllib.request.Request(test, headers={"User-Agent": "CyberLab/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read().decode(errors="ignore")
        except Exception as e:
            print(f"[!] Request failed: {e}")
            return

        if payload in body:
            print(f"[!] REFLECTED UNESCAPED: {payload}")
            if "<" in payload:
                print("[!] POSSIBLE XSS — HTML/JS context not escaped.")
                print(f"    URL: {test}")
                return
        elif MARKER in body:
            print(f"  [~] Marker reflected but encoded: {payload}")

    print("[+] No unescaped reflection detected (not conclusive).")
