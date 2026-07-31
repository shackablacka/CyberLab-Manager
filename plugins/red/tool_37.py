from pathlib import Path

NAME = "Report Viewer"
DESCRIPTION = "Browse and read saved Red Team scan reports."
ALLOWED_ROLES = ["admin", "instructor", "student"]

REPORT_DIR = Path("tools/red/reports")


def run(username, role):
    if not REPORT_DIR.exists() or not any(REPORT_DIR.iterdir()):
        print("[!] No reports yet — run a scanner first.")
        return

    reports = sorted(REPORT_DIR.iterdir(), key=lambda p: p.stat().st_mtime,
                     reverse=True)
    print("\n--- Saved Reports (newest first) ---")
    for i, path in enumerate(reports, 1):
        size = path.stat().st_size
        print(f"  {i:2d}. {path.name:<40} {size:>8} bytes")

    choice = input("\nReport number to view (0 = cancel): ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(reports)):
        return

    target = reports[int(choice) - 1]
    print(f"\n--- {target.name} ---")
    content = target.read_text(encoding="utf-8", errors="ignore")
    print(content[:4000])
    if len(content) > 4000:
        print(f"\n... truncated ({len(content)} total chars).")
        print(f"[*] Full file: {target}")
