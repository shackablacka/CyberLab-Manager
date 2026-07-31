import urllib.error
import urllib.parse
import urllib.request

NAME = "SQLi Error Probe"
DESCRIPTION = "Detect error-based SQL injection in a lab parameter."
ALLOWED_ROLES = ["admin", "instructor"]

PAYLOADS = ["'", "\"", "' OR '1'='1", "1' AND '1'='2"]
SQL_ERRORS = [
    "sql syntax", "mysql_fetch", "ora-", "postgresql",
    "sqlite3.", "unclosed quotation", "odbc", "jdbc",
    "syntax error", "warning: mysql", "pg_query",
]


def run(username, role):
    print("[!] LAB USE ONLY — authorized targets only.")
    url = input("URL with parameter (e.g. http://lab/item.php?id=1): ").strip()
    if not url or "=" not in url:
        print("[!] URL must contain a query parameter.")
        return

    base, param_value = url.rsplit("=", 1)
    for payload in PAYLOADS:
        test = base + "=" + urllib.parse.quote(param_value + payload)
        try:
            req = urllib.request.Request(test, headers={"User-Agent": "CyberLab/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read().decode(errors="ignore").lower()
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="ignore").lower()
        except Exception as e:
            print(f"[!] Request failed: {e}")
            return

        for marker in SQL_ERRORS:
            if marker in body:
                print(f"[!] POSSIBLE SQLi — payload '{payload}' triggered: {marker}")
                print(f"    URL: {test}")
                return

    print("[+] No SQL error signatures detected (not conclusive).")
