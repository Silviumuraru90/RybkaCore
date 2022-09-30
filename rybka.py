#!/usr/bin/env python3

# built-in and third-party libs
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

import string as string_str

from datetime import datetime
from string import Template
from binance.client import Client
from binance.enums import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import exists
from sys import platform


# custom libs
from custom_modules.cfg import bootstrap
from custom_modules.logging.logging import bcolors
from custom_modules.logging.logging import log



###############################################
###########     TIME MANAGEMENT     ###########
###############################################

start_time = time.time()
uptime = ""



###############################################
########   GLOBAL VARS from ENV VARS   ########
###############################################

DEBUG_LVL = bootstrap.DEBUG_LVL

RYBKA_MODE = bootstrap.RYBKA_MODE
TRADE_SYMBOL = bootstrap.TRADE_SYMBOL
SOCKET = bootstrap.SOCKET

RSI_PERIOD = bootstrap.RSI_PERIOD
RSI_FOR_BUY = bootstrap.RSI_FOR_BUY
RSI_FOR_SELL = bootstrap.RSI_FOR_SELL

TRADE_QUANTITY = bootstrap.TRADE_QUANTITY
AUX_TRADE_QUANTITY = TRADE_QUANTITY
MIN_PROFIT = bootstrap.MIN_PROFIT

RYBKA_EMAIL_SWITCH = bootstrap.RYBKA_EMAIL_SWITCH
RYBKA_EMAIL_SENDER_EMAIL = bootstrap.RYBKA_EMAIL_SENDER_EMAIL
RYBKA_EMAIL_SENDER_DEVICE_PASSWORD = bootstrap.RYBKA_EMAIL_SENDER_DEVICE_PASSWORD
RYBKA_EMAIL_RECIPIENT_EMAIL = bootstrap.RYBKA_EMAIL_RECIPIENT_EMAIL
RYBKA_EMAIL_RECIPIENT_NAME = bootstrap.RYBKA_EMAIL_RECIPIENT_NAME

SET_DISCLAIMER = bootstrap.SET_DISCLAIMER



###############################################
#########     DEMO AUX GLOBAL VARS    #########
###############################################

if RYBKA_MODE == "DEMO":
    balance_usdt = bootstrap.RYBKA_DEMO_BALANCE_USDT
    balance_egld = bootstrap.RYBKA_DEMO_BALANCE_EGLD
    balance_bnb = bootstrap.RYBKA_DEMO_BALANCE_BNB



###############################################
###########       GLOBAL VARS       ###########
###############################################

ktbr_config = {}
closed_candles = []
client = ""

if RYBKA_MODE == "LIVE":
    balance_usdt = 0
    balance_egld = 0
    balance_bnb = 0

    locked_balance_usdt = 0
    locked_balance_egld = 0
    locked_balance_bnb = 0

# value represented ~0.02 $. Considered with a high margin, considering it's bear market
# usual fee is ~0.0072 $  (1$ paid in fees for ~120 transactions)
# TODO this to be solved by a double socket opener, to check prices of two pairs in the same time
bnb_commission = 0.00005577
total_usdt_profit = 0

multiple_sells = "disabled"
nr_of_trades = 0
subsequent_valid_rsi_counter = 0

current_export_dir = ""

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
        log.INFO_BOLD(" ✅ Client initial config  -  DONE")
    except Exception as e:
        log.FATAL_7(f"Client initial config  -  FAILED\nError encountered at setting user config. via API KEY and API SECRET. Please check error below:\n{e}")


def binance_system_status():
    global client
    binance_status = client.get_system_status()
    if binance_status["status"] == 0:
        log.INFO_BOLD(f" ✅ Binance servers status -  {binance_status['msg'].upper()}")
    else:
        log.FATAL_7(f"Binance servers status -  {binance_status['msg'].upper()}")


def binance_account_status():
    global client
    acc_status = client.get_account_status()
    if acc_status['data'].upper() == "NORMAL":
        log.INFO_BOLD(f" ✅ Binance acc. status    -  {acc_status['data'].upper()}")
    else:
        log.FATAL_7(f"Binance acc. status    -  {acc_status['data'].upper()}")


