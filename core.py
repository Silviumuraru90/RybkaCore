#!/usr/bin/env python3

# Built-in and Third-Party Libs
import ctypes
import fileinput
import json
import logging
import math
import os
import platform
import random
import re
import shutil
import smtplib
import socket
import string as string_str
import subprocess
import sys
import time
import traceback
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import exists
from string import Template
from sys import platform

import click
import numpy
import psutil
import talib
import unicorn_binance_websocket_api
import websocket
from binance.client import Client
from binance.enums import *

logging.getLogger("unicorn_binance_websocket_api").disabled = True


def current_dir_path_export():
    current_dir_path = os.path.dirname(os.path.abspath(__file__))
    os.environ["CURRENT_DIR_PATH"] = current_dir_path


current_dir_path_export()

# Custom Libs
from custom_modules.cfg import bootstrap, variables_reinitialization
from custom_modules.logging.logging import bcolors, log
from custom_modules.telegram.telegram_passive import telegram

###############################################
########      UNIQUE ID FUNCTION      #########
###############################################


def id_generator(size=10, chars=string_str.ascii_uppercase + string_str.digits):
    return "".join(random.choice(chars) for elem in range(size))


###############################################
#########      ACCOUNT FUNCTIONS      #########
###############################################


def user_initial_config():
    global client
    try:
        client = Client(bootstrap.RYBKA_BIN_KEY, bootstrap.RYBKA_BIN_SECRET)
        log.INFO_BOLD(f" ✅ Client initial config  -  {bcolors.PURPLE}DONE")
    except Exception as e:
        traceback.print_exc()
        log.FATAL_7(
            f"Client initial config  -  FAILED\nError encountered at setting user config. via API KEY and API SECRET. Please check error below:\n{e}"
        )


def binance_system_status():
    global client
    binance_status = client.get_system_status()
    if binance_status["status"] == 0:
        log.INFO_BOLD(
            f" ✅ Binance servers status -  {bcolors.PURPLE}{binance_status['msg'].upper()}"
        )
    else:
        log.FATAL_7(f"Binance servers status -  {binance_status['msg'].upper()}")


def binance_account_status():
    global client
    acc_status = client.get_account_status()
    if acc_status["data"].upper() == "NORMAL":
        log.INFO_BOLD(f" ✅ Binance acc. status    -  {bcolors.PURPLE}{acc_status['data'].upper()}")
    else:
        log.FATAL_7(f"Binance acc. status    -  {acc_status['data'].upper()}")


def binance_api_account_status():
    global client
    acc_api_status = client.get_account_api_trading_status()
    if acc_api_status["data"]["isLocked"] is False:
        log.INFO_BOLD(
            f" ✅ API acc. locked status -  {bcolors.PURPLE}{str(acc_api_status['data']['isLocked']).upper()}"
        )
    else:
        log.FATAL_7(
            f"API acc. locked status -  {str(acc_api_status['data']['isLocked']).upper()}\nLocked status duration is - {acc_api_status['data']['plannedRecoverTime']}"
        )


def account_balance_update():
    global client
    global balance_usdt
    global balance_egld
    global balance_bnb
    global locked_balance_usdt
    global locked_balance_egld
    global locked_balance_bnb

    balance_aux_usdt = client.get_asset_balance(asset="USDT")
    if float(balance_aux_usdt["free"]) == round(float(balance_aux_usdt["free"]), 4):
        balance_usdt = round(float(balance_aux_usdt["free"]), 4)
    else:
        balance_usdt = round(float(balance_aux_usdt["free"]) + 0.0001, 4)
    locked_balance_usdt = round(float(balance_aux_usdt["locked"]), 4)

    balance_aux_egld = client.get_asset_balance(asset="EGLD")
    if float(balance_aux_egld["free"]) == round(float(balance_aux_egld["free"]), 4):
        balance_egld = round(float(balance_aux_egld["free"]), 4)
    else:
        balance_egld = round(float(balance_aux_egld["free"]) + 0.0001, 4)
    locked_balance_egld = round(float(balance_aux_egld["locked"]), 4)

    balance_aux_bnb = client.get_asset_balance(asset="BNB")
    balance_bnb = round(float(balance_aux_bnb["free"]), 8)
    locked_balance_bnb = round(float(balance_aux_bnb["locked"]), 8)


###############################################
#######   FILE MANIPULATION FUNCTIONS   #######
###############################################


def log_files_creation(direct_call="1"):
    global current_export_dir
    global RYBKA_EMAIL_RECIPIENT_EMAIL, RYBKA_EMAIL_SENDER_EMAIL, RYBKA_EMAIL_RECIPIENT_EMAIL, RYBKA_EMAIL_SENDER_EMAIL
    global RYBKA_TELEGRAM_SWITCH, RYBKA_EMAIL_SWITCH
    global RSI_FOR_SELL, RSI_FOR_BUY, USDT_SAFETY_NET, MIN_PROFIT, TRADE_QUANTITY, DEBUG_LVL

    try:
        if direct_call == "1":
            os.mkdir(current_export_dir)

            with open(
                f"{current_export_dir}/BNB_USDT_historical_prices",
                "w",
                encoding="utf8",
            ) as f:
                f.write(
                    f"Here is a detailed view of the history of candle prices for the [BNB-USDT] currency pair:\n\n"
                )
            with open(
                f"{current_export_dir}/{TRADE_SYMBOL}_historical_prices",
                "w",
                encoding="utf8",
            ) as f:
                f.write(
                    f"Here is a detailed view of the history of candle prices for the [{TRADE_SYMBOL}] currency pair:\n\n"
                )
            with open(
                f"{current_export_dir}/{TRADE_SYMBOL}_order_history",
                "w",
                encoding="utf8",
            ) as f:
                f.write(
                    f"Here is a detailed view of the history of orders done for the [{TRADE_SYMBOL}] currency pair:\n\n"
                )
            with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", "w", encoding="utf8") as f:
                f.write(f"DEBUG logs for the [{TRADE_SYMBOL}] currency pair:\n\n")

        with open(f"{current_export_dir}/{TRADE_SYMBOL}_weights", "w", encoding="utf8") as f:
            f.write(
                f"Here is a detailed view of weights set for the [{TRADE_SYMBOL}] currency pair:\n\n"
            )
            f.write(f"RYBKA_MODE      set to: {RYBKA_MODE:>50}\n")
            if DEBUG_LVL:
                f.write(f"DEBUG_LVL       set to: {DEBUG_LVL:>50}")
            f.write(f"SOCKET          set to: {SOCKET:>50}\n")
            f.write(f"TRADE SYMBOL    set to: {TRADE_SYMBOL:>50}\n")
            f.write(f"TRADE QUANTITY  set to: {str(TRADE_QUANTITY):>50} coins per transaction\n")
            f.write(f"MIN PROFIT      set to: {str(MIN_PROFIT):>50} USDT per transaction\n")
            f.write(f"USDT SAFETY NET set to: {str(USDT_SAFETY_NET):>50} USDT\n")
            f.write(f"RSI PERIOD      set to: {RSI_PERIOD:>50} minutes\n")
            f.write(f"RSI FOR BUY     set to: {RSI_FOR_BUY:>50} threshold\n")
            f.write(f"RSI FOR SELL    set to: {RSI_FOR_SELL:>50} threshold\n")
            f.write(f"EMAIL SWITCH    set to: {str(RYBKA_EMAIL_SWITCH):>50}\n")
            f.write(f"Telegram SWITCH set to: {str(RYBKA_TELEGRAM_SWITCH):>50}\n")
            if RYBKA_EMAIL_SENDER_EMAIL and RYBKA_EMAIL_RECIPIENT_EMAIL:
                f.write(f"SENDER EMAIL    set to: {RYBKA_EMAIL_SENDER_EMAIL:>50}\n")
                f.write(f"RECIPIENT EMAIL set to: {RYBKA_EMAIL_RECIPIENT_EMAIL:>50}\n")

        if direct_call == "1":
            log.INFO_BOLD(f" ✅ Files creation status  -  {bcolors.PURPLE}DONE")
            log.INFO("==============================================")

    except Exception as e:
        traceback.print_exc()
        log.FATAL_7(
            f"Attempt to create local folder [{current_export_dir}] and inner files for output analysis FAILED - with error:\n{e}"
        )


def rybka_mode_folder_creation():
    global RYBKA_MODE
    if os.path.isdir(RYBKA_MODE) is False:
        try:
            os.makedirs(RYBKA_MODE)
        except Exception as e:
            traceback.print_exc()
            log.FATAL_7(
                f"Attempt to create local folder for the mode in which software runs - [{RYBKA_MODE}] - FAILED with error:\n{e}"
            )


def TMP_folder(folder):
    if os.path.isdir(folder) is False:
        try:
            os.makedirs(folder)
        except Exception as e:
            traceback.print_exc()
            log.FATAL_7(f"Attempt to create local folder [{folder}] - FAILED with error:\n{e}")


def ktbr_configuration():
    global ktbr_config
    global RYBKA_MODE
    log.INFO(
        "====================================================================================================================================="
    )
    if exists(f"{RYBKA_MODE}/ktbr"):
        with open(f"{RYBKA_MODE}/ktbr", "r", encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/ktbr").st_size == 0:
                log.INFO_BOLD(
                    f" ✅ [{RYBKA_MODE}/ktbr] file exists, but its content doesn't present the right format, modifying that right now"
                )
                f.write("{}")
            else:
                try:
                    ktbr_config = json.loads(f.read())
                    log.INFO_BOLD(
                        f" ✅ [{RYBKA_MODE}/ktbr] file contains the following past transactions:\n"
                    )
                    for k, v in ktbr_config.items():
                        log.INFO(
                            f" 💳 Transaction [{k}]  ---  [{bcolors.OKGREEN}{bcolors.BOLD}{v[0]}{bcolors.ENDC}{bcolors.DARKGRAY}] \t EGLD bought at price of [{bcolors.OKGREEN}{bcolors.BOLD}{v[1]}{bcolors.ENDC}{bcolors.DARKGRAY}] \t USDT per EGLD{bcolors.ENDC}"
                        )
                except Exception as e:
                    traceback.print_exc()
                    log.FATAL_7(
                        f"[{RYBKA_MODE}/ktbr] file contains wrong formatted content!\nFailing with error:\n{e}"
                    )
    else:
        try:
            with open(f"{RYBKA_MODE}/ktbr", "w", encoding="utf8") as f:
                f.write("{}")
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/ktbr] file created!")
        except Exception as e:
            traceback.print_exc()
            log.FATAL_7(f"[{RYBKA_MODE}/ktbr] file could NOT be created!\nFailing with error:\n{e}")
    log.INFO(
        "====================================================================================================================================="
    )


def profit_file():
    global total_usdt_profit
    global RYBKA_MODE
    log.VERBOSE(
        "====================================================================================================================================="
    )
    if exists(f"{RYBKA_MODE}/usdt_profit"):
        with open(f"{RYBKA_MODE}/usdt_profit", "r", encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/usdt_profit").st_size == 0:
                log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/usdt_profit] file exists and is empty")
            else:
                try:
                    total_usdt_profit = round(float(f.read()), 4)
                    log.VERBOSE(
                        f" ✅ [{RYBKA_MODE}/usdt_profit] file contains the following already done profit: [{bcolors.PURPLE}{total_usdt_profit}{bcolors.DARKGRAY}] USDT"
                    )
                except Exception as e:
                    traceback.print_exc()
                    log.FATAL_7(
                        f"[{RYBKA_MODE}/usdt_profit] file contains wrong formatted content!\nFailing with error:\n{e}"
                    )
    else:
        try:
            open(f"{RYBKA_MODE}/usdt_profit", "w", encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/usdt_profit] file created!")
        except Exception as e:
            traceback.print_exc()
            log.FATAL_7(
                f"[{RYBKA_MODE}/usdt_profit] file could NOT be created!\nFailing with error:\n{e}"
            )
    log.VERBOSE(
        "====================================================================================================================================="
    )


def nr_of_trades_file():
    global nr_of_trades
    global RYBKA_MODE
    log.INFO(
        "====================================================================================================================================="
    )
    if exists(f"{RYBKA_MODE}/number_of_buy_trades"):
        with open(f"{RYBKA_MODE}/number_of_buy_trades", "r", encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/number_of_buy_trades").st_size == 0:
                log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/number_of_buy_trades] file exists and is empty")
            else:
                try:
                    nr_of_trades = int(f.read())
                    log.INFO_BOLD(
                        f" ✅ [{RYBKA_MODE}/number_of_buy_trades] file shows historical nr. of buy trades raising to: [{bcolors.PURPLE}{nr_of_trades}{bcolors.DARKGRAY}]"
                    )
                except Exception as e:
                    traceback.print_exc()
                    log.FATAL_7(
                        f"[{RYBKA_MODE}/number_of_buy_trades] file contains wrong formatted content!\nFailing with error:\n{e}"
                    )
    else:
        try:
            open(f"{RYBKA_MODE}/number_of_buy_trades", "w", encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/number_of_buy_trades] file created!")
        except Exception as e:
            traceback.print_exc()
            log.FATAL_7(
                f"[{RYBKA_MODE}/number_of_buy_trades] file could NOT be created!\nFailing with error:\n{e}"
            )
    log.INFO(
        "====================================================================================================================================="
    )


def full_order_history_file():
    global RYBKA_MODE
    log.INFO(
        "====================================================================================================================================="
    )
    if exists(f"{RYBKA_MODE}/full_order_history"):
        with open(f"{RYBKA_MODE}/full_order_history", "r", encoding="utf8"):
            if os.stat(f"{RYBKA_MODE}/full_order_history").st_size == 0:
                log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/full_order_history] file exists and is empty")
            else:
                log.INFO_BOLD(
                    f" ✅ [{RYBKA_MODE}/full_order_history] file exists and contains past information!"
                )
    else:
        try:
            open(f"{RYBKA_MODE}/full_order_history", "w", encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/full_order_history] file created!")
        except Exception as e:
            traceback.print_exc()
            log.FATAL_7(
                f"[{RYBKA_MODE}/full_order_history] file could NOT be created!\nFailing with error:\n{e}"
            )
    log.INFO(
        "====================================================================================================================================="
    )


def real_time_balances():
    global RYBKA_MODE
    log.INFO(
        "====================================================================================================================================="
    )
    if exists(f"{RYBKA_MODE}/real_time_balances"):
        log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/real_time_balances] file already exists!")
    else:
        try:
            open(f"{RYBKA_MODE}/real_time_balances", "w", encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/real_time_balances] file created!")
        except Exception as e:
            traceback.print_exc()
            log.FATAL_7(
                f"[{RYBKA_MODE}/real_time_balances] file could NOT be created!\nFailing with error:\n{e}"
            )
    log.INFO(
        "====================================================================================================================================="
    )


def ktbr_integrity():
    global balance_egld
    global RYBKA_MODE
    ktbr_config_check = {}
    sum_of_ktbr_cryptocurrency = 0

    with open(f"{RYBKA_MODE}/ktbr", "r", encoding="utf8") as f:
        ktbr_config_check = json.loads(f.read())

        for v in ktbr_config_check.values():
            sum_of_ktbr_cryptocurrency += v[0]

        log.VERBOSE(f"ktbr_config_check is {ktbr_config_check}")
        log.VERBOSE(f"sum_of_ktbr_cryptocurrency rounded is {round(sum_of_ktbr_cryptocurrency, 4)}")
        log.VERBOSE(f"ktbr_integrity()'s egld balance is {balance_egld}")

        if round(sum_of_ktbr_cryptocurrency, 4) <= balance_egld:
            log.INFO_BOLD(
                f" ✅ KTBR integrity status  -  {bcolors.PURPLE}VALID{bcolors.DARKGRAY}. Amount of EGLD bought and tracked: [{bcolors.OKGREEN}{round(sum_of_ktbr_cryptocurrency, 4)}{bcolors.DARKGRAY}]\n"
            )
        else:
            log.FATAL_7(
                f"KTBR integrity status  -  INVALID\nThis means that the amount of EGLD you have in cloud [{balance_egld}] is actually less now, than what you retain in the 'ktbr' file [{round(sum_of_ktbr_cryptocurrency, 4)}]. Probably you've spent a part of it in the meantime."
            )


def all_errors_file():
    global RYBKA_MODE
    log.INFO("==============================================")
    if exists(f"{RYBKA_MODE}/errors_thrown"):
        log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/errors_thrown] file already exists!")
    else:
        try:
            open(f"{RYBKA_MODE}/errors_thrown", "w", encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/errors_thrown] file created!")
        except Exception as e:
            traceback.print_exc()
            log.FATAL_7(
                f"[{RYBKA_MODE}/errors_thrown] file could NOT be created!\nFailing with error:\n{e}"
            )
    log.INFO("==============================================")


def create_telegram_and_rybka_tmp_files_if_not_created():
    if not exists("TEMP/pid_rybkaTmp") or (
        exists("TEMP/pid_rybkaTmp") and os.stat("TEMP/pid_rybkaTmp").st_size == 0
    ):
        with open("TEMP/pid_rybkaTmp", "w", encoding="utf8") as f:
            f.write(str("99999999"))
    if not exists("TEMP/core_runsTmp") or (
        exists("TEMP/core_runsTmp") and os.stat("TEMP/core_runsTmp").st_size == 0
    ):
        with open("TEMP/core_runsTmp", "w", encoding="utf8") as g:
            g.write(str("99999999"))
    if not exists("TEMP/telegram_pidTmp") or (
        exists("TEMP/telegram_pidTmp") and os.stat("TEMP/telegram_pidTmp").st_size == 0
    ):
        with open("TEMP/telegram_pidTmp", "w", encoding="utf8") as h:
            h.write(str("99999999"))


