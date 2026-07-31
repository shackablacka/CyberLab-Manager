import urllib.error
import urllib.request

NAME = "Robots.txt Analyzer"
DESCRIPTION = "Fetch robots.txt and sitemap.xml for hidden paths."
ALLOWED_ROLES = ["admin", "instructor", "student"]


def run(username, role):
    url = input("Target base URL: ").strip()
    if not url:
        return
    if not url.startswith("http"):
        url = "http://" + url
    url = url.rstrip("/")

    for path in ("/robots.txt", "/sitemap.xml"):
        full = url + path
        print(f"\n--- {full} ---")
        try:
            req = urllib.request.Request(full, headers={"User-Agent": "CyberLab/1.0"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                body = resp.read().decode(errors="ignore")
                if path == "/robots.txt":
                    disallowed = [
                        l.split(":", 1)[1].strip()
                        for l in body.splitlines()
                        if l.lower().startswith("disallow:")
                        and l.split(":", 1)[1].strip()
                    ]
                    print(body[:800])
                    if disallowed:
                        print(f"\n[!] {len(disallowed)} disallowed path(s) worth probing:")
                        for d in disallowed:
                            print(f"    {url}{d}")
                else:
                    print(body[:800])
        except urllib.error.HTTPError as e:
            print(f"  ({e.code}) not present")
        except Exception as e:
            print(f"  Error: {e}")
