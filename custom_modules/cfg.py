#!/usr/bin/env python3

import os


# Rybka proj. specific prerequisites
class Rybka_py_env_bootstrap():
    def __init__(self):
        self.BIN_KEY = os.environ.get("BIN_KEY")
        self.BIN_SECRET = os.environ.get("BIN_SECRET")
        try:
            self.DEBUG_LVL = int(os.environ.get("RYBKA_DEBUG_LVL"))
        except:
            self.DEBUG_LVL = None
        self.RYBKA_MODE = os.environ.get("RYBKA_MODE", "DEMO")
        self.TRADE_SYMBOL = os.environ.get("RYBKA_TRADE_SYMBOL", "EGLDUSDT")
        self.SOCKET = os.environ.get("RYBKA_SOCKET", f"wss://stream.binance.com:9443/ws/{self.TRADE_SYMBOL.lower()}@kline_1m")
        self.RSI_PERIOD = os.environ.get("RYBKA_RSI_PERIOD", 10)
        self.RSI_FOR_BUY = os.environ.get("RYBKA_RSI_FOR_BUY", 30)
        self.RSI_FOR_SELL = os.environ.get("RYBKA_RSI_FOR_SELL", 70)
        self.TRADE_QUANTITY = os.environ.get("RYBKA_TRADE_QUANTITY", 0.4)
        self.MIN_PROFIT = os.environ.get("RYBKA_MIN_PROFIT", 0.25)
        self.RYBKA_EMAIL_SWITCH = os.environ.get("RYBKA_EMAIL_SWITCH", False)
        self.RYBKA_EMAIL_SENDER_EMAIL = os.environ.get("RYBKA_EMAIL_SENDER_EMAIL")
        self.RYBKA_EMAIL_SENDER_DEVICE_PASSWORD = os.environ.get("RYBKA_EMAIL_SENDER_DEVICE_PASSWORD")
        self.RYBKA_EMAIL_RECIPIENT_EMAIL = os.environ.get("RYBKA_EMAIL_RECIPIENT_EMAIL")
        self.RYBKA_EMAIL_RECIPIENT_NAME = os.environ.get("RYBKA_EMAIL_RECIPIENT_NAME", "User")
        self.SET_DISCLAIMER = os.environ.get("RYBKA_DISCLAIMER", "True")
        if self.RYBKA_MODE == "DEMO":
            self.RYBKA_DEMO_BALANCE_USDT = os.environ.get("RYBKA_DEMO_BALANCE_USDT", 1500)
            self.RYBKA_DEMO_BALANCE_EGLD = os.environ.get("RYBKA_DEMO_BALANCE_EGLD", 100)
            self.RYBKA_DEMO_BALANCE_BNB = os.environ.get("RYBKA_DEMO_BALANCE_BNB", 0.2)

bootstrap = Rybka_py_env_bootstrap()