###############################################
##############   AUX FUNCTIONS   ##############
###############################################


def back_up():
    global RYBKA_MODE

    back_up_dir = f"BACK_UPS_FOR_{RYBKA_MODE}"
    if os.path.isdir(back_up_dir) is False:
        os.makedirs(back_up_dir)

    shutil.copyfile(f"{RYBKA_MODE}/ktbr", f"{back_up_dir}/ktbr")


def software_config_params():
    global RYBKA_EMAIL_RECIPIENT_EMAIL, RYBKA_EMAIL_SENDER_EMAIL, RYBKA_EMAIL_SENDER_EMAIL, RYBKA_TELEGRAM_SWITCH
    global RYBKA_EMAIL_SWITCH, RSI_FOR_SELL, RSI_FOR_BUY, MIN_PROFIT, USDT_SAFETY_NET, TRADE_QUANTITY, DEBUG_LVL
    global TRADE_QUANTITY
    print("\n\n")
    if RYBKA_MODE.upper() == "DEMO":
        log.PURPLE(
            "      ___           ___           ___           ___           ___           ___           ___           ___           ___     "
        )
        log.PURPLE(
            "     /\  \         |\__\         /\  \         /\__\         /\  \         /\  \         /\  \         /\  \         /\  \    "
        )
        log.PURPLE(
            "    /::\  \        |:|  |       /::\  \       /:/  /        /::\  \       /::\  \       /::\  \       /::\  \       /::\  \   "
        )
        log.PURPLE(
            "   /:/\:\  \       |:|  |      /:/\:\  \     /:/__/        /:/\:\  \     /:/\:\  \     /:/\:\  \     /:/\:\  \     /:/\:\  \  "
        )
        log.PURPLE(
            "  /::\~\:\  \      |:|__|__   /::\~\:\__\   /::\__\____   /::\~\:\  \   /:/  \:\  \   /:/  \:\  \   /::\~\:\  \   /::\~\:\  \ "
        )
        log.PURPLE(
            " /:/\:\ \:\__\     /::::\__\ /:/\:\ \:|__| /:/\:::::\__\ /:/\:\ \:\__\ /:/__/ \:\__\ /:/__/ \:\__\ /:/\:\ \:\__\ /:/\:\ \:\__\\"
        )
        log.PURPLE(
            " \/_|::\/:/  /    /:/~~/~    \:\~\:\/:/  / \/_|:|~~|~    \/__\:\/:/  / \:\  \  \/__/ \:\  \ /:/  / \/_|::\/:/  / \:\~\:\ \/__/"
        )
        log.PURPLE(
            "    |:|::/  /    /:/  /       \:\ \::/  /     |:|  |          \::/  /   \:\  \        \:\  /:/  /     |:|::/  /   \:\ \:\__\  "
        )
        log.PURPLE(
            "    |:|\/__/     \/__/         \:\/:/  /      |:|  |          /:/  /     \:\  \        \:\/:/  /      |:|\/__/     \:\ \/__/  "
        )
        log.PURPLE(
            "    |:|  |                      \::/__/       |:|  |         /:/  /       \:\__\        \::/  /       |:|  |        \:\__\    "
        )
        log.PURPLE(
            "     \|__|                       ~~            \|__|         \/__/         \/__/         \/__/         \|__|         \/__/    \n"
        )

        time.sleep(2)

        log.BLUE(
            "                          ██████╗ ███████╗███╗   ███╗ ██████╗     ███╗   ███╗ ██████╗ ██████╗ ███████╗ "
        )
        log.BLUE(
            "                          ██╔══██╗██╔════╝████╗ ████║██╔═══██╗    ████╗ ████║██╔═══██╗██╔══██╗██╔════╝ "
        )
        log.BLUE(
            "                          ██║  ██║█████╗  ██╔████╔██║██║   ██║    ██╔████╔██║██║   ██║██║  ██║█████╗   "
        )
        log.BLUE(
            "                          ██║  ██║██╔══╝  ██║╚██╔╝██║██║   ██║    ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝   "
        )
        log.BLUE(
            "                          ██████╔╝███████╗██║ ╚═╝ ██║╚██████╔╝    ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗ "
        )
        log.BLUE(
            "                          ╚═════╝ ╚══════╝╚═╝     ╚═╝ ╚═════╝     ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝ \n\n"
        )

    elif RYBKA_MODE.upper() == "LIVE":
        log.CYAN(
            "      ___           ___           ___           ___           ___           ___           ___           ___           ___     "
        )
        log.CYAN(
            "     /\  \         |\__\         /\  \         /\__\         /\  \         /\  \         /\  \         /\  \         /\  \    "
        )
        log.CYAN(
            "    /::\  \        |:|  |       /::\  \       /:/  /        /::\  \       /::\  \       /::\  \       /::\  \       /::\  \   "
        )
        log.CYAN(
            "   /:/\:\  \       |:|  |      /:/\:\  \     /:/__/        /:/\:\  \     /:/\:\  \     /:/\:\  \     /:/\:\  \     /:/\:\  \  "
        )
        log.CYAN(
            "  /::\~\:\  \      |:|__|__   /::\~\:\__\   /::\__\____   /::\~\:\  \   /:/  \:\  \   /:/  \:\  \   /::\~\:\  \   /::\~\:\  \ "
        )
        log.CYAN(
            " /:/\:\ \:\__\     /::::\__\ /:/\:\ \:|__| /:/\:::::\__\ /:/\:\ \:\__\ /:/__/ \:\__\ /:/__/ \:\__\ /:/\:\ \:\__\ /:/\:\ \:\__\\"
        )
        log.CYAN(
            " \/_|::\/:/  /    /:/~~/~    \:\~\:\/:/  / \/_|:|~~|~    \/__\:\/:/  / \:\  \  \/__/ \:\  \ /:/  / \/_|::\/:/  / \:\~\:\ \/__/"
        )
        log.CYAN(
            "    |:|::/  /    /:/  /       \:\ \::/  /     |:|  |          \::/  /   \:\  \        \:\  /:/  /     |:|::/  /   \:\ \:\__\  "
        )
        log.CYAN(
            "    |:|\/__/     \/__/         \:\/:/  /      |:|  |          /:/  /     \:\  \        \:\/:/  /      |:|\/__/     \:\ \/__/  "
        )
        log.CYAN(
            "    |:|  |                      \::/__/       |:|  |         /:/  /       \:\__\        \::/  /       |:|  |        \:\__\    "
        )
        log.CYAN(
            "     \|__|                       ~~            \|__|         \/__/         \/__/         \/__/         \|__|         \/__/    \n"
        )

        time.sleep(2)

        log.GREEN(
            "                              ██╗     ██╗██╗   ██╗███████╗    ███╗   ███╗ ██████╗ ██████╗ ███████╗ "
        )
        log.GREEN(
            "                              ██║     ██║██║   ██║██╔════╝    ████╗ ████║██╔═══██╗██╔══██╗██╔════╝ "
        )
        log.GREEN(
            "                              ██║     ██║██║   ██║█████╗      ██╔████╔██║██║   ██║██║  ██║█████╗   "
        )
        log.GREEN(
            "                              ██║     ██║╚██╗ ██╔╝██╔══╝      ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝   "
        )
        log.GREEN(
            "                              ███████╗██║ ╚████╔╝ ███████╗    ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗ "
        )
        log.GREEN(
            "                              ╚══════╝╚═╝  ╚═══╝  ╚══════╝    ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝ \n\n"
        )

    time.sleep(3)
    log.INFO("RybkaCore software started with the following parameters:\n")
    log.INFO_BOLD(f" 🔘 RYBKA_MODE      set to: {bcolors.PURPLE}{RYBKA_MODE:>50}")
    if DEBUG_LVL:
        log.INFO_BOLD(f"{bcolors.OKCYAN} 🔘 DEBUG_LVL       set to: {DEBUG_LVL:>50}{bcolors.ENDC}")
    log.INFO_BOLD(f" 🔘 SOCKET          set to: {bcolors.PURPLE}{SOCKET:>50}")
    log.INFO_BOLD(f" 🔘 TRADE SYMBOL    set to: {bcolors.PURPLE}{TRADE_SYMBOL:>50}")
    log.INFO_BOLD(
        f" 🔘 TRADE QUANTITY  set to: {bcolors.PURPLE}{str(TRADE_QUANTITY):>50}{bcolors.DARKGRAY} coins per transaction"
    )
    log.INFO_BOLD(
        f" 🔘 MIN PROFIT      set to: {bcolors.PURPLE}{str(MIN_PROFIT):>50}{bcolors.DARKGRAY} USDT per transaction"
    )
    log.INFO_BOLD(
        f" 🔘 USDT SAFETY NET set to: {bcolors.PURPLE}{str(USDT_SAFETY_NET):>50}{bcolors.DARKGRAY} USDT"
    )
    log.INFO_BOLD(
        f" 🔘 RSI PERIOD      set to: {bcolors.PURPLE}{RSI_PERIOD:>50}{bcolors.DARKGRAY} minutes"
    )
    log.INFO_BOLD(
        f" 🔘 RSI FOR BUY     set to: {bcolors.PURPLE}{RSI_FOR_BUY:>50}{bcolors.DARKGRAY} threshold"
    )
    log.INFO_BOLD(
        f" 🔘 RSI FOR SELL    set to: {bcolors.PURPLE}{RSI_FOR_SELL:>50}{bcolors.DARKGRAY} threshold"
    )
    log.INFO_BOLD(f" 🔘 EMAIL SWITCH    set to: {bcolors.PURPLE}{str(RYBKA_EMAIL_SWITCH):>50}")
    log.INFO_BOLD(f" 🔘 Telegram SWITCH set to: {bcolors.PURPLE}{str(RYBKA_TELEGRAM_SWITCH):>50}")
    if RYBKA_EMAIL_SENDER_EMAIL and RYBKA_EMAIL_RECIPIENT_EMAIL:
        log.INFO_BOLD(f" 🔘 SENDER EMAIL    set to: {bcolors.PURPLE}{RYBKA_EMAIL_SENDER_EMAIL:>50}")
        log.INFO_BOLD(
            f" 🔘 RECIPIENT EMAIL set to: {bcolors.PURPLE}{RYBKA_EMAIL_RECIPIENT_EMAIL:>50}"
        )
    log.INFO(" ")
    log.INFO(" ")
    log.INFO(" ")
    log.INFO_BOLD(f" ✅ Initial params config  -  {bcolors.PURPLE}DONE")


def disclaimer():
    time.sleep(1)
    print("\n\n\n\t\t\t\t\t  =====  DISCLAIMER!  =====  \n\n\n\n\n")
    time.sleep(2)
    print("\t\t  FOR AS LONG AS YOU INTEND TO USE THIS BOT (even when it does NOT run): \n")
    time.sleep(5)
    print(
        f"\t  ❌ DO NOT SET MANUALLY ANY OTHER ORDERS WITH THE TRADING PAIR [{TRADE_SYMBOL}]'s PARTS YOU RUN THIS BOT AGAINST! \n"
    )
    time.sleep(7)
    print(
        "\t  ❌ DO NOT CONVERT EGLD INTO ANY OTHER CURRENCY; OR IF YOU DO, DELETE THE TRADING QUANTITY FROM THE KTBR FILE, TO ASSURE THE GOOD FUTURE FUNCTIONING OF THE BOT! STOP THE BOT BEFORE DOING SUCH CHANGES, RESTART IT AFTER! \n\n\n"
    )
    time.sleep(13)
    print("\t\t  YOU ARE ALLOWED TO: \n")
    time.sleep(2)
    print(
        f"\t  ✅ TOP UP WITH EITHER PARTS OF THE TRADING PAIR [{TRADE_SYMBOL}] (EVEN DURING BOT'S RUNNING, BUT ONLY THE NEW USDT ADDED WILL BE CONSIDERED BY BOT TO BUY MORE). \n"
    )
    time.sleep(5)
    print(
        "\t  ✅ SELL ANY QUANTITY OF EGLD YOU HAD PREVIOUSLY BOUGHT, ASIDE FROM THE QUANTITY BOUGHT VIA BOT'S TRANSACTIONS (YOU CAN SELL IT EVEN DURING BOT'S RUNNING). \n\n\n"
    )
    time.sleep(10)
    print("\t\t  NOTES: \n")
    time.sleep(1)
    print(
        "\t  ⚠️  SET ENV VAR [DISCLAIMER] to 'disabled' if you DO NOT want to see this Disclaimer again! \n"
    )
    time.sleep(6)
    print("\t  ⚠️  CAPITAL AT RISK! TRADE ONLY THE CASH YOU ARE COMFORTABLE TO LOSE! \n\n\n")
    time.sleep(5)
    print('\t\t\t\t  "TIME IN THE MARKET IS BETTER THAN TIMING THE MARKET!" - Kenneth Fisher')
    time.sleep(5)


def email_engine_params(direct_call="1"):
    global RYBKA_EMAIL_SENDER_EMAIL, RYBKA_EMAIL_RECIPIENT_EMAIL, RYBKA_EMAIL_RECIPIENT_NAME, RYBKA_EMAIL_SWITCH
    if RYBKA_EMAIL_SWITCH.upper() == "TRUE":
        if RYBKA_EMAIL_RECIPIENT_NAME == "User":
            if direct_call == "1":
                log.WARN(
                    "\n[RYBKA_EMAIL_RECIPIENT_NAME] was NOT provided in the HOST MACHINE ENV., but will default to value [User]"
                )
        if (
            RYBKA_EMAIL_SENDER_EMAIL
            and RYBKA_EMAIL_SENDER_DEVICE_PASSWORD
            and RYBKA_EMAIL_RECIPIENT_EMAIL
        ):
            if direct_call == "1":
                log.INFO_BOLD(f" ✅ Email params in ENV    -  {bcolors.PURPLE}SET")
        else:
            log.FATAL_7(
                "Email params in ENV    -  NOT SET\nAs long as you have [RYBKA_EMAIL_SWITCH] set as [True], make sure you also set up the [RYBKA_EMAIL_SENDER_EMAIL, RYBKA_EMAIL_SENDER_DEVICE_PASSWORD, RYBKA_EMAIL_RECIPIENT_EMAIL] vars in your ENV!"
            )
    else:
        if direct_call == "1":
            log.INFO(" ")
            log.WARN(
                "Emails are turned [OFF]. Set [RYBKA_EMAIL_SWITCH] var as 'True' in env / config.ini. if you want email notifications enabled!"
            )
            log.INFO(" ")


def telegram_engine_switch(direct_call="1"):
    global RYBKA_TELEGRAM_SWITCH
    if RYBKA_TELEGRAM_SWITCH.upper() == "TRUE":
        if bootstrap.TELE_KEY and bootstrap.TELE_CHAT_ID:
            if direct_call == "1":
                log.INFO_BOLD(f" ✅ Telegram params in ENV -  {bcolors.PURPLE}SET")
        else:
            log.FATAL_7(
                "Telegram params in ENV -  NOT SET\nAs long as you have [RYBKA_TELEGRAM_SWITCH] set as [True], make sure you also set up the [RYBKA_TELEGRAM_API_KEY, RYBKA_TELEGRAM_CHAT_ID] vars in your ENV!"
            )
    else:
        if direct_call == "1":
            log.INFO(" ")
            log.WARN(
                "Telegram notifications are turned [OFF]. Set [RYBKA_TELEGRAM_SWITCH] var as 'True' in env / config.ini. if you want Telegram notifications enabled!"
            )
            log.INFO(" ")


def bot_uptime_and_current_price(current_price, output):
    global uptime

    check_time = time.time()
    uptime_seconds = round(check_time - start_time)
    uptime_minutes = math.floor(uptime_seconds / 60)
    uptime_hours = math.floor(uptime_minutes / 60)

    seconds_in_limit = uptime_seconds % 60
    minutes_in_limit = math.floor(uptime_seconds / 60) % 60
    hours_in_limit = math.floor(uptime_minutes / 60) % 24
    days = math.floor(uptime_hours / 24)

    if output == "CLI":
        if days < 1:
            price_and_uptime = f"[ {bcolors.OKCYAN}EGLD{bcolors.DARKGRAY} = {bcolors.PURPLE}{current_price:5} {bcolors.OKCYAN}USDT{bcolors.DARKGRAY} ] [ ⏰ {bcolors.OKGREEN}UPTIME{bcolors.DARKGRAY} = {bcolors.PURPLE}{hours_in_limit:2}h:{minutes_in_limit:2}m:{seconds_in_limit:2}s{bcolors.DARKGRAY} ] [ 💵 {bcolors.OKGREEN}PROFIT{bcolors.DARKGRAY} = {bcolors.PURPLE}{total_usdt_profit} ₮{bcolors.DARKGRAY} ]"
        else:
            price_and_uptime = f"[ {bcolors.OKCYAN}EGLD{bcolors.DARKGRAY} = {bcolors.PURPLE}{current_price:5} {bcolors.OKCYAN}USDT{bcolors.DARKGRAY} ] [ ⏰ {bcolors.OKGREEN}UPTIME{bcolors.DARKGRAY} = {bcolors.PURPLE}{days}d {hours_in_limit:2}h:{minutes_in_limit:2}m:{seconds_in_limit:2}s{bcolors.DARKGRAY} ] [ 💵 {bcolors.OKGREEN}PROFIT{bcolors.DARKGRAY} = {bcolors.PURPLE}{total_usdt_profit} ₮{bcolors.DARKGRAY} ]"

        log.INFO(price_and_uptime)

    elif output == "Telegram":
        if days < 1:
            return f"{hours_in_limit:2}h:{minutes_in_limit:2}m:{seconds_in_limit:2}s"
        return f"{days}d {hours_in_limit:2}h:{minutes_in_limit:2}m:{seconds_in_limit:2}s"


