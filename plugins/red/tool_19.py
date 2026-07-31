import ftplib

NAME = "FTP Anonymous Checker"
DESCRIPTION = "Test anonymous FTP login on a lab host."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    target = input("Target IP (lab only): ").strip()
    if not target:
        return

    try:
        ftp = ftplib.FTP()
        ftp.connect(target, 21, timeout=5)
        print(f"[+] Banner: {ftp.getwelcome()}")
        try:
            ftp.login("anonymous", "anonymous@lab.local")
            print("[!] VULNERABLE: anonymous login allowed")
            items = ftp.nlst()
            print(f"    {len(items)} item(s) visible (first 10):")
            for item in items[:10]:
                print(f"      {item}")
        except ftplib.error_perm:
            print("[+] Anonymous login rejected.")
        ftp.quit()
    except (ConnectionRefusedError, OSError) as e:
        print(f"[!] Connection failed: {e}")
