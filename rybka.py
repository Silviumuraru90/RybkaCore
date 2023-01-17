#!/usr/bin/env python3

# Built-in and Third-Party Libs
import websocket
import json
import talib
import numpy
import os
import time
import random
import smtplib
import platform
import socket
import re
import uuid
import shutil
import math
import subprocess
import ctypes
import click

import string as string_str

from datetime import datetime
from string import Template
from binance.client import Client
from binance.enums import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import exists
from sys import platform


def current_dir_path_export():
    current_dir_path = os.path.dirname(os.path.abspath(__file__))
    os.environ["CURRENT_DIR_PATH"] = current_dir_path

current_dir_path_export()

# Custom Libs
from custom_modules.cfg import bootstrap
from custom_modules.cfg import variables_reinitialization
from custom_modules.logging.logging import bcolors
from custom_modules.logging.logging import log
from custom_modules.telegram.telegram_passive import telegram



###############################################
########      UNIQUE ID FUNCTION      #########
###############################################

def id_generator(size=10, chars=string_str.ascii_uppercase + string_str.digits):
    return ''.join(random.choice(chars) for elem in range(size))



###############################################
#########      ACCOUNT FUNCTIONS      #########
###############################################


def user_initial_config():
    global client
    try:
        client = Client(bootstrap.BIN_KEY, bootstrap.BIN_SECRET)
        log.INFO_BOLD(f" ✅ Client initial config  -  {bcolors.PURPLE}DONE")
    except Exception as e:
        log.FATAL_7(f"Client initial config  -  FAILED\nError encountered at setting user config. via API KEY and API SECRET. Please check error below:\n{e}")


def binance_system_status():
    global client
    binance_status = client.get_system_status()
    if binance_status["status"] == 0:
        log.INFO_BOLD(f" ✅ Binance servers status -  {bcolors.PURPLE}{binance_status['msg'].upper()}")
    else:
        log.FATAL_7(f"Binance servers status -  {binance_status['msg'].upper()}")


def binance_account_status():
    global client
    acc_status = client.get_account_status()
    if acc_status['data'].upper() == "NORMAL":
        log.INFO_BOLD(f" ✅ Binance acc. status    -  {bcolors.PURPLE}{acc_status['data'].upper()}")
    else:
        log.FATAL_7(f"Binance acc. status    -  {acc_status['data'].upper()}")


def binance_api_account_status():
    global client
    acc_api_status = client.get_account_api_trading_status()
    if acc_api_status['data']['isLocked'] is False:
        log.INFO_BOLD(f" ✅ API acc. locked status -  {bcolors.PURPLE}{str(acc_api_status['data']['isLocked']).upper()}")
    else:
        log.FATAL_7(f"API acc. locked status -  {str(acc_api_status['data']['isLocked']).upper()}\nLocked status duration is - {acc_api_status['data']['plannedRecoverTime']}")


def account_balance_update():
    global client
    global balance_usdt
    global balance_egld
    global balance_bnb
    global locked_balance_usdt
    global locked_balance_egld
    global locked_balance_bnb

    balance_aux_usdt = client.get_asset_balance(asset='USDT')
    if float(balance_aux_usdt['free']) == round(float(balance_aux_usdt['free']), 4):
        balance_usdt = round(float(balance_aux_usdt['free']), 4)
    else:
        balance_usdt = round(float(balance_aux_usdt['free']) + 0.0001, 4)
    locked_balance_usdt = round(float(balance_aux_usdt['locked']), 4)

    balance_aux_egld = client.get_asset_balance(asset='EGLD')
    if float(balance_aux_egld['free']) == round(float(balance_aux_egld['free']), 4):
        balance_egld = round(float(balance_aux_egld['free']), 4)
    else:
        balance_egld = round(float(balance_aux_egld['free']) + 0.0001, 4)
    locked_balance_egld = round(float(balance_aux_egld['locked']), 4)

    balance_aux_bnb = client.get_asset_balance(asset='BNB')
    balance_bnb = round(float(balance_aux_bnb['free']), 6)
    locked_balance_bnb = round(float(balance_aux_bnb['locked']), 6)



###############################################
#######   FILE MANIPULATION FUNCTIONS   #######
###############################################


def log_files_creation(direct_call="1"):
    global current_export_dir

    try:
        if direct_call == "1":

            os.mkdir(current_export_dir)

            with open(f"{current_export_dir}/{TRADE_SYMBOL}_historical_prices", 'w', encoding="utf8") as f:
                f.write(f'Here is a detailed view of the history of candle prices for the [{TRADE_SYMBOL}] currency pair:\n\n')
            with open(f"{current_export_dir}/{TRADE_SYMBOL}_order_history", 'w', encoding="utf8") as f:
                f.write(f'Here is a detailed view of the history of orders done for the [{TRADE_SYMBOL}] currency pair:\n\n')
            with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'w', encoding="utf8") as f:
                f.write(f'DEBUG logs for the [{TRADE_SYMBOL}] currency pair:\n\n')
        
        with open(f"{current_export_dir}/{TRADE_SYMBOL}_weights", 'w', encoding="utf8") as f:
            f.write(f'Here is a detailed view of weights set for the [{TRADE_SYMBOL}] currency pair:\n\n')
            f.write(f"RYBKA_MODE      set to: {RYBKA_MODE:>50}\n")
            if DEBUG_LVL:
                f.write(f"DEBUG_LVL       set to: {DEBUG_LVL:>50}")
            f.write(f"SOCKET          set to: {SOCKET:>50}\n")
            f.write(f"TRADE SYMBOL    set to: {TRADE_SYMBOL:>50}\n")
            f.write(f"TRADE QUANTITY  set to: {TRADE_QUANTITY:>50} coins per transaction\n")
            f.write(f"MIN PROFIT      set to: {MIN_PROFIT:>50} USDT per transaction\n")
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
        log.FATAL_7(f"Attempt to create local folder [{current_export_dir}] and inner files for output analysis FAILED - with error:\n{e}")
        


def rybka_mode_folder_creation():
    global RYBKA_MODE
    if os.path.isdir(RYBKA_MODE) is False:
        try:
            os.makedirs(RYBKA_MODE)
        except Exception as e:
            log.FATAL_7(f"Attempt to create local folder for the mode in which software runs - [{RYBKA_MODE}] - FAILED with error:\n{e}")


def TMP_folder(folder):
    if os.path.isdir(folder) is False:
        try:
            os.makedirs(folder)
        except Exception as e:
            log.FATAL_7(f"Attempt to create local folder [{folder}] - FAILED with error:\n{e}")


def ktbr_configuration():
    global ktbr_config
    global RYBKA_MODE
    log.INFO("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/ktbr"):
        with open(f"{RYBKA_MODE}/ktbr", 'r', encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/ktbr").st_size == 0:
                log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/ktbr] file exists and is empty")
            else:
                try:
                    ktbr_config = json.loads(f.read())
                    log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/ktbr] file contains the following past transactions:\n")
                    for k, v in ktbr_config.items():
                        log.INFO(f" 💳 Transaction [{k}]  ---  [{bcolors.OKGREEN}{bcolors.BOLD}{v[0]}{bcolors.ENDC}{bcolors.DARKGRAY}] \t EGLD bought at price of [{bcolors.OKGREEN}{bcolors.BOLD}{v[1]}{bcolors.ENDC}{bcolors.DARKGRAY}] \t USDT per EGLD{bcolors.ENDC}")
                except Exception as e:
                    log.FATAL_7(f"[{RYBKA_MODE}/ktbr] file contains wrong formatted content!\nFailing with error:\n{e}")
    else:
        try:
            open(f"{RYBKA_MODE}/ktbr", 'w', encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/ktbr] file created!")
        except Exception as e:
            log.FATAL_7(f"[{RYBKA_MODE}/ktbr] file could NOT be created!\nFailing with error:\n{e}")
    log.INFO("=====================================================================================================================================")


def profit_file():
    global total_usdt_profit
    global RYBKA_MODE
    log.VERBOSE("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/usdt_profit"):
        with open(f"{RYBKA_MODE}/usdt_profit", 'r', encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/usdt_profit").st_size == 0:
                log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/usdt_profit] file exists and is empty")
            else:
                try:
                    total_usdt_profit = round(float(f.read()), 4)
                    log.VERBOSE(f" ✅ [{RYBKA_MODE}/usdt_profit] file contains the following already done profit: [{bcolors.PURPLE}{total_usdt_profit}{bcolors.DARKGRAY}] USDT")
                except Exception as e:
                    log.FATAL_7(f"[{RYBKA_MODE}/usdt_profit] file contains wrong formatted content!\nFailing with error:\n{e}")
    else:
        try:
            open(f"{RYBKA_MODE}/usdt_profit", 'w', encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/usdt_profit] file created!")
        except Exception as e:
            log.FATAL_7(f"[{RYBKA_MODE}/usdt_profit] file could NOT be created!\nFailing with error:\n{e}")
    log.VERBOSE("=====================================================================================================================================")


def commission_file():
    global bnb_commission
    global RYBKA_MODE
    log.VERBOSE("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/most_recent_commission"):
        with open(f"{RYBKA_MODE}/most_recent_commission", 'r', encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/most_recent_commission").st_size == 0:
                log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/most_recent_commission] file exists and is empty")
            else:
                try:
                    bnb_commission = float(f.read())
                    log.VERBOSE(f" ✅ [{RYBKA_MODE}/most_recent_commission] file contains the following most recent paid fee: [{bnb_commission}] BNB")
                except Exception as e:
                    log.FATAL_7(f"[{RYBKA_MODE}/most_recent_commission] file contains wrong formatted content!\nFailing with error:\n{e}")
    else:
        try:
            open(f"{RYBKA_MODE}/most_recent_commission", 'w', encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/most_recent_commission] file created!")
        except Exception as e:
            log.FATAL_7(f"[{RYBKA_MODE}/most_recent_commission] file could NOT be created!\nFailing with error:\n{e}")
    log.VERBOSE("=====================================================================================================================================")


