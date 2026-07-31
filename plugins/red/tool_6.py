import urllib.request
import urllib.error
from pathlib import Path

NAME = "Directory Brute-Forcer"
DESCRIPTION = "Probe a lab web server for common hidden paths."
ALLOWED_ROLES = ["admin", "instructor"]

REPORT_DIR = Path("tools/red/reports")
DEFAULT_WORDS = ["admin", "login", "uploads", "backup", "config", "db",
                 "test", "api", "private", "secret", ".git", "phpinfo.php"]


def run(username, role):
    url = input("Target base URL (lab only): ").strip()
    if not url:
        return
    if not url.startswith("http"):
        url = "http://" + url

    wordlist = input("Wordlist path (blank = built-in): ").strip()
    if wordlist and Path(wordlist).is_file():
        words = Path(wordlist).read_text(encoding="utf-8").split()
    else:
        words = DEFAULT_WORDS

    found = []
    print(f"[*] Probing {len(words)} paths on {url}...")
    for word in words:
        test = f"{url.rstrip('/')}/{word.lstrip('/')}"
        try:
            req = urllib.request.Request(test, headers={"User-Agent": "CyberLab/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                line = f"  [+] {test} -> {resp.status}"
                print(line)
                found.append(line)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                line = f"  [!] {test} -> {e.code}"
                print(line)
                found.append(line)
        except urllib.error.URLError:
            print("[!] Host unreachable.")
            return

    if found:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        out = REPORT_DIR / "dirbrute.txt"
        out.write_text("\n".join(found), encoding="utf-8")
        print(f"[+] Report saved: {out}")
    else:
        print("[-] Nothing found.")
