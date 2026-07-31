import getpass
import logging
import secrets
import string

from core.logger import setup_logger
from core.database import initialize_database
from core.auth import create_user, authenticate, user_exists
from core.menu import run_dashboard

log = setup_logger()


def generate_password(length=12):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_default_admin():
    username = "admin"

    if user_exists(username):
        log.info("Default admin already exists. Skipping creation.")
        return

    password = generate_password()

    created = create_user(
        username=username,
        password=password,
        role="admin",
    )

    if created:
        log.info("Default admin account created.")
        print("\n[+] Default admin created!")
        print(f"[!] Username: {username}")
        print(f"[!] Password: {password}")
        print("[!] CHANGE THIS PASSWORD IMMEDIATELY AFTER LOGIN!\n")
    else:
        log.error("Failed to create default admin.")


def login():
    print("\n====== LOGIN ======\n")

    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")

    success, role = authenticate(username, password)

    if success:
        log.info("Successful login: %s (role=%s)", username, role)
        print(f"\nWelcome {username}!")
        print(f"Role: {role}")
        return username, role

    log.warning("Failed login attempt: %s", username)
    print("\nInvalid username or password.")
    return None, None


def main():
    log.info("CyberLab-Manager starting up.")
    initialize_database()
    create_default_admin()

    user, role = login()

    if user:
        run_dashboard(user, role)
    else:
        log.warning("Login failed, exiting.")


if __name__ == "__main__":
    main()
