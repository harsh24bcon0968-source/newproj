"""
gui.py  — Upgraded Tkinter GUI for StockSim India.
Groww / Zerodha Kite inspired dark trading terminal UI.

Screen flow:
  LoginScreen  ──►  DashboardScreen  ──►  BuySellScreen
                         │                      │
                         └──► PortfolioScreen ◄─┘
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

# ── backend modules ──────────────────────────────────────────
import auth
import market
import portfolio as pf

# ══════════════════════════════════════════════════════════════
# DESIGN SYSTEM — Groww/Zerodha inspired palette
# ══════════════════════════════════════════════════════════════
BG          = "#0B0E15"   # deepest background
BG2         = "#111521"   # page background
SURFACE     = "#161B28"   # card / panel surface
SURFACE2    = "#1C2235"   # elevated card
BORDER      = "#232A3E"   # subtle border
BORDER2     = "#2D364F"   # slightly stronger border

GREEN       = "#1DB954"   # Groww-style profit green
GREEN_DIM   = "#0D6B30"   # muted green for bg fills
GREEN_TEXT  = "#4ADE80"   # lighter green for text
RED         = "#F44336"   # loss red
RED_DIM     = "#6B1A15"   # muted red bg
RED_TEXT    = "#FF6B6B"   # softer red for text

GOLD        = "#F0B429"   # balance / highlight
BLUE        = "#3B82F6"   # accent blue (secondary actions)
BLUE_DIM    = "#1E3A5F"

WHITE       = "#F1F5F9"
MUTED       = "#64748B"
MUTED2      = "#94A3B8"
LABEL_FG    = "#CBD5E1"

# Typography — clean, terminal-feel
FNT_DISPLAY = ("Helvetica", 26, "bold")
FNT_TITLE   = ("Helvetica", 20, "bold")
FNT_HEAD    = ("Helvetica", 13, "bold")
FNT_SUBHEAD = ("Helvetica", 11, "bold")
FNT_BODY    = ("Helvetica", 11)
FNT_SMALL   = ("Helvetica", 9)
FNT_TINY    = ("Helvetica", 8)
FNT_MONO    = ("Courier", 10, "bold")
FNT_NUM     = ("Helvetica", 18, "bold")
FNT_NUM_SM  = ("Helvetica", 13, "bold")

TICK_INTERVAL = 5


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def label(parent, text, font=FNT_BODY, fg=WHITE, bg=BG, **kw):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kw)


def styled_entry(parent, show=None, width=28):
    e = tk.Entry(
        parent, show=show, width=width,
        bg=SURFACE2, fg=WHITE, insertbackground=GREEN,
        font=FNT_BODY, relief="flat",
        highlightthickness=1, highlightcolor=GREEN,
        highlightbackground=BORDER2,
    )
    return e


def styled_button(parent, text, command, color=GREEN, fg=BG, width=18, font=None):
    f = font or ("Helvetica", 10, "bold")
    btn = tk.Button(
        parent, text=text, command=command,
        bg=color, fg=fg, font=f,
        relief="flat", cursor="hand2",
        padx=14, pady=7, width=width,
        activebackground=WHITE, activeforeground=BG,
        bd=0,
    )
    # Hover effect
    def on_enter(e):
        try:
            r, g, b = btn.winfo_rgb(color)
            r, g, b = r // 256, g // 256, b // 256
            lighter = "#{:02x}{:02x}{:02x}".format(
                min(255, r + 30), min(255, g + 30), min(255, b + 30))
            btn.config(bg=lighter)
        except Exception:
            pass
    def on_leave(e):
        btn.config(bg=color)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def ghost_button(parent, text, command, fg=MUTED2, width=12):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=SURFACE, fg=fg, font=("Helvetica", 10),
        relief="flat", cursor="hand2",
        padx=10, pady=6, width=width,
        activebackground=BORDER2, activeforeground=WHITE,
        bd=0, highlightthickness=1, highlightbackground=BORDER2,
    )
    btn.bind("<Enter>", lambda e: btn.config(fg=WHITE, highlightbackground=BLUE))
    btn.bind("<Leave>", lambda e: btn.config(fg=fg, highlightbackground=BORDER2))
    return btn


def divider(parent, bg=BORDER, height=1, pady=0):
    f = tk.Frame(parent, bg=bg, height=height)
    f.pack(fill="x", pady=pady)
    return f


def stat_card(parent, title, attr_name, value="—", value_fg=WHITE, width=None):
    """A metric card with a label and a large value."""
    kw = {"bg": SURFACE2, "padx": 18, "pady": 14,
          "highlightthickness": 1, "highlightbackground": BORDER}
    if width:
        kw["width"] = width
    card = tk.Frame(parent, **kw)
    tk.Label(card, text=title, font=FNT_SMALL, fg=MUTED2, bg=SURFACE2).pack(anchor="w")
    lbl = tk.Label(card, text=value, font=FNT_NUM_SM, fg=value_fg, bg=SURFACE2)
    lbl.pack(anchor="w", pady=(2, 0))
    return card, lbl


# ══════════════════════════════════════════════════════════════
# LOGIN SCREEN
# ══════════════════════════════════════════════════════════════

class LoginScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG2)
        self.app = app
        self._build()

    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        center = tk.Frame(self, bg=BG2)
        center.grid(row=0, column=0)

        # ── brand ─────────────────────────
        brand = tk.Frame(center, bg=BG2)
        brand.pack(pady=(0, 32))

        tk.Label(brand, text="📈", font=("Helvetica", 42), bg=BG2).pack()
        tk.Label(brand, text="HMG Trading Firm", font=FNT_DISPLAY,
                 fg=GOLD, bg=BG2).pack(pady=(4, 2))

        # ── card ──────────────────────────
        card = tk.Frame(center, bg=SURFACE,
                        highlightthickness=1, highlightbackground=BORDER2,
                        padx=44, pady=36)
        card.pack(ipadx=4, ipady=4)

        # Tabs
        self._mode = tk.StringVar(value="login")

        tab_inner = tk.Frame(card, bg=SURFACE)
        tab_inner.pack(fill="x", pady=(0, 24))

        self._tab_login = tk.Button(
            tab_inner, text="LOGIN", command=lambda: self._set_mode("login"),
            bg=SURFACE2, fg=WHITE, font=("Helvetica", 10, "bold"),
            relief="flat", cursor="hand2", padx=20, pady=8, bd=0,
        )

        self._tab_register = tk.Button(
            tab_inner, text="REGISTER", command=lambda: self._set_mode("register"),
            bg=SURFACE, fg=MUTED, font=("Helvetica", 10, "bold"),
            relief="flat", cursor="hand2", padx=20, pady=8, bd=0,
        )

        self._tab_login.pack(side="left")
        self._tab_register.pack(side="left")

        # ❌ REMOVED: green underline indicator completely

        # Fields
        tk.Frame(card, bg=SURFACE, height=16).pack()

        tk.Label(card, text="USERNAME", font=("Helvetica", 8, "bold"),
                 fg=MUTED, bg=SURFACE, anchor="w").pack(fill="x")

        self._user_entry = styled_entry(card, width=32)
        self._user_entry.pack(pady=(4, 16), fill="x", ipady=6)

        tk.Label(card, text="PASSWORD", font=("Helvetica", 8, "bold"),
                 fg=MUTED, bg=SURFACE, anchor="w").pack(fill="x")

        self._pass_entry = styled_entry(card, show="●", width=32)
        self._pass_entry.pack(pady=(4, 24), fill="x", ipady=6)

        self._action_btn = styled_button(
            card, "LOGIN", self._submit,
            width=32, font=("Helvetica", 11, "bold")
        )
        self._action_btn.pack(fill="x", ipady=3)

        self._status = tk.Label(
            card, text="", font=FNT_SMALL,
            fg=RED, bg=SURFACE, wraplength=300, justify="center"
        )
        self._status.pack(pady=(14, 0))

        self._user_entry.bind("<Return>", lambda e: self._submit())
        self._pass_entry.bind("<Return>", lambda e: self._submit())

        self._set_mode("login")

    def _set_mode(self, mode):
        self._mode.set(mode)

        if mode == "login":
            self._tab_login.config(bg=SURFACE2, fg=WHITE)
            self._tab_register.config(bg=SURFACE, fg=MUTED)
            self._action_btn.config(text="LOGIN")
        else:
            self._tab_login.config(bg=SURFACE, fg=MUTED)
            self._tab_register.config(bg=SURFACE2, fg=WHITE)
            self._action_btn.config(text="CREATE ACCOUNT")

        self._status.config(text="")

    def _submit(self):
        uname = self._user_entry.get().strip()
        pwd   = self._pass_entry.get().strip()
        mode  = self._mode.get()

        if not uname or not pwd:
            self._status.config(text="Please enter username and password.", fg=RED)
            return

        if mode == "register":
            ok, msg = auth.register_user(uname, pwd)
            if ok:
                self._status.config(text=f"✓ {msg}", fg=GREEN_TEXT)
                self._set_mode("login")
            else:
                self._status.config(text=msg, fg=RED_TEXT)
        else:
            ok, msg = auth.login_user(uname, pwd)
            if ok:
                self.app.current_user = uname
                self.app.show_frame(DashboardScreen)
            else:
                self._status.config(text=msg, fg=RED_TEXT)
# ══════════════════════════════════════════════════════════════
# DASHBOARD SCREEN
# ══════════════════════════════════════════════════════════════

class DashboardScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG2)
        self.app = app
        self._build()

    def on_show(self):
        self._refresh_balance()
        self._refresh_table()

    def _build(self):
        # ── top nav ───────────────────────────────────────────
        nav = tk.Frame(self, bg=SURFACE, pady=0,
                       highlightthickness=1, highlightbackground=BORDER)
        nav.pack(fill="x")

        nav_inner = tk.Frame(nav, bg=SURFACE, padx=20, pady=12)
        nav_inner.pack(fill="x")

        tk.Label(nav_inner, text="📈", font=("Helvetica", 16), bg=SURFACE).pack(side="left")
        tk.Label(nav_inner, text="StockSim India", font=FNT_HEAD,
                 fg=GOLD, bg=SURFACE).pack(side="left", padx=(6, 0))

        right_nav = tk.Frame(nav_inner, bg=SURFACE)
        right_nav.pack(side="right")

        self._tick_dot = tk.Label(right_nav, text="● LIVE", font=("Helvetica", 8, "bold"),
                                   fg=GREEN, bg=SURFACE)
        self._tick_dot.pack(side="left", padx=(0, 16))

        ghost_button(right_nav, "💼  Portfolio",
                     lambda: self.app.show_frame(PortfolioScreen), width=12).pack(side="left", padx=4)
        ghost_button(right_nav, "🔓  Logout",
                     self._logout, fg=RED_TEXT, width=8).pack(side="left", padx=4)

        # ── hero / summary strip ──────────────────────────────
        hero = tk.Frame(self, bg=BG, pady=0,
                        highlightthickness=1, highlightbackground=BORDER)
        hero.pack(fill="x")

        hero_inner = tk.Frame(hero, bg=BG, padx=24, pady=16)
        hero_inner.pack(fill="x")

        # Balance card
        bal_block = tk.Frame(hero_inner, bg=BG)
        bal_block.pack(side="left")
        tk.Label(bal_block, text="AVAILABLE BALANCE", font=("Helvetica", 8, "bold"),
                 fg=MUTED, bg=BG).pack(anchor="w")
        self._bal_lbl = tk.Label(bal_block, text="₹0.00",
                                   font=("Helvetica", 28, "bold"), fg=GOLD, bg=BG)
        self._bal_lbl.pack(anchor="w")

        # Portfolio mini-stats
        stats_frame = tk.Frame(hero_inner, bg=BG)
        stats_frame.pack(side="left", padx=40)

        self._hero_cards = {}
        for key, title in [("invested", "INVESTED"), ("curr_val", "CURR. VALUE"), ("pnl", "P&L TODAY")]:
            f = tk.Frame(stats_frame, bg=BG, padx=16)
            f.pack(side="left")
            tk.Label(f, text=title, font=("Helvetica", 7, "bold"), fg=MUTED, bg=BG).pack(anchor="w")
            lbl = tk.Label(f, text="—", font=FNT_SUBHEAD, fg=LABEL_FG, bg=BG)
            lbl.pack(anchor="w")
            self._hero_cards[key] = lbl

        # Quick buy/sell button
        btn_frame = tk.Frame(hero_inner, bg=BG)
        btn_frame.pack(side="right")
        styled_button(btn_frame, "⚡  BUY / SELL",
                      lambda: self.app.show_frame(BuySellScreen),
                      width=14, font=("Helvetica", 10, "bold")).pack()

        divider(self, bg=BORDER)

        # ── market watch ──────────────────────────────────────
        body = tk.Frame(self, bg=BG2, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        header_row = tk.Frame(body, bg=BG2)
        header_row.pack(fill="x", pady=(0, 10))
        tk.Label(header_row, text="Market Watch", font=FNT_HEAD,
                 fg=WHITE, bg=BG2).pack(side="left")
        tk.Label(header_row, text=f"Updates every {TICK_INTERVAL}s",
                 font=FNT_TINY, fg=MUTED, bg=BG2).pack(side="left", padx=12, pady=3)

        # Treeview
        self._apply_treeview_style()
        cols = ("Symbol", "Company Name", "Price (₹)", "Change %", "Volume")
        self._tree = ttk.Treeview(body, columns=cols, show="headings",
                                   height=20, style="Pro.Treeview")

        col_widths  = [100, 280, 140, 120, 120]
        col_anchors = ["center", "w", "e", "center", "e"]
        for col, w, anc in zip(cols, col_widths, col_anchors):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor=anc, minwidth=w)

        self._tree.tag_configure("up",   foreground=GREEN_TEXT, background="#0D1A15")
        self._tree.tag_configure("down", foreground=RED_TEXT,   background="#1A0D0D")
        self._tree.tag_configure("flat", foreground=LABEL_FG,   background=SURFACE)

        sb = ttk.Scrollbar(body, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)

        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._tree.bind("<Double-1>", self._on_row_dclick)

        # Status bar
        status_bar = tk.Frame(self, bg=SURFACE, pady=4, padx=20,
                               highlightthickness=1, highlightbackground=BORDER)
        status_bar.pack(fill="x", side="bottom")
        self._status_lbl = tk.Label(status_bar, text="Ready",
                                     font=FNT_TINY, fg=MUTED, bg=SURFACE)
        self._status_lbl.pack(side="left")

    def _refresh_balance(self):
        bal = pf.get_balance(self.app.current_user)
        self._bal_lbl.config(text=f"₹{bal:,.2f}")

        rows = pf.get_portfolio_summary(self.app.current_user)
        total_inv  = sum(r["invested"]      for r in rows)
        total_curr = sum(r["current_value"] for r in rows)
        total_pnl  = round(total_curr - total_inv, 2)
        pnl_color  = GREEN_TEXT if total_pnl >= 0 else RED_TEXT

        self._hero_cards["invested"].config(text=f"₹{total_inv:,.2f}")
        self._hero_cards["curr_val"].config(text=f"₹{total_curr:,.2f}")
        self._hero_cards["pnl"].config(
            text=f"{'+'if total_pnl>=0 else ''}₹{total_pnl:,.2f}", fg=pnl_color)

    def _refresh_table(self):
        for row in self._tree.get_children():
            self._tree.delete(row)

        for s in market.get_all_stocks():
            chg   = s["change_pct"]
            tag   = "up" if chg > 0 else ("down" if chg < 0 else "flat")
            arrow = "▲" if chg > 0 else ("▼" if chg < 0 else "—")
            # Simulate volume display
            volume = f"{int(abs(s['price']) * 100 + hash(s['symbol']) % 50000):,}"
            self._tree.insert("", "end", values=(
                s["symbol"],
                s["name"],
                f"₹{s['price']:,.2f}",
                f"{arrow} {abs(chg):.2f}%",
                volume,
            ), tags=(tag,))

    def refresh_live(self):
        self._refresh_balance()
        self._refresh_table()
        self._tick_dot.config(text="● UPDATED", fg=GOLD)
        self._status_lbl.config(text=f"Last updated: {time.strftime('%H:%M:%S')}")
        self.after(2000, lambda: (
            self._tick_dot.config(text="● LIVE", fg=GREEN),
            self._status_lbl.config(text="Ready"),
        ))

    def _on_row_dclick(self, event):
        item = self._tree.focus()
        if not item:
            return
        symbol = self._tree.item(item, "values")[0]
        self.app.preselect_stock = symbol
        self.app.show_frame(BuySellScreen)

    def _logout(self):
        self.app.current_user    = None
        self.app.preselect_stock = None
        self.app.show_frame(LoginScreen)

    def _apply_treeview_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Pro.Treeview",
                        background=SURFACE,
                        foreground=LABEL_FG,
                        fieldbackground=SURFACE,
                        rowheight=34,
                        font=("Helvetica", 10),
                        borderwidth=0,
                        relief="flat")
        style.configure("Pro.Treeview.Heading",
                        background=BG,
                        foreground=MUTED,
                        font=("Helvetica", 9, "bold"),
                        relief="flat",
                        borderwidth=0,
                        padding=(8, 6))
        style.map("Pro.Treeview",
                  background=[("selected", SURFACE2)],
                  foreground=[("selected", WHITE)])


# ══════════════════════════════════════════════════════════════
# BUY / SELL SCREEN
# ══════════════════════════════════════════════════════════════

class BuySellScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG2)
        self.app = app
        self._selected_symbol = tk.StringVar()
        self._trade_mode = tk.StringVar(value="BUY")
        self._build()

    def on_show(self):
        if self.app.preselect_stock:
            self._selected_symbol.set(self.app.preselect_stock)
            self.app.preselect_stock = None
        self._update_price()
        self._refresh_balance()
        self._refresh_transactions()
        self._update_trade_mode()

    def _build(self):
        # ── nav ───────────────────────────────────────────────
        nav = tk.Frame(self, bg=SURFACE, pady=0,
                       highlightthickness=1, highlightbackground=BORDER)
        nav.pack(fill="x")
        nav_inner = tk.Frame(nav, bg=SURFACE, padx=20, pady=12)
        nav_inner.pack(fill="x")

        ghost_button(nav_inner, "◀  Dashboard",
                     lambda: self.app.show_frame(DashboardScreen),
                     width=12).pack(side="left")
        tk.Label(nav_inner, text="Order Placement", font=FNT_HEAD,
                 fg=WHITE, bg=SURFACE).pack(side="left", padx=16)

        right = tk.Frame(nav_inner, bg=SURFACE)
        right.pack(side="right")
        tk.Label(right, text="Balance:", font=FNT_SMALL, fg=MUTED, bg=SURFACE).pack(side="left")
        self._bal_lbl = tk.Label(right, text="₹0.00", font=("Helvetica", 12, "bold"),
                                   fg=GOLD, bg=SURFACE)
        self._bal_lbl.pack(side="left", padx=(4, 16))
        ghost_button(right, "💼  Portfolio",
                     lambda: self.app.show_frame(PortfolioScreen), width=12).pack(side="left")

        divider(self, bg=BORDER)

        # ── body (2-column layout) ────────────────────────────
        body = tk.Frame(self, bg=BG2, padx=20, pady=20)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # ── LEFT: order form ──────────────────────────────────
        left = tk.Frame(body, bg=SURFACE,
                        highlightthickness=1, highlightbackground=BORDER2,
                        padx=28, pady=24, width=340)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 16))
        left.pack_propagate(False)

        # Stock selector
        tk.Label(left, text="SELECT STOCK", font=("Helvetica", 8, "bold"),
                 fg=MUTED, bg=SURFACE, anchor="w").pack(fill="x")

        symbols = market.get_symbol_list()
        if not self._selected_symbol.get():
            self._selected_symbol.set(symbols[0])

        self._combo = ttk.Combobox(left, textvariable=self._selected_symbol,
                                    values=symbols, state="readonly",
                                    font=("Helvetica", 11))
        self._combo.pack(pady=(4, 20), fill="x", ipady=5)
        self._combo.bind("<<ComboboxSelected>>", lambda e: self._update_price())

        self._apply_combo_style()

        # Price display
        price_card = tk.Frame(left, bg=BG, padx=16, pady=14,
                               highlightthickness=1, highlightbackground=BORDER2)
        price_card.pack(fill="x", pady=(0, 20))

        price_top = tk.Frame(price_card, bg=BG)
        price_top.pack(fill="x")
        tk.Label(price_top, text="MARKET PRICE", font=("Helvetica", 8, "bold"),
                 fg=MUTED, bg=BG).pack(side="left")
        self._price_change_lbl = tk.Label(price_top, text="", font=FNT_TINY, bg=BG)
        self._price_change_lbl.pack(side="right")

        self._price_lbl = tk.Label(price_card, text="₹0.00",
                                    font=("Helvetica", 26, "bold"), fg=WHITE, bg=BG)
        self._price_lbl.pack(anchor="w", pady=(4, 0))

        # BUY / SELL toggle
        toggle_frame = tk.Frame(left, bg=BORDER2, highlightthickness=0)
        toggle_frame.pack(fill="x", pady=(0, 20))

        self._buy_tab = tk.Button(
            toggle_frame, text="BUY", command=lambda: self._set_trade_mode("BUY"),
            bg=GREEN, fg=BG, font=("Helvetica", 11, "bold"),
            relief="flat", cursor="hand2", padx=0, pady=9, width=12, bd=0,
        )
        self._sell_tab = tk.Button(
            toggle_frame, text="SELL", command=lambda: self._set_trade_mode("SELL"),
            bg=SURFACE, fg=MUTED2, font=("Helvetica", 11, "bold"),
            relief="flat", cursor="hand2", padx=0, pady=9, width=12, bd=0,
        )
        self._buy_tab.pack(side="left", fill="x", expand=True)
        self._sell_tab.pack(side="left", fill="x", expand=True)

        # Quantity input
        tk.Label(left, text="QUANTITY (SHARES)", font=("Helvetica", 8, "bold"),
                 fg=MUTED, bg=SURFACE, anchor="w").pack(fill="x")

        qty_row = tk.Frame(left, bg=SURFACE)
        qty_row.pack(fill="x", pady=(4, 4))

        self._qty_entry = styled_entry(left, width=20)
        self._qty_entry.pack(fill="x", ipady=8, pady=(0, 4))
        self._qty_entry.bind("<KeyRelease>", lambda e: self._update_estimate())

        # Quick qty buttons
        quick_row = tk.Frame(left, bg=SURFACE)
        quick_row.pack(fill="x", pady=(0, 16))
        for qty in [1, 5, 10, 25]:
            btn = tk.Button(
                quick_row, text=str(qty),
                command=lambda q=qty: self._set_qty(q),
                bg=BG, fg=MUTED2, font=("Helvetica", 9),
                relief="flat", cursor="hand2", padx=8, pady=4, bd=0,
                highlightthickness=1, highlightbackground=BORDER2,
            )
            btn.pack(side="left", padx=(0, 6))
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg=WHITE, highlightbackground=GREEN))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg=MUTED2, highlightbackground=BORDER2))

        # Cost estimate card
        self._estimate_card = tk.Frame(left, bg=BG, padx=14, pady=12,
                                        highlightthickness=1, highlightbackground=BORDER)
        self._estimate_card.pack(fill="x", pady=(0, 20))

        row1 = tk.Frame(self._estimate_card, bg=BG)
        row1.pack(fill="x")
        tk.Label(row1, text="Estimated Total", font=FNT_SMALL, fg=MUTED, bg=BG).pack(side="left")
        self._cost_lbl = tk.Label(row1, text="—", font=FNT_SUBHEAD, fg=WHITE, bg=BG)
        self._cost_lbl.pack(side="right")

        # Execute button
        self._exec_btn = tk.Button(
            left, text="PLACE BUY ORDER",
            command=lambda: self._trade(self._trade_mode.get()),
            bg=GREEN, fg=BG,
            font=("Helvetica", 11, "bold"),
            relief="flat", cursor="hand2",
            padx=0, pady=12, bd=0,
        )
        self._exec_btn.pack(fill="x")

        # Hover on exec btn
        def _exec_enter(e):
            c = GREEN if self._trade_mode.get() == "BUY" else RED
            r, g, b = self._exec_btn.winfo_rgb(c)
            r, g, b = r // 256, g // 256, b // 256
            self._exec_btn.config(bg="#{:02x}{:02x}{:02x}".format(
                min(255, r + 25), min(255, g + 25), min(255, b + 25)))
        def _exec_leave(e):
            c = GREEN if self._trade_mode.get() == "BUY" else RED
            self._exec_btn.config(bg=c)
        self._exec_btn.bind("<Enter>", _exec_enter)
        self._exec_btn.bind("<Leave>", _exec_leave)

        # Status
        self._status = tk.Label(left, text="", font=("Helvetica", 10),
                                 fg=GREEN_TEXT, bg=SURFACE, wraplength=280)
        self._status.pack(pady=(12, 0))

        # ── RIGHT: transaction history ────────────────────────
        right_panel = tk.Frame(body, bg=BG2)
        right_panel.grid(row=0, column=1, sticky="nsew")

        header = tk.Frame(right_panel, bg=BG2)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="Order History", font=FNT_HEAD, fg=WHITE, bg=BG2).pack(side="left")

        txn_wrap = tk.Frame(right_panel, bg=SURFACE,
                             highlightthickness=1, highlightbackground=BORDER2)
        txn_wrap.pack(fill="both", expand=True)

        cols = ("Date / Time", "Type", "Stock", "Qty", "Price", "Total")
        self._txn_tree = ttk.Treeview(txn_wrap, columns=cols, show="headings",
                                       height=22, style="Pro.Treeview")
        widths  = [160, 70, 110, 60, 110, 120]
        anchors = ["w", "center", "center", "center", "e", "e"]
        for col, w, anc in zip(cols, widths, anchors):
            self._txn_tree.heading(col, text=col)
            self._txn_tree.column(col, width=w, anchor=anc)

        self._txn_tree.tag_configure("BUY",  foreground=GREEN_TEXT, background="#0A1A10")
        self._txn_tree.tag_configure("SELL", foreground=RED_TEXT,   background="#1A0A0A")

        tsb = ttk.Scrollbar(txn_wrap, orient="vertical", command=self._txn_tree.yview)
        self._txn_tree.configure(yscrollcommand=tsb.set)
        self._txn_tree.pack(side="left", fill="both", expand=True)
        tsb.pack(side="right", fill="y")

    def _apply_combo_style(self):
        style = ttk.Style()
        style.configure("TCombobox",
                        fieldbackground=SURFACE2,
                        background=SURFACE2,
                        foreground=WHITE,
                        selectbackground=SURFACE2,
                        selectforeground=WHITE,
                        borderwidth=1,
                        arrowcolor=MUTED2)

    def _set_qty(self, qty):
        self._qty_entry.delete(0, tk.END)
        self._qty_entry.insert(0, str(qty))
        self._update_estimate()

    def _set_trade_mode(self, mode):
        self._trade_mode.set(mode)
        self._update_trade_mode()

    def _update_trade_mode(self):
        mode = self._trade_mode.get()
        if mode == "BUY":
            self._buy_tab.config(bg=GREEN, fg=BG)
            self._sell_tab.config(bg=SURFACE, fg=MUTED2)
            self._exec_btn.config(text="PLACE BUY ORDER", bg=GREEN, fg=BG)
            self._price_lbl.config(fg=GREEN_TEXT)
        else:
            self._sell_tab.config(bg=RED, fg=WHITE)
            self._buy_tab.config(bg=SURFACE, fg=MUTED2)
            self._exec_btn.config(text="PLACE SELL ORDER", bg=RED, fg=WHITE)
            self._price_lbl.config(fg=RED_TEXT)

    def _refresh_balance(self):
        bal = pf.get_balance(self.app.current_user)
        self._bal_lbl.config(text=f"₹{bal:,.2f}")

    def _update_price(self):
        sym   = self._selected_symbol.get()
        price = market.get_price(sym)
        self._price_lbl.config(text=f"₹{price:,.2f}")
        self._update_estimate()

    def _update_estimate(self):
        sym = self._selected_symbol.get()
        try:
            qty   = int(self._qty_entry.get())
            price = market.get_price(sym)
            total = price * qty
            self._cost_lbl.config(text=f"₹{total:,.2f}")
        except ValueError:
            self._cost_lbl.config(text="—")

    def _trade(self, trade_type: str):
        sym = self._selected_symbol.get()
        try:
            qty = int(self._qty_entry.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            self._status.config(text="⚠ Enter a valid positive quantity.", fg=RED_TEXT)
            return

        if trade_type == "BUY":
            ok, msg = pf.buy_stock(self.app.current_user, sym, qty)
        else:
            ok, msg = pf.sell_stock(self.app.current_user, sym, qty)

        if ok:
            self._status.config(text=f"✓ {msg}", fg=GREEN_TEXT)
            self._refresh_balance()
            self._refresh_transactions()
            self._qty_entry.delete(0, tk.END)
            self._update_estimate()
        else:
            self._status.config(text=f"✗ {msg}", fg=RED_TEXT)

    def _refresh_transactions(self):
        for row in self._txn_tree.get_children():
            self._txn_tree.delete(row)
        txns = pf.get_transactions(self.app.current_user)
        for t in txns[:50]:
            self._txn_tree.insert("", "end", values=(
                t["timestamp"],
                t["type"],
                t["stock"],
                t["qty"],
                f"₹{t['price']:,.2f}",
                f"₹{t['total']:,.2f}",
            ), tags=(t["type"],))

    def refresh_live(self):
        self._update_price()


# ══════════════════════════════════════════════════════════════
# PORTFOLIO SCREEN
# ══════════════════════════════════════════════════════════════

class PortfolioScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG2)
        self.app = app
        self._build()

    def on_show(self):
        self._refresh()

    def _build(self):
        # ── nav ───────────────────────────────────────────────
        nav = tk.Frame(self, bg=SURFACE, pady=0,
                       highlightthickness=1, highlightbackground=BORDER)
        nav.pack(fill="x")
        nav_inner = tk.Frame(nav, bg=SURFACE, padx=20, pady=12)
        nav_inner.pack(fill="x")

        ghost_button(nav_inner, "◀  Dashboard",
                     lambda: self.app.show_frame(DashboardScreen),
                     width=12).pack(side="left")
        tk.Label(nav_inner, text="My Portfolio", font=FNT_HEAD,
                 fg=WHITE, bg=SURFACE).pack(side="left", padx=16)
        styled_button(nav_inner, "⚡  Trade",
                      lambda: self.app.show_frame(BuySellScreen),
                      width=10, font=("Helvetica", 10, "bold")).pack(side="right")

        divider(self, bg=BORDER)

        # ── summary cards ─────────────────────────────────────
        cards_strip = tk.Frame(self, bg=BG, padx=20, pady=16)
        cards_strip.pack(fill="x")

        self._card_labels = {}
        card_defs = [
            ("cash",     "CASH BALANCE",   GOLD),
            ("invested", "TOTAL INVESTED", LABEL_FG),
            ("curr_val", "CURRENT VALUE",  LABEL_FG),
            ("pnl",      "OVERALL P&L",    WHITE),
            ("ret",      "RETURN %",        WHITE),
        ]
        for key, title, fg in card_defs:
            c = tk.Frame(cards_strip, bg=SURFACE, padx=20, pady=14,
                         highlightthickness=1, highlightbackground=BORDER2)
            c.pack(side="left", padx=(0, 10), ipadx=4)
            tk.Label(c, text=title, font=("Helvetica", 8, "bold"),
                     fg=MUTED, bg=SURFACE).pack(anchor="w")
            lbl = tk.Label(c, text="—", font=("Helvetica", 15, "bold"),
                           fg=fg, bg=SURFACE)
            lbl.pack(anchor="w", pady=(4, 0))
            self._card_labels[key] = lbl

        divider(self, bg=BORDER, pady=0)

        # ── holdings table ────────────────────────────────────
        body = tk.Frame(self, bg=BG2, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Holdings", font=FNT_HEAD, fg=WHITE, bg=BG2).pack(
            anchor="w", pady=(0, 10))

        tbl_wrap = tk.Frame(body, bg=SURFACE,
                             highlightthickness=1, highlightbackground=BORDER2)
        tbl_wrap.pack(fill="both", expand=True)

        cols    = ("Symbol", "Qty", "Avg Buy ₹", "Curr Price ₹",
                   "Invested ₹", "Curr Value ₹", "P&L ₹", "P&L %")
        widths  = [100,  70,  120, 130, 130, 130, 120, 90]
        anchors = ["center", "center", "e", "e", "e", "e", "e", "center"]

        self._tree = ttk.Treeview(tbl_wrap, columns=cols, show="headings",
                                   height=16, style="Pro.Treeview")
        for col, w, anc in zip(cols, widths, anchors):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor=anc, minwidth=60)

        self._tree.tag_configure("profit", foreground=GREEN_TEXT, background="#0A1A10")
        self._tree.tag_configure("loss",   foreground=RED_TEXT,   background="#1A0A0A")
        self._tree.tag_configure("zero",   foreground=LABEL_FG,   background=SURFACE)

        sb = ttk.Scrollbar(tbl_wrap, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Empty state
        self._empty_frame = tk.Frame(body, bg=BG2)
        tk.Label(self._empty_frame, text="🪙", font=("Helvetica", 32), bg=BG2).pack(pady=(30, 8))
        tk.Label(self._empty_frame,
                 text="No holdings yet",
                 font=FNT_HEAD, fg=LABEL_FG, bg=BG2).pack()
        tk.Label(self._empty_frame,
                 text="Buy some stocks to start building your portfolio.",
                 font=FNT_SMALL, fg=MUTED, bg=BG2).pack(pady=(4, 0))

    def _refresh(self):
        user = self.app.current_user
        rows = pf.get_portfolio_summary(user)
        bal  = pf.get_balance(user)

        total_invested = sum(r["invested"]      for r in rows)
        total_curr     = sum(r["current_value"] for r in rows)
        total_pnl      = round(total_curr - total_invested, 2)
        ret_pct        = round((total_pnl / total_invested) * 100, 2) if total_invested else 0.0

        pnl_color = GREEN_TEXT if total_pnl >= 0 else RED_TEXT
        ret_color = GREEN_TEXT if ret_pct   >= 0 else RED_TEXT

        self._card_labels["cash"].config(text=f"₹{bal:,.2f}")
        self._card_labels["invested"].config(text=f"₹{total_invested:,.2f}")
        self._card_labels["curr_val"].config(text=f"₹{total_curr:,.2f}")
        self._card_labels["pnl"].config(
            text=f"{'+'if total_pnl>=0 else ''}₹{total_pnl:,.2f}", fg=pnl_color)
        self._card_labels["ret"].config(text=f"{ret_pct:+.2f}%", fg=ret_color)

        for row in self._tree.get_children():
            self._tree.delete(row)

        if not rows:
            self._empty_frame.pack(fill="x")
            return
        self._empty_frame.pack_forget()

        for r in sorted(rows, key=lambda x: x["current_value"], reverse=True):
            pnl = r["pnl"]
            tag = "profit" if pnl > 0 else ("loss" if pnl < 0 else "zero")
            self._tree.insert("", "end", values=(
                r["symbol"],
                r["qty"],
                f"₹{r['avg_price']:,.2f}",
                f"₹{r['current_price']:,.2f}",
                f"₹{r['invested']:,.2f}",
                f"₹{r['current_value']:,.2f}",
                f"{'+'if pnl>=0 else ''}₹{abs(pnl):,.2f}",
                f"{r['pnl_pct']:+.2f}%",
            ), tags=(tag,))

    def refresh_live(self):
        self._refresh()


# ══════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HMG Trading Company— Paper Trading")
        self.geometry("1200x740")
        self.minsize(1000, 640)
        self.resizable(True, True)
        self.configure(bg=BG2)

        # Global ttk style (applies Pro.Treeview cross-screen)
        self._init_global_style()

        self.current_user    = None
        self.preselect_stock = None

        self._container = tk.Frame(self, bg=BG2)
        self._container.pack(fill="both", expand=True)
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)

        self._frames: dict[type, tk.Frame] = {}
        for ScreenClass in (LoginScreen, DashboardScreen, BuySellScreen, PortfolioScreen):
            frame = ScreenClass(self._container, self)
            self._frames[ScreenClass] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginScreen)

        self._ticker_running = True
        self._tick_thread = threading.Thread(target=self._tick_loop, daemon=True)
        self._tick_thread.start()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_global_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Pro.Treeview",
                        background=SURFACE,
                        foreground=LABEL_FG,
                        fieldbackground=SURFACE,
                        rowheight=34,
                        font=("Helvetica", 10),
                        borderwidth=0,
                        relief="flat")
        style.configure("Pro.Treeview.Heading",
                        background=BG,
                        foreground=MUTED,
                        font=("Helvetica", 9, "bold"),
                        relief="flat",
                        borderwidth=0,
                        padding=(8, 8))
        style.map("Pro.Treeview",
                  background=[("selected", SURFACE2)],
                  foreground=[("selected", WHITE)])
        style.configure("Vertical.TScrollbar",
                        background=SURFACE,
                        troughcolor=BG,
                        arrowcolor=MUTED,
                        borderwidth=0,
                        relief="flat")

    def show_frame(self, screen_class: type):
        frame = self._frames[screen_class]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    def _tick_loop(self):
        while self._ticker_running:
            time.sleep(TICK_INTERVAL)
            market.tick_prices()
            self.after(0, self._on_tick)

    def _on_tick(self):
        if self.current_user is None:
            return
        for frame in self._frames.values():
            if hasattr(frame, "refresh_live"):
                frame.refresh_live()

    def _on_close(self):
        self._ticker_running = False
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()