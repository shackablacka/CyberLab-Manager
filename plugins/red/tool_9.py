import hashlib
from pathlib import Path

NAME = "Hash Calculator"
DESCRIPTION = "MD5/SHA1/SHA256 hashes for strings or files."
ALLOWED_ROLES = ["admin", "instructor", "student"]


def run(username, role):
    mode = input("Hash (1) string or (2) file? [1/2]: ").strip()

    if mode == "2":
        path = Path(input("File path: ").strip())
        if not path.is_file():
            print("[!] File not found.")
            return
        data = path.read_bytes()
    else:
        text = input("String to hash: ")
        if not text:
            return
        data = text.encode("utf-8")

    print("\n--- Hashes ---")
    print(f"  MD5:    {hashlib.md5(data).hexdigest()}")
    print(f"  SHA1:   {hashlib.sha1(data).hexdigest()}")
    print(f"  SHA256: {hashlib.sha256(data).hexdigest()}")