def binance_api_account_status():
    global client
    acc_api_status = client.get_account_api_trading_status()
    if acc_api_status['data']['isLocked'] is False:
        log.INFO_BOLD(f" ✅ API acc. locked status -  {str(acc_api_status['data']['isLocked']).upper()}")
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
    balance_usdt = round(float(balance_aux_usdt['free']), 4)
    locked_balance_usdt = round(float(balance_aux_usdt['locked']), 4)

    balance_aux_egld = client.get_asset_balance(asset='EGLD')
    balance_egld = round(float(balance_aux_egld['free']), 4)
    locked_balance_egld = round(float(balance_aux_egld['locked']), 4)

    balance_aux_bnb = client.get_asset_balance(asset='BNB')
    balance_bnb = round(float(balance_aux_bnb['free']), 6)
    locked_balance_bnb = round(float(balance_aux_bnb['locked']), 6)



###############################################
#######   FILE MANIPULATION FUNCTIONS   #######
###############################################


def log_files_creation():
    global current_export_dir

    current_export_dir = f'{RYBKA_MODE}_{TRADE_SYMBOL}_{datetime.now().strftime("%d_%m_%Y")}_AT_{datetime.now().strftime("%H_%M_%S")}_{id_generator()}'
    os.mkdir(current_export_dir)
    
    try:
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
            if RYBKA_EMAIL_SENDER_EMAIL and RYBKA_EMAIL_RECIPIENT_EMAIL:
                f.write(f"SENDER EMAIL    set to: {RYBKA_EMAIL_SENDER_EMAIL:>50}\n")
                f.write(f"RECIPIENT EMAIL set to: {RYBKA_EMAIL_RECIPIENT_EMAIL:>50}\n")
        log.INFO_BOLD(" ✅ Files creation status  -  DONE")
        log.INFO(" ")
        log.INFO("=====================================================================================================================================")
        log.INFO(f" Check files created for this run, under the newly created local folder {bcolors.BOLD}[{current_export_dir}]{bcolors.ENDC}")
        log.INFO("=====================================================================================================================================")
        log.INFO(" ")
    except Exception as e:
        log.FATAL_7(f"Attempt to create local folder [{current_export_dir}] and inner files for output analysis FAILED - with error:\n{e}")
        


def rybka_mode_folder_creation():
    global RYBKA_MODE
    if os.path.isdir(RYBKA_MODE) is False:
        os.makedirs(RYBKA_MODE)


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
                        log.INFO(f" 💎 Transaction [{k}]  ---  [{bcolors.BOLD}{v[0]}{bcolors.ENDC}{bcolors.OKGREEN}] \t EGLD bought at price of [{bcolors.BOLD}{v[1]}{bcolors.ENDC}{bcolors.OKGREEN}] \t USDT per EGLD{bcolors.ENDC}")
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
    log.INFO("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/usdt_profit"):
        with open(f"{RYBKA_MODE}/usdt_profit", 'r', encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/usdt_profit").st_size == 0:
                log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/usdt_profit] file exists and is empty")
            else:
                try:
                    total_usdt_profit = round(float(f.read()), 4)
                    log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/usdt_profit] file contains the following already done profit: [{total_usdt_profit}] USDT")
                except Exception as e:
                    log.FATAL_7(f"[{RYBKA_MODE}/usdt_profit] file contains wrong formatted content!\nFailing with error:\n{e}")
    else:
        try:
            open(f"{RYBKA_MODE}/usdt_profit", 'w', encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/usdt_profit] file created!")
        except Exception as e:
            log.FATAL_7(f"[{RYBKA_MODE}/usdt_profit] file could NOT be created!\nFailing with error:\n{e}")
    log.INFO("=====================================================================================================================================")


def commission_file():
    global bnb_commission
    global RYBKA_MODE
    log.INFO("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/most_recent_commission"):
        with open(f"{RYBKA_MODE}/most_recent_commission", 'r', encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/most_recent_commission").st_size == 0:
                log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/most_recent_commission] file exists and is empty")
            else:
                try:
                    bnb_commission = float(f.read())
                    log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/most_recent_commission] file contains the following most recent paid fee: [{bnb_commission}] BNB")
                except Exception as e:
                    log.FATAL_7(f"[{RYBKA_MODE}/most_recent_commission] file contains wrong formatted content!\nFailing with error:\n{e}")
    else:
        try:
            open(f"{RYBKA_MODE}/most_recent_commission", 'w', encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/most_recent_commission] file created!")
        except Exception as e:
            log.FATAL_7(f"[{RYBKA_MODE}/most_recent_commission] file could NOT be created!\nFailing with error:\n{e}")
    log.INFO("=====================================================================================================================================")


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
                    log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/number_of_buy_trades] file contains the following already done nr. of buy trades: [{nr_of_trades}]")
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

        if sum_of_ktbr_cryptocurrency <= balance_egld:
            log.DEBUG(" ✅ KTBR integrity status  -  VALID\n")
        else:
            log.FATAL_7("KTBR integrity status  -  INVALID\nThis means that the amount of EGLD you have in cloud is actually less now, than what you retain in the 'ktbr' file. Probably you've spent a part of it in the meantime.")

