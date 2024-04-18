#!/usr/bin/env python3

import configparser
import os

from termcolor import colored


# Rybka proj. specific prerequisites
class Rybka_py_env_bootstrap:
    def __init__(self):
        # API Authorization for Binance
        self.RYBKA_BIN_KEY = os.environ.get("RYBKA_BIN_KEY")
        self.RYBKA_BIN_SECRET = os.environ.get("RYBKA_BIN_SECRET")

        # API Authorization for Telegram
        self.TELE_KEY = os.environ.get("RYBKA_TELEGRAM_API_KEY")
        self.TELE_CHAT_ID = os.environ.get("RYBKA_TELEGRAM_CHAT_ID")

        # Disclaimer
        if not os.environ.get("RYBKA_DISCLAIMER"):
            self.SET_DISCLAIMER = (
                config.get(
                    "Rybka Standalone Configuration. For LIVE and DEMO modes",
                    "RYBKA_DISCLAIMER",
                )
                .strip("\n")
                .strip()
            )
        else:
            self.SET_DISCLAIMER = os.environ.get("RYBKA_DISCLAIMER").strip("\n").strip()

        # Var to set the bot only in BUY mode, disallowing sells
        if not os.environ.get("RYBKA_ALLOW_ONLY_BUYS"):
            self.ALLOW_ONLY_BUYS = int(
                config.get(
                    "Rybka Standalone Configuration. For LIVE and DEMO modes",
                    "RYBKA_ALLOW_ONLY_BUYS",
                )
            )
        else:
            self.ALLOW_ONLY_BUYS = int(
                os.environ.get("RYBKA_ALLOW_ONLY_BUYS").strip("\n").strip()
            )

        # Var to set the bot only in SELL mode, disallowing buys
        if not os.environ.get("RYBKA_ALLOW_ONLY_SELLS"):
            self.ALLOW_ONLY_SELLS = int(
                config.get(
                    "Rybka Standalone Configuration. For LIVE and DEMO modes",
                    "RYBKA_ALLOW_ONLY_SELLS",
                )
            )
        else:
            self.ALLOW_ONLY_SELLS = int(
                os.environ.get("RYBKA_ALLOW_ONLY_SELLS").strip("\n").strip()
            )

        # Heatmap algorithm controlled via such var, for a trading boost or the opposite
        if not os.environ.get("RYBKA_TRADING_BOOST_LVL"):
            self.TRADING_BOOST_LVL = int(
                config.get(
                    "Rybka Standalone Configuration. For LIVE and DEMO modes",
                    "RYBKA_TRADING_BOOST_LVL",
                )
            )
        else:
            self.TRADING_BOOST_LVL = int(
                os.environ.get("RYBKA_TRADING_BOOST_LVL").strip("\n").strip()
            )

        # Debug level
        try:
            self.DEBUG_LVL = int(
                config.get(
                    "Rybka Standalone Configuration. For LIVE and DEMO modes",
                    "RYBKA_DEBUG_LVL",
                )
            )
        except:
            self.DEBUG_LVL = None

        # Email related config.
        self.RYBKA_EMAIL_SENDER_DEVICE_PASSWORD = (
            str(os.environ.get("RYBKA_EMAIL_SENDER_DEVICE_PASSWORD")).strip("\n").strip()
        )
        if not os.environ.get("RYBKA_EMAIL_SWITCH"):
            self.RYBKA_EMAIL_SWITCH = (
                config.get(
                    "Rybka Standalone Configuration. For LIVE and DEMO modes",
                    "RYBKA_EMAIL_SWITCH",
                )
                .strip("\n")
                .strip()
            )
        else:
            self.RYBKA_EMAIL_SWITCH = os.environ.get("RYBKA_EMAIL_SWITCH").strip("\n").strip()
        if not os.environ.get("RYBKA_EMAIL_SENDER_EMAIL"):
            self.RYBKA_EMAIL_SENDER_EMAIL = (
                config.get(
                    "Rybka Standalone Configuration. For LIVE and DEMO modes",
                    "RYBKA_EMAIL_SENDER_EMAIL",
                )
                .strip("\n")
                .strip()
            )
        else:
            self.RYBKA_EMAIL_SENDER_EMAIL = (
                os.environ.get("RYBKA_EMAIL_SENDER_EMAIL").strip("\n").strip()
            )
        if not os.environ.get("RYBKA_EMAIL_RECIPIENT_EMAIL"):
            self.RYBKA_EMAIL_RECIPIENT_EMAIL = (
                config.get(
                    "Rybka Standalone Configuration. For LIVE and DEMO modes",
                    "RYBKA_EMAIL_RECIPIENT_EMAIL",
                )
                .strip("\n")
                .strip()
            )
        else:
            self.RYBKA_EMAIL_RECIPIENT_EMAIL = (
                os.environ.get("RYBKA_EMAIL_RECIPIENT_EMAIL").strip("\n").strip()
            )
        if not os.environ.get("RYBKA_EMAIL_RECIPIENT_NAME"):
            self.RYBKA_EMAIL_RECIPIENT_NAME = (
                config.get(
                    "Rybka Standalone Configuration. For LIVE and DEMO modes",
                    "RYBKA_EMAIL_RECIPIENT_NAME",
                )
                .strip("\n")
                .strip()
            )
        else:
            self.RYBKA_EMAIL_RECIPIENT_NAME = (
                os.environ.get("RYBKA_EMAIL_RECIPIENT_NAME").strip("\n").strip()
            )

        # Telegram related config.
        if not os.environ.get("RYBKA_TELEGRAM_SWITCH"):
            self.RYBKA_TELEGRAM_SWITCH = (
                config.get(
                    "Rybka Standalone Configuration. For LIVE and DEMO modes",
                    "RYBKA_TELEGRAM_SWITCH",
                )
                .strip("\n")
                .strip()
            )
        else:
            self.RYBKA_TELEGRAM_SWITCH = os.environ.get("RYBKA_TELEGRAM_SWITCH").strip("\n").strip()

        if not os.environ.get("RYBKA_ALL_LOG_TLG_SWITCH"):
            self.RYBKA_ALL_LOG_TLG_SWITCH = (
                config.get(
                    "Rybka Standalone Configuration. For LIVE and DEMO modes",
                    "RYBKA_ALL_LOG_TLG_SWITCH",
                )
                .strip("\n")
                .strip()
            )
        else:
            self.RYBKA_ALL_LOG_TLG_SWITCH = (
                os.environ.get("RYBKA_ALL_LOG_TLG_SWITCH").strip("\n").strip()
            )

        # Binance related config.
        self.TRADE_SYMBOL = (
            config.get(
                "Rybka Binance Configuration. For LIVE and DEMO modes",
                "RYBKA_TRADE_SYMBOL",
            )
            .strip("\n")
            .strip()
            .upper()
        )

        def validate_and_split_trading_pair(trading_pair):
            if trading_pair.endswith("USDT"):
                self.CRYPTOCOIN_SYMBOL = trading_pair[:-4]
                self.STABLECOIN_SYMBOL = "USDT"
            else:
                print(
                    colored(
                        "🔴 [FATAL] Invalid trading pair. Trading pair must end with [USDT]!",
                        "red",
                    )
                )
                exit(1)

        validate_and_split_trading_pair(self.TRADE_SYMBOL)


        self.RSI_PERIOD = int(
            config.get(
                "Rybka Binance Configuration. For LIVE and DEMO modes",
                "RYBKA_RSI_PERIOD",
            )
        )
        self.RSI_FOR_BUY = int(
            config.get(
                "Rybka Binance Configuration. For LIVE and DEMO modes",
                "RYBKA_RSI_FOR_BUY",
            )
        )
        self.RSI_FOR_SELL = int(
            config.get(
                "Rybka Binance Configuration. For LIVE and DEMO modes",
                "RYBKA_RSI_FOR_SELL",
            )
        )
        self.TRADE_QUANTITY = float(
            config.get(
                "Rybka Binance Configuration. For LIVE and DEMO modes",
                "RYBKA_TRADE_QUANTITY",
            )
        )
        self.MIN_PROFIT = float(
            config.get(
                "Rybka Binance Configuration. For LIVE and DEMO modes",
                "RYBKA_MIN_PROFIT",
            )
        )
        try:
            self.STABLECOIN_SAFETY_NET = float(
                config.get(
                    "Rybka Binance Configuration. For LIVE and DEMO modes",
                    "RYBKA_STABLECOIN_SAFETY_NET",
                )
            )
        except:
            self.STABLECOIN_SAFETY_NET = None

        # DEMO mode related config.
        try:
            self.RYBKA_DEMO_BALANCE_STABLECOIN = float(
                config.get(
                    "Rybka Standalone Configuration. Only for DEMO mode",
                    "RYBKA_DEMO_BALANCE_STABLECOIN",
                )
            )
        except:
            self.RYBKA_DEMO_BALANCE_STABLECOIN = 1500
        try:
            self.RYBKA_DEMO_BALANCE_CRYPTOCOIN = float(
                config.get(
                    "Rybka Standalone Configuration. Only for DEMO mode",
                    "RYBKA_DEMO_BALANCE_CRYPTOCOIN",
                )
            )
        except:
            self.RYBKA_DEMO_BALANCE_CRYPTOCOIN = 100
        try:
            self.RYBKA_DEMO_BALANCE_BNB = float(
                config.get(
                    "Rybka Standalone Configuration. Only for DEMO mode",
                    "RYBKA_DEMO_BALANCE_BNB",
                )
            )
        except:
            self.RYBKA_DEMO_BALANCE_BNB = 0.2
        with open("project_version", "r", encoding="utf8") as f:
            self.__version__ = f.read().strip("\n").strip()

        # Dev-only related config.
        if not os.environ.get("RYBKA_BALANCES_AUX"):
            self.RYBKA_BALANCES_AUX = (
                config.get(
                    "DEVELOPER-ONLY Configuration. Only for LIVE mode",
                    "RYBKA_BALANCES_AUX",
                )
                .strip("\n")
                .strip()
            )
        else:
            self.RYBKA_BALANCES_AUX = os.environ.get("RYBKA_BALANCES_AUX").strip("\n").strip()


config = configparser.ConfigParser()
bootstrap = ""


def variables_reinitialization():
    config.read(os.path.join(os.environ.get("CURRENT_DIR_PATH"), "config.ini"))

    global bootstrap
    bootstrap = Rybka_py_env_bootstrap()

    from custom_modules.logging.logging import log

    log.VERBOSE("Vars REINITIALIZED!")


variables_reinitialization()