def email_sender(email_message):
    global RYBKA_EMAIL_SWITCH, RYBKA_EMAIL_RECIPIENT_EMAIL, RYBKA_EMAIL_SENDER_EMAIL, RYBKA_EMAIL_RECIPIENT_NAME

    email_engine_params("0")

    if RYBKA_EMAIL_SWITCH.upper() == "TRUE":
        message_template = Template(
            """Dear ${PERSON_NAME},

            ${MESSAGE}



        ================================================================
        Email sent by RYBKA bot from machine having the following specs:

        hostname              ${HOSTNAME}
        mac-address         ${MAC_ADDR}
        ================================================================"""
        )

        s = smtplib.SMTP(host="smtp.gmail.com", port=587)
        s.starttls()
        s.login(RYBKA_EMAIL_SENDER_EMAIL, RYBKA_EMAIL_SENDER_DEVICE_PASSWORD)

        msg = MIMEMultipart()

        message = message_template.substitute(
            PERSON_NAME=RYBKA_EMAIL_RECIPIENT_NAME.title(),
            MESSAGE=email_message,
            HOSTNAME=socket.gethostname(),
            MAC_ADDR=":".join(re.findall("..", "%012x" % uuid.getnode())),
        )

        msg["From"] = RYBKA_EMAIL_SENDER_EMAIL
        msg["To"] = RYBKA_EMAIL_RECIPIENT_EMAIL
        msg["Subject"] = "RYBKA notification"

        msg.attach(MIMEText(message, "plain"))

        try:
            s.send_message(msg)
        except Exception as e:
            log.WARN(
                f"Sending email notification failed with error:\n{e}\nIf it's an authentication issue and you did set the correct password for your gmail account, you have the know that the actual required one is the DEVICE password for your gmail.\nIf you haven't got one configured yet, please set one up right here (connect with your sender address and then replace the password in the ENV with the newly created device password:\n       https://myaccount.google.com/apppasswords"
            )
        del msg

        s.quit()


def clear_terminal():
    if platform == "linux" or platform == "linux2":
        os.system("clear")
    elif platform == "win32":
        os.system("cls")


def re_sync_time():
    global DEBUG_LVL
    try:
        if platform == "linux" or platform == "linux2":
            pass
        elif platform == "win32":
            if DEBUG_LVL == 2 or DEBUG_LVL == 3:
                subprocess.call(["net", "start", "w32time"])
                subprocess.call(
                    [
                        "w32tm",
                        "/config",
                        "/syncfromflags:manual",
                        "/manualpeerlist:time.nist.gov",
                    ]
                )
                subprocess.call(["w32TM", "/resync"])
            else:
                devnull = open(os.devnull, "w", encoding="utf-8")
                subprocess.call(["net", "start", "w32time"], stdout=devnull, stderr=devnull)
                subprocess.call(
                    [
                        "w32tm",
                        "/config",
                        "/syncfromflags:manual",
                        "/manualpeerlist:time.nist.gov",
                    ],
                    stdout=devnull,
                    stderr=devnull,
                )
                subprocess.call(["w32TM", "/resync"], stdout=devnull, stderr=devnull)
            log.DEBUG("Time SYNC cmd completed successfully OR time is already synced")
    except Exception as e:
        log.WARN(f"Time SYNC cmd DID NOT complete successfully:\n{e}")


def isAdmin():
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def real_time_balances_update():
    global RYBKA_MODE
    global balance_usdt
    global balance_egld
    global balance_bnb

    try:
        with open(f"{RYBKA_MODE}/real_time_balances", "w", encoding="utf8") as f:
            f.write("Binance Account shows the following balances (EGLD, USDT and BNB only):\n")
            f.write(f"\n{log.logging_time()} EGLD balance is: {balance_egld}")
            f.write(f"\n{log.logging_time()} USDT balance is: {balance_usdt}")
            f.write(f"\n{log.logging_time()} BNB  balance is: {balance_bnb}")
    except Exception as e:
        log.WARN(f"Could not update balance file due to error: \n{e}")


def previous_runs_sanitation(target_folder):
    pattern = r".*_.*_.*_.*_.*_.*_.*_.*_.*_.*"

    folders = [f for f in os.listdir(".") if os.path.isdir(f)]

    found_match = False
    for folder in folders:
        if re.match(pattern, folder):
            found_match = True
            shutil.move(folder, target_folder)

    if found_match:
        log.ORANGE(" ✅ Previous run(s)' folder(s) found and moved to the 'archived_logs' folder.")
    else:
        log.ORANGE(" ✅ Current dir is already sanitized.")

    graphs_subdir_path = "custom_modules/telegram/data/pics"

    if not os.path.exists(graphs_subdir_path):
        os.makedirs(graphs_subdir_path)
        print(f"\n ✅ Created subdirectory: {graphs_subdir_path}")
    else:
        print(f"\n ✅ Subdirectory already exists: [{graphs_subdir_path}]")

    graphs_list = os.listdir(graphs_subdir_path)
    if graphs_list != []:
        log.ORANGE("\n ⚠️  Residual graph files found. Deleting them:")
    else:
        log.ORANGE("\n ✅ No residual graph files found.")

    for graph_name in graphs_list:
        graph_path = os.path.join(graphs_subdir_path, graph_name)
        if os.path.isfile(graph_path):
            os.remove(graph_path)
            log.ORANGE(f"\n\t ✅ Deleted file: {graphs_subdir_path} --> {graph_name}")


def move_and_replace(target_folder, path=None):
    original_dir = os.getcwd()

    if path:
        os.chdir(path)

    with open(target_folder, encoding="utf-8") as f:
        num_lines = sum(1 for line in f)

    if num_lines > 10000:
        log.INFO(
            f"File [${target_folder}] reached more than 10k lines. Archiving it and creating a fresher one."
        )
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename, extension = os.path.splitext(target_folder)
        new_filename = f"{filename}_{timestamp}{extension}"
        archive_path = os.path.join(os.getcwd(), "archive")
        if not os.path.exists(archive_path):
            os.makedirs(archive_path)
        shutil.move(target_folder, os.path.join(archive_path, new_filename))
        with open(target_folder, "w", encoding="utf-8") as f:
            f.write("")

    if path:
        os.chdir(original_dir)


###############################################
###########   WEBSOCKET FUNCTIONS   ###########
###############################################