def all_errors_file():
    global RYBKA_MODE
    log.INFO("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/errors_thrown"):
        log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/errors_thrown] file already exists!\n")
    else:
        try:
            open(f"{RYBKA_MODE}/errors_thrown", 'w', encoding="utf8").close()
            log.INFO_BOLD(f" ✅ [{RYBKA_MODE}/errors_thrown] file created!")
        except Exception as e:
            log.FATAL_7(f"[{RYBKA_MODE}/errors_thrown] file could NOT be created!\nFailing with error:\n{e}")
    log.INFO("=====================================================================================================================================")


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
    log.INFO("\n\n")
    log.INFO_BOLD("\t\t\t\t██████╗░██╗░░░██╗██████╗░██╗░░██╗░█████╗░")
    log.INFO_BOLD("\t\t\t\t██╔══██╗╚██╗░██╔╝██╔══██╗██║░██╔╝██╔══██╗")
    log.INFO_BOLD("\t\t\t\t██████╔╝░╚████╔╝░██████╦╝█████═╝░███████║")
    log.INFO_BOLD("\t\t\t\t██╔══██╗░░╚██╔╝░░██╔══██╗██╔═██╗░██╔══██║")
    log.INFO_BOLD("\t\t\t\t██║░░██║░░░██║░░░██████╦╝██║░╚██╗██║░░██║")
    log.INFO_BOLD("\t\t\t\t╚═╝░░╚═╝░░░╚═╝░░░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝\n")
    log.INFO_BOLD(f"\t\t\t\t             - MODE: {RYBKA_MODE} -           \n\n")
                    
    log.INFO(f"Rybka software started with the following parameters:\n")
    log.INFO_BOLD(f" 🔘 RYBKA_MODE      set to: {RYBKA_MODE:>50}")
    if DEBUG_LVL:
        log.INFO_BOLD(f"{bcolors.OKCYAN}DEBUG_LVL       set to: {DEBUG_LVL:>50}{bcolors.ENDC}")
    log.INFO_BOLD(f" 🔘 SOCKET          set to: {SOCKET:>50}")
    log.INFO_BOLD(f" 🔘 TRADE SYMBOL    set to: {TRADE_SYMBOL:>50}")
    log.INFO_BOLD(f" 🔘 TRADE QUANTITY  set to: {TRADE_QUANTITY:>50} coins per transaction")
    log.INFO_BOLD(f" 🔘 MIN PROFIT      set to: {MIN_PROFIT:>50} USDT per transaction")
    log.INFO_BOLD(f" 🔘 RSI PERIOD      set to: {RSI_PERIOD:>50} minutes")
    log.INFO_BOLD(f" 🔘 RSI FOR BUY     set to: {RSI_FOR_BUY:>50} threshold")
    log.INFO_BOLD(f" 🔘 RSI FORSELL     set to: {RSI_FOR_SELL:>50} threshold")
    log.INFO_BOLD(f" 🔘 EMAIL SWITCH    set to: {str(RYBKA_EMAIL_SWITCH):>50}")
    if RYBKA_EMAIL_SENDER_EMAIL and RYBKA_EMAIL_RECIPIENT_EMAIL:
        log.INFO_BOLD(f" 🔘 SENDER EMAIL    set to: {RYBKA_EMAIL_SENDER_EMAIL:>50}")
        log.INFO_BOLD(f" 🔘 RECIPIENT EMAIL set to: {RYBKA_EMAIL_RECIPIENT_EMAIL:>50}")
    log.INFO(" ")
    log.INFO(" ")
    log.INFO(" ")
    log.INFO_BOLD(" ✅ Initial params config  -  DONE")



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


def email_engine_params():
    if RYBKA_EMAIL_SWITCH:
        if RYBKA_EMAIL_RECIPIENT_NAME == "User":
            log.WARN("\n[RYBKA_EMAIL_RECIPIENT_NAME] was NOT provided in the HOST MACHINE ENV., but will default to value [User]")
        if RYBKA_EMAIL_SENDER_EMAIL and RYBKA_EMAIL_SENDER_DEVICE_PASSWORD and RYBKA_EMAIL_RECIPIENT_EMAIL:
            log.INFO_BOLD("\n ✅ Email params in ENV    -  SET")
        else:
            log.FATAL_7("Email params in ENV    -  NOT SET\nAs long as you have [RYBKA_EMAIL_SWITCH] set as [True], make sure you also set up the [RYBKA_EMAIL_SENDER_EMAIL, RYBKA_EMAIL_SENDER_DEVICE_PASSWORD, RYBKA_EMAIL_RECIPIENT_EMAIL] vars in your ENV!")
    else:
        log.INFO(" ")
        log.WARN("Emails are turned [OFF]. Set [RYBKA_EMAIL_SWITCH] var as 'True' in env. if you want email notifications enabled!")
        log.INFO(" ")