def nr_of_trades_file():
    global nr_of_trades
    global RYBKA_MODE
    log.INFO("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/number_of_buy_trades"):
        with open(f"{RYBKA_MODE}/number_of_buy_trades", 'r', encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/number_of_buy_trades").st_size == 0:
                log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/number_of_buy_trades] file exists and is empty")
            else:
                try:
                    nr_of_trades = int(f.read())
                    log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/number_of_buy_trades] file shows historical nr. of buy trades raising to: [{bcolors.PURPLE}{nr_of_trades}{bcolors.DARKGRAY}]")
                except Exception as e:
                    log.FATAL_7(f"[{RYBKA_MODE}/number_of_buy_trades] file contains wrong formatted content!\nFailing with error:\n{e}")
    else:
        try:
            open(f"{RYBKA_MODE}/number_of_buy_trades", 'w', encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/number_of_buy_trades] file created!")
        except Exception as e:
            log.FATAL_7(f"[{RYBKA_MODE}/number_of_buy_trades] file could NOT be created!\nFailing with error:\n{e}")
    log.INFO("=====================================================================================================================================")


def full_order_history_file():
    global RYBKA_MODE
    log.INFO("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/full_order_history"):
        with open(f"{RYBKA_MODE}/full_order_history", 'r', encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/full_order_history").st_size == 0:
                log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/full_order_history] file exists and is empty")
            else:
                log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/full_order_history] file exists and contains past information!")
    else:
        try:
            open(f"{RYBKA_MODE}/full_order_history", 'w', encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/full_order_history] file created!")
        except Exception as e:
            log.FATAL_7(f"[{RYBKA_MODE}/full_order_history] file could NOT be created!\nFailing with error:\n{e}")
    log.INFO("=====================================================================================================================================")


def real_time_balances():
    global RYBKA_MODE
    log.INFO("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/real_time_balances"):
        log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/real_time_balances] file already exists!")
    else:
        try:
            open(f"{RYBKA_MODE}/real_time_balances", 'w', encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/real_time_balances] file created!")
        except Exception as e:
            log.FATAL_7(f"[{RYBKA_MODE}/real_time_balances] file could NOT be created!\nFailing with error:\n{e}")
    log.INFO("=====================================================================================================================================")


def ktbr_integrity():
    global balance_egld
    global RYBKA_MODE
    ktbr_config_check={}
    sum_of_ktbr_cryptocurrency = 0
    
    with open(f"{RYBKA_MODE}/ktbr", 'r', encoding="utf8") as f:
        ktbr_config_check = json.loads(f.read())

        for v in ktbr_config_check.values():
            sum_of_ktbr_cryptocurrency+=v[0]

        log.VERBOSE(f"ktbr_config_check is {ktbr_config_check}")
        log.VERBOSE(f"sum_of_ktbr_cryptocurrency rounded is {round(sum_of_ktbr_cryptocurrency, 4)}")
        log.VERBOSE(f"ktbr_integrity()'s egld balance is {balance_egld}")
        
        if round(sum_of_ktbr_cryptocurrency, 4) <= balance_egld:
            log.DEBUG(" ✅ KTBR integrity status  -  VALID\n")
        else:
            log.FATAL_7("KTBR integrity status  -  INVALID\nThis means that the amount of EGLD you have in cloud is actually less now, than what you retain in the 'ktbr' file. Probably you've spent a part of it in the meantime.")

def all_errors_file():
    global RYBKA_MODE
    log.INFO("==============================================")
    if exists(f"{RYBKA_MODE}/errors_thrown"):
        log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/errors_thrown] file already exists!")
    else:
        try:
            open(f"{RYBKA_MODE}/errors_thrown", 'w', encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/errors_thrown] file created!")
        except Exception as e:
            log.FATAL_7(f"[{RYBKA_MODE}/errors_thrown] file could NOT be created!\nFailing with error:\n{e}")
    log.INFO("==============================================")


###############################################
##############   AUX FUNCTIONS   ##############
###############################################



def back_up():
    global RYBKA_MODE

    back_up_dir = f'{current_export_dir}/{RYBKA_MODE}_BACK_UPS/LOGS_AT_{datetime.now().strftime("%d_%m_%Y")}_{datetime.now().strftime("%H_%M_%S")}'
    if os.path.isdir(back_up_dir) is False:
        os.makedirs(back_up_dir)

    shutil.copyfile(f'{RYBKA_MODE}/number_of_buy_trades', f"{back_up_dir}/number_of_buy_trades")
    shutil.copyfile(f'{RYBKA_MODE}/most_recent_commission', f"{back_up_dir}/most_recent_commission")
    shutil.copyfile(f'{RYBKA_MODE}/usdt_profit', f"{back_up_dir}/usdt_profit")
    shutil.copyfile(f'{RYBKA_MODE}/ktbr', f"{back_up_dir}/ktbr")


def software_config_params():
    print("\n\n")
    log.ORANGE(f"\t\t\t\t██████╗░██╗░░░██╗██████╗░██╗░░██╗░█████╗░")
    log.ORANGE(f"\t\t\t\t██╔══██╗╚██╗░██╔╝██╔══██╗██║░██╔╝██╔══██╗")
    log.ORANGE(f"\t\t\t\t██████╔╝░╚████╔╝░██████╦╝█████═╝░███████║")
    log.ORANGE(f"\t\t\t\t██╔══██╗░░╚██╔╝░░██╔══██╗██╔═██╗░██╔══██║")
    log.ORANGE(f"\t\t\t\t██║░░██║░░░██║░░░██████╦╝██║░╚██╗██║░░██║")
    log.ORANGE(f"\t\t\t\t╚═╝░░╚═╝░░░╚═╝░░░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝\n")
    log.ORANGE(f"\t\t\t\t             - MODE: {RYBKA_MODE} -           \n\n")
                    
    log.INFO(f"Rybka software started with the following parameters:\n")
    log.INFO_BOLD(f" 🔘 RYBKA_MODE      set to: {bcolors.PURPLE}{RYBKA_MODE:>50}")
    if DEBUG_LVL:
        log.INFO_BOLD(f"{bcolors.OKCYAN} 🔘 DEBUG_LVL       set to: {DEBUG_LVL:>50}{bcolors.ENDC}")
    log.INFO_BOLD(f" 🔘 SOCKET          set to: {bcolors.PURPLE}{SOCKET:>50}")
    log.INFO_BOLD(f" 🔘 TRADE SYMBOL    set to: {bcolors.PURPLE}{TRADE_SYMBOL:>50}")
    log.INFO_BOLD(f" 🔘 TRADE QUANTITY  set to: {bcolors.PURPLE}{TRADE_QUANTITY:>50}{bcolors.DARKGRAY} coins per transaction")
    log.INFO_BOLD(f" 🔘 MIN PROFIT      set to: {bcolors.PURPLE}{MIN_PROFIT:>50}{bcolors.DARKGRAY} USDT per transaction")
    log.INFO_BOLD(f" 🔘 RSI PERIOD      set to: {bcolors.PURPLE}{RSI_PERIOD:>50}{bcolors.DARKGRAY} minutes")
    log.INFO_BOLD(f" 🔘 RSI FOR BUY     set to: {bcolors.PURPLE}{RSI_FOR_BUY:>50}{bcolors.DARKGRAY} threshold")
    log.INFO_BOLD(f" 🔘 RSI FOR SELL    set to: {bcolors.PURPLE}{RSI_FOR_SELL:>50}{bcolors.DARKGRAY} threshold")
    log.INFO_BOLD(f" 🔘 EMAIL SWITCH    set to: {bcolors.PURPLE}{str(RYBKA_EMAIL_SWITCH):>50}")
    log.INFO_BOLD(f" 🔘 Telegram SWITCH set to: {bcolors.PURPLE}{str(RYBKA_TELEGRAM_SWITCH):>50}")
    if RYBKA_EMAIL_SENDER_EMAIL and RYBKA_EMAIL_RECIPIENT_EMAIL:
        log.INFO_BOLD(f" 🔘 SENDER EMAIL    set to: {bcolors.PURPLE}{RYBKA_EMAIL_SENDER_EMAIL:>50}")
        log.INFO_BOLD(f" 🔘 RECIPIENT EMAIL set to: {bcolors.PURPLE}{RYBKA_EMAIL_RECIPIENT_EMAIL:>50}")
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
    print(f"\t  ❌ DO NOT SET MANUALLY ANY OTHER ORDERS WITH THE TRADING PAIR [{TRADE_SYMBOL}]'s PARTS YOU RUN THIS BOT AGAINST! \n")
    time.sleep(7)
    print("\t  ❌ DO NOT CONVERT EGLD INTO ANY OTHER CURRENCY; OR IF YOU DO, DELETE THE TRADING QUANTITY FROM THE KTBR FILE, TO ASSURE THE GOOD FUTURE FUNCTIONING OF THE BOT! STOP THE BOT BEFORE DOING SUCH CHANGES, RESTART IT AFTER! \n\n\n")
    time.sleep(13)
    print("\t\t  YOU ARE ALLOWED TO: \n")
    time.sleep(2)
    print(f"\t  ✅ TOP UP WITH EITHER PARTS OF THE TRADING PAIR [{TRADE_SYMBOL}] (EVEN DURING BOT'S RUNNING). \n")
    time.sleep(5)
    print("\t  ✅ SELL ANY QUANTITY OF EGLD YOU HAD PREVIOUSLY BOUGHT, ASIDE FROM THE QUANTITY BOUGHT VIA BOT'S TRANSACTIONS (YOU CAN SELL IT EVEN DURING BOT'S RUNNING). \n\n\n")
    time.sleep(10)
    print("\t\t  NOTES: \n")
    time.sleep(1)
    print("\t  ⚠️  SET ENV VAR [DISCLAIMER] to 'disabled' if you DO NOT want to see this Disclaimer again! \n")
    time.sleep(6)
    print("\t  ⚠️  CAPITAL AT RISK! TRADE ONLY THE CASH YOU ARE COMFORTABLE TO LOSE! \n\n\n")
    time.sleep(5)
    print("\t\t\t\t  \"TIME IN THE MARKET IS BETTER THAN TIMING THE MARKET!\" - Kenneth Fisher")
    time.sleep(5)


