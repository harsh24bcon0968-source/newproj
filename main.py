"""
main.py — Entry point for StockSim India.

Run this file:
    python main.py

Requirements: Python 3.10+ (uses X | Y type union syntax in portfolio.py).
No third-party libraries needed — only tkinter, json, random, hashlib,
threading, time, datetime (all stdlib).
"""

from gui import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()