def bot_uptime():
    global uptime
    check_time = time.time()
    uptime_seconds = round(check_time - start_time)
    uptime_minutes = round(uptime_seconds / 60, 1)
    uptime_hours = round(uptime_minutes / 60, 1)
    uptime_days = round(uptime_hours / 24, 1)
    uptime_weeks = round(uptime_days / 7, 1)
    uptime_months = round(uptime_days / 30, 1)
    
    uptime = f"Rybka bot uptime is [{uptime_seconds}] in seconds | [{uptime_minutes}] in minutes | [{uptime_hours}] in hours | [{uptime_days}] in days | [{uptime_weeks}] in weeks | [{uptime_months}] in months\n"
    log.INFO(uptime)
    

def email_sender(email_message):
    global RYBKA_EMAIL_SWITCH

    if RYBKA_EMAIL_SWITCH:
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
            # TODO sync time cmd for linux
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
    log.INFO_BOLD(f'Connection to Binance servers established, listening to [{TRADE_SYMBOL}] data')
    log.INFO("=====================================================================================================================================")
    log.INFO_BOLD("Initiating a one-time 10-min info gathering timeframe. Please wait...")
    log.INFO("=====================================================================================================================================")
    

def on_close(ws, close_status_code, close_msg):
    print(f"{bcolors.CRED}{bcolors.BOLD}❌ FATAL {log.logging_time()}> Closed connection, something went wrong. Please consult logs and restart the bot.{bcolors.ENDC}")
    log.all_errors_file_update(f"❌ FATAL (1) {log.logging_time()}> Closed connection, something went wrong. Please consult logs and restart the bot.")

    archive_folder = 'archived_logs'
    if not os.path.isdir(archive_folder):
        os.makedirs(archive_folder)
    shutil.move(current_export_dir, archive_folder)

    if close_status_code or close_msg:
        print(f"{bcolors.CRED}{bcolors.BOLD}❌ FATAL {log.logging_time()}> Close status code: {str(close_status_code)}{bcolors.ENDC}")
        print(f"{bcolors.CRED}{bcolors.BOLD}❌ FATAL {log.logging_time()}> Close message: {str(close_msg)}{bcolors.ENDC}")
        log.all_errors_file_update(f"❌ FATAL (1) {log.logging_time()}> Close status code: {str(close_status_code)}")
        log.all_errors_file_update(f"❌ FATAL (1) {log.logging_time()}> Close message: {str(close_msg)}")
        email_sender(f"{log.logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot STOPPED working.\n\n Close Status Code: {str(close_status_code)}\n Close Message: {str(close_msg)}")
    else:
        email_sender(f"{log.logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot STOPPED working. No DEBUG close message or status code provided")


