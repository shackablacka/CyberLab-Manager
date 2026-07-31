from pathlib import Path

NAME = "Password Policy Auditor"
DESCRIPTION = "Check local password policy settings (login.defs, PAM)."
ALLOWED_ROLES = ["admin", "instructor"]

FILES = [Path("/etc/login.defs"), Path("/etc/pam.d/common-password")]

IMPORTANT_KEYS = {
    "PASS_MAX_DAYS": 90,
    "PASS_MIN_DAYS": 0,
    "PASS_WARN_AGE": 7,
}


def run(username, role):
    print("=== Password Policy Audit ===\n")

    for file in FILES:
        if not file.exists():
            continue
        print(f"--- {file} ---")
        try:
            lines = file.read_text(errors="ignore").splitlines()
        except PermissionError:
            print("  (unreadable — need root)")
            continue

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                continue
            if "=" in stripped:
                key, _, value = stripped.partition("=")
                key = key.strip()
                value = value.strip()
                if key in IMPORTANT_KEYS:
                    threshold = IMPORTANT_KEYS[key]
                    status = ""
                    if key == "PASS_MAX_DAYS" and value.isdigit():
                        if int(value) > threshold:
                            status = f"  <-- recommended <= {threshold}"
                        else:
                            status = "  (ok)"
                    elif key == "PASS_WARN_AGE" and value.isdigit():
                        if int(value) < threshold:
                            status = f"  <-- recommended >= {threshold}"
                        else:
                            status = "  (ok)"
                    print(f"  {key} = {value}{status}")

    # PAM complexity
    pam = Path("/etc/pam.d/common-password")
    if pam.exists():
        print(f"\n--- PAM complexity hints ---")
        for line in pam.read_text(errors="ignore").splitlines():
            if "pam_pwquality" in line:
                print(f"  {line}")
        print("  (Check /etc/security/pwquality.conf for minlen, ucredit, etc.)")