def email_engine_params(direct_call="1"):
    if RYBKA_EMAIL_SWITCH.upper() == "TRUE":
        if RYBKA_EMAIL_RECIPIENT_NAME == "User":
            if direct_call == "1":
                log.WARN("\n[RYBKA_EMAIL_RECIPIENT_NAME] was NOT provided in the HOST MACHINE ENV., but will default to value [User]")
        if RYBKA_EMAIL_SENDER_EMAIL and RYBKA_EMAIL_SENDER_DEVICE_PASSWORD and RYBKA_EMAIL_RECIPIENT_EMAIL:
            if direct_call == "1":
                log.INFO_BOLD(f" ✅ Email params in ENV    -  {bcolors.PURPLE}SET")
        else:
            log.FATAL_7("Email params in ENV    -  NOT SET\nAs long as you have [RYBKA_EMAIL_SWITCH] set as [True], make sure you also set up the [RYBKA_EMAIL_SENDER_EMAIL, RYBKA_EMAIL_SENDER_DEVICE_PASSWORD, RYBKA_EMAIL_RECIPIENT_EMAIL] vars in your ENV!")
    else:
        if direct_call == "1":
            log.INFO(" ")
            log.WARN("Emails are turned [OFF]. Set [RYBKA_EMAIL_SWITCH] var as 'True' in env. if you want email notifications enabled!")
            log.INFO(" ")


def telegram_engine_switch(direct_call="1"):
    if RYBKA_TELEGRAM_SWITCH.upper() == "TRUE":
        if bootstrap.TELE_KEY and bootstrap.TELE_CHAT_ID:
            if direct_call == "1":
                log.INFO_BOLD(f" ✅ Telegram params in ENV -  {bcolors.PURPLE}SET")
        else:
            log.FATAL_7("Telegram params in ENV -  NOT SET\nAs long as you have [RYBKA_TELEGRAM_SWITCH] set as [True], make sure you also set up the [RYBKA_TELEGRAM_API_KEY, RYBKA_TELEGRAM_CHAT_ID] vars in your ENV!")
    else:
        if direct_call == "1":
            log.INFO(" ")
            log.WARN("Telegram notifications are turned [OFF]. Set [RYBKA_TELEGRAM_SWITCH] var as 'True' in env. if you want Telegram notifications enabled!")
            log.INFO(" ")


def bot_uptime_and_current_price(current_price):
    global uptime
    check_time = time.time()
    uptime_seconds = round(check_time - start_time)
    uptime_minutes = math.floor(uptime_seconds / 60)
    uptime_hours = math.floor(uptime_minutes / 60)
    
    seconds_in_limit = uptime_seconds % 60
    minutes_in_limit = math.floor(uptime_seconds / 60) % 60
    hours_in_limit = math.floor(uptime_minutes / 60) % 24
    days = math.floor(uptime_hours / 24)
    
    if days < 1:
        price_and_uptime = f"◼️ [EGLD = {bcolors.PURPLE}{current_price:5}{bcolors.DARKGRAY} USDT]   ◼️⬛️◼️   [UPTIME = {bcolors.PURPLE}{hours_in_limit:2}h:{minutes_in_limit:2}m:{seconds_in_limit:2}s{bcolors.DARKGRAY}] ◼️" 
    else:
        price_and_uptime = f"◼️ [EGLD = {bcolors.PURPLE}{current_price:5}{bcolors.DARKGRAY} USDT]   ◼️⬛️◼️   [UPTIME = {bcolors.PURPLE}{days}d {hours_in_limit:2}h:{minutes_in_limit:2}m:{seconds_in_limit:2}s{bcolors.DARKGRAY}] ◼️"

    log.INFO(price_and_uptime)


def email_sender(email_message):
    global RYBKA_EMAIL_SWITCH

    email_engine_params("0")

    if RYBKA_EMAIL_SWITCH.upper() == "TRUE":
        message_template = Template('''Dear ${PERSON_NAME}, 

            ${MESSAGE}



        ================================================================
        Email sent by RYBKA bot from machine having the following specs:

        hostname              ${HOSTNAME}
        mac-address         ${MAC_ADDR}
        ================================================================''')

        s = smtplib.SMTP(host='smtp.gmail.com', port=587)
        s.starttls()
        s.login(RYBKA_EMAIL_SENDER_EMAIL, RYBKA_EMAIL_SENDER_DEVICE_PASSWORD)
            
        msg = MIMEMultipart()

        message = message_template.substitute(PERSON_NAME = RYBKA_EMAIL_RECIPIENT_NAME.title(), MESSAGE = email_message, HOSTNAME = socket.gethostname(), MAC_ADDR = ':'.join(re.findall('..', '%012x' % uuid.getnode())))

        msg['From'] = RYBKA_EMAIL_SENDER_EMAIL
        msg['To'] = RYBKA_EMAIL_RECIPIENT_EMAIL
        msg['Subject'] = "RYBKA notification"

        msg.attach(MIMEText(message, 'plain'))

        try:
            s.send_message(msg)
        except Exception as e:
            log.WARN(f"Sending email notification failed with error:\n{e}\nIf it's an authentication issue and you did set the correct password for your gmail account, you have the know that the actual required one is the DEVICE password for your gmail.\nIf you haven't got one configured yet, please set one up right here (connect with your sender address and then replace the password in the ENV with the newly created device password:\n       https://myaccount.google.com/apppasswords")
        del msg

        s.quit()


def clear_terminal():
    if platform == "linux" or platform == "linux2":
        os.system('clear')
    elif platform == "win32":
        os.system('cls')


def re_sync_time():
    try:
        if platform == "linux" or platform == "linux2":
            pass
        elif platform == "win32":
            if DEBUG_LVL == 2 or DEBUG_LVL == 3:
                subprocess.call(['net', 'start', 'w32time'])
                subprocess.call(['w32tm', '/config', '/syncfromflags:manual', '/manualpeerlist:time.nist.gov'])
                subprocess.call(['w32TM', '/resync'])
            else:
                devnull = open(os.devnull, 'w')
                subprocess.call(['net', 'start', 'w32time'], stdout=devnull, stderr=devnull)
                subprocess.call(['w32tm', '/config', '/syncfromflags:manual', '/manualpeerlist:time.nist.gov'], stdout=devnull, stderr=devnull)
                subprocess.call(['w32TM', '/resync'], stdout=devnull, stderr=devnull)
            log.DEBUG(f"Time SYNC cmd completed successfully OR time is already synced")
    except Exception as e:
        log.WARN(f"Time SYNC cmd DID NOT complete successfully:\n{e}")


def isAdmin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def real_time_balances_update():
    global RYBKA_MODE
    global balance_usdt
    global balance_egld
    global balance_bnb

    try:
        with open(f"{RYBKA_MODE}/real_time_balances", 'w', encoding="utf8") as f:
            f.write("Most recent balances update shows:\n")
            f.write(f"\n{log.logging_time()} EGLD balance is: {balance_egld}")
            f.write(f"\n{log.logging_time()} USDT balance is: {balance_usdt}")
            f.write(f"\n{log.logging_time()} BNB  balance is: {balance_bnb}")
    except Exception as e:
        log.WARN(f"Could not update balance file due to error: \n{e}")



###############################################
###########   WEBSOCKET FUNCTIONS   ###########
###############################################


def on_open(ws):
    log.INFO("=====================================================================================================================================")
    log.INFO_BOLD(f'Connection to Binance servers established, listening to [{bcolors.PURPLE}{TRADE_SYMBOL}{bcolors.DARKGRAY}] data')
    log.INFO("=====================================================================================================================================")
    log.INFO_BOLD("Initiating a one-time 10-min info gathering timeframe. Please wait...")
    log.INFO("=====================================================================================================================================")
    