def on_error(ws, message):
    if str(message).strip():
        print(f"{bcolors.CRED}{bcolors.BOLD}❌ FATAL {log.logging_time()}> Software encountered an error and got shutdown! Additional error message provided:\n{message}{bcolors.ENDC}")
        log.all_errors_file_update(f"❌ FATAL (1) {log.logging_time()}> Software encountered an error and got shutdown! Additional error message provided:\n{message}")
    else:
        print(f"{bcolors.CRED}{bcolors.BOLD}❌ FATAL {log.logging_time()}> Software encountered an error and got shutdown! No additional error message provided{bcolors.ENDC}")
        log.all_errors_file_update(f"❌ FATAL (1) {log.logging_time()}> Software encountered an error and got shutdown! No additional error message provided")


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
    
    log.HIGH_VERBOSITY(message)
    candle = json.loads(message)['k']
    is_candle_closed = candle['x']
    candle_close_price = round(float(candle['c']), 4)
    
    if is_candle_closed:
        closed_candles.append(candle_close_price)

        bot_uptime()

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
            log.INFO_BOLD(f"#####################  Bot is gathering data for technical analysis. Currently at min [{len(closed_candles):2} of 10] of processing  #####################")
            log.INFO(f"#####################################################################################################################################")
        log.DEBUG(f"History of target prices is {closed_candles}")

        if len(closed_candles) > 30:
            closed_candles = closed_candles[10:]
                
        if len(closed_candles) > RSI_PERIOD:
            np_candle_closes = numpy.array(closed_candles)
            rsi = talib.RSI(np_candle_closes, RSI_PERIOD)

            latest_rsi = round(rsi[-1], 2)

            log.VERBOSE(f"Latest RSI indicates {latest_rsi}")

            if subsequent_valid_rsi_counter == 1:
                log.DEBUG(f"Invalidating one RSI period, as a buy / sell action just occured.\n")
                subsequent_valid_rsi_counter = 0
            else:
                if latest_rsi < RSI_FOR_BUY:    
                    log.INFO("===============================")
                    log.INFO("          BUY SIGNAL!")
                    log.INFO("===============================")

                    if RYBKA_MODE == "LIVE":
                        for i in range(1,11):
                            try:
                                account_balance_update()
                                log.INFO_BOLD(f"Account Balance Sync. - Successful")
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
                        f.write(f"{log.logging_time()} {'BNB commision (bnb_commission) is':90} {bnb_commission:40}\n")
                        f.write(f"{log.logging_time()} {'Total USDT profit (total_usdt_profit) is':90} {total_usdt_profit:40}\n")
                        f.write(f"{log.logging_time()} {'Multiple sells (multiple_sells) set to':90} {multiple_sells:40}\n")
                        f.write(f"{log.logging_time()} {'TRADE_QUANTITY (BEFORE processing) (TRADE_QUANTITY) is':90} {TRADE_QUANTITY:40}\n")
                        f.write(f"\n{log.logging_time()} {'Closed candles (str(closed_candles)) are':90} {str(closed_candles)}\n")
                        f.write(f"\n{log.logging_time()} {'KTBR config (BEFORE processing) (str(json.dumps(ktbr_config))) is':90} \n {str(json.dumps(ktbr_config))}\n\n")

                    if balance_bnb / bnb_commission >= 100:
                        log.DEBUG(f"BNB balance [{balance_bnb}] is enough for transactions.")

                        if balance_usdt / 12 > 1:

                            min_buy_share = candle_close_price / 12
                            min_order_quantity = round(float(1 / min_buy_share), 4)

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
                                    if possible_nr_of_trades < len(ktbr_config) * 0.7:
                                        multiple_sells = "enabled"
                                    else:
                                        multiple_sells = "disabled"
                                else:
                                    multiple_sells = "disabled"
                                
                                heatmap_actions = round(float(possible_nr_of_trades * 0.6))
                                heatmap_size = round(float(heatmap_actions * 0.4))
                                heatmap_limit = round(float((heatmap_actions - heatmap_size) / 1.2))

                                with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                    f.write(f'\n\n{log.logging_time()} Within BUY (part II):\n')
                                    f.write(f"{log.logging_time()} {'HEATMAP actions (BEFORE processing) (heatmap_actions) is':90} {heatmap_actions:40}\n")
                                    f.write(f"{log.logging_time()} {'HEATMAP size (BEFORE processing) (heatmap_size) is':90} {heatmap_size:40}\n")
                                    f.write(f"{log.logging_time()} {'HEATMAP limit (BEFORE processing) (heatmap_limit) is':90} {heatmap_limit:40}\n")

                                if heatmap_actions == heatmap_size:
                                    heatmap_actions += 2
                                elif heatmap_actions - heatmap_size < 2:
                                    heatmap_actions += 1
                                if heatmap_limit < 2:
                                    heatmap_limit = 2
                                if heatmap_size < 2:
                                    heatmap_size = 2

                                log.VERBOSE(f"heatmap_actions is {heatmap_actions}")
                                log.VERBOSE(f"heatmap_size is {heatmap_size}")
                                log.VERBOSE(f"heatmap_limit is {heatmap_limit}")

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
                                    f.write(f"{log.logging_time()} {'HEATMAP actions (AFTER processing) (heatmap_actions) is':90} {heatmap_actions:40}\n")
                                    f.write(f"{log.logging_time()} {'HEATMAP size (AFTER processing) (heatmap_size) is':90} {heatmap_size:40}\n")
                                    f.write(f"{log.logging_time()} {'HEATMAP limit (AFTER processing) (heatmap_limit) is':90} {heatmap_limit:40}\n")
                                    f.write(f"{log.logging_time()} {'HEATMAP counter (heatmap_counter) is':90} {heatmap_counter:40}\n")
                                    f.write(f"{log.logging_time()} {'HEATMAP center coin counter (heatmap_center_coin_counter) is':90} {heatmap_center_coin_counter:40}\n")
                                    f.write(f"{log.logging_time()} {'Min Buy share (min_buy_share) is':90} {min_buy_share:40}\n")
                                    f.write(f"{log.logging_time()} {'Min Order QTTY (min_order_quantity) is':90} {min_order_quantity:40}\n")
                                    f.write(f"{log.logging_time()} {'Current price rounded down (current_price_rounded_down) set to':90} {current_price_rounded_down:40}\n")
                                    f.write(f"{log.logging_time()} {'TRADE_QUANTITY (AFTER processing) (TRADE_QUANTITY) is':90} {TRADE_QUANTITY:40}\n")
                                    f.write(f"{log.logging_time()} {'Possible Nr. of trades (possible_nr_of_trades) is':90} {possible_nr_of_trades:40}\n")
                                    f.write(f"{log.logging_time()} KTBR array of prices (str(ktbr_config_array_of_prices)) is {str(ktbr_config_array_of_prices)}\n\n\n")

                                if heatmap_center_coin_counter >= heatmap_limit or heatmap_counter >= heatmap_actions:
                                    log.INFO(f"HEATMAP DOES NOT ALLOW BUYING!")
                                    log.INFO(f"heatmap_center_coin_counter [{heatmap_center_coin_counter}] is >= heatmap_limit [{heatmap_limit}] OR heatmap_counter [{heatmap_counter}] is >= heatmap_actions [{heatmap_actions}]\n\n\n\n")
                                    with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                        f.write(f'\n\n{log.logging_time()} Within BUY (part IV):\n')
                                        f.write(f"{log.logging_time()} HEATMAP DOES NOT ALLOW BUYING!")
                                        f.write(f"{log.logging_time()} heatmap_center_coin_counter [{heatmap_center_coin_counter}] is >= heatmap_limit [{heatmap_limit}] OR heatmap_counter [{heatmap_counter}] is >= heatmap_actions [{heatmap_actions}]")
                                else:
                                    log.VERBOSE(f"HEATMAP ALLOWS BUYING!\n")
                                    try:
                                        back_up()
                                        if RYBKA_MODE == "LIVE":
                                            order = client.order_market_buy(symbol=TRADE_SYMBOL, quantity=TRADE_QUANTITY)
                                        elif RYBKA_MODE == "DEMO":
                                            order_id_tmp = id_generator()
                                            order = {'symbol': 'EGLDUSDT', 'orderId': '', 'orderListId': -1, 'clientOrderId': 'TXgNl8RNNipASGTrleH6ZY', 'transactTime': 1661098548719, 'price': '0.00000000', 'origQty': '0.19000000', 'executedQty': '0.19000000', 'cummulativeQuoteQty': '10.20300000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'fills': [{'price': '', 'qty': '0.19000000', 'commission': '', 'commissionAsset': 'EGLD', 'tradeId': 75747997}]}
                                            order["orderId"] = order_id_tmp
                                            order['executedQty'] = TRADE_QUANTITY
                                            order['fills'][0]['price'] = candle_close_price
                                            order['fills'][0]['commission'] = bnb_commission

                                            balance_usdt -= candle_close_price * TRADE_QUANTITY
                                            balance_egld += TRADE_QUANTITY
                                            balance_bnb -= bnb_commission

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
                                            log.INFO_BOLD(f"Transaction ID [{order['orderId']}] - Bought [{int(float(order['executedQty']) * 10 ** 4) / 10 ** 4}] EGLD at price per 1 EGLD of [{int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4}] USDT")

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
                                                f.write(f"{log.logging_time()} {'Order commision is':90} {str(order['fills'][0]['commission']):40}\n")
                                                f.write(f"{log.logging_time()} KTBR config (AFTER processing) (str(json.dumps(ktbr_config))) is {str(json.dumps(ktbr_config)):40}\n")
                                            
                                            back_up()
                                            
                                            if RYBKA_MODE == "LIVE":
                                                for i in range(1,11):
                                                    try:
                                                        account_balance_update()
                                                        log.INFO_BOLD(f"Account Balance Sync. - Successful")
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
                                                f.write(f'{log.logging_time()} Buy order done now at [{str(order_time)}]\n')
                                                f.write(f"{log.logging_time()} Transaction ID [{str(order['orderId'])}] - Bought [{str(int(float(order['executedQty']) * 10 ** 4) / 10 ** 4)}] EGLD at price per 1 EGLD of [{str(int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4)}] USDT\n\n\n")
                                            with open(f"{RYBKA_MODE}/full_order_history", 'a', encoding="utf8") as f:
                                                f.write(f'{log.logging_time()} Buy order done now at [{str(order_time)}]\n')
                                                f.write(f"{log.logging_time()} Transaction ID [{str(order['orderId'])}] - Bought [{str(int(float(order['executedQty']) * 10 ** 4) / 10 ** 4)}] EGLD at price per 1 EGLD of [{str(int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4)}] USDT\n\n\n")
                                            
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
                                        log.FATAL_7(f"Make sure the API_KEY and API_SECRET have valid values and time server is synced with NIST's!\nOrder could NOT be placed due to an error:\n{e}")
                            else:
                                log.WARN(f"Bot might still be able to buy some crypto, but only at a [{min_order_quantity}] EGLD trading quantity, not at the current one set of [{TRADE_QUANTITY}] EGLD per transaction!\n")
                                with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                    f.write(f'\n\n{log.logging_time()} Within BUY (part VIII):\n')
                                    f.write(f'{log.logging_time()} Bot might still be able to buy some crypto, but only at a [{min_order_quantity}] EGLD trading quantity, not at the current one set of [{TRADE_QUANTITY}] EGLD per transaction!\n')
                        else:
                            log.WARN(f"Not enough [USDT] to set other BUY orders! Wait for SELLS, or fill up the account with more [USDT].")
                            #TODO add log.WARN message and email func within the same 'if' clause for enabling / disabling such emails
                            log.WARN(f"Notifying user (via email) that bot might need more money for buy actions, if possible.")
                            email_sender(f"[RYBKA MODE - {RYBKA_MODE}] Bot might be able to buy more, but doesn't have enought USDT in balance [{balance_usdt}]\n\nTOP UP if possible!")
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
                                log.INFO_BOLD(f"Account Balance Sync. - Successful")
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
                                log.INFO(f"Identified buy ID [{k:11}], qtty [{v[0]:5}] bought at price of [{v[1]:5}] as being eligible for sell")
                                log.VERBOSE(f"Multiple sells set as [{multiple_sells}]")
                                eligible_sells.append(k)
                                if multiple_sells == "disabled":
                                    break

                        log.INFO(" ")
                        with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                            f.write(f'\n\n\n{log.logging_time()} Within SELL (part II):\n')
                            f.write(f"{log.logging_time()} {'Eligible sells (eligible_sells) is':90} {str(eligible_sells)}\n")

                        if eligible_sells:
                            for sell in eligible_sells:
                                log.DEBUG(f"Selling buy [{sell:11}] of qtty [{ktbr_config[sell][0]:5}]")

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
                                        balance_egld -= ktbr_config[sell][0]
                                        balance_bnb -= bnb_commission

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

                                        log.INFO_BOLD(f"Transaction ID [{order['orderId']}] - Sold [{qtty_aux}] EGLD at price per 1 EGLD of [{price_aux}] USDT")

                                        total_usdt_profit = int((total_usdt_profit + (price_aux - ktbr_config[sell][1]) * ktbr_config[sell][0]) * 10 ** 4) / 10 ** 4
                                        with open(f"{RYBKA_MODE}/usdt_profit", 'w', encoding="utf8") as f:
                                            f.write(str(total_usdt_profit))

                                        bnb_commission = float(order['fills'][0]['commission'])
                                        with open(f"{RYBKA_MODE}/most_recent_commission", 'w', encoding="utf8") as f:
                                            f.write(str(order['fills'][0]['commission']))

                                        with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                            f.write(f'\n\n{log.logging_time()} Within SELL (part III):\n')
                                            f.write(f"{log.logging_time()} Selling buy [{str(sell):11}] {'of qtty':90} [{str(ktbr_config[sell][0]):5}]\n")
                                        
                                        previous_buy_info = f"What got sold: BUY ID [{str(sell)}] of QTTY [{str(ktbr_config[sell][0]):5}] at bought PRICE of [{str(ktbr_config[sell][1]):5}] USDT"

                                        del ktbr_config[sell]
                                        with open(f"{RYBKA_MODE}/ktbr", 'w', encoding="utf8") as f:
                                            f.write(str(json.dumps(ktbr_config)))

                                        with open(f"{current_export_dir}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                            f.write(f'\n\n{log.logging_time()} Within SELL (part IV):\n')
                                            f.write(f"{log.logging_time()} {'Order time (order_time) is':90} {str(order_time):40}")
                                            f.write(f"{log.logging_time()} Transaction ID [{str(order['orderId'])}] - Sold [{qtty_aux}] EGLD at price per 1 EGLD of [{str(price_aux)}] USDT\n")
                                            f.write(f"{log.logging_time()} {'Order (order) is':90} {str(json.dumps(order))}\n")
                                            f.write(f"{log.logging_time()} {'Order status (order_status) is':90} {str(json.dumps(order_status))}\n")
                                            f.write(f"{log.logging_time()} {'Order commission is':90} {str(order['fills'][0]['commission']):40}\n")
                                            f.write(f"{log.logging_time()} KTBR config (AFTER processing) (str(json.dumps(ktbr_config))) is {str(json.dumps(ktbr_config)):40}\n")

                                        back_up()

                                        if RYBKA_MODE == "LIVE":
                                            for i in range(1,11):
                                                try:
                                                    account_balance_update()
                                                    log.INFO_BOLD(f"Account Balance Sync. - Successful")
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
                                    log.FATAL_7(f"Make sure the API_KEY and API_SECRET have valid values and time server is synced with NIST's!\nOrder could NOT be placed due to an error:\n{e}")
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


def main():
    global balance_usdt
    global balance_egld
    global balance_bnb
    global locked_balance_usdt
    global locked_balance_egld
    global locked_balance_bnb
    global total_usdt_profit
    global RYBKA_MODE
    global RSI_PERIOD

    rybka_mode_folder_creation()
    all_errors_file()

    clear_terminal()

    if platform == "linux" or platform == "linux2":
        # TODO cmd of checking elevation privileges
        pass
    elif platform == "win32":
        if isAdmin() != True:
            log.FATAL_7("Please run the script with admin privileges as bot needs access to auto-update HOST's time with NIST servers!")
    
    if RYBKA_MODE == "LIVE":
        log.INFO("====================================================================================================")
        log.INFO("====================================================================================================")
        log.INFO_BOLD("=================================  ✅ RYBKA MODE   ---   LIVE ✅  ==================================")
        log.INFO("====================================================================================================")
        log.INFO("====================================================================================================")


        time.sleep(3)
        clear_terminal()

        if not SET_DISCLAIMER == "False":
            disclaimer()
            clear_terminal()
    elif RYBKA_MODE == "DEMO":
        log.INFO("====================================================================================================")
        log.INFO("====================================================================================================")
        log.INFO_BOLD("===============================  🛠️  RYBKA MODE   ---   DEMO 🛠️ ====================================")
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
    log_files_creation()

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
            log.WARN(f"USDT Balance of [{balance_usdt:7}] coins  --->  is set by default, by the bot. Modify it by setting in ENV the var [RYBKA_DEMO_BALANCE_USDT] and restart the terminal / bot.")
        if balance_egld == 100:
            log.WARN(f"EGLD Balance of [{balance_egld:7}] coins  --->  is set by default, by the bot. Modify it by setting in ENV the var [RYBKA_DEMO_BALANCE_EGLD] and restart the terminal / bot.")
        if balance_bnb == 0.2:
            log.WARN(f"BNB  Balance of [{balance_bnb:7}] coins  --->  is set by default, by the bot. Modify it by setting in ENV the var [RYBKA_DEMO_BALANCE_BNB]  and restart the terminal / bot.")
        log.INFO(" ")

    log.INFO("=====================================================================================================================================")
    log.INFO_BOLD(f"Account's AVAILABLE balance is:\n\t\t\t\t\t⚖️  USDT  ---  [{balance_usdt}]\n\t\t\t\t\t⚖️  EGLD  ---  [{balance_egld}]\n\n\t\t\t\t\t⚖️  BNB   ---  [{balance_bnb}] (for transaction fees)")
    log.INFO("=====================================================================================================================================")
    if RYBKA_MODE == "LIVE":
        log.INFO_BOLD(f"Account's LOCKED balance in limit orders is:\n\t\t\t\t\t⚖️  LOCKED USDT  ---  [{locked_balance_usdt}]\n\t\t\t\t\t⚖️  LOCKED EGLD  ---  [{locked_balance_egld}]\n\n\t\t\t\t\t⚖️  LOCKED BNB   ---  [{locked_balance_bnb}]")
        log.INFO("=====================================================================================================================================")
    log.INFO("=====================================================================================================================================")
    log.INFO_BOLD(f"Rybka's historical registered PROFIT is:\n\t\t\t\t\t💰 [{total_usdt_profit}] USDT")
    log.INFO("=====================================================================================================================================")
    log.INFO("=====================================================================================================================================")

    email_sender(f"{log.logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot is starting up. Find logs into the local folder: \n\t[{current_export_dir}]")

    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message, on_error = on_error)
    ws.run_forever()


main()
