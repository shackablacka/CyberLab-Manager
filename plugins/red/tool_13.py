from pathlib import Path

NAME = "Wordlist Generator"
DESCRIPTION = "Build custom password wordlists from a base word."
ALLOWED_ROLES = ["admin", "instructor"]

REPORT_DIR = Path("tools/red/reports")


def run(username, role):
    base = input("Base word (e.g. org name): ").strip()
    if not base:
        return
    years = input("Append year range (e.g. 2020-2026, blank=skip): ").strip()

    variants = {base, base.lower(), base.upper(), base.capitalize()}
    leet = str.maketrans({"a": "@", "e": "3", "i": "1", "o": "0", "s": "$"})
    variants |= {v.translate(leet) for v in list(variants)}

    words = set()
    suffixes = ["", "!", "1", "01", "123", "123!", "@123"]
    for v in variants:
        for s in suffixes:
            words.add(v + s)

    if "-" in years:
        try:
            start, end = years.split("-")
            for y in range(int(start), int(end) + 1):
                for v in list(variants):
                    words.add(f"{v}{y}")
                    words.add(f"{v}{y}!")
        except ValueError:
            print("[!] Bad year range, skipped.")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / f"wordlist_{base}.txt"
    out.write_text("\n".join(sorted(words)), encoding="utf-8")
    print(f"[+] {len(words)} words written to {out}")