def on_close(ws, close_status_code, close_msg):
    print(f"{bcolors.CRED}{bcolors.BOLD}❌ FATAL {log.logging_time()}      > Closed connection, something went wrong. Please consult logs and restart the bot.{bcolors.ENDC}")
    log.all_errors_file_update(f"❌ FATAL (1) {log.logging_time()}      > Closed connection, something went wrong. Please consult logs and restart the bot.")
    telegram.LOG("FATAL", f"🏴‍☠️ Bot is shutting down... [{RYBKA_MODE}]")

    archive_folder = 'archived_logs'
    if not os.path.isdir(archive_folder):
        os.makedirs(archive_folder)
    shutil.move(current_export_dir, archive_folder)

    if close_status_code or close_msg:
        print(f"{bcolors.CRED}{bcolors.BOLD}❌ FATAL {log.logging_time()}      > Close status code: {str(close_status_code)}{bcolors.ENDC}")
        print(f"{bcolors.CRED}{bcolors.BOLD}❌ FATAL {log.logging_time()}      > Close message: {str(close_msg)}{bcolors.ENDC}")
        log.all_errors_file_update(f"❌ FATAL (1) {log.logging_time()}      > Close status code: {str(close_status_code)}")
        log.all_errors_file_update(f"❌ FATAL (1) {log.logging_time()}      > Close message: {str(close_msg)}")
        telegram.LOG("FATAL", f"[RYBKA MODE - {RYBKA_MODE}] Bot STOPPED working.\n\n Close Status Code: {str(close_status_code)}\n Close Message: {str(close_msg)}")
        email_sender(f"{log.logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot STOPPED working.\n\n Close Status Code: {str(close_status_code)}\n Close Message: {str(close_msg)}")
    else:
        email_sender(f"{log.logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot STOPPED working. No DEBUG close message or status code provided")


def on_error(ws, message):
    if str(message).strip():
        print(f"{bcolors.CRED}{bcolors.BOLD}❌ FATAL {log.logging_time()}      > Software encountered an error and got shutdown! Additional error message provided:\n{message}{bcolors.ENDC}")
        log.all_errors_file_update(f"❌ FATAL {log.logging_time()}      > Software encountered an error and got shutdown! Additional error message provided:\n{message}")
        if str(message).strip() == "7":
            exit(7)
    else:
        print(f"{bcolors.CRED}{bcolors.BOLD}❌ FATAL {log.logging_time()}      > Software encountered an error and got shutdown! No additional error message provided{bcolors.ENDC}")
        log.all_errors_file_update(f"❌ FATAL {log.logging_time()}      > Software encountered an error and got shutdown! No additional error message provided")
        if str(message).strip() == "7":
            exit(7)

