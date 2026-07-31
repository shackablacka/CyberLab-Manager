import base64
import urllib.error
import urllib.request
from pathlib import Path

NAME = "HTTP Basic Auth Auditor"
DESCRIPTION = "Test weak credentials on lab HTTP Basic Auth."
ALLOWED_ROLES = ["admin", "instructor"]

DEFAULT_CREDS = [
    ("admin", "admin"), ("admin", "password"), ("admin", "admin123"),
    ("admin", "1234"), ("test", "test"), ("user", "user"),
]


def run(username, role):
    print("[!] LAB USE ONLY — authorized targets only.")
    confirm = input("Type 'LAB' to confirm: ").strip()
    if confirm != "LAB":
        return

    url = input("Protected URL: ").strip()
    if not url.startswith("http"):
        url = "http://" + url

    cred_file = input("Credential file user:pass (blank = built-in): ").strip()
    if cred_file and Path(cred_file).is_file():
        creds = [
            tuple(line.strip().split(":", 1))
            for line in Path(cred_file).read_text().splitlines()
            if ":" in line
        ]
    else:
        creds = DEFAULT_CREDS

    for user, pw in creds:
        token = base64.b64encode(f"{user}:{pw}".encode()).decode()
        req = urllib.request.Request(url, headers={
            "User-Agent": "CyberLab/1.0",
            "Authorization": f"Basic {token}",
        })
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                if resp.status == 200:
                    print(f"[!] VALID CREDENTIALS: {user}:{pw}")
                    return
        except urllib.error.HTTPError as e:
            if e.code != 401:
                print(f"  [~] {user}:{pw} -> HTTP {e.code}")
        except Exception as e:
            print(f"[!] Request failed: {e}")
            return

    print("[+] No weak credentials succeeded.")
