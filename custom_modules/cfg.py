#!/usr/bin/env python3

import os
import configparser


# Rybka proj. specific prerequisites
class Rybka_py_env_bootstrap():
    def __init__(self):
        # API Authorization
        self.BIN_KEY = os.environ.get("BIN_KEY")
        self.BIN_SECRET = os.environ.get("BIN_SECRET")

        # Disclaimer
        if not os.environ.get("RYBKA_DISCLAIMER"):
            self.SET_DISCLAIMER = config.get("Rybka Binance Configuration. For LIVE and DEMO modes", "SET_DISCLAIMER").strip("\n").strip()
        else:
            self.SET_DISCLAIMER = os.environ.get("RYBKA_DISCLAIMER").strip("\n").strip()
        
        # Debug level
        try:
            self.DEBUG_LVL = int(config.get("Rybka Standalone Configuration. For LIVE and DEMO modes", "RYBKA_DEBUG_LVL"))
        except:
            self.DEBUG_LVL = None
        
        # Email related configuration
        self.RYBKA_EMAIL_SENDER_DEVICE_PASSWORD = os.environ.get("RYBKA_EMAIL_SENDER_DEVICE_PASSWORD").strip("\n").strip()
        if not os.environ.get("RYBKA_EMAIL_SWITCH"):
            self.RYBKA_EMAIL_SWITCH = config.get("Rybka Standalone Configuration. For LIVE and DEMO modes", "RYBKA_EMAIL_SWITCH").strip("\n").strip()
        else:
            self.RYBKA_EMAIL_SWITCH = os.environ.get("RYBKA_EMAIL_SWITCH").strip("\n").strip()
        if not os.environ.get("RYBKA_EMAIL_SENDER_EMAIL"):
            self.RYBKA_EMAIL_SENDER_EMAIL = config.get("Rybka Standalone Configuration. For LIVE and DEMO modes", "RYBKA_EMAIL_SENDER_EMAIL").strip("\n").strip()
        else:
            self.RYBKA_EMAIL_SENDER_EMAIL = os.environ.get("RYBKA_EMAIL_SENDER_EMAIL").strip("\n").strip()
        if not os.environ.get("RYBKA_EMAIL_RECIPIENT_EMAIL"):
            self.RYBKA_EMAIL_RECIPIENT_EMAIL = config.get("Rybka Standalone Configuration. For LIVE and DEMO modes", "RYBKA_EMAIL_RECIPIENT_EMAIL").strip("\n").strip()
        else:
            self.RYBKA_EMAIL_RECIPIENT_EMAIL = os.environ.get("RYBKA_EMAIL_RECIPIENT_EMAIL").strip("\n").strip()
        if not os.environ.get("RYBKA_EMAIL_RECIPIENT_NAME"):
            self.RYBKA_EMAIL_RECIPIENT_NAME = config.get("Rybka Standalone Configuration. For LIVE and DEMO modes", "RYBKA_EMAIL_RECIPIENT_NAME").strip("\n").strip()
        else:
            self.RYBKA_EMAIL_RECIPIENT_NAME = os.environ.get("RYBKA_EMAIL_RECIPIENT_NAME").strip("\n").strip()

        # Binance related configuration
        self.TRADE_SYMBOL = config.get("Rybka Binance Configuration. For LIVE and DEMO modes", "RYBKA_TRADE_SYMBOL").strip("\n").strip()
        self.SOCKET = f"wss://stream.binance.com:9443/ws/{self.TRADE_SYMBOL.lower()}@kline_1m"
        self.RSI_PERIOD = int(config.get("Rybka Binance Configuration. For LIVE and DEMO modes", "RYBKA_RSI_PERIOD"))
        self.RSI_FOR_BUY = int(config.get("Rybka Binance Configuration. For LIVE and DEMO modes", "RYBKA_RSI_FOR_BUY"))
        self.RSI_FOR_SELL = int(config.get("Rybka Binance Configuration. For LIVE and DEMO modes", "RYBKA_RSI_FOR_SELL"))
        self.TRADE_QUANTITY = float(config.get("Rybka Binance Configuration. For LIVE and DEMO modes", "RYBKA_TRADE_QUANTITY"))
        self.MIN_PROFIT = float(config.get("Rybka Binance Configuration. For LIVE and DEMO modes", "RYBKA_MIN_PROFIT"))

        # DEMO mode related configuration
        try:
            self.RYBKA_DEMO_BALANCE_USDT = int(config.get("Rybka Standalone Configuration. Only for DEMO mode", "RYBKA_DEMO_BALANCE_USDT")).strip("\n").strip()
        except:
            self.RYBKA_DEMO_BALANCE_USDT = 1500
        try:
            self.RYBKA_DEMO_BALANCE_EGLD = int(config.get("Rybka Standalone Configuration. Only for DEMO mode", "RYBKA_DEMO_BALANCE_EGLD"))
        except:
            self.RYBKA_DEMO_BALANCE_EGLD = 100
        try:
            self.RYBKA_DEMO_BALANCE_BNB = int(config.get("Rybka Standalone Configuration. Only for DEMO mode", "RYBKA_DEMO_BALANCE_BNB"))
        except:
            self.RYBKA_DEMO_BALANCE_BNB = 0.2
        with open("project_version", 'r', encoding="utf8") as f:
            self.__version__ = f.read().strip("\n").strip()


config = configparser.ConfigParser() 
bootstrap = ""

def variables_reinitialization():
    
    config.read(os.path.join(os.environ.get("CURRENT_DIR_PATH"), "env_vars_config.ini"))

    global bootstrap
    bootstrap = Rybka_py_env_bootstrap()

    from custom_modules.logging.logging import log
    log.VERBOSE("Vars REINITIALIZED!")


variables_reinitialization()
