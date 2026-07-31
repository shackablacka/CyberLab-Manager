import math
import string

NAME = "Password Strength Auditor"
DESCRIPTION = "Estimate password entropy and flag weak choices."
ALLOWED_ROLES = ["admin", "instructor", "student"]

COMMON = {"password", "123456", "qwerty", "letmein", "admin", "welcome",
          "password1", "12345678", "abc123", "iloveyou"}


def run(username, role):
    pw = input("Password to audit (not stored): ")

    pool = 0
    pool += 26 if any(c in string.ascii_lowercase for c in pw) else 0
    pool += 26 if any(c in string.ascii_uppercase for c in pw) else 0
    pool += 10 if any(c in string.digits for c in pw) else 0
    pool += 32 if any(not c.isalnum() for c in pw) else 0

    entropy = len(pw) * math.log2(pool) if pool else 0

    print(f"\n  Length   : {len(pw)}")
    print(f"  Char pool: {pool}")
    print(f"  Entropy  : {entropy:.1f} bits")

    if pw.lower() in COMMON:
        print("  [!] CRITICAL: password is in the common-password list.")
    if entropy < 40:
        print("  Rating   : WEAK — crackable in seconds/minutes.")
    elif entropy < 60:
        print("  Rating   : MODERATE — improve length and variety.")
    else:
        print("  Rating   : STRONG.")
