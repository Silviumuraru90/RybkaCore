#!/usr/bin/env python3

# built-in and third-party libs
from datetime import datetime
from contextlib import contextmanager
import sys, os

# custom libs
from ..cfg import bootstrap



###############################################
#####   LOGGING TYPES && COLORED OUTPUT  ######
###############################################

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CRED = '\33[31m'


class RybkaLogging:

    @staticmethod
    def logging_time():
        return(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] > ')

    def all_errors_file_update(self, error_message):
        try:
            with open(f"{bootstrap.RYBKA_MODE}/errors_thrown", 'a', encoding="utf8") as f:
                f.write(f"\nError thrown was: \n{error_message}\n")
        except Exception as e:
            print(f"{bcolors.WARNING}⚠️  WARN {self.logging_time()} > Could not update 'errors_thrown' file due to error: \n{e}{bcolors.ENDC}")

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
        with open(os.devnull, "w") as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            try:
                yield
            finally:
                sys.stdout = old_stdout

    def INFO(self, message):
        print(f"{bcolors.OKGREEN}INFO {self.logging_time()}    > {message}{bcolors.ENDC}")

    def INFO_BOLD(self, message):
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}INFO {self.logging_time()}    > {message}{bcolors.ENDC}")

    def INFO_UNDERLINE(self, message):
        print(f"{bcolors.OKGREEN}INFO {self.logging_time()}    > {bcolors.UNDERLINE}{message}{bcolors.ENDC}")

    def INFO_BOLD_UNDERLINE(self, message):
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}INFO {self.logging_time()}    > {bcolors.UNDERLINE}{message}{bcolors.ENDC}")

    def DEBUG(self, message):
        if bootstrap.DEBUG_LVL == 1 or bootstrap.DEBUG_LVL == 2 or bootstrap.DEBUG_LVL == 3:
            print(f"{bcolors.OKCYAN}🛠️  DEBUG {self.logging_time()}             > {message}{bcolors.ENDC}")

    def VERBOSE(self, message):
        if bootstrap.DEBUG_LVL == 2 or bootstrap.DEBUG_LVL == 3:
            print(f"{bcolors.OKBLUE}🛠️ 🛠️  VERBOSE {self.logging_time()}         > {message}{bcolors.ENDC}")

    def HIGH_VERBOSITY(self, message):
        if bootstrap.DEBUG_LVL == 3:
            print(f"{bcolors.HEADER}🛠️ 🛠️ 🛠️  HIGH_VERBOSITY {self.logging_time()}> {message}{bcolors.ENDC}")

    def WARN(self, message):
        print(f"{bcolors.WARNING}⚠️  WARN {self.logging_time()} > {message}{bcolors.ENDC}")
        self.all_errors_file_update(f"⚠️ WARN {self.logging_time()}     > {message}")

    def FATAL(self, message):
        print(f"{bcolors.CRED}{bcolors.BOLD}❌ FATAL {self.logging_time()}> {message}{bcolors.ENDC}")
        self.all_errors_file_update(f"❌ FATAL (1) {self.logging_time()}> {message}")
        exit(1)

    def FATAL_7(self, message):
        print(f"{bcolors.CRED}{bcolors.BOLD}❌ FATAL {self.logging_time()}> {message}{bcolors.ENDC}")
        self.all_errors_file_update(f"❌ FATAL (7) {self.logging_time()}> {message}")
        exit(7)


log = RybkaLogging()
