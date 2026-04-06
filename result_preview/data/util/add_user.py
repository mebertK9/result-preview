"""
Run this script once locally to generate password hashes.
Paste the printed line into the USERS dict in users.py.

Usage:
    python add_user.py
"""
from werkzeug.security import generate_password_hash

username = input("Username: ").strip()
password = input("Password: ").strip()
hashed = generate_password_hash(password)
print(f'\nPaste this into users.py → USERS:\n    "{username}": "{hashed}",')