#!/usr/bin/env python3

# built-in and third-party libs
import os
import sys
from datetime import datetime

import requests
import telepot

# custom libs
from ..cfg import bootstrap


# re-stating bcolors and logging methods is needed to avoid circular imports
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    CRED = "\33[31m"
    DARKGRAY = "\033[90m"
    PURPLE = "\033[95m"


class TelegramEngine:
    def __init__(self):
        self.apiKey = bootstrap.TELE_KEY
        self.chatId = bootstrap.TELE_CHAT_ID
        self.text_url = (
            f"https://api.telegram.org/bot{self.apiKey}/sendMessage?chat_id={self.chatId}"
        )
        self.photo_url = f"https://api.telegram.org/bot{self.apiKey}/sendPhoto"

    @staticmethod
    def refresh_bootstrap_object():
        global bootstrap
        from ..cfg import bootstrap

    @staticmethod
    def logging_time():
        return f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] > '

    def all_errors_file_update(self, error_message):
        try:
            with open(f"{os.environ.get('RYBKA_MODE')}/errors_thrown", "a", encoding="utf8") as f:
                f.write(f"\nError / warn thrown was: \n{error_message}\n")
        except Exception as e:
            print(
                f"{bcolors.WARNING}⚠️  [{os.environ.get('RYBKA_MODE')}] [WARN] {self.logging_time()} > Could not update 'errors_thrown' file due to error: \n{e}{bcolors.ENDC}"
            )

    def WARN(self, message):
        print(
            f"{bcolors.WARNING}⚠️  [{os.environ.get('RYBKA_MODE')}] [WARN] {self.logging_time()}       > {message}{bcolors.ENDC}"
        )
        self.all_errors_file_update(
            f"⚠️  [{os.environ.get('RYBKA_MODE')}] [WARN] {self.logging_time()}       > {message}"
        )

    def FATAL(self, message):
        print(
            f"{bcolors.CRED}{bcolors.BOLD}❌ FATAL {self.logging_time()}      > {message}{bcolors.ENDC}"
        )
        self.all_errors_file_update(f"❌ FATAL (1) {self.logging_time()}      > {message}")
        sys.exit(1)

    def HIGH_VERBOSITY(self, message):
        self.refresh_bootstrap_object()
        if bootstrap.DEBUG_LVL == 3:
            print(
                f"{bcolors.HEADER}🛠️ 🛠️ 🛠️  HV {self.logging_time()}     > {message}{bcolors.ENDC}"
            )

    def LOG_EXCEPTION(self, e):
        with open(
            f"{os.environ.get('CURRENT_EXPORT_DIR')}/{os.environ.get('TRADE_SYMBOL')}_DEBUG",
            "a",
            encoding="utf8",
        ) as f:
            f.write(
                f"{self.logging_time()} Make sure the [RYBKA_TELEGRAM_API_KEY] and [RYBKA_TELEGRAM_CHAT_ID] have valid values or that internet is available.\nNotification could NOT be sent due to an error:\n{e}"
            )
        self.all_errors_file_update(
            f"⚠️  [{os.environ.get('RYBKA_MODE')}] [WARN] {self.logging_time()}       > Make sure the [RYBKA_TELEGRAM_API_KEY] and [RYBKA_TELEGRAM_CHAT_ID] have valid values or that internet is available.\nNotification could NOT be sent due to an error:\n{e}"
        )
        self.FATAL(
            f"Make sure the [RYBKA_TELEGRAM_API_KEY] and [RYBKA_TELEGRAM_CHAT_ID] have valid values or that internet is available.\nNotification could NOT be sent due to an error:\n{e}"
        )

    def LOG(self, message, mode="default"):
        self.refresh_bootstrap_object()
        if bootstrap.RYBKA_TELEGRAM_SWITCH.upper() == "TRUE":
            try:
                if mode == "default":
                    bot_message = f"{message}"
                if mode.upper() == "INFO":
                    bot_message = f"⬜️ `INFO ☞ {message}`"
                elif mode.upper() == "DEBUG":
                    bot_message = f"🛠️  `DEBUG ☞ {message}`"
                elif mode.upper() == "VERBOSE":
                    bot_message = f"🛠️ 🛠️  `VERBOSE ☞ {message}`"
                elif mode.upper() == "HIGH_VERBOSITY":
                    bot_message = f"🛠️ 🛠️ 🛠️  `HIGH_VERBOSITY ☞ {message}`"
                elif mode.upper() == "WARN":
                    bot_message = f"⚠️  `WARN ☞ {message}`"
                elif mode.upper() == "FATAL":
                    bot_message = f"🛑 `FATAL ☞ {message}`"
                response = requests.get(f"{self.text_url}&parse_mode=Markdown&text={bot_message}")
                self.HIGH_VERBOSITY(response.json())
            except Exception as e:
                self.WARN(f"[mode={mode}] - [{message}] message could not be sent via TELEGRAM!")
                self.LOG_EXCEPTION(e)

    def local_pic(self, image):
        try:
            bot = telepot.Bot(self.apiKey)
            bot.sendPhoto(
                self.chatId,
                photo=open(f"custom_modules/telegram/data/pics/{image}.png", "rb"),
            )
        except Exception as e:
            self.WARN("Local image could not be sent via TELEGRAM!")
            self.LOG_EXCEPTION(e)

    def web_pic(self, image_url):
        try:
            response = requests.post(
                self.photo_url, json={"chat_id": self.chatId, "photo": f"{image_url}"}
            )
            self.HIGH_VERBOSITY(response.json())
        except Exception as e:
            self.WARN("Web image could not be sent via TELEGRAM!")
            self.LOG_EXCEPTION(e)


telegram = TelegramEngine()
