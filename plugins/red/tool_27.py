import base64
import codecs
import urllib.parse

NAME = "Encoder / Decoder"
DESCRIPTION = "Base64, hex, URL, and ROT13 encode/decode utility."
ALLOWED_ROLES = ["admin", "instructor", "student"]


def run(username, role):
    print("1. Base64 encode     5. Hex encode")
    print("2. Base64 decode     6. Hex decode")
    print("3. URL encode        7. ROT13")
    print("4. URL decode")
    choice = input("Select: ").strip()
    text = input("Text: ")
    if not text:
        return

    try:
        if choice == "1":
            print(base64.b64encode(text.encode()).decode())
        elif choice == "2":
            print(base64.b64decode(text).decode(errors="ignore"))
        elif choice == "3":
            print(urllib.parse.quote(text))
        elif choice == "4":
            print(urllib.parse.unquote(text))
        elif choice == "5":
            print(text.encode().hex())
        elif choice == "6":
            print(bytes.fromhex(text).decode(errors="ignore"))
        elif choice == "7":
            print(codecs.decode(text, "rot_13"))
        else:
            print("[!] Invalid choice.")
    except Exception as e:
        print(f"[!] Failed: {e}")
