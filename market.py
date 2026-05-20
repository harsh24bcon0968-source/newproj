"""
market.py - Stock market simulation engine.
Holds the master list of Indian stocks and simulates price changes.
The GUI polls get_all_stocks() to refresh the dashboard.
"""

import random

# ──────────────────────────────────────────────────────────────
# Master stock list  (symbol → display name + initial price ₹)
# ──────────────────────────────────────────────────────────────
_STOCK_DATA = {
    "RELIANCE":   {"name": "Reliance Industries",      "price": 2450.00},
    "TCS":        {"name": "Tata Consultancy Svcs",    "price": 3680.00},
    "INFY":       {"name": "Infosys Ltd",               "price": 1520.00},
    "HDFCBANK":   {"name": "HDFC Bank",                 "price": 1640.00},
    "ICICIBANK":  {"name": "ICICI Bank",                "price": 1050.00},
    "SBIN":       {"name": "State Bank of India",       "price": 765.00},
    "BAJFINANCE": {"name": "Bajaj Finance",             "price": 6800.00},
    "HINDUNILVR": {"name": "Hindustan Unilever",        "price": 2380.00},
    "WIPRO":      {"name": "Wipro Ltd",                 "price": 480.00},
    "AXISBANK":   {"name": "Axis Bank",                 "price": 1120.00},
    "LT":         {"name": "Larsen & Toubro",           "price": 3450.00},
    "KOTAKBANK":  {"name": "Kotak Mahindra Bank",       "price": 1780.00},
    "ASIANPAINT": {"name": "Asian Paints",              "price": 2850.00},
    "MARUTI":     {"name": "Maruti Suzuki",             "price": 10200.00},
    "SUNPHARMA":  {"name": "Sun Pharmaceutical",        "price": 1380.00},
    "TATAMOTORS": {"name": "Tata Motors",               "price": 620.00},
    "ONGC":       {"name": "Oil & Natural Gas Corp",    "price": 275.00},
    "POWERGRID":  {"name": "Power Grid Corp",           "price": 310.00},
    "ULTRACEMCO": {"name": "UltraTech Cement",          "price": 9800.00},
    "NESTLEIND":  {"name": "Nestle India",              "price": 22500.00},
}

# Tracks the *live* price separately so history isn't lost
_live_prices: dict[str, float] = {s: d["price"] for s, d in _STOCK_DATA.items()}

# Keeps the last ~50 price points per stock for the trend chart
_price_history: dict[str, list[float]] = {s: [d["price"]] for s, d in _STOCK_DATA.items()}


# ──────────────────────────────────────────────────────────────
# Public API used by GUI / portfolio
# ──────────────────────────────────────────────────────────────

def get_all_stocks() -> list[dict]:
    """
    Return a list of stock dicts with current prices.
    Each dict: {symbol, name, price, change_pct}
    """
    stocks = []
    for symbol, data in _STOCK_DATA.items():
        prev = _price_history[symbol][-2] if len(_price_history[symbol]) > 1 else data["price"]
        curr = _live_prices[symbol]
        change_pct = ((curr - prev) / prev) * 100
        stocks.append({
            "symbol": symbol,
            "name":   data["name"],
            "price":  curr,
            "change_pct": round(change_pct, 2),
        })
    return stocks


def get_price(symbol: str) -> float:
    """Return the current live price for a single stock."""
    return _live_prices.get(symbol, 0.0)


def get_price_history(symbol: str) -> list[float]:
    """Return the list of historical prices for charting."""
    return list(_price_history.get(symbol, []))


def tick_prices() -> None:
    """
    Simulate one market tick: each stock moves ±0.5% to ±3%.
    Call this every few seconds from the GUI main loop.
    """
    for symbol in _live_prices:
        # Weighted random: small moves are much more common
        magnitude = random.choices(
            [0.005, 0.01, 0.02, 0.03],
            weights=[50, 30, 15, 5]
        )[0]
        direction = random.choice([-1, 1])
        change = _live_prices[symbol] * magnitude * direction
        new_price = round(max(_live_prices[symbol] + change, 1.0), 2)
        _live_prices[symbol] = new_price

        hist = _price_history[symbol]
        hist.append(new_price)
        if len(hist) > 60:        # keep last 60 ticks
            hist.pop(0)


def get_symbol_list() -> list[str]:
    """Return a sorted list of all stock symbols (for dropdowns)."""
    return sorted(_STOCK_DATA.keys())