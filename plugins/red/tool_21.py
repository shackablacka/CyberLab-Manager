import re

NAME = "Hash Identifier"
DESCRIPTION = "Identify likely hash algorithm from a hash string."
ALLOWED_ROLES = ["admin", "instructor", "student"]

PATTERNS = [
    (r"^\$2[aby]\$\d{2}\$.{53}$", "bcrypt"),
    (r"^\$6\$.+", "SHA-512 crypt (Linux shadow)"),
    (r"^\$5\$.+", "SHA-256 crypt (Linux shadow)"),
    (r"^\$1\$.+", "MD5 crypt"),
    (r"^[a-f0-9]{32}$", "MD5 or NTLM"),
    (r"^[a-f0-9]{40}$", "SHA-1"),
    (r"^[a-f0-9]{64}$", "SHA-256"),
    (r"^[a-f0-9]{128}$", "SHA-512"),
    (r"^[A-F0-9]{32}$", "NTLM (uppercase)"),
]


def run(username, role):
    h = input("Paste the hash: ").strip()
    if not h:
        return

    matches = [name for pattern, name in PATTERNS if re.match(pattern, h)]
    if matches:
        print("\nPossible hash type(s):")
        for m in matches:
            print(f"  [+] {m}")
    else:
        print(f"[!] Unknown pattern (length {len(h)}).")
    print("\nTip: verify with 'hashid' or 'hash-identifier' if installed.")