def on_message(ws, message):
    global uptime
    global start_time
    global client
    global closed_candles
    global ktbr_config
    global balance_usdt
    global balance_egld
    global balance_bnb
    global total_usdt_profit
    global bnb_commission
    global multiple_sells
    global nr_of_trades
    global subsequent_valid_rsi_counter
    global RYBKA_MODE
    global TRADE_QUANTITY
    global RSI_PERIOD
    global TRADE_SYMBOL
    global RSI_FOR_BUY
    global RSI_FOR_SELL
    global MIN_PROFIT
    global TRADING_BOOST_LVL
    
    log.HIGH_VERBOSITY(message)
    candle = json.loads(message)['k']
    is_candle_closed = candle['x']
    candle_close_price = round(float(candle['c']), 4)
    
    if is_candle_closed:
        closed_candles.append(candle_close_price)

        bootstraping_vars()
        log_files_creation("0")
        telegram_engine_switch("0")

        with open("TEMP/priceTmp", 'w', encoding="utf8") as f:
            f.write(str(candle_close_price))

        for i in range(0,10):
            try:
                client.ping()
                break
            except Exception as e:
                log.WARN(f"Binance server ping failed with error:\n{e}")
                time.sleep(3)

        with open(f"{current_export_dir}/{TRADE_SYMBOL}_historical_prices", 'a', encoding="utf8") as f:
            f.write(f'{log.logging_time()} Price of [EGLD] is [{candle_close_price} USDT]\n')

        if len(closed_candles) < 11:
            log.INFO(f"#####################################################################################################################################")
            log.INFO_BOLD(f"#####################  Bot is gathering data for technical analysis. Currently at min {bcolors.OKGREEN}[{len(closed_candles):2} of 10]{bcolors.ENDC}{bcolors.DARKGRAY} of processing  #####################")
            log.INFO(f"#####################################################################################################################################")
        log.DEBUG(f"History of target prices is {closed_candles}")

        bot_uptime_and_current_price(candle_close_price)

        if len(closed_candles) > 30:
            closed_candles = closed_candles[10:]
                
        if len(closed_candles) > RSI_PERIOD:
            np_candle_closes = numpy.array(closed_candles)
            rsi = talib.RSI(np_candle_closes, RSI_PERIOD)

            latest_rsi = round(rsi[-1], 2)

            log.VERBOSE(f"Latest RSI indicates {latest_rsi}")

            if subsequent_valid_rsi_counter == 1:
                log.DEBUG(f"Invalidating one RSI period, as a buy / sell action just occurred.\n")
                subsequent_valid_rsi_counter = 0
            else:
                if latest_rsi < RSI_FOR_BUY or len(ktbr_config) == 0 or len(ktbr_config) == 1:  
                    
                    if len(ktbr_config) == 0 or len(ktbr_config) == 1:
                        log.INFO("===============================")
                        log.INFO(" ALWAYS BUY POLICY ACTIVATED!")
                        log.INFO("===============================")
                    else:
                        log.INFO("===============================")
                        log.INFO("          BUY SIGNAL!")
                        log.INFO("===============================")

                    if RYBKA_MODE == "LIVE":
                        for i in range(1,11):
                            try:
                                account_balance_update()
                                log.DEBUG(f"Account Balance Sync. - Successful")
                                break
                            except Exception as e:
                                if i == 10:
                                    log.FATAL_7(f"Account Balance Sync. - Failed as:\n{e}")
                                time.sleep(3)

                    real_time_balances_update()

                    with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                        f.write(f'\n\n\n{log.logging_time()} Within BUY (part I):\n')
                        f.write(f'{log.logging_time()} {"Latest RSI (latest_rsi) is":90} {latest_rsi:40}\n')
                        f.write(f"{log.logging_time()} {'BNB balance (balance_bnb) is':90} {balance_bnb:40}\n")
                        f.write(f"{log.logging_time()} {'USDT balance (balance_usdt) is':90} {balance_usdt:40}\n")
                        f.write(f"{log.logging_time()} {'EGLD balance (balance_egld) is':90} {balance_egld:40}\n")
                        f.write(f"{log.logging_time()} {'BNB commission (bnb_commission) is':90} {bnb_commission:40}\n")
                        f.write(f"{log.logging_time()} {'Total USDT profit (total_usdt_profit) is':90} {total_usdt_profit:40}\n")
                        f.write(f"{log.logging_time()} {'Multiple sells (multiple_sells) set to':90} {multiple_sells:40}\n")
                        f.write(f"{log.logging_time()} {'TRADE_QUANTITY (BEFORE processing) (TRADE_QUANTITY) is':90} {TRADE_QUANTITY:40}\n")
                        f.write(f"\n{log.logging_time()} {'Closed candles (str(closed_candles)) are':90} {str(closed_candles)}\n")
                        f.write(f"\n{log.logging_time()} {'KTBR config (BEFORE processing) (str(json.dumps(ktbr_config))) is':90} \n {str(json.dumps(ktbr_config))}\n\n")

                    if balance_bnb / bnb_commission >= 100:
                        log.DEBUG(f"BNB balance [{balance_bnb}] is enough for transactions.")

                        if balance_usdt / 12 > 1:

                            min_buy_share = candle_close_price / 12
                            min_order_quantity = round(float(1 / min_buy_share), 2)

                            TRADE_QUANTITY = AUX_TRADE_QUANTITY

                            if min_order_quantity > TRADE_QUANTITY:
                                log.WARN(f"We can NOT trade at this quantity: [{TRADE_QUANTITY}]. Enforcing a min quantity (per buy action) of [{min_order_quantity}] EGLD coins.")
                                TRADE_QUANTITY = min_order_quantity
                            else:
                                log.DEBUG(f"We CAN trade at this quantity: [{TRADE_QUANTITY}]. No need to enforce a higher min trading limit.")
                            
                            possible_nr_of_trades = math.floor(balance_usdt / (TRADE_QUANTITY * candle_close_price))
                            log.INFO(f"Remaining possible nr. of buy orders: {possible_nr_of_trades}\n")

                            if possible_nr_of_trades != 0:

                                if len(ktbr_config) > 5:
                                    if possible_nr_of_trades < len(ktbr_config) * 0.8:
                                        multiple_sells = "enabled"
                                    else:
                                        multiple_sells = "disabled"
                                else:
                                    multiple_sells = "disabled"
                                
                                ########   Make sure `division by 0` is not hit when editing the weights in here   ########
                                if possible_nr_of_trades == 1:
                                    heatmap_actions = 1
                                    heatmap_size = 2
                                    heatmap_limit = 1
                                else:
                                    if int(TRADING_BOOST_LVL) == 1:
                                        heatmap_actions = round(float(possible_nr_of_trades * 0.4))
                                    elif int(TRADING_BOOST_LVL) == 2:
                                        heatmap_actions = round(float(possible_nr_of_trades * 0.6))
                                    elif int(TRADING_BOOST_LVL) == 3:
                                        heatmap_actions = round(float(possible_nr_of_trades * 0.75))
                                    elif int(TRADING_BOOST_LVL) == 4:
                                        heatmap_actions = round(float(possible_nr_of_trades * 0.9))
                                    elif int(TRADING_BOOST_LVL) == 5:
                                        heatmap_actions = possible_nr_of_trades
                                    if heatmap_actions == 0 or heatmap_actions == 1:
                                        heatmap_size = 2
                                        heatmap_limit = 1
                                    else:
                                        if int(TRADING_BOOST_LVL) == 1:
                                            heatmap_size = round(float(heatmap_actions * 0.65))
                                        elif int(TRADING_BOOST_LVL) == 2:
                                            heatmap_size = round(float(heatmap_actions * 0.4))
                                        elif int(TRADING_BOOST_LVL) == 3:
                                            heatmap_size = round(float(heatmap_actions * 0.25))
                                        elif int(TRADING_BOOST_LVL) == 4:
                                            heatmap_size = 3
                                        elif int(TRADING_BOOST_LVL) == 5:
                                            heatmap_size = 2
                                        if heatmap_size == 0 or heatmap_size == 1:
                                            heatmap_size = 2
                                        if int(TRADING_BOOST_LVL) == 1:
                                            heatmap_limit = round(float((heatmap_actions / heatmap_size) + heatmap_size * 0.15))
                                        elif int(TRADING_BOOST_LVL) == 2:
                                            heatmap_limit = round(float((heatmap_actions / heatmap_size) + heatmap_size * 0.3))
                                        elif int(TRADING_BOOST_LVL) == 3:
                                            heatmap_limit = round(float((heatmap_actions / heatmap_size) + heatmap_size * 0.5))
                                        elif int(TRADING_BOOST_LVL) == 4:
                                            heatmap_limit = round(float((heatmap_actions / heatmap_size) + heatmap_size * 0.85))
                                        elif int(TRADING_BOOST_LVL) == 5:
                                            heatmap_limit = round(float((heatmap_actions / heatmap_size) + heatmap_size * 1.5))
                                ############################################################################################

                                log.VERBOSE(f"possible_nr_of_trades is {possible_nr_of_trades}")
                                log.VERBOSE(f"heatmap_actions is {heatmap_actions}")
                                log.VERBOSE(f"heatmap_size is {heatmap_size}")
                                log.VERBOSE(f"heatmap_limit is {heatmap_limit}")
                                log.DEBUG(f"TRADING_BOOST_LVL is {str(TRADING_BOOST_LVL)}")

                                current_price_rounded_down = math.floor(round(float(candle_close_price), 4))

                                heatmap_counter = 0
                                ktbr_config_array_of_prices = []

                                for v in ktbr_config.values():
                                    ktbr_config_array_of_prices.append(math.floor(float(v[1])))

                                for n in range(-round(float(heatmap_size/2)), round(float(heatmap_size/2))):
                                    if current_price_rounded_down + n in ktbr_config_array_of_prices:
                                        heatmap_counter += ktbr_config_array_of_prices.count(current_price_rounded_down + n)

                                heatmap_center_coin_counter = ktbr_config_array_of_prices.count(current_price_rounded_down)  

                                with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                    f.write(f'\n\n{log.logging_time()} Within BUY (part III):\n')
                                    f.write(f"{log.logging_time()} {'HEATMAP actions (heatmap_actions) is':90} {heatmap_actions:40}\n")
                                    f.write(f"{log.logging_time()} {'HEATMAP size (heatmap_size) is':90} {heatmap_size:40}\n")
                                    f.write(f"{log.logging_time()} {'HEATMAP limit (heatmap_limit) is':90} {heatmap_limit:40}\n")
                                    f.write(f"{log.logging_time()} {'HEATMAP counter (heatmap_counter) is':90} {heatmap_counter:40}\n")
                                    f.write(f"{log.logging_time()} {'HEATMAP center coin counter (heatmap_center_coin_counter) is':90} {heatmap_center_coin_counter:40}\n")
                                    f.write(f"{log.logging_time()} {'TRADING BOOST LVL (TRADING_BOOST_LVL) is':90} {str(TRADING_BOOST_LVL):40}\n")
                                    f.write(f"{log.logging_time()} {'Min Buy share (min_buy_share) is':90} {min_buy_share:40}\n")
                                    f.write(f"{log.logging_time()} {'Min Order QTTY (min_order_quantity) is':90} {min_order_quantity:40}\n")
                                    f.write(f"{log.logging_time()} {'Current price rounded down (current_price_rounded_down) set to':90} {current_price_rounded_down:40}\n")
                                    f.write(f"{log.logging_time()} {'TRADE_QUANTITY (AFTER processing) (TRADE_QUANTITY) is':90} {TRADE_QUANTITY:40}\n")
                                    f.write(f"{log.logging_time()} {'Possible Nr. of trades (possible_nr_of_trades) is':90} {possible_nr_of_trades:40}\n")
                                    f.write(f"{log.logging_time()} KTBR array of prices (str(ktbr_config_array_of_prices)) is {str(ktbr_config_array_of_prices)}\n\n\n")

                                if heatmap_center_coin_counter >= heatmap_limit or heatmap_counter >= heatmap_actions:
                                    log.INFO(f"HEATMAP DOES NOT ALLOW BUYING!")
                                    log.DEBUG(f"heatmap_center_coin_counter [{heatmap_center_coin_counter}] is >= heatmap_limit [{heatmap_limit}] OR heatmap_counter [{heatmap_counter}] is >= heatmap_actions [{heatmap_actions}]\n\n\n\n")
                                    with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                        f.write(f'\n\n{log.logging_time()} Within BUY (part IV):\n')
                                        f.write(f"{log.logging_time()} HEATMAP DOES NOT ALLOW BUYING!")
                                        f.write(f"{log.logging_time()} heatmap_center_coin_counter [{heatmap_center_coin_counter}] is >= heatmap_limit [{heatmap_limit}] OR heatmap_counter [{heatmap_counter}] is >= heatmap_actions [{heatmap_actions}]")
                                elif float(balance_usdt) < float(TRADE_QUANTITY) * float(candle_close_price) + 2:
                                    log.INFO("Way too low diff between acc. balance and current price * trade quantity. Not allowing buy.")
                                else:
                                    log.VERBOSE(f"HEATMAP ALLOWS BUYING!\n")
                                    try:
                                        back_up()
                                        if RYBKA_MODE == "LIVE":
                                            log.VERBOSE(f"Before BUY. USDT balance is [{balance_usdt}]")
                                            log.VERBOSE(f"Before BUY. EGLD balance is [{balance_egld}]")
                                            log.VERBOSE(f"Before BUY. BNB  balance is [{balance_bnb}]")
                                            order = client.order_market_buy(symbol=TRADE_SYMBOL, quantity=TRADE_QUANTITY)
                                        elif RYBKA_MODE == "DEMO":
                                            order_id_tmp = id_generator()
                                            order = {'symbol': 'EGLDUSDT', 'orderId': '', 'orderListId': -1, 'clientOrderId': 'TXgNl8RNNipASGTrleH6ZY', 'transactTime': 1661098548719, 'price': '0.00000000', 'origQty': '0.19000000', 'executedQty': '0.19000000', 'cummulativeQuoteQty': '10.20300000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'fills': [{'price': '', 'qty': '0.19000000', 'commission': '', 'commissionAsset': 'EGLD', 'tradeId': 75747997}]}
                                            order["orderId"] = order_id_tmp
                                            order['executedQty'] = TRADE_QUANTITY
                                            order['fills'][0]['price'] = candle_close_price
                                            order['fills'][0]['commission'] = bnb_commission

                                            balance_usdt -= candle_close_price * TRADE_QUANTITY
                                            balance_usdt = round(balance_usdt, 4)
                                            balance_egld += TRADE_QUANTITY
                                            balance_egld = round(balance_egld, 4)
                                            balance_bnb -= bnb_commission
                                            balance_bnb = round(balance_bnb, 6)

                                        order_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                        log.DEBUG(f'BUY Order placed now at [{order_time}]\n')
                                        time.sleep(3)
                                        
                                        if RYBKA_MODE == "LIVE":
                                            order_status = client.get_order(symbol = TRADE_SYMBOL, orderId = order["orderId"])
                                        elif RYBKA_MODE == "DEMO":
                                            order_status = {'symbol': 'EGLDUSDT', 'orderId': 0, 'orderListId': -1, 'clientOrderId': 'TXgNl8RNNipASGTrleH6ZY', 'price': '0.00000000', 'origQty': '0.19000000', 'executedQty': '0.19000000', 'cummulativeQuoteQty': '10.20300000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1661098548719, 'updateTime': 1661098548719, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
                                            order_status['orderId'] = order_id_tmp

                                        if order_status['status'] == "FILLED":
                                            log.INFO_BOLD_UNDERLINE(" ✅ BUY Order filled successfully!\n")

                                            # avoid rounding up on quantity & price bought
                                            log.INFO_SPECIAL(f"🟢 Bought [{int(float(order['executedQty']) * 10 ** 4) / 10 ** 4}] EGLD at price per 1 EGLD of [{int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4}] USDT")
                                            telegram.LOG("INFO", f"\n🟢 Bought [{int(float(order['executedQty']) * 10 ** 4) / 10 ** 4}] EGLD at [{int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4}] USDT/EGLD")

                                            usdt_trade_fee = round(float(0.08 / 100 * round(float(order['cummulativeQuoteQty']), 4)), 4)
                                            log.VERBOSE(f"BUY action's usdt trade fee is {usdt_trade_fee}")

                                            total_usdt_profit = round(total_usdt_profit - usdt_trade_fee, 4)
                                            with open(f"{RYBKA_MODE}/usdt_profit", 'w', encoding="utf8") as f:
                                                f.write(str(total_usdt_profit))

                                            bnb_commission = float(order['fills'][0]['commission'])
                                            with open(f"{RYBKA_MODE}/most_recent_commission", 'w', encoding="utf8") as f:
                                                f.write(str(order['fills'][0]['commission']))

                                            ktbr_config[order['orderId']] = [int(float(order['executedQty']) * 10 ** 4) / 10 ** 4, int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4]
                                            with open(f"{RYBKA_MODE}/ktbr", 'w', encoding="utf8") as f:
                                                f.write(str(json.dumps(ktbr_config)))

                                            nr_of_trades += 1

                                            with open(f"{RYBKA_MODE}/number_of_buy_trades", 'w', encoding="utf8") as f:
                                                f.write(str(nr_of_trades))

                                            with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                                f.write(f'\n\n{log.logging_time()} Within BUY (part V):\n')
                                                f.write(f"{log.logging_time()} HEATMAP ALLOWS BUYING!\n")
                                                f.write(f"{log.logging_time()} {'Order time (order_time) is':90} {str(order_time):40}")
                                                f.write(f"{log.logging_time()} Transaction ID [{str(order['orderId'])}] - Bought [{str(int(float(order['executedQty']) * 10 ** 4) / 10 ** 4)}] EGLD at price per 1 EGLD of [{str(int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4)}] USDT\n")
                                                f.write(f"{log.logging_time()} {'Order (order) is':90} {str(json.dumps(order))}\n")
                                                f.write(f"{log.logging_time()} {'Order status (order_status) is':90} {str(json.dumps(order_status))}\n")
                                                f.write(f"{log.logging_time()} {'USDT trade fee (usdt_trade_fee) is':90} {str(usdt_trade_fee)}\n")
                                                f.write(f"{log.logging_time()} {'Order commission is':90} {str(order['fills'][0]['commission']):40}\n")
                                                f.write(f"{log.logging_time()} KTBR config (AFTER processing) (str(json.dumps(ktbr_config))) is {str(json.dumps(ktbr_config)):40}\n")
                                            
                                            back_up()
                                            
                                            if RYBKA_MODE == "LIVE":
                                                for i in range(1,11):
                                                    try:
                                                        account_balance_update()
                                                        log.DEBUG(f"Account Balance Sync. - Successful")
                                                        break
                                                    except Exception as e:
                                                        if i == 10:
                                                            log.FATAL_7(f"Account Balance Sync. - Failed as:\n{e}")
                                                        time.sleep(3)

                                            real_time_balances_update()

                                            if not DEBUG_LVL == 3:
                                                log.DEBUG(f"USDT balance is [{balance_usdt}]")
                                                log.DEBUG(f"EGLD balance is [{balance_egld}]")
                                                log.DEBUG(f"BNB  balance is [{balance_bnb}]")

                                            log.VERBOSE(f"After BUY - balance update. USDT balance is [{balance_usdt}]")
                                            log.VERBOSE(f"After BUY - balance update. EGLD balance is [{balance_egld}]")
                                            log.VERBOSE(f"After BUY - balance update. BNB  balance is [{balance_bnb}]")

                                            ktbr_integrity()

                                            with open(f"{current_export_dir}/{TRADE_SYMBOL}_order_history", 'a', encoding="utf8") as f:
                                                f.write(f'{log.logging_time()} Buy order done now at [{str(order_time)}]\n')
                                                f.write(f"{log.logging_time()} Transaction ID [{str(order['orderId'])}] - Bought [{str(int(float(order['executedQty']) * 10 ** 4) / 10 ** 4)}] EGLD at price per 1 EGLD of [{str(int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4)}] USDT\n\n\n")
                                            with open(f"{RYBKA_MODE}/full_order_history", 'a', encoding="utf8") as f:
                                                f.write(f'{log.logging_time()} Buy order done now at [{str(order_time)}]\n')
                                                f.write(f"{log.logging_time()} Transaction ID [{str(order['orderId'])}] - Bought [{str(int(float(order['executedQty']) * 10 ** 4) / 10 ** 4)}] EGLD at price per 1 EGLD of [{str(int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4)}] USDT\n\n\n")
                                            
                                            if int(heatmap_limit) > 12 or len(ktbr_config) < 2:
                                                subsequent_valid_rsi_counter = 0
                                            else:
                                                subsequent_valid_rsi_counter = 1

                                            re_sync_time()
                                        else:
                                            with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                                f.write(f'\n\n{log.logging_time()} Within BUY (part VI):\n')
                                                f.write(f'{log.logging_time()} Buy order was NOT filled successfully! Please check the cause!\n')
                                                f.write(f"{log.logging_time()} Order (order) is {str(json.dumps(order))}\n")
                                                f.write(f"{log.logging_time()} Order status (order_status) is {str(json.dumps(order_status))}\n")
                                            log.FATAL_7(f"Buy order was NOT filled successfully! Please check the cause!")
                                    except Exception as e:
                                        with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                            f.write(f'\n\n{log.logging_time()} Within BUY (part VII):\n')
                                            f.write(f'{log.logging_time()} Order could NOT be placed due to an error:\n{e}\n')
                                        log.FATAL_7(f"Make sure the [BIN_KEY] and [BIN_SECRET] ENV vars have valid values and time server is synced with NIST's!\nOrder could NOT be placed due to an error:\n{e}")
                            else:
                                log.WARN(f"Bot might still be able to buy some crypto, but only at a [{min_order_quantity}] EGLD trading quantity, not at the current one set of [{TRADE_QUANTITY}] EGLD per transaction!\n")
                                with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                    f.write(f'\n\n{log.logging_time()} Within BUY (part VIII):\n')
                                    f.write(f'{log.logging_time()} Bot might still be able to buy some crypto, but only at a [{min_order_quantity}] EGLD trading quantity, not at the current one set of [{TRADE_QUANTITY}] EGLD per transaction!\n')
                        else:
                            log.WARN(f"Not enough [USDT] to set other BUY orders! Wait for SELLS, or fill up the account with more [USDT].")
                            #TODO add log.WARN message and email func within the same 'if' clause for enabling / disabling such emails
                            #log.WARN(f"Notifying user (via email) that bot might need more money for buy actions, if possible.")
                            #email_sender(f"[RYBKA MODE - {RYBKA_MODE}] Bot might be able to buy more, but doesn't have enought USDT in balance [{balance_usdt}]\n\nTOP UP if possible!")
                            with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                f.write(f'\n\n{log.logging_time()} Within BUY (part IX):\n')
                                f.write(f'{log.logging_time()} Not enough [USDT] to set other BUY orders! Wait for SELLS, or fill up the account with more [USDT].\n')
                    else:
                        email_sender(f"{log.logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot doesn't have enought BNB in balance [{balance_bnb}] to sustain many more trades.\n\nHence, it will stop at this point. Please TOP UP!")
                        with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                            f.write(f'\n\n{log.logging_time()} Within BUY (part X):\n')
                            f.write(f'{log.logging_time()} BNB balance [{str(balance_bnb)}] is NOT enough to sustain many more transactions. Please TOP UP!\n')
                        log.FATAL_7(f"BNB balance [{balance_bnb}] is NOT enough to sustain many more transactions. Please TOP UP!")

                if latest_rsi > RSI_FOR_SELL:

                    log.INFO("================================")
                    log.INFO("          SELL SIGNAL!")
                    log.INFO("================================")

                    if RYBKA_MODE == "LIVE":
                        for i in range(1,11):
                            try:
                                account_balance_update()
                                log.DEBUG(f"Account Balance Sync. - Successful")
                                break
                            except Exception as e:
                                if i == 10:
                                    log.FATAL_7(f"Account Balance Sync. - Failed as:\n{e}")
                                time.sleep(3)

                    real_time_balances_update()

                    with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                        f.write(f'\n\n\n{log.logging_time()} Within SELL (part I):\n')
                        f.write(f'{log.logging_time()} {"Latest RSI (latest_rsi) is":90} {latest_rsi:40}\n')
                        f.write(f"{log.logging_time()} {'BNB balance (balance_bnb) is':90} {balance_bnb:40}\n")
                        f.write(f"{log.logging_time()} {'USDT balance (balance_usdt) is':90} {balance_usdt:40}\n")
                        f.write(f"{log.logging_time()} {'EGLD balance (balance_egld) is':90} {balance_egld:40}\n")
                        f.write(f"{log.logging_time()} {'BNB commission (bnb_commission) is':90} {bnb_commission:40}\n")
                        f.write(f"{log.logging_time()} {'Total USDT profit (total_usdt_profit) is':90} {total_usdt_profit:40}\n")
                        f.write(f"{log.logging_time()} {'Multiple sells (multiple_sells) set to':90} {multiple_sells:40}\n")
                        f.write(f"\n{log.logging_time()} {'Closed candles (multiple_sells) are':90} {closed_candles}\n")
                        f.write(f"\n{log.logging_time()} KTBR config (BEFORE processing) (str(json.dumps(ktbr_config))) is \n {str(json.dumps(ktbr_config))}\n\n")

                    if balance_bnb / bnb_commission >= 100:
                        log.DEBUG(f"BNB balance [{balance_bnb}] is enough for transactions.")
                        
                        eligible_sells = []

                        for k, v in ktbr_config.items():
                            if v[1] + MIN_PROFIT < candle_close_price:
                                log.DEBUG(f"Identified buy ID [{k}], qtty [{v[0]}] bought at price of [{v[1]}] as being eligible for sell")
                                log.VERBOSE(f"Multiple sells set as [{multiple_sells}]")
                                eligible_sells.append(k)
                                if multiple_sells == "disabled":
                                    break
                                elif len(eligible_sells) == 4:
                                    break

                        log.INFO(" ")
                        with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                            f.write(f'\n\n\n{log.logging_time()} Within SELL (part II):\n')
                            f.write(f"{log.logging_time()} {'Eligible sells (eligible_sells) is':90} {str(eligible_sells)}\n")

                        if eligible_sells:
                            for sell in eligible_sells:
                                log.DEBUG(f"Selling buy [{sell}] of qtty [{ktbr_config[sell][0]}]")

                                try:
                                    back_up()
                                    if RYBKA_MODE == "LIVE":
                                        order = client.order_market_sell(symbol=TRADE_SYMBOL, quantity=ktbr_config[sell][0])
                                    elif RYBKA_MODE == "DEMO":
                                        order = {'symbol': 'EGLDUSDT', 'orderId': '', 'orderListId': -1, 'clientOrderId': 'TXgNl8RNNipASGTrleH6ZY', 'transactTime': 1661098548719, 'price': '0.00000000', 'origQty': '0.19000000', 'executedQty': '0.19000000', 'cummulativeQuoteQty': '10.20300000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'fills': [{'price': '', 'qty': '0.19000000', 'commission': '', 'commissionAsset': 'EGLD', 'tradeId': 75747997}]}
                                        order["orderId"] = str(sell)
                                        order['executedQty'] = ktbr_config[sell][0]
                                        order['fills'][0]['price'] = candle_close_price
                                        order['fills'][0]['commission'] = bnb_commission

                                        balance_usdt += candle_close_price * ktbr_config[sell][0]
                                        balance_usdt = round(balance_usdt, 4)
                                        balance_egld -= ktbr_config[sell][0]
                                        balance_egld = round(balance_egld, 4)
                                        balance_bnb -= bnb_commission
                                        balance_bnb = round(balance_bnb, 6)

                                    order_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                    log.DEBUG(f'SELL Order placed now at [{order_time}]\n')
                                    time.sleep(1)
                                    
                                    if RYBKA_MODE == "LIVE":
                                        order_status = client.get_order(symbol = TRADE_SYMBOL, orderId = order["orderId"])
                                    elif RYBKA_MODE == "DEMO":
                                        order_status = {'symbol': 'EGLDUSDT', 'orderId': 953796254, 'orderListId': -1, 'clientOrderId': 'TXgNl8RNNipASGTrleH6ZY', 'price': '0.00000000', 'origQty': '0.19000000', 'executedQty': '0.19000000', 'cummulativeQuoteQty': '10.20300000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1661098548719, 'updateTime': 1661098548719, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
                                        order_status['orderId'] = str(sell)
                                    
                                    if order_status['status'] == "FILLED":
                                        log.INFO_BOLD_UNDERLINE(" ✅ SELL Order filled successfully!\n")
                                        # avoid rounding up on quantity & price sold
                                        qtty_aux = int(float(order['executedQty']) * 10 ** 4) / 10 ** 4
                                        price_aux = int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4

                                        log.INFO_SPECIAL(f"🟢 Sold [{qtty_aux}] EGLD at price per 1 EGLD of [{price_aux}] USDT. Previously bought at [{str(ktbr_config[sell][1])}] USDT")
                                        telegram.LOG("INFO", f"\n🟢 Sold [{qtty_aux}] EGLD at [{price_aux}] USDT/EGLD.\nWas bought at [{str(ktbr_config[sell][1])}] USDT/EGLD")

                                        usdt_trade_fee = round(float(0.08 / 100 * round(float(order['cummulativeQuoteQty']), 4)), 4)
                                        log.VERBOSE(f"SELL action's usdt trade fee is {usdt_trade_fee}")

                                        total_usdt_profit = round(int((total_usdt_profit + (price_aux - ktbr_config[sell][1]) * ktbr_config[sell][0]) * 10 ** 4) / 10 ** 4 - usdt_trade_fee, 4)
                                        with open(f"{RYBKA_MODE}/usdt_profit", 'w', encoding="utf8") as f:
                                            f.write(str(total_usdt_profit))

                                        bnb_commission = float(order['fills'][0]['commission'])
                                        with open(f"{RYBKA_MODE}/most_recent_commission", 'w', encoding="utf8") as f:
                                            f.write(str(order['fills'][0]['commission']))

                                        with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                            f.write(f'\n\n{log.logging_time()} Within SELL (part III):\n')
                                            f.write(f"{log.logging_time()} Selling buy [{str(sell)}] {'of qtty':90} [{str(ktbr_config[sell][0])}]\n")
                                        
                                        previous_buy_info = f"What got sold: BUY ID [{str(sell)}] of QTTY [{str(ktbr_config[sell][0])}] at bought PRICE of [{str(ktbr_config[sell][1])}] USDT"

                                        del ktbr_config[sell]
                                        with open(f"{RYBKA_MODE}/ktbr", 'w', encoding="utf8") as f:
                                            f.write(str(json.dumps(ktbr_config)))

                                        with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                            f.write(f'\n\n{log.logging_time()} Within SELL (part IV):\n')
                                            f.write(f"{log.logging_time()} {'Order time (order_time) is':90} {str(order_time):40}")
                                            f.write(f"{log.logging_time()} Transaction ID [{str(order['orderId'])}] - Sold [{qtty_aux}] EGLD at price per 1 EGLD of [{str(price_aux)}] USDT\n")
                                            f.write(f"{log.logging_time()} {'Order (order) is':90} {str(json.dumps(order))}\n")
                                            f.write(f"{log.logging_time()} {'Order status (order_status) is':90} {str(json.dumps(order_status))}\n")
                                            f.write(f"{log.logging_time()} {'USDT trade fee (usdt_trade_fee) is':90} {str(usdt_trade_fee)}\n")
                                            f.write(f"{log.logging_time()} {'Order commission is':90} {str(order['fills'][0]['commission']):40}\n")
                                            f.write(f"{log.logging_time()} KTBR config (AFTER processing) (str(json.dumps(ktbr_config))) is {str(json.dumps(ktbr_config)):40}\n")

                                        back_up()

                                        if RYBKA_MODE == "LIVE":
                                            for i in range(1,11):
                                                try:
                                                    account_balance_update()
                                                    log.DEBUG(f"Account Balance Sync. - Successful")
                                                    break
                                                except Exception as e:
                                                    if i == 10:
                                                        log.FATAL_7(f"Account Balance Sync. - Failed as:\n{e}")
                                                    time.sleep(3)
                                        
                                        real_time_balances_update()

                                        log.DEBUG(f"USDT balance is [{balance_usdt}]")
                                        log.DEBUG(f"EGLD balance is [{balance_egld}]")
                                        log.DEBUG(f"BNB  balance is [{balance_bnb}]")

                                        ktbr_integrity()
                                        
                                        with open(f"{current_export_dir}/{TRADE_SYMBOL}_order_history", 'a', encoding="utf8") as f:
                                            f.write(f'{log.logging_time()} Sell order done now at [{str(order_time)}]\n')
                                            f.write(f"{log.logging_time()} Transaction ID [{order['orderId']}] - Sold [{str(qtty_aux)}] EGLD at price per 1 EGLD of [{str(price_aux)}] USDT\n")
                                            f.write(f"{log.logging_time()} {previous_buy_info} \n\n\n")
                                        with open(f"{RYBKA_MODE}/full_order_history", 'a', encoding="utf8") as f:
                                            f.write(f'{log.logging_time()} Sell order done now at [{str(order_time)}]\n')
                                            f.write(f"{log.logging_time()} Transaction ID [{order['orderId']}] - Sold [{str(qtty_aux)}] EGLD at price per 1 EGLD of [{str(price_aux)}] USDT\n")
                                            f.write(f"{log.logging_time()} {previous_buy_info} \n\n\n")

                                        if not multiple_sells == "enabled":
                                            subsequent_valid_rsi_counter = 1
                                    else:
                                        with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                            f.write(f'\n\n{log.logging_time()} Within SELL (part V):\n')
                                            f.write(f'{log.logging_time()} Sell order was NOT filled successfully! Please check the cause!\n')
                                            f.write(f"{log.logging_time()} {'Order (order) is':90} {str(json.dumps(order))}\n")
                                            f.write(f"{log.logging_time()} {'Order status (order_status) is':90} {str(json.dumps(order_status))}\n")
                                        log.FATAL_7(f"Sell order was NOT filled successfully! Please check the cause!")
                                except Exception as e:
                                    with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                        f.write(f'\n\n{log.logging_time()} Within SELL (part VI):\n')
                                        f.write(f'{log.logging_time()} Order could NOT be placed due to an error:\n{e}\n')
                                    log.FATAL_7(f"Make sure the [BIN_KEY] and [BIN_SECRET] ENV vars have valid values and time server is synced with NIST's!\nOrder could NOT be placed due to an error:\n{e}")
                            re_sync_time()
                        else:
                            log.INFO(f"No buy transactions are eligible to be sold at this moment!")
                            with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                f.write(f'\n\n{log.logging_time()} Within SELL (part VII):\n')
                                f.write(f'{log.logging_time()} No buy transactions are eligible to be sold at this moment!\n')
                    else:
                        email_sender(f"[RYBKA MODE - {RYBKA_MODE}] Bot doesn't have enought BNB in balance [{balance_bnb}] to sustain many more trades.\n\nHence, it will stop at this point. Please TOP UP!")
                        with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                            f.write(f'\n\n{log.logging_time()} Within SELL (part VIII):\n')
                            f.write(f'{log.logging_time()} BNB balance [{str(balance_bnb)}] is NOT enough to sustain many more transactions. Please TOP UP!\n')
                        log.FATAL_7(f"BNB balance [{balance_bnb}] is NOT enough to sustain many more transactions. Please TOP UP!")


@click.command()
@click.option('--mode', '-m', type=click.Choice(['demo', 'live'], case_sensitive=False), help='Choose the run mode of the software')
@click.option("--version", is_flag=True, help = "Show the version of the software", required = False)
def main(version, mode):
    """\b
    \b#################################################################################
    \b###                            🔸 RYBKA Software 🔸                           ###
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

    global RYBKA_MODE
    global TRADE_SYMBOL
    global RSI_PERIOD
    global RYBKA_TELEGRAM_SWITCH

    global balance_usdt
    global balance_egld
    global balance_bnb
    global locked_balance_usdt
    global locked_balance_egld
    global locked_balance_bnb
    global total_usdt_profit

    global current_export_dir


    if not version and not mode:
        click.echo(click.get_current_context().get_help())
        exit(111)
    
    if version:
        print(f"🔍 Rybka Software Version  ➜  [{bootstrap.__version__}]")
        exit(111)

    if mode:
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


    ###############################################
    ###########   FUNCTIONS' SEQUENCE   ###########
    ###############################################

    clear_terminal()

    ###########  Prerequisites - start  ###########
    log.ORANGE("\nPREREQUISITE PROCESS...\n")
    time.sleep(1)

    process_pid = os.getpid()
    log.ORANGE(f"RYBKA Software got allocated PID [{process_pid}]\n\n\n")
    TMP_folder("TEMP")
    with open("TEMP/pidTmp", 'w', encoding="utf8") as f:
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

    if platform == "linux" or platform == "linux2":
        pass
    elif platform == "win32":
        if isAdmin() != True:
            log.FATAL_7("Please run the script with admin privileges, as bot needs access to auto-update HOST's time with NIST servers!")
    
    if RYBKA_MODE == "LIVE":
        log.INFO("====================================================================================================")
        log.INFO("====================================================================================================")
        log.INFO_BOLD(f"=================================  ✅ {bcolors.PURPLE}RYBKA MODE   ---   LIVE{bcolors.DARKGRAY} ✅  ==================================")
        log.INFO("====================================================================================================")
        log.INFO("====================================================================================================")


        time.sleep(3)
        clear_terminal()

        if not SET_DISCLAIMER.upper() == "FALSE":
            disclaimer()
            clear_terminal()
    elif RYBKA_MODE == "DEMO":
        log.INFO("====================================================================================================")
        log.INFO("====================================================================================================")
        log.INFO_BOLD(f"===============================  🛠️  {bcolors.PURPLE}RYBKA MODE   ---   DEMO{bcolors.DARKGRAY} 🛠️   ===================================")
        log.INFO("====================================================================================================")
        log.INFO("====================================================================================================")
        time.sleep(3)
        clear_terminal()
    else:
        log.FATAL_7(f"PLEASE be clear about the mode you want the bot to operate in! RYBKA MODE set to [{RYBKA_MODE}]!")
    
    if RSI_PERIOD < 10:
        log.WARN("Please DO NOT set a value less than [10] for the [RYBKA_RSI_PERIOD] ENV var! To ensure a trustworthy tech. analysis at an RSI level  --->  defaulting to value [10].")
        RSI_PERIOD = 10

    def main_files():
        ktbr_configuration()
        profit_file()
        commission_file()
        nr_of_trades_file()
        full_order_history_file()
        real_time_balances()
        back_up()

    re_sync_time()
    software_config_params()
    user_initial_config()
    email_engine_params()
    binance_system_status()
    telegram_engine_switch()

    log.INFO(" ")
    log.INFO("=====================================================================================================================================")
    log.INFO(f" Check files created for this run, under the newly created local folder {bcolors.BOLD}[{bcolors.PURPLE}{current_export_dir}{bcolors.DARKGRAY}]{bcolors.ENDC}")
    log.INFO("=====================================================================================================================================")
    log.INFO(" ")

    if RYBKA_MODE == "LIVE":
        for i in range(1,6):
            try:
                binance_account_status()
                binance_api_account_status()
                account_balance_update()
                ktbr_integrity()
                break
            except Exception as e:
                if i == 5:
                    log.FATAL_7(f"Account-related functions failed to proceed successfully. Error:\n{e}")
                time.sleep(5)

    main_files()
    real_time_balances_update()

    if RYBKA_MODE == "DEMO":
        log.INFO(" ")
        if balance_usdt == 1500:
            log.WARN(f"USDT Balance of [{balance_usdt}] coins  --->  is set by default, by the bot. You can modify this value within the 'config.ini' file, for var [RYBKA_DEMO_BALANCE_USDT]")
        if balance_egld == 100:
            log.WARN(f"EGLD Balance of [{balance_egld}]  coins  --->  is set by default, by the bot. You can modify this value within the 'config.ini' file, for var [RYBKA_DEMO_BALANCE_EGLD]")
        if balance_bnb == 0.2:
            log.WARN(f"BNB  Balance of [{balance_bnb}]  coins  --->  is set by default, by the bot. You can modify this value within the 'config.ini' file, for var [RYBKA_DEMO_BALANCE_BNB]")
        log.INFO(" ")

    log.INFO("=====================================================================================================================================")
    log.INFO_BOLD(f"Account's AVAILABLE balance is:\n\t\t\t\t\t\t\t⚖️  {bcolors.PURPLE}USDT{bcolors.DARKGRAY}  ---  [{bcolors.OKGREEN}{balance_usdt}{bcolors.DARKGRAY}]\n\t\t\t\t\t\t\t⚖️  {bcolors.PURPLE}EGLD{bcolors.DARKGRAY}  ---  [{bcolors.OKGREEN}{balance_egld}{bcolors.DARKGRAY}]\n\n\t\t\t\t\t\t\t⚖️  {bcolors.PURPLE}BNB{bcolors.DARKGRAY}   ---  [{bcolors.OKGREEN}{balance_bnb}{bcolors.DARKGRAY}] (for transaction fees)")
    log.INFO("=====================================================================================================================================")
    if RYBKA_MODE == "LIVE":
        log.INFO_BOLD(f"Account's LOCKED balance in limit orders is:\n\t\t\t\t\t\t\t⚖️  {bcolors.PURPLE}LOCKED USDT{bcolors.DARKGRAY}  ---  [{bcolors.OKGREEN}{locked_balance_usdt}{bcolors.DARKGRAY}]\n\t\t\t\t\t\t\t⚖️  {bcolors.PURPLE}LOCKED EGLD{bcolors.DARKGRAY}  ---  [{bcolors.OKGREEN}{locked_balance_egld}{bcolors.DARKGRAY}]\n\n\t\t\t\t\t\t\t⚖️  {bcolors.PURPLE}LOCKED BNB{bcolors.DARKGRAY}   ---  [{bcolors.OKGREEN}{locked_balance_bnb}{bcolors.DARKGRAY}]")
        log.INFO("=====================================================================================================================================")
    log.INFO("=====================================================================================================================================")
    log.INFO_BOLD(f"Rybka's historical registered PROFIT is:\n\t\t\t\t\t\t\t💰 [{bcolors.OKGREEN}{total_usdt_profit}{bcolors.DARKGRAY}] {bcolors.PURPLE}USDT")
    log.INFO("=====================================================================================================================================")
    log.INFO("=====================================================================================================================================")

    telegram.LOG("INFO", f"🏁 Bot started! [{RYBKA_MODE}]")
    email_sender(f"{log.logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot is starting up. Find logs into the local folder: \n\t[{current_export_dir}]")

    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message, on_error = on_error)
    ws.run_forever()


if __name__ == '__main__':

    ###############################################
    ###########     TIME MANAGEMENT     ###########
    ###############################################

    start_time = time.time()
    uptime = ""


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
        
        global DEBUG_LVL, RSI_FOR_BUY, RSI_FOR_SELL, TRADING_BOOST_LVL
        global TRADE_QUANTITY, AUX_TRADE_QUANTITY, MIN_PROFIT
        global RYBKA_EMAIL_SWITCH, RYBKA_EMAIL_SENDER_EMAIL, RYBKA_EMAIL_RECIPIENT_EMAIL, RYBKA_EMAIL_RECIPIENT_NAME
        global RYBKA_TELEGRAM_SWITCH
        global SET_DISCLAIMER

        DEBUG_LVL = bootstrap.DEBUG_LVL

        TRADING_BOOST_LVL = bootstrap.TRADING_BOOST_LVL
        if TRADING_BOOST_LVL not in [1, 2, 3, 4, 5]:
            log.FATAL_7(f"Please consult [README.md] file for valid values of [RYBKA_TRADING_BOOST_LVL] var.\n[{TRADING_BOOST_LVL}] is not a valid value!")

        RSI_FOR_BUY = bootstrap.RSI_FOR_BUY
        RSI_FOR_SELL = bootstrap.RSI_FOR_SELL

        TRADE_QUANTITY = round(bootstrap.TRADE_QUANTITY, 2)
        AUX_TRADE_QUANTITY = TRADE_QUANTITY
        MIN_PROFIT = bootstrap.MIN_PROFIT

        RYBKA_EMAIL_SWITCH = bootstrap.RYBKA_EMAIL_SWITCH
        RYBKA_EMAIL_SENDER_EMAIL = bootstrap.RYBKA_EMAIL_SENDER_EMAIL
        RYBKA_EMAIL_RECIPIENT_EMAIL = bootstrap.RYBKA_EMAIL_RECIPIENT_EMAIL
        RYBKA_EMAIL_RECIPIENT_NAME = bootstrap.RYBKA_EMAIL_RECIPIENT_NAME

        RYBKA_TELEGRAM_SWITCH = bootstrap.RYBKA_TELEGRAM_SWITCH

        SET_DISCLAIMER = bootstrap.SET_DISCLAIMER

    bootstraping_vars()

    ###############################################
    ###########       GLOBAL VARS       ###########
    ###############################################

    RYBKA_MODE = ""
    ktbr_config = {}
    closed_candles = []
    client = ""

    bnb_commission = 0.00005577
    total_usdt_profit = 0

    multiple_sells = "disabled"
    nr_of_trades = 0
    subsequent_valid_rsi_counter = 0

    current_export_dir = ""


    main()
