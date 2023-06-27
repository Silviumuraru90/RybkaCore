#!/usr/bin/env python3

# built-in and third-party libs
import os
import sys
from contextlib import contextmanager
from datetime import datetime

import colored

from custom_modules.telegram.telegram_passive import telegram

# custom libs
from ..cfg import bootstrap

###############################################
#####   LOGGING TYPES && COLORED OUTPUT  ######
###############################################


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


class RybkaLogging:
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

    #####  Usage  ################################
    #                                            #
    #   print("this can be seen in CLI")         #
    #   with log.suppress_stdout():              #
    #        print("this can't be seen in CLI")  #
    #                                            #
    ##############################################
    @staticmethod
    @contextmanager
    def suppress_stdout():
        with open(os.devnull, "w", encoding="utf8") as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            try:
                yield
            finally:
                sys.stdout = old_stdout

    @staticmethod
    def ORANGE(message):
        print(colored.fg(202) + f"{message}")

    def INFO(self, message):
        print(
            f"{bcolors.DARKGRAY}◻️ [{os.environ.get('RYBKA_MODE')}] [INFO] {self.logging_time()}        > {message}{bcolors.ENDC}"
        )
        if bootstrap.RYBKA_ALL_LOG_TLG_SWITCH.upper() == "TRUE":
            telegram.LOG(message, "INFO")

    def INFO_BOLD(self, message):
        print(
            f"{bcolors.DARKGRAY}{bcolors.BOLD}◻️ [{os.environ.get('RYBKA_MODE')}] [INFO] {self.logging_time()}        > {message}{bcolors.ENDC}"
        )
        if bootstrap.RYBKA_ALL_LOG_TLG_SWITCH.upper() == "TRUE":
            telegram.LOG(message, "INFO")

    def INFO_UNDERLINE(self, message):
        print(
            f"{bcolors.DARKGRAY}◻️ [{os.environ.get('RYBKA_MODE')}] [INFO] {self.logging_time()}        > {bcolors.UNDERLINE}{message}{bcolors.ENDC}"
        )
        if bootstrap.RYBKA_ALL_LOG_TLG_SWITCH.upper() == "TRUE":
            telegram.LOG(message, "INFO")

    def INFO_BOLD_UNDERLINE(self, message):
        print(
            f"{bcolors.DARKGRAY}{bcolors.BOLD}◻️ [{os.environ.get('RYBKA_MODE')}] [INFO] {self.logging_time()}        > {bcolors.UNDERLINE}{message}{bcolors.ENDC}"
        )
        if bootstrap.RYBKA_ALL_LOG_TLG_SWITCH.upper() == "TRUE":
            telegram.LOG(message, "INFO")

    def INFO_SPECIAL(self, message):
        print(
            f"{bcolors.OKGREEN}◻️ [{os.environ.get('RYBKA_MODE')}] [INFO] {self.logging_time()}        > {message}{bcolors.ENDC}"
        )
        if bootstrap.RYBKA_ALL_LOG_TLG_SWITCH.upper() == "TRUE":
            telegram.LOG(message, "INFO")

    def DEBUG(self, message):
        self.refresh_bootstrap_object()
        if bootstrap.DEBUG_LVL == 1 or bootstrap.DEBUG_LVL == 2 or bootstrap.DEBUG_LVL == 3:
            print(
                f"{bcolors.OKCYAN}🛠️  [{os.environ.get('RYBKA_MODE')}] [DEBUG] {self.logging_time()}      > {message}{bcolors.ENDC}"
            )
            if bootstrap.RYBKA_ALL_LOG_TLG_SWITCH.upper() == "TRUE":
                telegram.LOG(message, "DEBUG")

    def VERBOSE(self, message):
        self.refresh_bootstrap_object()
        if bootstrap.DEBUG_LVL == 2 or bootstrap.DEBUG_LVL == 3:
            print(
                f"{bcolors.OKBLUE}🛠️ 🛠️  [{os.environ.get('RYBKA_MODE')}] [VERBOSE] {self.logging_time()}  > {message}{bcolors.ENDC}"
            )
            if bootstrap.RYBKA_ALL_LOG_TLG_SWITCH.upper() == "TRUE":
                telegram.LOG(message, "VERBOSE")

    def HIGH_VERBOSITY(self, message):
        self.refresh_bootstrap_object()
        if bootstrap.DEBUG_LVL == 3:
            print(
                f"{bcolors.HEADER}🛠️ 🛠️ 🛠️  [{os.environ.get('RYBKA_MODE')}] [HV] {self.logging_time()}     > {message}{bcolors.ENDC}"
            )
            if bootstrap.RYBKA_ALL_LOG_TLG_SWITCH.upper() == "TRUE":
                telegram.LOG(message, "HIGH_VERBOSITY")

    def WARN(self, message):
        print(
            f"{bcolors.WARNING}⚠️  [{os.environ.get('RYBKA_MODE')}] [WARN] {self.logging_time()}       > {message}{bcolors.ENDC}"
        )
        self.all_errors_file_update(
            f"⚠️  [{os.environ.get('RYBKA_MODE')}] [WARN] {self.logging_time()}       > {message}"
        )
        if bootstrap.RYBKA_ALL_LOG_TLG_SWITCH.upper() == "TRUE":
            telegram.LOG(message, "WARN")

    def FATAL(self, message):
        print(
            f"{bcolors.CRED}{bcolors.BOLD}❌ [{os.environ.get('RYBKA_MODE')}] [FATAL] {self.logging_time()}      > {message}{bcolors.ENDC}"
        )
        self.all_errors_file_update(
            f"❌ [{os.environ.get('RYBKA_MODE')}] [FATAL (1)] {self.logging_time()}      > {message}"
        )
        telegram.LOG(message, "FATAL")
        sys.exit(1)

    def FATAL_7(self, message):
        print(
            f"{bcolors.CRED}{bcolors.BOLD}❌ [{os.environ.get('RYBKA_MODE')}] [FATAL (7)] {self.logging_time()}  > {message}{bcolors.ENDC}"
        )
        self.all_errors_file_update(
            f"❌ [{os.environ.get('RYBKA_MODE')}] [FATAL (7)] {self.logging_time()}  > {message}"
        )
        if "ⓇⓎⒷⓀⒶⒸⓄⓇⒺ" in message:
            telegram.LOG(message)
        else:
            telegram.LOG(message, "FATAL")
        sys.exit(7)

    @staticmethod
    def refresh_bootstrap_object():
        global bootstrap
        from ..cfg import bootstrap


log = RybkaLogging()
