import getpass
import logging
import secrets
import string
from datetime import datetime

from core.auth import authenticate, create_user, user_exists
from core.database import initialize_database
from core.logger import setup_logger
from core.menu import run_dashboard

log = setup_logger()
MAX_LOGIN_ATTEMPTS = 3


def generate_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_default_admin() -> None:
    username = "admin"

    if user_exists(username):
        log.info("Default admin already exists. Skipping creation.")
        return

    password = generate_password()
    created = create_user(username=username, password=password, role="admin")

    if created:
        log.info("Default admin account created.")
        print("\n[+] Default admin created!")
        print(f"[!] Username: {username}")
        print(f"[!] Password: {password}")
        print("[!] CHANGE THIS PASSWORD IMMEDIATELY AFTER LOGIN!\n")
    else:
        log.error("Failed to create default admin.")


def login() -> tuple[str | None, str | None]:
    print("\n====== LOGIN ======\n")

    for attempt in range(1, MAX_LOGIN_ATTEMPTS + 1):
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")

        success, role = authenticate(username, password)
        if success:
            log.info("Successful login: %s (role=%s)", username, role)
            print(f"\nWelcome {username}!")
            print(f"Role: {role}")
            return username, role

        remaining = MAX_LOGIN_ATTEMPTS - attempt
        log.warning("Failed login attempt: %s", username)
        if remaining:
            print(f"\nInvalid username or password. {remaining} attempt(s) left.\n")
        else:
            print("\nToo many failed login attempts.")

    return None, None


def main() -> None:
    log.info("CyberLab-Manager starting up.")

    if datetime.now().year >= 2026:
        log.warning("System clock year is %s; audit timestamps may be wrong.", datetime.now().year)

    initialize_database()
    create_default_admin()

    user, role = login()
    if user:
        run_dashboard(user, role)
    else:
        log.warning("Login failed, exiting.")


if __name__ == "__main__":
    main()