@click.command()
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["demo", "live"], case_sensitive=False),
    help="Choose the run mode of the software",
)
@click.option("--version", is_flag=True, help="Show the version of the software", required=False)
@click.option("--head", is_flag=True, help="Show the version of the software", required=False)
def main(version, mode, head):
    """\b
    \b#################################################################################
    \b###                          🔸 RYBKACORE Software 🔸                         ###
    \b###                                                                           ###
    \b###   📖 Docs: https://gitlab.com/Silviu_space/rybka/-/blob/master/README.md  ###
    \b#################################################################################
    \b###                                                                           ###
    \b###   🔹 Author:    ©️ Silviu-Iulian Muraru                                    ###
    \b###   🔹 Email:     silviumuraru90@yahoo.com                                  ###
    \b###   🔹 LinkedIn:  https://www.linkedin.com/in/silviu-muraru-iulian/         ###
    \b###                                                                           ###
    \b#################################################################################
    """

    ###############################################
    ###########   CLI ARGS MANAGEMENT   ###########
    ###############################################

    global RYBKA_MODE, DEBUG_LVL
    global RSI_PERIOD, RSI_FOR_BUY, RSI_FOR_SELL
    global TRADING_BOOST_LVL, TRADE_QUANTITY, TRADE_SYMBOL, AUX_TRADE_QUANTITY
    global USDT_SAFETY_NET, MIN_PROFIT
    global RYBKA_TELEGRAM_SWITCH
    global RYBKA_ALL_LOG_TLG_SWITCH
    global RYBKA_BALANCES_AUX
    global SET_DISCLAIMER

    global balance_usdt, balance_egld, balance_bnb
    global locked_balance_usdt, locked_balance_egld, locked_balance_bnb
    global total_usdt_profit

    global current_export_dir, archived_logs_folder

    global uptime, start_time
    global client, closed_candles
    global ktbr_config
    global bnb_commission
    global multiple_sells, nr_of_trades
    global subsequent_valid_rsi_counter
    global archived_logs_folder, current_export_dir

    # In need of a dummy value in the case where the candle closes for EGLDUSDT before it closed for BNBUSDT, hence the value is not attributed to the BNB side, but only after up to 1 more minute
    global bnb_candle_close_price, bnb_conversion_done
    bnb_candle_close_price = 0
    bnb_conversion_done = 0

    if not version and not mode and not head:
        click.echo(click.get_current_context().get_help())
        sys.exit(111)

    if version:
        print(f"🔍 RybkaCore Software Version  ➜  [{bootstrap.__version__}]")
        sys.exit(111)

    if mode and head:
        RYBKA_MODE = mode.upper()

        # in need for the logging.py module
        os.environ["RYBKA_MODE"] = RYBKA_MODE

        if RYBKA_MODE == "DEMO":
            balance_usdt = bootstrap.RYBKA_DEMO_BALANCE_USDT
            balance_egld = bootstrap.RYBKA_DEMO_BALANCE_EGLD
            balance_bnb = bootstrap.RYBKA_DEMO_BALANCE_BNB
        elif RYBKA_MODE == "LIVE":
            balance_usdt = 0
            balance_egld = 0
            balance_bnb = 0

            locked_balance_usdt = 0
            locked_balance_egld = 0
            locked_balance_bnb = 0
    else:
        sys.exit(0)

    ###############################################
    ###########   FUNCTIONS' SEQUENCE   ###########
    ###############################################

    clear_terminal()

    try:
        archived_logs_folder = "archived_logs"
        TMP_folder(archived_logs_folder)
    except Exception as e:
        traceback.print_exc()
        log.FATAL_7(
            f"[{archived_logs_folder}] folder could not be created. Reason for failure:\n{e}"
        )

    try:
        previous_runs_sanitation(archived_logs_folder)
    except Exception as e:
        traceback.print_exc()
        log.FATAL_7(f"[SANITATION] process failed. Reason for failure:\n{e}")

    if platform == "linux" or platform == "linux2":
        pass
    elif platform == "win32":
        log.ORANGE(
            "\n===========================================================================\n 📋 Checking Rybka's permissions and syncing time... Please wait!"
        )
        if isAdmin() is not True:
            log.FATAL_7(
                "Please run the script with admin privileges, as bot needs access to auto-update HOST's time with NIST servers!"
            )

    re_sync_time()

    time.sleep(2)

    ###########  Prerequisites - start  ###########
    log.ORANGE("\n 📋 PREREQUISITE PROCESS STARTING...\n")
    time.sleep(1)

    process_pid = os.getpid()
    log.DEBUG(f"Allocating other PIDs [{process_pid}, ...]\n\n\n")
    TMP_folder("TEMP")
    with open("TEMP/core_pidTmp", "w", encoding="utf8") as f:
        f.write(str(process_pid))
    time.sleep(1)

    rybka_mode_folder_creation()
    all_errors_file()

    current_export_dir = f'{RYBKA_MODE}_{TRADE_SYMBOL}_{datetime.now().strftime("%d_%m_%Y")}_AT_{datetime.now().strftime("%H_%M_%S")}_{id_generator()}'
    # In need for Telegram notif. file
    os.environ["CURRENT_EXPORT_DIR"] = current_export_dir
    os.environ["TRADE_SYMBOL"] = TRADE_SYMBOL

    log_files_creation()
    time.sleep(2)
    ###########   Prerequisites - end   ###########

    clear_terminal()

    if RYBKA_MODE == "LIVE" and not SET_DISCLAIMER.upper() == "FALSE":
        disclaimer()
        clear_terminal()

    if RSI_PERIOD < 10:
        log.WARN(
            "Please DO NOT set a value less than [10] for the [RYBKA_RSI_PERIOD] ENV var! To ensure a trustworthy tech. analysis at an RSI level  --->  defaulting to value [10]."
        )
        RSI_PERIOD = 10

    def main_files():
        profit_file()
        nr_of_trades_file()
        full_order_history_file()
        real_time_balances()
        back_up()
        move_and_replace("errors_thrown", RYBKA_MODE)
        move_and_replace("full_order_history", RYBKA_MODE)

    software_config_params()
    user_initial_config()
    email_engine_params()
    binance_system_status()
    telegram_engine_switch()

    log.INFO(" ")
    log.INFO(
        "====================================================================================================================================="
    )
    log.INFO(
        f" Check files created for this run, under the newly created local folder {bcolors.BOLD}[{bcolors.PURPLE}{current_export_dir}{bcolors.DARKGRAY}]{bcolors.ENDC}"
    )
    log.INFO(
        "====================================================================================================================================="
    )
    log.INFO(" ")

    # Needs to be set before any [ktbr_integrity()] call, to make sure this is firstly created, in LIVE mode, if non-existing
    ktbr_configuration()

    if RYBKA_MODE == "LIVE":
        for i in range(1, 6):
            try:
                binance_account_status()
                binance_api_account_status()
                account_balance_update()
                ktbr_integrity()
                break
            except Exception as e:
                if i == 5:
                    traceback.print_exc()
                    log.FATAL_7(
                        f"Account-related functions failed to proceed successfully. Error:\n{e}"
                    )
                time.sleep(5)

    main_files()
    real_time_balances_update()

    if RYBKA_MODE == "DEMO":
        log.INFO(" ")
        if balance_usdt == 1500:
            log.WARN(
                f"USDT Balance of [{balance_usdt}] coins  --->  is set by default, by the bot. You can modify this value within the 'config.ini' file, for var [RYBKA_DEMO_BALANCE_USDT]"
            )
        if balance_egld == 100:
            log.WARN(
                f"EGLD Balance of [{balance_egld}]  coins  --->  is set by default, by the bot. You can modify this value within the 'config.ini' file, for var [RYBKA_DEMO_BALANCE_EGLD]"
            )
        if balance_bnb == 0.2:
            log.WARN(
                f"BNB  Balance of [{balance_bnb}]  coins  --->  is set by default, by the bot. You can modify this value within the 'config.ini' file, for var [RYBKA_DEMO_BALANCE_BNB]"
            )
        log.INFO(" ")

    log.INFO(
        "====================================================================================================================================="
    )
    log.INFO_BOLD(
        f"Account's AVAILABLE balance is:\n\t\t\t\t\t\t\t⚖️  {bcolors.PURPLE}USDT{bcolors.DARKGRAY}  ---  [{bcolors.OKGREEN}{balance_usdt}{bcolors.DARKGRAY}]\n\t\t\t\t\t\t\t⚖️  {bcolors.PURPLE}EGLD{bcolors.DARKGRAY}  ---  [{bcolors.OKGREEN}{balance_egld}{bcolors.DARKGRAY}]\n\n\t\t\t\t\t\t\t⚖️  {bcolors.PURPLE}BNB{bcolors.DARKGRAY}   ---  [{bcolors.OKGREEN}{balance_bnb}{bcolors.DARKGRAY}] (for transaction fees)"
    )
    log.INFO(
        "====================================================================================================================================="
    )
    if RYBKA_MODE == "LIVE":
        log.INFO_BOLD(
            f"Account's LOCKED balance in limit orders is:\n\t\t\t\t\t\t\t⚖️  {bcolors.PURPLE}LOCKED USDT{bcolors.DARKGRAY}  ---  [{bcolors.OKGREEN}{locked_balance_usdt}{bcolors.DARKGRAY}]\n\t\t\t\t\t\t\t⚖️  {bcolors.PURPLE}LOCKED EGLD{bcolors.DARKGRAY}  ---  [{bcolors.OKGREEN}{locked_balance_egld}{bcolors.DARKGRAY}]\n\n\t\t\t\t\t\t\t⚖️  {bcolors.PURPLE}LOCKED BNB{bcolors.DARKGRAY}   ---  [{bcolors.OKGREEN}{locked_balance_bnb}{bcolors.DARKGRAY}]"
        )
        log.INFO(
            "====================================================================================================================================="
        )
    log.INFO(
        "====================================================================================================================================="
    )
    log.INFO_BOLD(
        f"Rybka's historical registered PROFIT is:\n\t\t\t\t\t\t\t💰 [{bcolors.OKGREEN}{total_usdt_profit}{bcolors.DARKGRAY}] {bcolors.PURPLE}USDT"
    )
    log.INFO(
        "====================================================================================================================================="
    )
    log.INFO(
        "====================================================================================================================================="
    )

    telegram.LOG(f" 🟢 🅡🅨🅑🅚🅐🅒🅞🅡🅔 🟢\n          [[{RYBKA_MODE} mode]]")
    email_sender(
        f"{log.logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot is starting up. Find logs into the local folder: \n\t[{current_export_dir}]"
    )

    if RYBKA_TELEGRAM_SWITCH.upper() == "TRUE":
        create_telegram_and_rybka_tmp_files_if_not_created()

        def handling_open_of_telegram_listener():
            with open("TEMP/telegram_pidTmp", "r", encoding="utf8") as file:
                telegram_process = int(file.read())
                if not psutil.pid_exists(telegram_process):
                    telegram_pid = subprocess.Popen(["python3", "tlgrm_interactive.py"])
                else:
                    telegram_pid = "placeholder"
            return telegram_pid

        try:
            with open("TEMP/pid_rybkaTmp", "r", encoding="utf8") as file1:
                pID = int(file1.read())
                with open("TEMP/core_runsTmp", "r", encoding="utf8") as file2:
                    core_runs = int(file2.read())
                if (
                    psutil.pid_exists(pID)
                    and "python" in psutil.Process(pID).name()
                    and core_runs == 1
                ):
                    telegram_pid = handling_open_of_telegram_listener()
                elif not psutil.pid_exists(pID):
                    telegram_pid = handling_open_of_telegram_listener()
                else:
                    # case of "restarter" pid existing, but more than 1 core runs
                    # likely for this case to happen on non-hardcoded-errors that restart the restarter
                    # not so likely for Telegram PID to not still exist, but treating the case nonetheless
                    telegram_pid = handling_open_of_telegram_listener()
        except Exception as e:
            traceback.print_exc()
            log.FATAL_7(
                f"Some helper files do not exist. They are needed in order for the Telegram Listener to work well\n{e}"
            )
    else:
        log.INFO(" ")
        log.WARN(
            "Telegram Listener is turned [OFF]. Set [RYBKA_TELEGRAM_SWITCH] var as 'True' in env / config.ini. if you want Telegram notifications enabled!"
        )
        log.INFO(" ")

    time.sleep(1)

    if telegram_pid != "placeholder":
        with open("TEMP/telegram_pidTmp", "w", encoding="utf8") as f:
            f.write(str(telegram_pid.pid))

    try:
        unicorn_stream_obj = unicorn_binance_websocket_api.BinanceWebSocketApiManager(
            exchange="binance.com", warn_on_update=False
        )
        unicorn_stream_obj.create_stream(["kline_1m"], ["EGLDUSDT", "BNBUSDT"])

        log.INFO(
            "====================================================================================================================================="
        )
        log.INFO_BOLD(
            f"Connection to Binance servers established, listening to [{bcolors.PURPLE}{TRADE_SYMBOL}{bcolors.DARKGRAY}] data"
        )
        log.INFO(
            "====================================================================================================================================="
        )
        if len(closed_candles) >= 10:
            log.WARN(
                "YOU MANUALLY ADDED A HISTORY OF PRICES! IGNORING THE 10-min TIMEFRAME OF GATHERING LAST 10 PRICES/coin!"
            )
        else:
            log.INFO_BOLD("Initiating a one-time 10-min info gathering timeframe. Please wait...")
        log.INFO(
            "=====================================================================================================================================\n"
        )

    except Exception as e:
        traceback.print_exc()
        log.FATAL_7(f"The Unicorn object could not be created:\n{e}")

    try:

        def balances_update_via_telegram_cmd():
            if RYBKA_BALANCES_AUX.upper() == "TRUE" and RYBKA_MODE == "LIVE":
                for i in range(1, 11):
                    try:
                        account_balance_update()
                        log.DEBUG("Account Balance Sync. - Successful")
                        break
                    except Exception as e:
                        if i == 10:
                            traceback.print_exc()
                            log.FATAL_7(f"Account Balance Sync. - Failed as:\n{e}")
                        time.sleep(3)

                real_time_balances_update()

                if exists("LIVE/real_time_balances"):
                    with open("LIVE/real_time_balances", "r", encoding="utf8") as f:
                        if os.stat("LIVE/real_time_balances").st_size == 0:
                            telegram.LOG(" 🚫 [[LIVE/real_time_balances]] file exists but is empty")
                        else:
                            balances = f.read()
                            for elem in balances.split("\n"):
                                if ">" in elem:
                                    elem = f'🟣 {elem.split(">")[1]}'
                                if elem:
                                    telegram.LOG(f"{elem}")
                else:
                    telegram.LOG(" 🛑 The file for balances does NOT exist!")

                pattern = r"RYBKA_BALANCES_AUX =.*"
                replacement = "RYBKA_BALANCES_AUX = False"

                for line in fileinput.input("config.ini", inplace=True):
                    new_line = re.sub(pattern, replacement, line)
                    print(new_line, end="")

        while True:
            oldest_data_from_stream_buffer = unicorn_stream_obj.pop_stream_data_from_stream_buffer()
            if oldest_data_from_stream_buffer:
                log.HIGH_VERBOSITY(f"Stream buffer is: {oldest_data_from_stream_buffer}")

                try:
                    json.loads(oldest_data_from_stream_buffer)["data"]
                except KeyError:
                    continue

                candle = json.loads(oldest_data_from_stream_buffer)

                # When bnb_candle_close_price is 0 (assigned above), we still have to override this just 1 time (when it is 0) with the first price a candle provides, to not make subsequent fractions divide by 0
                if candle["data"]["s"] == "BNBUSDT" and bnb_candle_close_price == 0:
                    bnb_candle_close_price = round(float(candle["data"]["k"]["c"]), 4)

                if candle["data"]["s"] == "BNBUSDT" and candle["data"]["k"]["x"]:
                    bnb_candle_close_price = round(float(candle["data"]["k"]["c"]), 4)

                is_candle_egld_usdt = candle["data"]["s"]
                is_candle_closed = candle["data"]["k"]["x"]
                candle_close_price = round(float(candle["data"]["k"]["c"]), 4)

                if is_candle_closed and is_candle_egld_usdt == "EGLDUSDT":
                    closed_candles.append(candle_close_price)

                    bootstraping_vars()
                    log_files_creation("0")
                    telegram_engine_switch("0")

                    balances_update_via_telegram_cmd()

                    with open("TEMP/priceTmp", "w", encoding="utf8") as f:
                        f.write(str(candle_close_price))

                    with open("TEMP/uptimeTmp", "w", encoding="utf8") as f:
                        f.write(str(bot_uptime_and_current_price(candle_close_price, "Telegram")))

                    for i in range(0, 10):
                        try:
                            client.ping()
                            break
                        except Exception as e:
                            log.WARN(f"Binance server ping failed with error:\n{e}")
                            time.sleep(3)

                    with open(
                        f"{current_export_dir}/{TRADE_SYMBOL}_historical_prices",
                        "a",
                        encoding="utf8",
                    ) as f:
                        f.write(
                            f"{log.logging_time()} Price of [EGLD] is [{candle_close_price} USDT]\n"
                        )

                    with open(
                        f"{current_export_dir}/BNB_USDT_historical_prices",
                        "a",
                        encoding="utf8",
                    ) as f:
                        f.write(
                            f"{log.logging_time()} Price of [BNB] is [{bnb_candle_close_price} USDT]\n"
                        )

                    if len(closed_candles) < 11:
                        log.INFO(
                            "#####################################################################################################################################"
                        )
                        log.INFO_BOLD(
                            f"#####################  Bot is gathering data for technical analysis. Currently at min {bcolors.OKGREEN}[{len(closed_candles):2} of 10]{bcolors.ENDC}{bcolors.DARKGRAY} of processing  #####################"
                        )
                        log.INFO(
                            "#####################################################################################################################################"
                        )
                    log.DEBUG(f"History of target prices is {closed_candles}")

                    bot_uptime_and_current_price(candle_close_price, "CLI")

                    if len(closed_candles) > 30:
                        closed_candles = closed_candles[10:]

                    if len(closed_candles) > RSI_PERIOD:
                        np_candle_closes = numpy.array(closed_candles)
                        rsi = talib.RSI(np_candle_closes, RSI_PERIOD)

                        latest_rsi = round(rsi[-1], 2)

                        log.VERBOSE(f"Latest RSI indicates {latest_rsi}")

                        ###################################
                        ###       SPECIAL POLICY 1      ###
                        ################################################################################################################################
                        ###   Put in place to make the price go up or down towards a higher margin, then make a buy or sell. This makes ktbr be      ###
                        ###      distributed in a more uniform manner than just making constant buys / sells with small differences of price         ###
                        ###      between them until it will hit a bottleneck on heatmap (HEATMAP policy).                                            ###
                        ################################################################################################################################

                        if subsequent_valid_rsi_counter != 0:
                            log.DEBUG(
                                "Invalidating 3 RSI 1-min ticks (in care of a BUY) or 2 RSI 1-min ticks (in care of a SELL), as a transaction just occurred.\nMultiple sells don't fall under this policy\n"
                            )
                            subsequent_valid_rsi_counter -= 1

                            ###################################
                            ###   END of SPECIAL POLICY 1   ###
                            ###################################

                        else:
                            ###################################
                            ###       SPECIAL POLICY 2      ###
                            ################################################################################################################################
                            ###   Put in place to buy even though there are ktbr buy transactions above, in majority and RSI wouldn't indicate a buy.    ###
                            ###   This policy evaluates the prices compared to the other buys and if there are at least 10 buys, activates and           ###
                            ###      makes the bot buy EGLD if the current price is way below the majority of other buys and almost all the buys         ###
                            ###      under the current $ price got sold. So that it will buy even if price goes up, but ktbr contains lots of buy        ###
                            ###      transactions. By this, we ensure a higher profit, as it makes the bot works in time that otherwise would've been    ###
                            ###      skipped.                                                                                                            ###
                            ################################################################################################################################

                            policy = "not_overridden"

                            def buy_when_most_buys_are_above():
                                with open(f"{RYBKA_MODE}/ktbr", "r", encoding="utf8") as f:
                                    check_ktbr = json.loads(f.read())
                                    control = 0

                                    if len(check_ktbr) > 10 and len(check_ktbr) < 51:
                                        control = math.floor(len(check_ktbr) / 7)
                                    elif len(check_ktbr) > 50:
                                        control = math.floor(len(check_ktbr) / 12)

                                    verification_counter = 0
                                    control_zone_counter = 0
                                    for v in check_ktbr.values():
                                        if (
                                            round(
                                                candle_close_price
                                                - math.floor(candle_close_price / 10),
                                                2,
                                            )
                                            > v[1]
                                        ):
                                            verification_counter += 1

                                        if v[1] > round(
                                            candle_close_price
                                            - math.floor(candle_close_price / 10),
                                            2,
                                        ) and v[1] < round(
                                            candle_close_price
                                            + math.floor(candle_close_price / 10),
                                            2,
                                        ):
                                            control_zone_counter += 1

                                    if verification_counter > control or control_zone_counter > 1:
                                        return "not_overridden"

                                    return "overridden"

                                # just a reassurance if ktbr is deleted unexpectedly by "outside" means. To be sure no overridden happens if the above "with" won't evaluate.
                                return "not_overridden"

                            policy = buy_when_most_buys_are_above()

                            ###################################
                            ###   END of SPECIAL POLICY 2   ###
                            ###################################

                            ###################################
                            ###       SPECIAL POLICY 3      ###
                            ################################################################################################################################
                            ###   Put in place to buy even though there are less or equal to 4 transactions done in ktbr only and price might even       ###
                            ###      go up, as this policy invalidates RSI as well, granting an even higher profit in time, by making the bot work       ###
                            ###      in "dead time".                                                                                                     ###
                            ################################################################################################################################

                            if (
                                latest_rsi < RSI_FOR_BUY
                                or len(ktbr_config) in [0, 4]
                                or policy == "overridden"
                                or bnb_conversion_done == 1
                            ):
                                ###################################
                                ###   END of SPECIAL POLICY 3   ###
                                ###################################

                                bnb_conversion_done = 0

                                log.DEBUG(f"Policy 2 was [{policy}].")

                                if RYBKA_MODE == "LIVE":
                                    for i in range(1, 11):
                                        try:
                                            account_balance_update()
                                            log.DEBUG("Account Balance Sync. - Successful")
                                            break
                                        except Exception as e:
                                            if i == 10:
                                                traceback.print_exc()
                                                log.FATAL_7(
                                                    f"Account Balance Sync. - Failed as:\n{e}"
                                                )
                                            time.sleep(3)

                                real_time_balances_update()

                                safety_net_check = (
                                    balance_usdt
                                    - 2
                                    - TRADE_QUANTITY * round(float(candle_close_price), 4)
                                )

                                if USDT_SAFETY_NET and safety_net_check < USDT_SAFETY_NET:
                                    log.INFO(
                                        f"Another buy may bring the safety net for USDT to [{str(safety_net_check)}]. Which is lower than the one imposed, of [{str(USDT_SAFETY_NET)}]. Hence, it's not permitted!"
                                    )
                                else:
                                    log.VERBOSE(f"safety_net_check is {str(safety_net_check)}")
                                    log.VERBOSE(f"USDT_SAFETY_NET is {str(USDT_SAFETY_NET)}")
                                    log.DEBUG(
                                        f"Another buy would NOT enter the safety net [{str(USDT_SAFETY_NET)}]. Permitted."
                                    )

                                    if len(ktbr_config) in [0, 4]:
                                        log.INFO("===============================")
                                        log.INFO(" ALWAYS BUY POLICY ACTIVATED!")
                                        log.INFO("===============================")
                                    else:
                                        log.INFO("===============================")
                                        log.INFO(
                                            f"          {bcolors.OKCYAN}BUY{bcolors.ENDC} SIGNAL!"
                                        )
                                        log.INFO("===============================")

                                    with open(
                                        f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                        "a",
                                        encoding="utf8",
                                    ) as f:
                                        f.write(
                                            f"\n\n\n{log.logging_time()} Within BUY (part I):\n"
                                        )
                                        f.write(
                                            f'{log.logging_time()} {"Latest RSI (latest_rsi) is":90} {latest_rsi:40}\n'
                                        )
                                        f.write(
                                            f"{log.logging_time()} {'BNB balance (balance_bnb) is':90} {balance_bnb:40}\n"
                                        )
                                        f.write(
                                            f"{log.logging_time()} {'USDT balance (balance_usdt) is':90} {balance_usdt:40}\n"
                                        )
                                        f.write(
                                            f"{log.logging_time()} {'EGLD balance (balance_egld) is':90} {balance_egld:40}\n"
                                        )
                                        f.write(
                                            f"{log.logging_time()} {'Total USDT profit (total_usdt_profit) is':90} {total_usdt_profit:40}\n"
                                        )
                                        f.write(
                                            f"{log.logging_time()} {'Multiple sells (multiple_sells) set to':90} {multiple_sells:40}\n"
                                        )
                                        f.write(
                                            f"{log.logging_time()} {'TRADE_QUANTITY (BEFORE processing) (TRADE_QUANTITY) is':90} {TRADE_QUANTITY:40}\n"
                                        )
                                        f.write(
                                            f"\n{log.logging_time()} {'Closed candles (str(closed_candles)) are':90} {str(closed_candles)}\n"
                                        )
                                        f.write(
                                            f"\n{log.logging_time()} {'KTBR config (BEFORE processing) (str(json.dumps(ktbr_config))) is':90} \n {str(json.dumps(ktbr_config))}\n\n"
                                        )

                                    min_buy_share = candle_close_price / 12
                                    min_order_quantity = round(float(1 / min_buy_share), 2)

                                    TRADE_QUANTITY = AUX_TRADE_QUANTITY

                                    if min_order_quantity > TRADE_QUANTITY:
                                        log.DEBUG(
                                            f"We can NOT trade at this quantity: [{TRADE_QUANTITY}]. Enforcing a min quantity (per buy action) of [{min_order_quantity}] EGLD coins."
                                        )
                                        TRADE_QUANTITY = min_order_quantity
                                    else:
                                        log.DEBUG(
                                            f"We CAN trade at this quantity: [{TRADE_QUANTITY}]. No need to enforce a higher min trading limit."
                                        )

                                    if TRADE_QUANTITY < 0.01:
                                        TRADE_QUANTITY = 0.01
                                        log.DEBUG(
                                            f"Turns out that the TRADE_QUANTITY [{TRADE_QUANTITY}] is under Binance's imposed minimum of trade quantity for EGLDUSDT pair or `0.01`. Setting TRADE_QUANTITY=0.01"
                                        )

                                    if (
                                        round(
                                            float(
                                                (
                                                    round(
                                                        float(balance_bnb * bnb_candle_close_price),
                                                        6,
                                                    )
                                                )
                                                / (
                                                    round(
                                                        float(
                                                            0.08
                                                            / 100
                                                            * candle_close_price
                                                            * TRADE_QUANTITY
                                                        ),
                                                        4,
                                                    )
                                                )
                                            ),
                                            4,
                                        )
                                    ) >= 30:
                                        log.DEBUG(
                                            f"BNB balance [{balance_bnb}] is enough for transactions."
                                        )

                                        if balance_usdt / 12 > 1:
                                            possible_nr_of_trades = math.floor(
                                                (round(float(balance_usdt - USDT_SAFETY_NET), 4))
                                                / (TRADE_QUANTITY * candle_close_price)
                                            )
                                            log.INFO(
                                                f"Remaining possible nr. of buy orders: {possible_nr_of_trades}\n"
                                            )

                                            ###################################
                                            ###       SPECIAL POLICY 4      ###
                                            ################################################################################################################################
                                            ###   This "HEATMAP" policy is set in place to dinamically make the bot greedy or not and adapt the greediness based on      ###
                                            ###      a heatmap it construct and widens with every new buy transaction successfully completed. The more buys, the less    ###
                                            ###      greedy it becomes. The more sells of those buys, the more greedy it becomes. But this is NOT a rule of thumb, as    ###
                                            ###      it constructs N price-frames (limits) that dinamically move, per each 1$ the price of EGLD - USDT pair gains or     ###
                                            ###      loses - hence the margin of such frame, might get more greedy, even though it just made a buy, because it may find  ###
                                            ###      itself  in a totally other frame. It counts the number of buy transactions done in a frame (let's say from 33$ to   ###
                                            ###      37$) and limits itself to do only X transactions in there, but it also dinamically limits itself to a nr. of        ###
                                            ###      coins per interval (an interval is a 1$ frame, like 33$-34$ or 34$-35$). So it does a limited priceframe with       ###
                                            ###      nested limits all across it, per each 1$ level. Then, when the price goes up or down, the whoe frame moves, as its  ###
                                            ###      its center is always the price of EGLD in $.                                                                        ###
                                            ###                                                                                                                          ###
                                            ###      It's by far the most important aspect of the bot and most sensitive core script of RybkaCore. This also allows the  ###
                                            ###      formation of inner policies controled by the user via the [RYBKA_TRADING_BOOST_LVL] variable.                       ###
                                            ################################################################################################################################

                                            if possible_nr_of_trades >= 0:
                                                ###################################
                                                ###       SPECIAL POLICY 5      ###
                                                ################################################################################################################################
                                                ###   This "Multiple Sells" policy is set in place to gain speed when there are too many buys done already.                  ###
                                                ###   It will sell more currency previously bought, at once, within one minute, not re-evaluating the RSI for subsequent     ###
                                                ###      eligible sells. This way, the bot, if overloaded with buys, in raport to the total nr. of possible buys remaining   ###
                                                ###      will get cash again and will do it quickly, so that it can work more and thus make more profit.                     ###
                                                ################################################################################################################################

                                                if len(ktbr_config) > 5:
                                                    if (
                                                        possible_nr_of_trades
                                                        < len(ktbr_config) * 0.8
                                                    ):
                                                        multiple_sells = "enabled"
                                                    else:
                                                        multiple_sells = "disabled"
                                                else:
                                                    multiple_sells = "disabled"

                                                ###################################
                                                ###   END of SPECIAL POLICY 5   ###
                                                ###################################

                                                #####  LEGEND  ###############################################################################################################################
                                                ##   "heatmap_size" is the size (+ and -) from the real-time EGLD/USDT price, based on which the logics of the heatmap get applied on top   ##
                                                ##   "heatmap_center_coin_counter" is a counter for the nr. of buy transactions bought and still tracked at current price of EGLD in USDT   ##
                                                ##   "heatmap_limit" is a limit for the aforementioned counter                                                                              ##
                                                ##   "heatmap_actions" is a counter for the nr. of buy transactions bought and still tracked within the current "heatmap_size"              ##
                                                ##   "heatmap_counter" is a limit for the aforementioned counter                                                                            ##
                                                ##############################################################################################################################################
                                                #
                                                ########   Make sure `division by 0` is not hit when editing the weights in here   ########
                                                if possible_nr_of_trades == 1:
                                                    heatmap_actions = 1
                                                    heatmap_size = 2
                                                    heatmap_limit = 1
                                                else:
                                                    if int(TRADING_BOOST_LVL) == 1:
                                                        heatmap_actions = round(
                                                            float(possible_nr_of_trades * 0.4)
                                                        )
                                                    elif int(TRADING_BOOST_LVL) == 2:
                                                        heatmap_actions = round(
                                                            float(possible_nr_of_trades * 0.6)
                                                        )
                                                    elif int(TRADING_BOOST_LVL) == 3:
                                                        heatmap_actions = round(
                                                            float(possible_nr_of_trades * 0.75)
                                                        )
                                                    elif int(TRADING_BOOST_LVL) == 4:
                                                        heatmap_actions = round(
                                                            float(possible_nr_of_trades * 0.9)
                                                        )
                                                    elif int(TRADING_BOOST_LVL) == 5:
                                                        heatmap_actions = possible_nr_of_trades
                                                    if heatmap_actions == 0 or heatmap_actions == 1:
                                                        heatmap_size = 2
                                                        heatmap_limit = 1
                                                    else:
                                                        if int(TRADING_BOOST_LVL) == 1:
                                                            heatmap_size = round(
                                                                float(heatmap_actions * 0.65)
                                                            )
                                                        elif int(TRADING_BOOST_LVL) == 2:
                                                            heatmap_size = round(
                                                                float(heatmap_actions * 0.4)
                                                            )
                                                        elif int(TRADING_BOOST_LVL) == 3:
                                                            heatmap_size = round(
                                                                float(heatmap_actions * 0.25)
                                                            )
                                                        elif int(TRADING_BOOST_LVL) == 4:
                                                            heatmap_size = 3
                                                        elif int(TRADING_BOOST_LVL) == 5:
                                                            heatmap_size = 2
                                                        if heatmap_size == 0 or heatmap_size == 1:
                                                            heatmap_size = 2
                                                        if int(TRADING_BOOST_LVL) == 1:
                                                            heatmap_limit = round(
                                                                float(
                                                                    (heatmap_actions / heatmap_size)
                                                                    + heatmap_size * 0.15
                                                                )
                                                            )
                                                        elif int(TRADING_BOOST_LVL) == 2:
                                                            heatmap_limit = round(
                                                                float(
                                                                    (heatmap_actions / heatmap_size)
                                                                    + heatmap_size * 0.3
                                                                )
                                                            )
                                                        elif int(TRADING_BOOST_LVL) == 3:
                                                            heatmap_limit = round(
                                                                float(
                                                                    (heatmap_actions / heatmap_size)
                                                                    + heatmap_size * 0.5
                                                                )
                                                            )
                                                        elif int(TRADING_BOOST_LVL) == 4:
                                                            heatmap_limit = round(
                                                                float(
                                                                    (heatmap_actions / heatmap_size)
                                                                    + heatmap_size * 0.85
                                                                )
                                                            )
                                                        elif int(TRADING_BOOST_LVL) == 5:
                                                            heatmap_limit = round(
                                                                float(
                                                                    (heatmap_actions / heatmap_size)
                                                                    + heatmap_size * 1.5
                                                                )
                                                            )
                                                ############################################################################################

                                                log.VERBOSE(
                                                    f"possible_nr_of_trades is {possible_nr_of_trades}"
                                                )
                                                log.VERBOSE(f"heatmap_actions is {heatmap_actions}")
                                                log.VERBOSE(f"heatmap_size is {heatmap_size}")
                                                log.VERBOSE(f"heatmap_limit is {heatmap_limit}")
                                                log.DEBUG(
                                                    f"TRADING_BOOST_LVL is {str(TRADING_BOOST_LVL)}"
                                                )

                                                current_price_rounded_down = math.floor(
                                                    round(float(candle_close_price), 4)
                                                )

                                                heatmap_counter = 0
                                                ktbr_config_array_of_prices = []

                                                for v in ktbr_config.values():
                                                    ktbr_config_array_of_prices.append(
                                                        math.floor(float(v[1]))
                                                    )

                                                for n in range(
                                                    -round(float(heatmap_size / 2)),
                                                    round(float(heatmap_size / 2)),
                                                ):
                                                    if (
                                                        current_price_rounded_down + n
                                                        in ktbr_config_array_of_prices
                                                    ):
                                                        heatmap_counter += (
                                                            ktbr_config_array_of_prices.count(
                                                                current_price_rounded_down + n
                                                            )
                                                        )

                                                heatmap_center_coin_counter = (
                                                    ktbr_config_array_of_prices.count(
                                                        current_price_rounded_down
                                                    )
                                                )

                                                with open(
                                                    f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                    "a",
                                                    encoding="utf8",
                                                ) as f:
                                                    f.write(
                                                        f"\n\n{log.logging_time()} Within BUY (part III):\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} {'HEATMAP actions (heatmap_actions) is':90} {heatmap_actions:40}\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} {'HEATMAP size (heatmap_size) is':90} {heatmap_size:40}\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} {'HEATMAP limit (heatmap_limit) is':90} {heatmap_limit:40}\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} {'HEATMAP counter (heatmap_counter) is':90} {heatmap_counter:40}\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} {'HEATMAP center coin counter (heatmap_center_coin_counter) is':90} {heatmap_center_coin_counter:40}\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} {'TRADING BOOST LVL (TRADING_BOOST_LVL) is':90} {str(TRADING_BOOST_LVL):40}\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} {'Min Buy share (min_buy_share) is':90} {min_buy_share:40}\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} {'Min Order QTTY (min_order_quantity) is':90} {min_order_quantity:40}\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} {'Current price rounded down (current_price_rounded_down) set to':90} {current_price_rounded_down:40}\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} {'TRADE_QUANTITY (AFTER processing) (TRADE_QUANTITY) is':90} {TRADE_QUANTITY:40}\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} {'Possible Nr. of trades (possible_nr_of_trades) is':90} {possible_nr_of_trades:40}\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} KTBR array of prices (str(ktbr_config_array_of_prices)) is {str(ktbr_config_array_of_prices)}\n\n\n"
                                                    )

                                                if heatmap_center_coin_counter >= heatmap_limit:
                                                    log.INFO(
                                                        f"Buying not allowed!\nAt current 1$ price range of [{str(current_price_rounded_down)}-{str(current_price_rounded_down+1)}$], we have enought buys [{str(heatmap_center_coin_counter)}], considering the limit [{str(heatmap_limit)}]\n"
                                                    )
                                                    with open(
                                                        f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                        "a",
                                                        encoding="utf8",
                                                    ) as f:
                                                        f.write(
                                                            f"\n\n{log.logging_time()} Within BUY (part IV):\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} HEATMAP DOES NOT ALLOW BUYING!"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} heatmap_center_coin_counter [{heatmap_center_coin_counter}] is >= heatmap_limit [{heatmap_limit}]"
                                                        )
                                                elif heatmap_counter >= heatmap_actions:
                                                    log.INFO(
                                                        f"Buying not allowed!\nWithin a small price range of [{str(current_price_rounded_down-round(float(heatmap_size / 2)))}-{str(current_price_rounded_down+round(float(heatmap_size / 2)))}$], we have too many buys [{str(heatmap_counter)}], considering the limit [{str(heatmap_actions)}]\n"
                                                    )

                                                    ###################################
                                                    ###   END of SPECIAL POLICY 4   ###
                                                    ###################################

                                                    with open(
                                                        f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                        "a",
                                                        encoding="utf8",
                                                    ) as f:
                                                        f.write(
                                                            f"\n\n{log.logging_time()} Within BUY (part IV):\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} HEATMAP DOES NOT ALLOW BUYING!"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} heatmap_counter [{heatmap_counter}] is >= heatmap_actions [{heatmap_actions}]"
                                                        )
                                                elif (
                                                    float(balance_usdt)
                                                    < float(TRADE_QUANTITY)
                                                    * float(candle_close_price)
                                                    + 2
                                                ):
                                                    log.DEBUG(
                                                        "Way too low diff between acc. balance and current price * trade quantity. Not allowing a buy transaction."
                                                    )
                                                else:
                                                    log.VERBOSE("HEATMAP ALLOWS BUYING!\n")
                                                    try:
                                                        if RYBKA_MODE == "LIVE":
                                                            log.VERBOSE(
                                                                f"Before BUY. USDT balance is [{balance_usdt}]"
                                                            )
                                                            log.VERBOSE(
                                                                f"Before BUY. EGLD balance is [{balance_egld}]"
                                                            )
                                                            log.VERBOSE(
                                                                f"Before BUY. BNB  balance is [{balance_bnb}]"
                                                            )
                                                            order = client.order_market_buy(
                                                                symbol=TRADE_SYMBOL,
                                                                quantity=TRADE_QUANTITY,
                                                            )
                                                        elif RYBKA_MODE == "DEMO":
                                                            order_id_tmp = id_generator()
                                                            order = {
                                                                "symbol": "EGLDUSDT",
                                                                "orderId": "",
                                                                "orderListId": -1,
                                                                "clientOrderId": "TXgNl8RNNipASGTrleH6ZY",
                                                                "transactTime": 1661098548719,
                                                                "price": "0.00000000",
                                                                "origQty": "0.19000000",
                                                                "executedQty": "0.19000000",
                                                                "cummulativeQuoteQty": "10.20300000",
                                                                "status": "FILLED",
                                                                "timeInForce": "GTC",
                                                                "type": "MARKET",
                                                                "side": "BUY",
                                                                "fills": [
                                                                    {
                                                                        "price": "",
                                                                        "qty": "0.19000000",
                                                                        "commission": "",
                                                                        "commissionAsset": "EGLD",
                                                                        "tradeId": 75747997,
                                                                    }
                                                                ],
                                                            }
                                                            order["orderId"] = order_id_tmp
                                                            order["executedQty"] = TRADE_QUANTITY
                                                            order["fills"][0][
                                                                "price"
                                                            ] = candle_close_price
                                                            order["fills"][0]["commission"] = round(
                                                                float(
                                                                    round(
                                                                        float(
                                                                            0.08
                                                                            / 100
                                                                            * candle_close_price
                                                                            * TRADE_QUANTITY
                                                                        ),
                                                                        4,
                                                                    )
                                                                    / bnb_candle_close_price
                                                                ),
                                                                8,
                                                            )

                                                            balance_usdt -= (
                                                                candle_close_price * TRADE_QUANTITY
                                                            )
                                                            balance_usdt = round(balance_usdt, 4)
                                                            balance_egld += TRADE_QUANTITY
                                                            balance_egld = round(balance_egld, 4)
                                                            balance_bnb -= round(
                                                                float(
                                                                    round(
                                                                        float(
                                                                            0.08
                                                                            / 100
                                                                            * candle_close_price
                                                                            * TRADE_QUANTITY
                                                                        ),
                                                                        4,
                                                                    )
                                                                    / bnb_candle_close_price
                                                                ),
                                                                8,
                                                            )
                                                            balance_bnb = round(balance_bnb, 8)

                                                        order_time = datetime.now().strftime(
                                                            "%d/%m/%Y %H:%M:%S"
                                                        )
                                                        log.DEBUG(
                                                            f"BUY Order placed now at [{order_time}]\n"
                                                        )
                                                        time.sleep(5)

                                                        if RYBKA_MODE == "LIVE":
                                                            for i in range(1, 11):
                                                                try:
                                                                    order_status = client.get_order(
                                                                        symbol=TRADE_SYMBOL,
                                                                        orderId=order["orderId"],
                                                                    )
                                                                    log.DEBUG(
                                                                        "EGLD Buy Order status retrieval - Successful"
                                                                    )
                                                                    break
                                                                except Exception as e:
                                                                    if i == 10:
                                                                        traceback.print_exc()
                                                                        log.FATAL_7(
                                                                            f"EGLD Buy Order status retrieval - Failed as:\n{e}"
                                                                        )
                                                                    time.sleep(3)

                                                        elif RYBKA_MODE == "DEMO":
                                                            order_status = {
                                                                "symbol": "EGLDUSDT",
                                                                "orderId": 0,
                                                                "orderListId": -1,
                                                                "clientOrderId": "TXgNl8RNNipASGTrleH6ZY",
                                                                "price": "0.00000000",
                                                                "origQty": "0.19000000",
                                                                "executedQty": "0.19000000",
                                                                "cummulativeQuoteQty": "10.20300000",
                                                                "status": "FILLED",
                                                                "timeInForce": "GTC",
                                                                "type": "MARKET",
                                                                "side": "BUY",
                                                                "stopPrice": "0.00000000",
                                                                "icebergQty": "0.00000000",
                                                                "time": 1661098548719,
                                                                "updateTime": 1661098548719,
                                                                "isWorking": True,
                                                                "origQuoteOrderQty": "0.00000000",
                                                            }
                                                            order_status["orderId"] = order_id_tmp

                                                        if order_status["status"] == "FILLED":
                                                            log.INFO_BOLD_UNDERLINE(
                                                                " ✅ BUY Order filled successfully!\n"
                                                            )

                                                            # avoid rounding up on quantity & price bought
                                                            log.INFO_SPECIAL(
                                                                f" 🟣 [{RYBKA_MODE}] Bought [{int(float(order['executedQty']) * 10 ** 4) / 10 ** 4}] EGLD at price per 1 EGLD of [{int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4}] USDT\n"
                                                            )
                                                            telegram.LOG(
                                                                f" 🟣 [[{RYBKA_MODE}]] Bought [[{int(float(order['executedQty']) * 10 ** 4) / 10 ** 4}]] EGLD at [[{int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4}]] USDT/EGLD",
                                                            )

                                                            usdt_trade_fee = round(
                                                                float(
                                                                    0.08
                                                                    / 100
                                                                    * round(
                                                                        float(
                                                                            order[
                                                                                "cummulativeQuoteQty"
                                                                            ]
                                                                        ),
                                                                        4,
                                                                    )
                                                                ),
                                                                4,
                                                            )
                                                            log.VERBOSE(
                                                                f"BUY action's usdt trade fee is {usdt_trade_fee}"
                                                            )

                                                            total_usdt_profit = round(
                                                                total_usdt_profit - usdt_trade_fee,
                                                                4,
                                                            )
                                                            with open(
                                                                f"{RYBKA_MODE}/usdt_profit",
                                                                "w",
                                                                encoding="utf8",
                                                            ) as f:
                                                                f.write(str(total_usdt_profit))

                                                            bnb_commission = float(
                                                                order["fills"][0]["commission"]
                                                            )
                                                            with open(
                                                                f"{RYBKA_MODE}/most_recent_commission",
                                                                "w",
                                                                encoding="utf8",
                                                            ) as f:
                                                                f.write(
                                                                    str(
                                                                        order["fills"][0][
                                                                            "commission"
                                                                        ]
                                                                    )
                                                                )

                                                            ktbr_config[order["orderId"]] = [
                                                                int(
                                                                    float(order["executedQty"])
                                                                    * 10**4
                                                                )
                                                                / 10**4,
                                                                int(
                                                                    float(
                                                                        order["fills"][0]["price"]
                                                                    )
                                                                    * 10**4
                                                                )
                                                                / 10**4,
                                                            ]
                                                            with open(
                                                                f"{RYBKA_MODE}/ktbr",
                                                                "w",
                                                                encoding="utf8",
                                                            ) as f:
                                                                f.write(
                                                                    str(json.dumps(ktbr_config))
                                                                )

                                                            nr_of_trades += 1

                                                            with open(
                                                                f"{RYBKA_MODE}/number_of_buy_trades",
                                                                "w",
                                                                encoding="utf8",
                                                            ) as f:
                                                                f.write(str(nr_of_trades))

                                                            with open(
                                                                f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                                "a",
                                                                encoding="utf8",
                                                            ) as f:
                                                                f.write(
                                                                    f"\n\n{log.logging_time()} Within BUY (part V):\n"
                                                                )
                                                                f.write(
                                                                    f"{log.logging_time()} HEATMAP ALLOWS BUYING!\n"
                                                                )
                                                                f.write(
                                                                    f"{log.logging_time()} {'Order time (order_time) is':90} {str(order_time):40}"
                                                                )
                                                                f.write(
                                                                    f"{log.logging_time()} Transaction ID [{str(order['orderId'])}] - Bought [{str(int(float(order['executedQty']) * 10 ** 4) / 10 ** 4)}] EGLD at price per 1 EGLD of [{str(int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4)}] USDT\n"
                                                                )
                                                                f.write(
                                                                    f"{log.logging_time()} {'Order (order) is':90} {str(json.dumps(order))}\n"
                                                                )
                                                                f.write(
                                                                    f"{log.logging_time()} {'Order status (order_status) is':90} {str(json.dumps(order_status))}\n"
                                                                )
                                                                f.write(
                                                                    f"{log.logging_time()} {'USDT trade fee (usdt_trade_fee) is':90} {str(usdt_trade_fee)}\n"
                                                                )
                                                                f.write(
                                                                    f"{log.logging_time()} {'Order commission is':90} {str(bnb_commission):40}\n"
                                                                )
                                                                f.write(
                                                                    f"{log.logging_time()} KTBR config (AFTER processing) (str(json.dumps(ktbr_config))) is {str(json.dumps(ktbr_config)):40}\n"
                                                                )

                                                            back_up()
                                                            move_and_replace(
                                                                "errors_thrown", RYBKA_MODE
                                                            )
                                                            move_and_replace(
                                                                "full_order_history", RYBKA_MODE
                                                            )
                                                            move_and_replace(
                                                                f"{TRADE_SYMBOL}_DEBUG",
                                                                current_export_dir,
                                                            )
                                                            move_and_replace(
                                                                f"{TRADE_SYMBOL}_historical_prices",
                                                                current_export_dir,
                                                            )
                                                            move_and_replace(
                                                                f"BNB_USDT_historical_prices",
                                                                current_export_dir,
                                                            )
                                                            move_and_replace(
                                                                f"{TRADE_SYMBOL}_order_history",
                                                                current_export_dir,
                                                            )

                                                            if RYBKA_MODE == "LIVE":
                                                                for i in range(1, 11):
                                                                    try:
                                                                        account_balance_update()
                                                                        log.DEBUG(
                                                                            "Account Balance Sync. - Successful"
                                                                        )
                                                                        break
                                                                    except Exception as e:
                                                                        if i == 10:
                                                                            traceback.print_exc()
                                                                            log.FATAL_7(
                                                                                f"Account Balance Sync. - Failed as:\n{e}"
                                                                            )
                                                                        time.sleep(3)

                                                            real_time_balances_update()

                                                            if DEBUG_LVL != 3:
                                                                log.DEBUG(
                                                                    f"USDT balance is [{balance_usdt}]"
                                                                )
                                                                log.DEBUG(
                                                                    f"EGLD balance is [{balance_egld}]"
                                                                )
                                                                log.DEBUG(
                                                                    f"BNB  balance is [{balance_bnb}]"
                                                                )

                                                            log.VERBOSE(
                                                                f"After BUY - balance update. USDT balance is [{balance_usdt}]"
                                                            )
                                                            log.VERBOSE(
                                                                f"After BUY - balance update. EGLD balance is [{balance_egld}]"
                                                            )
                                                            log.VERBOSE(
                                                                f"After BUY - balance update. BNB  balance is [{balance_bnb}]"
                                                            )

                                                            if RYBKA_MODE == "LIVE":
                                                                ktbr_integrity()

                                                            with open(
                                                                f"{current_export_dir}/{TRADE_SYMBOL}_order_history",
                                                                "a",
                                                                encoding="utf8",
                                                            ) as f:
                                                                f.write(
                                                                    f"{log.logging_time()} Buy order done now at [{str(order_time)}]\n"
                                                                )
                                                                f.write(
                                                                    f"{log.logging_time()} Transaction ID [{str(order['orderId'])}] - Bought [{str(int(float(order['executedQty']) * 10 ** 4) / 10 ** 4)}] EGLD at price per 1 EGLD of [{str(int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4)}] USDT\n\n\n"
                                                                )
                                                            with open(
                                                                f"{RYBKA_MODE}/full_order_history",
                                                                "a",
                                                                encoding="utf8",
                                                            ) as f:
                                                                f.write(
                                                                    f"{log.logging_time()} Buy order done now at [{str(order_time)}]\n"
                                                                )
                                                                f.write(
                                                                    f"{log.logging_time()} Transaction ID [{str(order['orderId'])}] - Bought [{str(int(float(order['executedQty']) * 10 ** 4) / 10 ** 4)}] EGLD at price per 1 EGLD of [{str(int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4)}] USDT\n\n\n"
                                                                )

                                                            if len(ktbr_config) > 4:
                                                                subsequent_valid_rsi_counter = 3

                                                            re_sync_time()
                                                        else:
                                                            with open(
                                                                f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                                "a",
                                                                encoding="utf8",
                                                            ) as f:
                                                                f.write(
                                                                    f"\n\n{log.logging_time()} Within BUY (part VI):\n"
                                                                )
                                                                f.write(
                                                                    f"{log.logging_time()} Buy order was NOT filled successfully! Please check the cause!\n"
                                                                )
                                                                f.write(
                                                                    f"{log.logging_time()} Order (order) is {str(json.dumps(order))}\n"
                                                                )
                                                                f.write(
                                                                    f"{log.logging_time()} Order status (order_status) is {str(json.dumps(order_status))}\n"
                                                                )
                                                            log.FATAL_7(
                                                                "Buy order was NOT filled successfully! Please check the cause!"
                                                            )
                                                    except Exception as e:
                                                        with open(
                                                            f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                            "a",
                                                            encoding="utf8",
                                                        ) as f:
                                                            f.write(
                                                                f"\n\n{log.logging_time()} Within BUY (part VII):\n"
                                                            )
                                                            f.write(
                                                                f"{log.logging_time()} Order could NOT be placed due to an error:\n{e}\n"
                                                            )
                                                        traceback.print_exc()
                                                        log.FATAL_7(
                                                            f"Make sure the [RYBKA_BIN_KEY] and [RYBKA_BIN_SECRET] ENV vars have valid values and time server is synced with NIST's!\nOrder could NOT be placed due to an error:\n{e}"
                                                        )
                                            else:
                                                log.WARN(
                                                    f"Bot might still be able to buy some crypto, but only at a [{min_order_quantity}] EGLD trading quantity, not at the current one set of [{TRADE_QUANTITY}] EGLD per transaction!\n"
                                                )
                                                with open(
                                                    f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                    "a",
                                                    encoding="utf8",
                                                ) as f:
                                                    f.write(
                                                        f"\n\n{log.logging_time()} Within BUY (part VIII):\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} Bot might still be able to buy some crypto, but only at a [{min_order_quantity}] EGLD trading quantity, not at the current one set of [{TRADE_QUANTITY}] EGLD per transaction!\n"
                                                    )
                                        else:
                                            log.WARN(
                                                "Not enough [USDT] to set other BUY orders! Wait for SELLS, or fill up the account with more [USDT]."
                                            )
                                            # TODO add log.WARN message and email func within the same 'if' clause for enabling / disabling such emails
                                            # log.WARN(f"Notifying user (via email) that bot might need more money for buy actions, if possible.")
                                            # email_sender(f"[RYBKA MODE - {RYBKA_MODE}] Bot might be able to buy more, but doesn't have enough USDT in balance [{balance_usdt}]\n\nTOP UP if possible!")
                                            with open(
                                                f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                "a",
                                                encoding="utf8",
                                            ) as f:
                                                f.write(
                                                    f"\n\n{log.logging_time()} Within BUY (part IX):\n"
                                                )
                                                f.write(
                                                    f"{log.logging_time()} Not enough [USDT] to set other BUY orders! Wait for SELLS, or fill up the account with more [USDT].\n"
                                                )
                                    else:
                                        if RYBKA_MODE == "LIVE":
                                            email_sender(
                                                f"{log.logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot doesn't have enough BNB in balance [{balance_bnb}] to sustain many more trades.\n\nHence, to avoid stopping the bot, Rybka will automatically convert a bit over 10 USDT into BNB. This does NOT take from Safety Net!"
                                            )
                                            with open(
                                                f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                "a",
                                                encoding="utf8",
                                            ) as f:
                                                f.write(
                                                    f"\n\n{log.logging_time()} Within BUY (part X):\n"
                                                )
                                                f.write(
                                                    f"{log.logging_time()} BNB balance [{str(balance_bnb)}] is NOT enough to sustain many more transactions. Hence, to avoid stopping the bot, Rybka will automatically convert a bit over 10 USDT into BNB. This does NOT take from Safety Net!\n"
                                                )

                                            if round(float(balance_usdt - USDT_SAFETY_NET), 4) > 15:
                                                bnb_min_buy_share = bnb_candle_close_price / 12
                                                bnb_min_order_quantity = round(
                                                    float(1 / bnb_min_buy_share), 3
                                                )

                                                # treating the rare case of a sky-high price of BNB (of 24001 or above, in USDT), scenario in which the value of `bnb_min_order_quantity` would be equal to `0.0`
                                                if bnb_min_order_quantity == 0:
                                                    bnb_min_order_quantity = 0.001

                                                order = client.order_market_buy(
                                                    symbol="BNBUSDT",
                                                    quantity=bnb_min_order_quantity,
                                                )

                                                bnb_conversion_done = 1

                                                order_time = datetime.now().strftime(
                                                    "%d/%m/%Y %H:%M:%S"
                                                )
                                                log.DEBUG(
                                                    f"BNB BUY Order placed now at [{order_time}]\n"
                                                )
                                                log.VERBOSE(
                                                    f"bnb_min_order_quantity is [{str(bnb_min_order_quantity)}]\n"
                                                )
                                                log.VERBOSE(
                                                    f"bnb_candle_close_price is [{str(bnb_candle_close_price)}]\n"
                                                )
                                                log.VERBOSE(
                                                    f"bnb_min_buy_share is [{str(bnb_min_buy_share)}]\n"
                                                )

                                                time.sleep(5)

                                                with open(
                                                    f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                    "a",
                                                    encoding="utf8",
                                                ) as f:
                                                    f.write(
                                                        f"\n\n\n{log.logging_time()} Within BNB buy order (part I):\n"
                                                    )
                                                    f.write(
                                                        f'{log.logging_time()} {"bnb_min_order_quantity":90} {str(bnb_min_order_quantity)}\n'
                                                    )
                                                    f.write(
                                                        f'{log.logging_time()} {"bnb_candle_close_price":90} {str(bnb_candle_close_price)}\n'
                                                    )
                                                    f.write(
                                                        f'{log.logging_time()} {"bnb_min_buy_share":90} {str(bnb_min_buy_share)}\n'
                                                    )

                                                for i in range(1, 11):
                                                    try:
                                                        order_status = client.get_order(
                                                            symbol="BNBUSDT",
                                                            orderId=order["orderId"],
                                                        )
                                                        log.DEBUG(
                                                            "1. BNB Buy Order status retrieval - Successful"
                                                        )
                                                        break
                                                    except Exception as e:
                                                        if i == 10:
                                                            traceback.print_exc()
                                                            log.FATAL_7(
                                                                f"1. BNB Buy Order status retrieval - Failed as:\n{e}"
                                                            )
                                                        time.sleep(3)

                                                with open(
                                                    f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                    "a",
                                                    encoding="utf8",
                                                ) as f:
                                                    f.write(
                                                        f"\n\n\n{log.logging_time()} Within BNB buy order (part I):\n"
                                                    )
                                                    f.write(
                                                        f'{log.logging_time()} {"Order status is":90} {str(order_status)}\n'
                                                    )

                                                if order_status["status"] == "FILLED":
                                                    log.INFO_BOLD_UNDERLINE(
                                                        " ✅ BNB BUY Order filled successfully!\n"
                                                    )

                                                    # avoid rounding up on quantity & price bought
                                                    log.INFO_SPECIAL(
                                                        f" ☑️  ♻️  Bought [{int(float(order['executedQty']) * 10 ** 8) / 10 ** 8}] BNB at price per 1 BNB of [{int(float(order['fills'][0]['price']) * 10 ** 8) / 10 ** 8}] USDT\n"
                                                    )
                                                    telegram.LOG(
                                                        f" ☑️ ♻️ Bought [[{int(float(order['executedQty']) * 10 ** 8) / 10 ** 8}]] BNB at [[{int(float(order['fills'][0]['price']) * 10 ** 8) / 10 ** 8}]] USDT/BNB",
                                                    )

                                                    for i in range(1, 11):
                                                        try:
                                                            account_balance_update()
                                                            log.DEBUG(
                                                                "Account Balance Sync. - Successful"
                                                            )
                                                            break
                                                        except Exception as e:
                                                            if i == 10:
                                                                traceback.print_exc()
                                                                log.FATAL_7(
                                                                    f"Account Balance Sync. - Failed as:\n{e}"
                                                                )
                                                            time.sleep(3)

                                                    real_time_balances_update()

                                                    if DEBUG_LVL != 3:
                                                        log.DEBUG(
                                                            f"USDT balance is [{balance_usdt}]"
                                                        )
                                                        log.DEBUG(
                                                            f"EGLD balance is [{balance_egld}]"
                                                        )
                                                        log.DEBUG(
                                                            f"BNB  balance is [{balance_bnb}]"
                                                        )

                                                else:
                                                    with open(
                                                        f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                        "a",
                                                        encoding="utf8",
                                                    ) as f:
                                                        f.write(
                                                            f"\n\n{log.logging_time()} Within BUY (part VI):\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} BNB Buy order was NOT filled successfully! Please check the cause!\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} BNB Order (order) is {str(json.dumps(order))}\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} BNB Order status (order_status) is {str(json.dumps(order_status))}\n"
                                                        )
                                                    log.FATAL_7(
                                                        "BNB Buy order was NOT filled successfully! Please check the cause!"
                                                    )
                                            else:
                                                log.FATAL_7(
                                                    f"USDT balance [{balance_usdt}] is NOT enough to sustain many more transactions."
                                                )
                                        elif RYBKA_MODE == "DEMO":
                                            email_sender(
                                                f"{log.logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot doesn't have enough BNB in balance [{balance_bnb}] to sustain many more trades.\nAs we are in [RYBKA MODE - {RYBKA_MODE}] - bot will STOP at this point, as the user could've added infinite amounts of BNB at start, but decided not to.\n\n"
                                            )
                                            with open(
                                                f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                "a",
                                                encoding="utf8",
                                            ) as f:
                                                f.write(
                                                    f"\n\n{log.logging_time()} Within BUY (part X):\n"
                                                )
                                                f.write(
                                                    f"{log.logging_time()} BNB balance [{str(balance_bnb)}] is NOT enough to sustain many more transactions. As we are in [RYBKA MODE - {RYBKA_MODE}] - bot will STOP at this point, as the user could've added infinite amounts of BNB at start, but decided not to.\n"
                                                )
                                            log.FATAL_7(
                                                f"BNB balance [{balance_bnb}] is NOT enough to sustain many more transactions. As we are in [RYBKA MODE - {RYBKA_MODE}] - bot will STOP at this point, as the user could've added infinite amounts of BNB at start, but decided not to."
                                            )

                            if latest_rsi > RSI_FOR_SELL or bnb_conversion_done == 1:
                                log.INFO("================================")
                                log.INFO(f"          {bcolors.OKCYAN}SELL{bcolors.ENDC} SIGNAL!")
                                log.INFO("================================")

                                bnb_conversion_done = 0

                                if RYBKA_MODE == "LIVE":
                                    for i in range(1, 11):
                                        try:
                                            account_balance_update()
                                            log.DEBUG("Account Balance Sync. - Successful")
                                            break
                                        except Exception as e:
                                            if i == 10:
                                                traceback.print_exc()
                                                log.FATAL_7(
                                                    f"Account Balance Sync. - Failed as:\n{e}"
                                                )
                                            time.sleep(3)

                                real_time_balances_update()

                                with open(
                                    f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                    "a",
                                    encoding="utf8",
                                ) as f:
                                    f.write(f"\n\n\n{log.logging_time()} Within SELL (part I):\n")
                                    f.write(
                                        f'{log.logging_time()} {"Latest RSI (latest_rsi) is":90} {latest_rsi:40}\n'
                                    )
                                    f.write(
                                        f"{log.logging_time()} {'BNB balance (balance_bnb) is':90} {balance_bnb:40}\n"
                                    )
                                    f.write(
                                        f"{log.logging_time()} {'USDT balance (balance_usdt) is':90} {balance_usdt:40}\n"
                                    )
                                    f.write(
                                        f"{log.logging_time()} {'EGLD balance (balance_egld) is':90} {balance_egld:40}\n"
                                    )
                                    f.write(
                                        f"{log.logging_time()} {'Total USDT profit (total_usdt_profit) is':90} {total_usdt_profit:40}\n"
                                    )
                                    f.write(
                                        f"{log.logging_time()} {'Multiple sells (multiple_sells) set to':90} {multiple_sells:40}\n"
                                    )
                                    f.write(
                                        f"\n{log.logging_time()} {'Closed candles (multiple_sells) are':90} {closed_candles}\n"
                                    )
                                    f.write(
                                        f"\n{log.logging_time()} KTBR config (BEFORE processing) (str(json.dumps(ktbr_config))) is \n {str(json.dumps(ktbr_config))}\n\n"
                                    )

                                # To estimate if we have enough BNB for commissions on SELLing part for the bot, we have to calculate the possibility of allowing multiple_sells
                                # Hence we estimate selling half of the `ktbr` at median quantity and price in it and making sure we have over 5 times that amount in bnb, for commission
                                # which may not be 5 times exactly, as the trade_quantity and price are not evenly distributed across `ktbr` to begin with
                                if len(ktbr_config) == 0:
                                    ktbr_half_length = 2
                                    avg_coin_qtty = TRADE_QUANTITY
                                    avg_coin_price = candle_close_price
                                else:
                                    sum_coins = 0
                                    sum_price = 0

                                    for v in ktbr_config.values():
                                        sum_coins += float(v[0])
                                        sum_price += float(v[1])

                                    avg_coin_qtty = round(float(sum_coins / len(ktbr_config)), 4)
                                    avg_coin_price = round(float(sum_price / len(ktbr_config)), 4)
                                    ktbr_half_length = len(ktbr_config) / 2

                                if (
                                    round(
                                        float(
                                            (round(float(balance_bnb * bnb_candle_close_price), 6))
                                            / (
                                                round(
                                                    float(
                                                        0.08
                                                        / 100
                                                        * avg_coin_price
                                                        * avg_coin_qtty
                                                        * round(float(ktbr_half_length), 4)
                                                    ),
                                                    4,
                                                )
                                            )
                                        ),
                                        4,
                                    )
                                ) >= 5:
                                    log.DEBUG(
                                        f"BNB balance [{balance_bnb}] is enough for transactions."
                                    )

                                    eligible_sells = []

                                    for k, v in ktbr_config.items():
                                        future_fee = round(
                                            float(
                                                round(
                                                    float(0.08 / 100 * candle_close_price * v[0]), 4
                                                )
                                                / bnb_candle_close_price
                                            ),
                                            8,
                                        )
                                        log.VERBOSE(f"future_fee is {future_fee}")

                                        min_profit_aux = MIN_PROFIT

                                        while MIN_PROFIT - future_fee <= 0.8 * MIN_PROFIT:
                                            log.HIGH_VERBOSITY(
                                                f"NET MIN_PROFIT [{str(round(float(MIN_PROFIT - future_fee), 8))}] is less than 80% of MIN_PROFIT"
                                            )
                                            MIN_PROFIT += round(float(0.1 * MIN_PROFIT), 8)
                                            MIN_PROFIT = round(MIN_PROFIT, 8)
                                        else:
                                            log.DEBUG(
                                                f"MIN_PROFIT [{str(MIN_PROFIT)}] is more than 5x the fee [{str(future_fee)}] of the current possible sell transaction [{k}], qtty [{v[0]}] bought at price of [{v[1]}]"
                                            )

                                        if min_profit_aux != MIN_PROFIT:
                                            log.DEBUG(
                                                f"Value of [MIN_PROFIT] ENV var got adjusted from [{str(min_profit_aux)}] to [{str(MIN_PROFIT)}], as the fee tends to be pretty high [{str(future_fee)}] is raport to profit!"
                                            )

                                        if v[1] + MIN_PROFIT < candle_close_price:
                                            log.DEBUG(
                                                f"Identified buy ID [{k}], qtty [{v[0]}] bought at price of [{v[1]}] as being eligible for sell"
                                            )
                                            log.VERBOSE(f"Multiple sells set as [{multiple_sells}]")
                                            eligible_sells.append(k)
                                            if multiple_sells == "disabled":
                                                break
                                            elif len(eligible_sells) == 4:
                                                break

                                    log.INFO(" ")
                                    with open(
                                        f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                        "a",
                                        encoding="utf8",
                                    ) as f:
                                        f.write(
                                            f"\n\n\n{log.logging_time()} Within SELL (part II):\n"
                                        )
                                        f.write(
                                            f"{log.logging_time()} {'Eligible sells (eligible_sells) is':90} {str(eligible_sells)}\n"
                                        )

                                    if eligible_sells:
                                        for sell in eligible_sells:
                                            log.DEBUG(
                                                f"Selling buy [{sell}] of qtty [{ktbr_config[sell][0]}]"
                                            )

                                            try:
                                                if RYBKA_MODE == "LIVE":
                                                    order = client.order_market_sell(
                                                        symbol=TRADE_SYMBOL,
                                                        quantity=ktbr_config[sell][0],
                                                    )
                                                elif RYBKA_MODE == "DEMO":
                                                    order = {
                                                        "symbol": "EGLDUSDT",
                                                        "orderId": "",
                                                        "orderListId": -1,
                                                        "clientOrderId": "TXgNl8RNNipASGTrleH6ZY",
                                                        "transactTime": 1661098548719,
                                                        "price": "0.00000000",
                                                        "origQty": "0.19000000",
                                                        "executedQty": "0.19000000",
                                                        "cummulativeQuoteQty": "10.20300000",
                                                        "status": "FILLED",
                                                        "timeInForce": "GTC",
                                                        "type": "MARKET",
                                                        "side": "BUY",
                                                        "fills": [
                                                            {
                                                                "price": "",
                                                                "qty": "0.19000000",
                                                                "commission": "",
                                                                "commissionAsset": "EGLD",
                                                                "tradeId": 75747997,
                                                            }
                                                        ],
                                                    }
                                                    order["orderId"] = str(sell)
                                                    order["executedQty"] = ktbr_config[sell][0]
                                                    order["fills"][0]["price"] = candle_close_price
                                                    order["fills"][0]["commission"] = round(
                                                        float(
                                                            round(
                                                                float(
                                                                    0.08
                                                                    / 100
                                                                    * candle_close_price
                                                                    * ktbr_config[sell][0]
                                                                ),
                                                                4,
                                                            )
                                                            / bnb_candle_close_price
                                                        ),
                                                        8,
                                                    )

                                                    balance_usdt += (
                                                        candle_close_price * ktbr_config[sell][0]
                                                    )
                                                    balance_usdt = round(balance_usdt, 4)
                                                    balance_egld -= ktbr_config[sell][0]
                                                    balance_egld = round(balance_egld, 4)
                                                    balance_bnb -= round(
                                                        float(
                                                            round(
                                                                float(
                                                                    0.08
                                                                    / 100
                                                                    * candle_close_price
                                                                    * ktbr_config[sell][0]
                                                                ),
                                                                4,
                                                            )
                                                            / bnb_candle_close_price
                                                        ),
                                                        8,
                                                    )
                                                    balance_bnb = round(balance_bnb, 8)

                                                order_time = datetime.now().strftime(
                                                    "%d/%m/%Y %H:%M:%S"
                                                )
                                                log.DEBUG(
                                                    f"SELL Order placed now at [{order_time}]\n"
                                                )
                                                time.sleep(5)

                                                if RYBKA_MODE == "LIVE":
                                                    for i in range(1, 11):
                                                        try:
                                                            order_status = client.get_order(
                                                                symbol=TRADE_SYMBOL,
                                                                orderId=order["orderId"],
                                                            )
                                                            log.DEBUG(
                                                                "EGLD Sell Order status retrieval - Successful"
                                                            )
                                                            break
                                                        except Exception as e:
                                                            if i == 10:
                                                                traceback.print_exc()
                                                                log.FATAL_7(
                                                                    f"EGLD Sell Order status retrieval - Failed as:\n{e}"
                                                                )
                                                            time.sleep(3)

                                                elif RYBKA_MODE == "DEMO":
                                                    order_status = {
                                                        "symbol": "EGLDUSDT",
                                                        "orderId": 953796254,
                                                        "orderListId": -1,
                                                        "clientOrderId": "TXgNl8RNNipASGTrleH6ZY",
                                                        "price": "0.00000000",
                                                        "origQty": "0.19000000",
                                                        "executedQty": "0.19000000",
                                                        "cummulativeQuoteQty": "10.20300000",
                                                        "status": "FILLED",
                                                        "timeInForce": "GTC",
                                                        "type": "MARKET",
                                                        "side": "BUY",
                                                        "stopPrice": "0.00000000",
                                                        "icebergQty": "0.00000000",
                                                        "time": 1661098548719,
                                                        "updateTime": 1661098548719,
                                                        "isWorking": True,
                                                        "origQuoteOrderQty": "0.00000000",
                                                    }
                                                    order_status["orderId"] = str(sell)

                                                if order_status["status"] == "FILLED":
                                                    log.INFO_BOLD_UNDERLINE(
                                                        " ✅ SELL Order filled successfully!\n"
                                                    )
                                                    # avoid rounding up on quantity & price sold
                                                    qtty_aux = (
                                                        int(float(order["executedQty"]) * 10**4)
                                                        / 10**4
                                                    )
                                                    price_aux = (
                                                        int(
                                                            float(order["fills"][0]["price"])
                                                            * 10**4
                                                        )
                                                        / 10**4
                                                    )

                                                    log.INFO_SPECIAL(
                                                        f" 🟢 [{RYBKA_MODE}] Sold [{qtty_aux}] EGLD at price per 1 EGLD of [{price_aux}] USDT. Previously bought at [{str(ktbr_config[sell][1])}] USDT\n"
                                                    )
                                                    telegram.LOG(
                                                        f" 🟢 [[{RYBKA_MODE}]] Sold [[{qtty_aux}]] EGLD at [[{price_aux}]] USDT/EGLD.\nWas bought at [[{str(ktbr_config[sell][1])}]] USDT/EGLD",
                                                    )

                                                    usdt_trade_fee = round(
                                                        float(
                                                            0.08
                                                            / 100
                                                            * round(
                                                                float(order["cummulativeQuoteQty"]),
                                                                4,
                                                            )
                                                        ),
                                                        4,
                                                    )
                                                    log.VERBOSE(
                                                        f"SELL action's usdt trade fee is {usdt_trade_fee}"
                                                    )

                                                    total_usdt_profit = round(
                                                        int(
                                                            (
                                                                total_usdt_profit
                                                                + (price_aux - ktbr_config[sell][1])
                                                                * ktbr_config[sell][0]
                                                            )
                                                            * 10**4
                                                        )
                                                        / 10**4
                                                        - usdt_trade_fee,
                                                        4,
                                                    )
                                                    with open(
                                                        f"{RYBKA_MODE}/usdt_profit",
                                                        "w",
                                                        encoding="utf8",
                                                    ) as f:
                                                        f.write(str(total_usdt_profit))

                                                    bnb_commission = float(
                                                        order["fills"][0]["commission"]
                                                    )

                                                    with open(
                                                        f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                        "a",
                                                        encoding="utf8",
                                                    ) as f:
                                                        f.write(
                                                            f"\n\n{log.logging_time()} Within SELL (part III):\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} Selling buy [{str(sell)}] {'of qtty':90} [{str(ktbr_config[sell][0])}]\n"
                                                        )

                                                    previous_buy_info = f"What got sold: BUY ID [{str(sell)}] of QTTY [{str(ktbr_config[sell][0])}] at bought PRICE of [{str(ktbr_config[sell][1])}] USDT"

                                                    del ktbr_config[sell]
                                                    with open(
                                                        f"{RYBKA_MODE}/ktbr", "w", encoding="utf8"
                                                    ) as f:
                                                        f.write(str(json.dumps(ktbr_config)))

                                                    with open(
                                                        f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                        "a",
                                                        encoding="utf8",
                                                    ) as f:
                                                        f.write(
                                                            f"\n\n{log.logging_time()} Within SELL (part IV):\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} {'Order time (order_time) is':90} {str(order_time):40}"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} Transaction ID [{str(order['orderId'])}] - Sold [{qtty_aux}] EGLD at price per 1 EGLD of [{str(price_aux)}] USDT\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} {'Order (order) is':90} {str(json.dumps(order))}\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} {'Order status (order_status) is':90} {str(json.dumps(order_status))}\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} {'USDT trade fee (usdt_trade_fee) is':90} {str(usdt_trade_fee)}\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} {'Order commission is':90} {str(bnb_commission):40}\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} KTBR config (AFTER processing) (str(json.dumps(ktbr_config))) is {str(json.dumps(ktbr_config)):40}\n"
                                                        )

                                                    back_up()
                                                    move_and_replace("errors_thrown", RYBKA_MODE)
                                                    move_and_replace(
                                                        "full_order_history", RYBKA_MODE
                                                    )
                                                    move_and_replace(
                                                        f"{TRADE_SYMBOL}_DEBUG", current_export_dir
                                                    )
                                                    move_and_replace(
                                                        f"{TRADE_SYMBOL}_historical_prices",
                                                        current_export_dir,
                                                    )
                                                    move_and_replace(
                                                        f"BNB_USDT_historical_prices",
                                                        current_export_dir,
                                                    )
                                                    move_and_replace(
                                                        f"{TRADE_SYMBOL}_order_history",
                                                        current_export_dir,
                                                    )

                                                    if RYBKA_MODE == "LIVE":
                                                        for i in range(1, 11):
                                                            try:
                                                                account_balance_update()
                                                                log.DEBUG(
                                                                    "Account Balance Sync. - Successful"
                                                                )
                                                                break
                                                            except Exception as e:
                                                                if i == 10:
                                                                    traceback.print_exc()
                                                                    log.FATAL_7(
                                                                        f"Account Balance Sync. - Failed as:\n{e}"
                                                                    )
                                                                time.sleep(3)

                                                    real_time_balances_update()

                                                    log.DEBUG(f"USDT balance is [{balance_usdt}]")
                                                    log.DEBUG(f"EGLD balance is [{balance_egld}]")
                                                    log.DEBUG(f"BNB  balance is [{balance_bnb}]")

                                                    if RYBKA_MODE == "LIVE":
                                                        ktbr_integrity()

                                                    with open(
                                                        f"{current_export_dir}/{TRADE_SYMBOL}_order_history",
                                                        "a",
                                                        encoding="utf8",
                                                    ) as f:
                                                        f.write(
                                                            f"{log.logging_time()} Sell order done now at [{str(order_time)}]\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} Transaction ID [{order['orderId']}] - Sold [{str(qtty_aux)}] EGLD at price per 1 EGLD of [{str(price_aux)}] USDT\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} {previous_buy_info} \n\n\n"
                                                        )
                                                    with open(
                                                        f"{RYBKA_MODE}/full_order_history",
                                                        "a",
                                                        encoding="utf8",
                                                    ) as f:
                                                        f.write(
                                                            f"{log.logging_time()} Sell order done now at [{str(order_time)}]\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} Transaction ID [{order['orderId']}] - Sold [{str(qtty_aux)}] EGLD at price per 1 EGLD of [{str(price_aux)}] USDT\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} {previous_buy_info} \n\n\n"
                                                        )

                                                    if multiple_sells != "enabled":
                                                        subsequent_valid_rsi_counter = 2
                                                else:
                                                    with open(
                                                        f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                        "a",
                                                        encoding="utf8",
                                                    ) as f:
                                                        f.write(
                                                            f"\n\n{log.logging_time()} Within SELL (part V):\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} Sell order was NOT filled successfully! Please check the cause!\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} {'Order (order) is':90} {str(json.dumps(order))}\n"
                                                        )
                                                        f.write(
                                                            f"{log.logging_time()} {'Order status (order_status) is':90} {str(json.dumps(order_status))}\n"
                                                        )
                                                    log.FATAL_7(
                                                        "Sell order was NOT filled successfully! Please check the cause!"
                                                    )
                                            except Exception as e:
                                                with open(
                                                    f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                    "a",
                                                    encoding="utf8",
                                                ) as f:
                                                    f.write(
                                                        f"\n\n{log.logging_time()} Within SELL (part VI):\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} Order could NOT be placed due to an error:\n{e}\n"
                                                    )
                                                traceback.print_exc()
                                                log.FATAL_7(
                                                    f"Make sure the [RYBKA_BIN_KEY] and [RYBKA_BIN_SECRET] ENV vars have valid values and time server is synced with NIST's!\nOrder could NOT be placed due to an error:\n{e}"
                                                )
                                        re_sync_time()
                                    else:
                                        log.INFO(
                                            "No buy transactions are eligible to be sold at this moment!\n"
                                        )
                                        with open(
                                            f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                            "a",
                                            encoding="utf8",
                                        ) as f:
                                            f.write(
                                                f"\n\n{log.logging_time()} Within SELL (part VII):\n"
                                            )
                                            f.write(
                                                f"{log.logging_time()} No buy transactions are eligible to be sold at this moment!\n"
                                            )
                                else:
                                    if RYBKA_MODE == "LIVE":
                                        email_sender(
                                            f"{log.logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot doesn't have enough BNB in balance [{balance_bnb}] to sustain many more trades.\n\nHence, to avoid stopping the bot, Rybka will automatically convert a bit over 10 USDT into BNB. This does NOT take from Safety Net!"
                                        )
                                        with open(
                                            f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                            "a",
                                            encoding="utf8",
                                        ) as f:
                                            f.write(
                                                f"\n\n{log.logging_time()} Within BUY (part X):\n"
                                            )
                                            f.write(
                                                f"{log.logging_time()} BNB balance [{str(balance_bnb)}] is NOT enough to sustain many more transactions. Hence, to avoid stopping the bot, Rybka will automatically convert a bit over 10 USDT into BNB. This does NOT take from Safety Net!\n"
                                            )

                                        if round(float(balance_usdt - USDT_SAFETY_NET), 4) > 15:
                                            bnb_min_buy_share = bnb_candle_close_price / 12
                                            bnb_min_order_quantity = round(
                                                float(1 / bnb_min_buy_share), 3
                                            )

                                            # treating the rare case of a sky-high price of BNB (of 24001 or above, in USDT), scenario in which the value of `bnb_min_order_quantity` would be equal to `0.0`
                                            if bnb_min_order_quantity == 0:
                                                bnb_min_order_quantity = 0.001

                                            order = client.order_market_buy(
                                                symbol="BNBUSDT",
                                                quantity=bnb_min_order_quantity,
                                            )

                                            bnb_conversion_done = 1

                                            order_time = datetime.now().strftime(
                                                "%d/%m/%Y %H:%M:%S"
                                            )
                                            log.DEBUG(
                                                f"BNB BUY Order placed now at [{order_time}]\n"
                                            )
                                            log.VERBOSE(
                                                f"bnb_min_order_quantity is [{str(bnb_min_order_quantity)}]\n"
                                            )
                                            log.VERBOSE(
                                                f"bnb_candle_close_price is [{str(bnb_candle_close_price)}]\n"
                                            )
                                            log.VERBOSE(
                                                f"bnb_min_buy_share is [{str(bnb_min_buy_share)}]\n"
                                            )

                                            time.sleep(25)

                                            with open(
                                                f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                "a",
                                                encoding="utf8",
                                            ) as f:
                                                f.write(
                                                    f"\n\n\n{log.logging_time()} Within BNB buy order (part II):\n"
                                                )
                                                f.write(
                                                    f'{log.logging_time()} {"bnb_min_order_quantity":90} {str(bnb_min_order_quantity)}\n'
                                                )
                                                f.write(
                                                    f'{log.logging_time()} {"bnb_candle_close_price":90} {str(bnb_candle_close_price)}\n'
                                                )
                                                f.write(
                                                    f'{log.logging_time()} {"bnb_min_buy_share":90} {str(bnb_min_buy_share)}\n'
                                                )

                                            for i in range(1, 11):
                                                try:
                                                    order_status = client.get_order(
                                                        symbol="BNBUSDT",
                                                        orderId=order["orderId"],
                                                    )
                                                    log.DEBUG(
                                                        "2. BNB Buy Order status retrieval - Successful"
                                                    )
                                                    break
                                                except Exception as e:
                                                    if i == 10:
                                                        traceback.print_exc()
                                                        log.FATAL_7(
                                                            f"2. BNB Buy Order status retrieval - Failed as:\n{e}"
                                                        )
                                                    time.sleep(3)

                                            with open(
                                                f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                "a",
                                                encoding="utf8",
                                            ) as f:
                                                f.write(
                                                    f"\n\n\n{log.logging_time()} Within BNB buy order (part II):\n"
                                                )
                                                f.write(
                                                    f'{log.logging_time()} {"Order status is":90} {str(order_status)}\n'
                                                )

                                            if order_status["status"] == "FILLED":
                                                log.INFO_BOLD_UNDERLINE(
                                                    " ✅ BNB BUY Order filled successfully!\n"
                                                )

                                                # avoid rounding up on quantity & price bought
                                                log.INFO_SPECIAL(
                                                    f" ☑️  ♻️  Bought [{int(float(order['executedQty']) * 10 ** 8) / 10 ** 8}] BNB at price per 1 BNB of [{int(float(order['fills'][0]['price']) * 10 ** 8) / 10 ** 8}] USDT\n"
                                                )
                                                telegram.LOG(
                                                    f" ☑️ ♻️ Bought [[{int(float(order['executedQty']) * 10 ** 8) / 10 ** 8}]] BNB at [[{int(float(order['fills'][0]['price']) * 10 ** 8) / 10 ** 8}]] USDT/BNB",
                                                )

                                                for i in range(1, 11):
                                                    try:
                                                        account_balance_update()
                                                        log.DEBUG(
                                                            "Account Balance Sync. - Successful"
                                                        )
                                                        break
                                                    except Exception as e:
                                                        if i == 10:
                                                            traceback.print_exc()
                                                            log.FATAL_7(
                                                                f"Account Balance Sync. - Failed as:\n{e}"
                                                            )
                                                        time.sleep(3)

                                                real_time_balances_update()

                                                if DEBUG_LVL != 3:
                                                    log.DEBUG(f"USDT balance is [{balance_usdt}]")
                                                    log.DEBUG(f"EGLD balance is [{balance_egld}]")
                                                    log.DEBUG(f"BNB  balance is [{balance_bnb}]")

                                            else:
                                                with open(
                                                    f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                                    "a",
                                                    encoding="utf8",
                                                ) as f:
                                                    f.write(
                                                        f"\n\n{log.logging_time()} Within BUY (part VI):\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} BNB Buy order was NOT filled successfully! Please check the cause!\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} BNB Order (order) is {str(json.dumps(order))}\n"
                                                    )
                                                    f.write(
                                                        f"{log.logging_time()} BNB Order status (order_status) is {str(json.dumps(order_status))}\n"
                                                    )
                                                log.FATAL_7(
                                                    "BNB Buy order was NOT filled successfully! Please check the cause!"
                                                )
                                        else:
                                            log.FATAL_7(
                                                f"USDT balance [{balance_usdt}] is NOT enough to sustain many more transactions."
                                            )
                                    elif RYBKA_MODE == "DEMO":
                                        email_sender(
                                            f"{log.logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot doesn't have enough BNB in balance [{balance_bnb}] to sustain many more trades.\nAs we are in [RYBKA MODE - {RYBKA_MODE}] - bot will STOP at this point, as the user could've added infinite amounts of BNB at start, but decided not to.\n\n"
                                        )
                                        with open(
                                            f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG",
                                            "a",
                                            encoding="utf8",
                                        ) as f:
                                            f.write(
                                                f"\n\n{log.logging_time()} Within SELL (part VIII):\n"
                                            )
                                            f.write(
                                                f"{log.logging_time()} BNB balance [{str(balance_bnb)}] is NOT enough to sustain many more transactions. As we are in [RYBKA MODE - {RYBKA_MODE}] - bot will STOP at this point, as the user could've added infinite amounts of BNB at start, but decided not to.\n"
                                            )
                                        log.FATAL_7(
                                            f"BNB balance [{balance_bnb}] is NOT enough to sustain many more transactions. As we are in [RYBKA MODE - {RYBKA_MODE}] - bot will STOP at this point, as the user could've added infinite amounts of BNB at start, but decided not to."
                                        )

                        if RYBKA_MODE == "LIVE":
                            if random.randint(1, 60) <= 2:
                                for i in range(1, 11):
                                    try:
                                        account_balance_update()
                                        log.DEBUG("Account Balance Sync. - Successful")
                                        break
                                    except Exception as e:
                                        if i == 10:
                                            traceback.print_exc()
                                            log.FATAL_7(f"Account Balance Sync. - Failed as:\n{e}")
                                        time.sleep(3)
                                real_time_balances_update()

    except KeyboardInterrupt:
        print(
            f"{bcolors.CRED}{bcolors.BOLD}❌ [{RYBKA_MODE}] [FATAL (7)] {log.logging_time()}  > Process stopped by user. Wait a few seconds!\n{bcolors.ENDC}"
        )
        unicorn_stream_obj.stop_manager_with_all_streams()
        log.FATAL_7(f" 🔴 ⓇⓎⒷⓀⒶⒸⓄⓇⒺ 🔴\n          [[{RYBKA_MODE} mode]]\n")

    except Exception as e:
        print(
            f"{bcolors.CRED}{bcolors.BOLD}❌ [{RYBKA_MODE}] [FATAL (7)] {log.logging_time()}      > Stopping ... just wait a few seconds!\n{e}{bcolors.ENDC}"
        )
        traceback.print_exc()
        unicorn_stream_obj.stop_manager_with_all_streams()
        email_sender(
            f"{log.logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot STOPPED working.\n\n Check terminal / log files for more details."
        )
        log.FATAL_7(f" 🔴 ⓇⓎⒷⓀⒶⒸⓄⓇⒺ 🔴\n          [[{RYBKA_MODE} mode]]\n")


