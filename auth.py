"""
auth.py - Authentication logic (register / login).
GUI calls these functions; they talk to database.py — never to JSON directly.
"""

import hashlib
from database import get_user, save_user, user_exists

STARTING_BALANCE = 100_000.0   # ₹1,00,000


def _hash_password(password: str) -> str:
    """Simple SHA-256 hash so passwords aren't stored as plain text."""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.
    Returns (success: bool, message: str).
    """
    username = username.strip()
    password = password.strip()

    if not username or not password:
        return False, "Username and password cannot be empty."

    if len(username) < 3:
        return False, "Username must be at least 3 characters."

    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    if user_exists(username):
        return False, f"Username '{username}' is already taken."

    user_data = {
        "password": _hash_password(password),
        "balance": STARTING_BALANCE,
        "portfolio": {},       # { "SYMBOL": {"qty": int, "avg_price": float} }
        "transactions": []     # list of transaction dicts
    }
    save_user(username, user_data)
    return True, "Account created successfully! Please log in."


def login_user(username: str, password: str) -> tuple[bool, str]:
    """
    Validate credentials.
    Returns (success: bool, message: str).
    """
    username = username.strip()
    password = password.strip()

    if not username or not password:
        return False, "Please enter both username and password."

    user = get_user(username)
    if user is None:
        return False, "Username not found."

    if user["password"] != _hash_password(password):
        return False, "Incorrect password."

    return True, "Login successful."