"""
database.py - Handles all JSON file read/write operations.
Think of this as the "storage layer" — no business logic here, just load/save.
"""

import json
import os

DB_FILE = "data.json"

# ──────────────────────────────────────────────
# Default structure written on first run
# ──────────────────────────────────────────────
DEFAULT_DB = {
    "users": {}
    # Each user entry looks like:
    # "username": {
    #     "password": "hashed_or_plain",
    #     "balance": 100000.0,
    #     "portfolio": {
    #         "RELIANCE": {"qty": 5, "avg_price": 2400.0}
    #     },
    #     "transactions": [
    #         {"type": "BUY", "stock": "RELIANCE", "qty": 5,
    #          "price": 2400.0, "total": 12000.0, "timestamp": "..."}
    #     ]
    # }
}


def load_db() -> dict:
    """Load the entire database from data.json. Creates file if missing."""
    if not os.path.exists(DB_FILE):
        save_db(DEFAULT_DB)
        return DEFAULT_DB.copy()
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(data: dict) -> None:
    """Persist the entire database dict back to data.json."""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_user(username: str) -> dict | None:
    """Return a single user's data dict, or None if not found."""
    db = load_db()
    return db["users"].get(username)


def save_user(username: str, user_data: dict) -> None:
    """Write (create or update) a single user's data."""
    db = load_db()
    db["users"][username] = user_data
    save_db(db)


def user_exists(username: str) -> bool:
    """Quick existence check without loading the full user object."""
    db = load_db()
    return username in db["users"]