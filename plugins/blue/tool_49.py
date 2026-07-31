from pathlib import Path

NAME = "Blue Team Report Viewer"
DESCRIPTION = "Browse and read saved Blue Team reports."
ALLOWED_ROLES = ["admin", "instructor", "student"]

REPORT_DIR = Path("tools/blue/reports")


def run(username, role):
    if not REPORT_DIR.exists():
        print("[!] No reports directory found.")
        return

    all_files = []
    for item in sorted(REPORT_DIR.rglob("*"), key=lambda p: p.stat().st_mtime,
                       reverse=True):
        if item.is_file():
            all_files.append(item)

    if not all_files:
        print("[!] No reports saved yet. Run a tool that generates reports first.")
        return

    print(f"\n--- Blue Team Reports ({len(all_files)} files, newest first) ---\n")

    page_size = 15
    page = 0

    while True:
        start = page * page_size
        end = start + page_size
        batch = all_files[start:end]

        if not batch:
            print("[*] No more files.")
            break

        for i, path in enumerate(batch, start + 1):
            size = path.stat().st_size
            rel = path.relative_to(REPORT_DIR)
            print(f"  {i:3d}. {str(rel):<50} {size:>10,} bytes")

        print(f"\n  Page {page + 1} of {(len(all_files) - 1) // page_size + 1}")
        choice = input("\nFile number to view (n=next page, 0=back): ").strip()

        if choice == "0":
            return
        if choice.lower() == "n":
            page += 1
            continue
        if not choice.isdigit():
            continue

        index = int(choice) - 1
        if not (0 <= index < len(all_files)):
            print("[!] Invalid number.")
            continue

        target = all_files[index]
        print(f"\n{'=' * 60}")
        print(f"File: {target}")
        print(f"{'=' * 60}\n")

        try:
            content = target.read_text(encoding="utf-8", errors="ignore")
        except UnicodeDecodeError:
            print("[!] Binary file — cannot display as text.")
            continue

        print(content[:5000])

        if len(content) > 5000:
            print(f"\n... truncated ({len(content):,} total characters)")
            print(f"[*] Full path: {target}")