if __name__ == "__main__":
    ###############################################
    ###########     TIME MANAGEMENT     ###########
    ###############################################

    start_time = time.time()
    uptime = ""

    ###############################################
    ########          GLOBAL VARS          ########
    ###############################################

    WEIGHTS_DICT_OUTDATED = {}
    WEIGHTS_DICT_UPDATED = {}

    ###############################################
    ########   GLOBAL VARS from ENV VARS   ########
    ###############################################

    TRADE_SYMBOL = bootstrap.TRADE_SYMBOL
    SOCKET = bootstrap.SOCKET
    RSI_PERIOD = bootstrap.RSI_PERIOD

    RYBKA_EMAIL_SENDER_DEVICE_PASSWORD = bootstrap.RYBKA_EMAIL_SENDER_DEVICE_PASSWORD

    def bootstraping_vars():
        variables_reinitialization()
        from custom_modules.cfg import bootstrap

        global WEIGHTS_DICT_OUTDATED, WEIGHTS_DICT_UPDATED, TELEGRAM_WEIGHTS

        global DEBUG_LVL, RSI_FOR_BUY, RSI_FOR_SELL, TRADING_BOOST_LVL
        global TRADE_QUANTITY, AUX_TRADE_QUANTITY, MIN_PROFIT, USDT_SAFETY_NET
        global RYBKA_EMAIL_SWITCH, RYBKA_EMAIL_SENDER_EMAIL, RYBKA_EMAIL_RECIPIENT_EMAIL, RYBKA_EMAIL_RECIPIENT_NAME
        global RYBKA_TELEGRAM_SWITCH
        global RYBKA_ALL_LOG_TLG_SWITCH
        global RYBKA_BALANCES_AUX
        global SET_DISCLAIMER

        DEBUG_LVL = bootstrap.DEBUG_LVL

        TRADING_BOOST_LVL = bootstrap.TRADING_BOOST_LVL
        if TRADING_BOOST_LVL not in [1, 2, 3, 4, 5]:
            log.FATAL_7(
                f"Please consult [README.md] file for valid values of [RYBKA_TRADING_BOOST_LVL] var.\n[{str(TRADING_BOOST_LVL)}] is not a valid value!"
            )

        RSI_FOR_BUY = bootstrap.RSI_FOR_BUY
        RSI_FOR_SELL = bootstrap.RSI_FOR_SELL

        TRADE_QUANTITY = round(bootstrap.TRADE_QUANTITY, 2)
        AUX_TRADE_QUANTITY = TRADE_QUANTITY
        MIN_PROFIT = bootstrap.MIN_PROFIT
        USDT_SAFETY_NET = bootstrap.USDT_SAFETY_NET

        RYBKA_EMAIL_SWITCH = bootstrap.RYBKA_EMAIL_SWITCH
        RYBKA_EMAIL_SENDER_EMAIL = bootstrap.RYBKA_EMAIL_SENDER_EMAIL
        RYBKA_EMAIL_RECIPIENT_EMAIL = bootstrap.RYBKA_EMAIL_RECIPIENT_EMAIL
        RYBKA_EMAIL_RECIPIENT_NAME = bootstrap.RYBKA_EMAIL_RECIPIENT_NAME

        RYBKA_TELEGRAM_SWITCH = bootstrap.RYBKA_TELEGRAM_SWITCH
        RYBKA_ALL_LOG_TLG_SWITCH = bootstrap.RYBKA_ALL_LOG_TLG_SWITCH
        RYBKA_BALANCES_AUX = bootstrap.RYBKA_BALANCES_AUX

        SET_DISCLAIMER = bootstrap.SET_DISCLAIMER

        def parse_weights():
            WEIGHTS_DICT_UPDATED.update({"RYBKA_DEBUG_LVL": DEBUG_LVL})
            WEIGHTS_DICT_UPDATED.update({"RYBKA_TRADING_BOOST_LVL": TRADING_BOOST_LVL})
            WEIGHTS_DICT_UPDATED.update({"RYBKA_RSI_FOR_BUY": RSI_FOR_BUY})
            WEIGHTS_DICT_UPDATED.update({"RYBKA_RSI_FOR_SELL": RSI_FOR_SELL})
            WEIGHTS_DICT_UPDATED.update({"RYBKA_TRADE_QUANTITY": TRADE_QUANTITY})
            WEIGHTS_DICT_UPDATED.update({"RYBKA_MIN_PROFIT": MIN_PROFIT})
            WEIGHTS_DICT_UPDATED.update({"RYBKA_USDT_SAFETY_NET": USDT_SAFETY_NET})
            WEIGHTS_DICT_UPDATED.update({"RYBKA_EMAIL_SWITCH": RYBKA_EMAIL_SWITCH})
            WEIGHTS_DICT_UPDATED.update({"RYBKA_EMAIL_SENDER_EMAIL": RYBKA_EMAIL_SENDER_EMAIL})
            WEIGHTS_DICT_UPDATED.update(
                {"RYBKA_EMAIL_RECIPIENT_EMAIL": RYBKA_EMAIL_RECIPIENT_EMAIL}
            )
            WEIGHTS_DICT_UPDATED.update({"RYBKA_EMAIL_RECIPIENT_NAME": RYBKA_EMAIL_RECIPIENT_NAME})
            WEIGHTS_DICT_UPDATED.update({"RYBKA_TELEGRAM_SWITCH": RYBKA_TELEGRAM_SWITCH})
            WEIGHTS_DICT_UPDATED.update({"RYBKA_ALL_LOG_TLG_SWITCH": RYBKA_ALL_LOG_TLG_SWITCH})
            WEIGHTS_DICT_UPDATED.update({"RYBKA_BALANCES_AUX": RYBKA_BALANCES_AUX})
            WEIGHTS_DICT_UPDATED.update({"RYBKA_DISCLAIMER": SET_DISCLAIMER})

        if not WEIGHTS_DICT_UPDATED:
            parse_weights()
            WEIGHTS_DICT_OUTDATED = WEIGHTS_DICT_UPDATED.copy()
        else:
            parse_weights()
            for k in WEIGHTS_DICT_UPDATED.keys():
                if (
                    WEIGHTS_DICT_UPDATED[k] != WEIGHTS_DICT_OUTDATED[k]
                    and k != "RYBKA_BALANCES_AUX"
                ):
                    log.INFO(" ")
                    log.INFO_SPECIAL(
                        f" ⚖️  Rybka's weight: [{k.replace('_',' ')}] got updated from [{WEIGHTS_DICT_OUTDATED[k]}] to [{WEIGHTS_DICT_UPDATED[k]}]!"
                    )
                    telegram.LOG(
                        f" 🟢 Rybka's weight:\n[[{k.replace('_',' ')}]]\n\n⇢ updated from [[{WEIGHTS_DICT_OUTDATED[k]}]] to [[{WEIGHTS_DICT_UPDATED[k]}]]!",
                    )
                    log.INFO(" ")
                    WEIGHTS_DICT_OUTDATED.update({k: WEIGHTS_DICT_UPDATED[k]})

        TELEGRAM_WEIGHTS = WEIGHTS_DICT_UPDATED.copy()
        TELEGRAM_WEIGHTS.update({"RYBKA_TRADE_SYMBOL": bootstrap.TRADE_SYMBOL})
        TELEGRAM_WEIGHTS.update({"RYBKA_RSI_PERIOD": bootstrap.RSI_PERIOD})

        with open("TEMP/weightsTmp", "w", encoding="utf8") as f:
            f.write(json.dumps((TELEGRAM_WEIGHTS)))

    bootstraping_vars()

    ###############################################
    ###########       GLOBAL VARS       ###########
    ###############################################

    RYBKA_MODE = ""
    ktbr_config = {}
    closed_candles = []
    client = ""

    total_usdt_profit = 0

    multiple_sells = "disabled"
    nr_of_trades = 0
    subsequent_valid_rsi_counter = 0

    current_export_dir = ""

    main()
