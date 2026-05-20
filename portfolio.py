"""
portfolio.py - Trading engine: buy, sell, portfolio valuation.
All functions accept a username, load from DB, mutate, and save back.
GUI never touches the database or price engine directly for trades.
"""

from datetime import datetime
from database import get_user, save_user
from market import get_price


# ─────────────────────────────────────────────────────────────
# Buy
# ─────────────────────────────────────────────────────────────

def buy_stock(username: str, symbol: str, qty: int) -> tuple[bool, str]:
    """
    Purchase `qty` shares of `symbol` for `username`.
    Updates balance, portfolio, and transaction history.
    Returns (success, message).
    """
    if qty <= 0:
        return False, "Quantity must be a positive integer."

    user = get_user(username)
    if user is None:
        return False, "User not found."

    price      = get_price(symbol)
    total_cost = round(price * qty, 2)

    if user["balance"] < total_cost:
        return (
            False,
            f"Insufficient balance.\n"
            f"Need ₹{total_cost:,.2f} but you have ₹{user['balance']:,.2f}."
        )

    # Deduct balance
    user["balance"] = round(user["balance"] - total_cost, 2)

    # Update portfolio (weighted average price)
    portfolio = user["portfolio"]
    if symbol in portfolio:
        old_qty   = portfolio[symbol]["qty"]
        old_avg   = portfolio[symbol]["avg_price"]
        new_qty   = old_qty + qty
        new_avg   = round((old_avg * old_qty + price * qty) / new_qty, 2)
        portfolio[symbol] = {"qty": new_qty, "avg_price": new_avg}
    else:
        portfolio[symbol] = {"qty": qty, "avg_price": price}

    # Log transaction
    user["transactions"].append({
        "type":      "BUY",
        "stock":     symbol,
        "qty":       qty,
        "price":     price,
        "total":     total_cost,
        "timestamp": _now(),
    })

    save_user(username, user)
    return True, (
        f"✅ Bought {qty} share(s) of {symbol} @ ₹{price:,.2f}\n"
        f"Total: ₹{total_cost:,.2f}  |  Remaining Balance: ₹{user['balance']:,.2f}"
    )


# ─────────────────────────────────────────────────────────────
# Sell
# ─────────────────────────────────────────────────────────────

def sell_stock(username: str, symbol: str, qty: int) -> tuple[bool, str]:
    """
    Sell `qty` shares of `symbol` for `username`.
    Returns (success, message).
    """
    if qty <= 0:
        return False, "Quantity must be a positive integer."

    user = get_user(username)
    if user is None:
        return False, "User not found."

    portfolio = user["portfolio"]
    if symbol not in portfolio or portfolio[symbol]["qty"] == 0:
        return False, f"You don't own any shares of {symbol}."

    held = portfolio[symbol]["qty"]
    if qty > held:
        return False, f"You only hold {held} share(s) of {symbol}."

    price      = get_price(symbol)
    total_recv = round(price * qty, 2)

    # Credit balance
    user["balance"] = round(user["balance"] + total_recv, 2)

    # Update portfolio
    new_qty = held - qty
    if new_qty == 0:
        del portfolio[symbol]
    else:
        portfolio[symbol]["qty"] = new_qty

    # Log transaction
    user["transactions"].append({
        "type":      "SELL",
        "stock":     symbol,
        "qty":       qty,
        "price":     price,
        "total":     total_recv,
        "timestamp": _now(),
    })

    save_user(username, user)
    return True, (
        f"✅ Sold {qty} share(s) of {symbol} @ ₹{price:,.2f}\n"
        f"Received: ₹{total_recv:,.2f}  |  New Balance: ₹{user['balance']:,.2f}"
    )


# ─────────────────────────────────────────────────────────────
# Portfolio summary
# ─────────────────────────────────────────────────────────────

def get_portfolio_summary(username: str) -> list[dict]:
    """
    Return a list of dicts — one per holding — with P&L info.
    Each dict: {symbol, qty, avg_price, current_price, invested, current_value, pnl, pnl_pct}
    """
    user = get_user(username)
    if user is None:
        return []

    rows = []
    for symbol, info in user["portfolio"].items():
        qty       = info["qty"]
        avg       = info["avg_price"]
        curr      = get_price(symbol)
        invested  = round(avg * qty, 2)
        curr_val  = round(curr * qty, 2)
        pnl       = round(curr_val - invested, 2)
        pnl_pct   = round((pnl / invested) * 100, 2) if invested else 0.0
        rows.append({
            "symbol":        symbol,
            "qty":           qty,
            "avg_price":     avg,
            "current_price": curr,
            "invested":      invested,
            "current_value": curr_val,
            "pnl":           pnl,
            "pnl_pct":       pnl_pct,
        })
    return rows


def get_balance(username: str) -> float:
    user = get_user(username)
    return user["balance"] if user else 0.0


def get_transactions(username: str) -> list[dict]:
    user = get_user(username)
    return user["transactions"][::-1] if user else []   # newest first


# ─────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now().strftime("%d-%b-%Y %H:%M:%S")