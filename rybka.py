#!/usr/bin/env python3

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



###############################################
###########     TIME MANAGEMENT     ###########
###############################################

start_time = time.time()
uptime = ""



###############################################
###########  TO BE SET AS ENV VARS  ###########
###############################################

RYBKA_MODE = os.environ.get("RYBKA_MODE", "DEMO")

TRADE_SYMBOL = os.environ.get("RYBKA_TRADE_SYMBOL", "EGLDUSDT")
SOCKET = os.environ.get("RYBKA_SOCKET", f"wss://stream.binance.com:9443/ws/{TRADE_SYMBOL.lower()}@kline_1m")

RSI_PERIOD = os.environ.get("RYBKA_RSI_PERIOD", 10)
RSI_FOR_BUY = os.environ.get("RYBKA_RSI_FOR_BUY", 30)
RSI_FOR_SELL = os.environ.get("RYBKA_RSI_FOR_SELL", 70)

TRADE_QUANTITY = os.environ.get("RYBKA_TRADE_QUANTITY", 0.25)
AUX_TRADE_QUANTITY = TRADE_QUANTITY
MIN_PROFIT = os.environ.get("RYBKA_MIN_PROFIT", 0.25)

RYBKA_EMAIL_SWITCH = os.environ.get("RYBKA_EMAIL_SWITCH", False)
RYBKA_EMAIL_SENDER_EMAIL = os.environ.get("RYBKA_EMAIL_SENDER_EMAIL")
RYBKA_EMAIL_SENDER_DEVICE_PASSWORD = os.environ.get("RYBKA_EMAIL_SENDER_DEVICE_PASSWORD")
RYBKA_EMAIL_RECIPIENT_EMAIL = os.environ.get("RYBKA_EMAIL_RECIPIENT_EMAIL")
RYBKA_EMAIL_RECIPIENT_NAME = os.environ.get("RYBKA_EMAIL_RECIPIENT_NAME", "User")

SET_DISCLAIMER = os.environ.get("DISCLAIMER", "enabled")



###############################################
#########        DEMO AUX VARS        #########
###############################################

if RYBKA_MODE == "DEMO":
    balance_usdt = os.environ.get("RYBKA_BALANCE_USDT", 1500)
    balance_egld = os.environ.get("RYBKA_BALANCE_EGLD", 100)
    balance_bnb = os.environ.get("RYBKA_BALANCE_BNB", 0.02)



###############################################
###########         AUX VARS        ###########
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
        client = Client(os.environ.get('BIN_KEY'), os.environ.get('BIN_SECRET'))
        print("\n ✅ Client initial config  -  DONE")
    except Exception as e:
        print("\n ❌ Client initial config  -  FAILED")
        print(f"Error encountered at setting user config. via API KEY and API SECRET. Please check error below:\n{e}")
        all_errors_file_update(f"Error encountered at setting user config. via API KEY and API SECRET. Please check error below:\n{e}")
        exit(7)


def binance_system_status():
    global client
    binance_status = client.get_system_status()
    if binance_status["status"] == 0:
        print(f"\n ✅ Binance servers status - {binance_status['msg'].upper()}")
    else:
        print(f"\n ❌ Binance servers status - {binance_status['msg'].upper()}")
        exit(7)


def binance_account_status():
    global client
    acc_status = client.get_account_status()
    if acc_status['data'].upper() == "NORMAL":
        print(f"\n ✅ Binance acc. status    - {acc_status['data'].upper()}")
    else:
        print(f"\n ❌ Binance acc. status    - {acc_status['data'].upper()}")
        exit(7)


def binance_api_account_status():
    global client
    acc_api_status = client.get_account_api_trading_status()
    if acc_api_status['data']['isLocked'] is False:
        print(f"\n ✅ API acc. locked status - {str(acc_api_status['data']['isLocked']).upper()}")
    else:
        print(f"\n ❌ API acc. locked status - {str(acc_api_status['data']['isLocked']).upper()}")
        print(f"Locked status duration is - {acc_api_status['data']['plannedRecoverTime']}")
        exit(7)


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
    
    current_export_dir = f'{TRADE_SYMBOL}_{datetime.now().strftime("%d_%m_%Y")}_AT_{datetime.now().strftime("%H_%M_%S")}_{id_generator()}'
    os.environ["CURRENT_EXPORT_DIR"] = current_export_dir
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
            f.write(f"SOCKET          set to: {SOCKET:>50}\n")
            f.write(f"TRADE_SYMBOL    set to: {TRADE_SYMBOL:>50}\n")
            f.write(f"TRADE_QUANTITY  set to: {TRADE_QUANTITY:>50} coins per transaction\n")
            f.write(f"MIN_PROFIT      set to: {MIN_PROFIT:>50} $ per transaction\n")
            f.write(f"RSI_PERIOD      set to: {RSI_PERIOD:>50} minutes\n")
            f.write(f"RSI_FOR_BUY     set to: {RSI_FOR_BUY:>50} threshold\n")
            f.write(f"RSI_FOR_SELL    set to: {RSI_FOR_SELL:>50} threshold\n")
        print("\n ✅ Files creation status  -  DONE\n")
        print("\n=====================================================================================================================================")
        print(f" Check files created for this run, under the newly created local folder [{current_export_dir}]")
        print("=====================================================================================================================================")
    except Exception as e:
        print(f"Attempt to create local folder [{current_export_dir}] and inner files for output analysis - [❌] FAILED - with error:\n{e}")
        all_errors_file_update(f"Attempt to create local folder [{current_export_dir}] and inner files for output analysis - [❌] FAILED - with error:\n{e}")
        print("\n ❌ Files creation status  -  DONE\n")
        exit(7)


def rybka_mode_folder_creation():
    global RYBKA_MODE
    if os.path.isdir(RYBKA_MODE) is False:
        os.makedirs(RYBKA_MODE)


def ktbr_configuration():
    global ktbr_config
    global RYBKA_MODE
    print("\n=====================================================================================================================================")
    print("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/ktbr"):
        with open(f"{RYBKA_MODE}/ktbr", 'r', encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/ktbr").st_size == 0:
                print(f" ✅ [{RYBKA_MODE}/ktbr] file exists and is empty")
            else:
                try:
                    ktbr_config = json.loads(f.read())
                    print(f"\n ✅ [{RYBKA_MODE}/ktbr] file contains the following past transactions:\n")
                    for k, v in ktbr_config.items():
                        print(f" ✅ Transaction [{k:11}]  ---  [{v[0]:4}] EGLD bought at price of [{v[1]:5}]$ per EGLD")
                except Exception as e:
                    print(f"\n ❌ [{RYBKA_MODE}/ktbr] file contains wrong formatted content!\nFailing with error:\n\n{e}")
                    all_errors_file_update(f" ❌ [{RYBKA_MODE}/ktbr] file contains wrong formatted content!\nFailing with error:\n\n{e}")
                    exit(7)
    else:
        try:
            open(f"{RYBKA_MODE}/ktbr", 'w', encoding="utf8").close()
            print(f" ✅ [{RYBKA_MODE}/ktbr] file created!")
        except Exception as e:
            print(f"\n ❌ [{RYBKA_MODE}/ktbr] file could NOT be created!\nFailing with error:\n\n{e}")
            all_errors_file_update(f" ❌ [{RYBKA_MODE}/ktbr] file could NOT be created!\nFailing with error:\n\n{e}")
            exit(7)
    print("=====================================================================================================================================")
    print("=====================================================================================================================================")


def profit_file():
    global total_usdt_profit
    global RYBKA_MODE
    print("\n=====================================================================================================================================")
    print("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/usdt_profit"):
        with open(f"{RYBKA_MODE}/usdt_profit", 'r', encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/usdt_profit").st_size == 0:
                print(f" ✅ [{RYBKA_MODE}/usdt_profit] file exists and is empty")
            else:
                try:
                    total_usdt_profit = round(float(f.read()), 4)
                    print(f"\n ✅ [{RYBKA_MODE}/usdt_profit] file contains the following already done profit: [{total_usdt_profit}]$\n")
                except Exception as e:
                    print(f"\n ❌ [{RYBKA_MODE}/usdt_profit] file contains wrong formatted content!\nFailing with error:\n\n{e}")
                    all_errors_file_update(f" ❌ [{RYBKA_MODE}/usdt_profit] file contains wrong formatted content!\nFailing with error:\n\n{e}")
                    exit(7)
    else:
        try:
            open(f"{RYBKA_MODE}/usdt_profit", 'w', encoding="utf8").close()
            print(f" ✅ [{RYBKA_MODE}/usdt_profit] file created!")
        except Exception as e:
            print(f"\n ❌ [{RYBKA_MODE}/usdt_profit] file could NOT be created!\nFailing with error:\n\n{e}")
            all_errors_file_update(f" ❌ [{RYBKA_MODE}/usdt_profit] file could NOT be created!\nFailing with error:\n\n{e}")
            exit(7)
    print("=====================================================================================================================================")
    print("=====================================================================================================================================")


def commission_file():
    global bnb_commission
    global RYBKA_MODE
    print("\n=====================================================================================================================================")
    print("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/most_recent_commission"):
        with open(f"{RYBKA_MODE}/most_recent_commission", 'r', encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/most_recent_commission").st_size == 0:
                print(f" ✅ [{RYBKA_MODE}/most_recent_commission] file exists and is empty")
            else:
                try:
                    bnb_commission = float(f.read())
                    print(f"\n ✅ [{RYBKA_MODE}/most_recent_commission] file contains the following most recent paid fee: [{bnb_commission}] BNB\n")
                except Exception as e:
                    print(f"\n ❌ [{RYBKA_MODE}/most_recent_commission] file contains wrong formatted content!\nFailing with error:\n\n{e}")
                    all_errors_file_update(f" ❌ [{RYBKA_MODE}/most_recent_commission] file contains wrong formatted content!\nFailing with error:\n\n{e}")
                    exit(7)
    else:
        try:
            open(f"{RYBKA_MODE}/most_recent_commission", 'w', encoding="utf8").close()
            print(f" ✅ [{RYBKA_MODE}/most_recent_commission] file created!")
        except Exception as e:
            print(f"\n ❌ [{RYBKA_MODE}/most_recent_commission] file could NOT be created!\nFailing with error:\n\n{e}")
            all_errors_file_update(f" ❌ [{RYBKA_MODE}/most_recent_commission] file could NOT be created!\nFailing with error:\n\n{e}")
            exit(7)
    print("=====================================================================================================================================")
    print("=====================================================================================================================================")


def nr_of_trades_file():
    global nr_of_trades
    global RYBKA_MODE
    print("\n=====================================================================================================================================")
    print("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/number_of_buy_trades"):
        with open(f"{RYBKA_MODE}/number_of_buy_trades", 'r', encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/number_of_buy_trades").st_size == 0:
                print(f" ✅ [{RYBKA_MODE}/number_of_buy_trades] file exists and is empty")
            else:
                try:
                    nr_of_trades = int(f.read())
                    print(f"\n ✅ [{RYBKA_MODE}/number_of_buy_trades] file contains the following already done nr. of buy trades: [{nr_of_trades}]\n")
                except Exception as e:
                    print(f"\n ❌ [{RYBKA_MODE}/number_of_buy_trades] file contains wrong formatted content!\nFailing with error:\n\n{e}")
                    all_errors_file_update(f" ❌ [{RYBKA_MODE}/number_of_buy_trades] file contains wrong formatted content!\nFailing with error:\n\n{e}")
                    exit(7)
    else:
        try:
            open(f"{RYBKA_MODE}/number_of_buy_trades", 'w', encoding="utf8").close()
            print(f" ✅ [{RYBKA_MODE}/number_of_buy_trades] file created!")
        except Exception as e:
            print(f"\n ❌ [{RYBKA_MODE}/number_of_buy_trades] file could NOT be created!\nFailing with error:\n\n{e}")
            all_errors_file_update(f" ❌ [{RYBKA_MODE}/number_of_buy_trades] file could NOT be created!\nFailing with error:\n\n{e}")
            exit(7)
    print("=====================================================================================================================================")
    print("=====================================================================================================================================")


def full_order_history_file():
    global RYBKA_MODE
    print("\n=====================================================================================================================================")
    print("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/full_order_history"):
        with open(f"{RYBKA_MODE}/full_order_history", 'r', encoding="utf8") as f:
            if os.stat(f"{RYBKA_MODE}/full_order_history").st_size == 0:
                print(f" ✅ [{RYBKA_MODE}/full_order_history] file exists and is empty")
            else:
                print(f"\n ✅ [{RYBKA_MODE}/full_order_history] file exists and contains past information!\n")
    else:
        try:
            open(f"{RYBKA_MODE}/full_order_history", 'w', encoding="utf8").close()
            print(f" ✅ [{RYBKA_MODE}/full_order_history] file created!")
        except Exception as e:
            print(f"\n ❌ [{RYBKA_MODE}/full_order_history] file could NOT be created!\nFailing with error:\n\n{e}")
            all_errors_file_update(f" ❌ [{RYBKA_MODE}/full_order_history] file could NOT be created!\nFailing with error:\n\n{e}")
            exit(7)
    print("=====================================================================================================================================")
    print("=====================================================================================================================================")


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
            print("\n ✅ KTBR integrity status  - VALID\n")
        else:
            print("\n ❌ KTBR integrity status  - INVALID\n")
            print("This means that the amount of EGLD you have in cloud is actually less now, than what you retain in the 'ktbr' file. Probably you've spent a part of it in the meantime.")
            exit(7)


def all_errors_file():
    global RYBKA_MODE
    print("\n=====================================================================================================================================")
    print("=====================================================================================================================================")
    if exists(f"{RYBKA_MODE}/errors_thrown"):
        print(f"\n ✅ [{RYBKA_MODE}/errors_thrown] file already exists!\n")
    else:
        try:
            open(f"{RYBKA_MODE}/errors_thrown", 'w', encoding="utf8").close()
            print(f" ✅ [{RYBKA_MODE}/errors_thrown] file created!")
        except Exception as e:
            print(f"\n ❌ [{RYBKA_MODE}/errors_thrown] file could NOT be created!\nFailing with error:\n\n{e}")
            exit(7)
    print("=====================================================================================================================================")
    print("=====================================================================================================================================")


###############################################
##############   AUX FUNCTIONS   ##############
###############################################


def logging_time():
    return(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] ===')


def back_up():
    global RYBKA_MODE

    back_up_dir = f'{os.environ.get("CURRENT_EXPORT_DIR")}/{RYBKA_MODE}_BACK_UPS/LOGS_AT_{datetime.now().strftime("%d_%m_%Y")}_{datetime.now().strftime("%H_%M_%S")}'
    if os.path.isdir(back_up_dir) is False:
        os.makedirs(back_up_dir)

    shutil.copyfile(f'{RYBKA_MODE}/number_of_buy_trades', f"{back_up_dir}/number_of_buy_trades")
    shutil.copyfile(f'{RYBKA_MODE}/most_recent_commission', f"{back_up_dir}/most_recent_commission")
    shutil.copyfile(f'{RYBKA_MODE}/usdt_profit', f"{back_up_dir}/usdt_profit")
    shutil.copyfile(f'{RYBKA_MODE}/ktbr', f"{back_up_dir}/ktbr")


def software_config_params():
    print("\n\n\n\t\t\t\t██████╗░██╗░░░██╗██████╗░██╗░░██╗░█████╗░")
    print("\t\t\t\t██╔══██╗╚██╗░██╔╝██╔══██╗██║░██╔╝██╔══██╗")
    print("\t\t\t\t██████╔╝░╚████╔╝░██████╦╝█████═╝░███████║")
    print("\t\t\t\t██╔══██╗░░╚██╔╝░░██╔══██╗██╔═██╗░██╔══██║")
    print("\t\t\t\t██║░░██║░░░██║░░░██████╦╝██║░╚██╗██║░░██║")
    print("\t\t\t\t╚═╝░░╚═╝░░░╚═╝░░░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝\n")
    print(f"\t\t\t\t             - MODE: {RYBKA_MODE} -           \n")
                    
    print(f"\nRybka software started with the following parameters:\n")
    print(f"RYBKA_MODE      set to: {RYBKA_MODE:>50}")
    print(f"SOCKET          set to: {SOCKET:>50}")
    print(f"TRADE_SYMBOL    set to: {TRADE_SYMBOL:>50}")
    print(f"TRADE_QUANTITY  set to: {TRADE_QUANTITY:>50} coins per transaction")
    print(f"MIN_PROFIT      set to: {MIN_PROFIT:>50} $ per transaction")
    print(f"RSI_PERIOD      set to: {RSI_PERIOD:>50} minutes")
    print(f"RSI_FOR_BUY     set to: {RSI_FOR_BUY:>50} threshold")
    print(f"RSI_FOR_SELL    set to: {RSI_FOR_SELL:>50} threshold")

    print("\n ✅ Initial params config  -  DONE")



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
            print("\n[RYBKA_EMAIL_RECIPIENT_NAME] was NOT provided in the HOST MACHINE ENV., but will default to value [User]")
        if RYBKA_EMAIL_SENDER_EMAIL and RYBKA_EMAIL_SENDER_DEVICE_PASSWORD and RYBKA_EMAIL_RECIPIENT_EMAIL:
            print("\n ✅ Email params in ENV    -  SET")
        else:
            print("\n ❌ Email params in ENV    -  NOT SET")
            print("\nAs long as you have [RYBKA_EMAIL_SWITCH] set as [True], make sure you also set up the [RYBKA_EMAIL_SENDER_EMAIL, RYBKA_EMAIL_SENDER_DEVICE_PASSWORD, RYBKA_EMAIL_RECIPIENT_EMAIL] vars in your ENV!")
            exit(7)
    else:
        print("\n ⚠️  Emails are turned [OFF]. Set [RYBKA_EMAIL_SWITCH] var as 'True' in env. if you want email notifications enabled!")


def bot_uptime():
    global uptime
    check_time = time.time()
    uptime_seconds = round(check_time - start_time)
    uptime_minutes = round(uptime_seconds / 60, 1)
    uptime_hours = round(uptime_minutes / 60, 1)
    uptime_days = round(uptime_hours / 24, 1)
    uptime_weeks = round(uptime_days / 7, 1)
    uptime_months = round(uptime_days / 30, 1)
    
    uptime = f"\n{logging_time()} Rybka bot uptime is {uptime_seconds:11} in seconds | {uptime_minutes:9} in minutes | {uptime_hours:7} in hours | {uptime_days:5} in days | {uptime_weeks:4} in weeks | {uptime_months:4} in months\n"
    print(uptime)


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
            print(f"{logging_time()} Sending email notification failed with error:\n{e}\n\n")
            all_errors_file_update(f"Sending email notification failed with error:\n{e}")
            print(f"{logging_time()} If it's an authentication issue and you did set the correct password for your gmail account, you have the know that the actual required one is the DEVICE password for your gmail.\n")
            print(f"{logging_time()} If you haven't got one configured yet, please set one up right here (connect with your sender address and then replace the password in the ENV with the newly created device password:\n       https://myaccount.google.com/apppasswords")
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
            subprocess.call(['net', 'start', 'w32time'])
            subprocess.call(['w32tm', '/config', '/syncfromflags:manual', '/manualpeerlist:time.nist.gov'])
            subprocess.call(['w32TM', '/resync'])
            print(f"\n{logging_time()} ✅ Time SYNC cmd completed successfully OR time is already synced")
    except Exception as e:
        print(f"\n{logging_time()} ❌ Time SYNC cmd DID NOT complete successfully:\n{e}")
        all_errors_file_update(f" ❌ Time SYNC cmd DID NOT complete successfully:\n{e}")


def isAdmin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin



def all_errors_file_update(error):
    global RYBKA_MODE
    try:
        with open(f"{RYBKA_MODE}/errors_thrown", 'a', encoding="utf8") as f:
            f.write(f"\nError thrown at {logging_time()} was: \n{error}\n")
    except Exception as e:
        print(f"Could not update 'errors_thrown' file due to error: \n{e}")



###############################################
###########   WEBSOCKET FUNCTIONS   ###########
###############################################


def on_open(ws):
    print("\n\n\n=====================================================================================================================================")
    print(f'{logging_time()} Connection to Binance servers established, listening to [{TRADE_SYMBOL}] data')
    print("=====================================================================================================================================")
    print("\n=====================================================================================================================================")
    print(f"{logging_time()} Initiating a one-time 10-min info gathering timeframe. Please wait...")
    print("=====================================================================================================================================\n\n\n\n\n")
    

def on_close(ws, close_status_code, close_msg):
    print(f'\n{logging_time()} Closed connection, something went wrong. Please consult logs and restart the bot.')
    
    archive_folder = 'archived_logs'
    if not os.path.isdir(archive_folder):
        os.makedirs(archive_folder)
    shutil.move(os.environ.get('CURRENT_EXPORT_DIR'), archive_folder)

    if close_status_code or close_msg:
        print(f"\n{logging_time()} Close status code: {str(close_status_code)}")
        print(f"\n{logging_time()} Close message: {str(close_msg)}")
        all_errors_file_update(f"Close status code: {str(close_status_code)}")
        all_errors_file_update(f"Close message: {str(close_msg)}")
        email_sender(f"{logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot STOPPED working.\n\n Close Status Code: {str(close_status_code)}\n Close Message: {str(close_msg)}")
    else:
        pass
        email_sender(f"{logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot STOPPED working. No DEBUG close message or status code provided")


def on_error(ws, message):
    print(f'\n\n\n{logging_time()} Software encountered an error and got shutdown!\n')
    if str(message).strip():
        print(f'\n{logging_time()} Additional error message:\n{message}\n')
        all_errors_file_update(f"Software encountered an error and got shutdown!\nAdditional error message:\n{message}\n")
    else:
        print(f'\n{logging_time()} No additional error message provided\n')
        all_errors_file_update(f"Software encountered an error and got shutdown!\nNo additional error message provided\n")


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
    

    candle = json.loads(message)['k']
    is_candle_closed = candle['x']
    candle_close_price = round(float(candle['c']), 4)
    
    if is_candle_closed:
        closed_candles.append(candle_close_price)

        bot_uptime()

        for i in range(0,10):
            try:
                client.ping()
                print(f"{logging_time()} Pinged Binance server to maintain connection.")
                break
            except Exception as e:
                print(f"{logging_time()} Binance server ping failed with error:\n{e}")
                all_errors_file_update(f"Binance server ping failed with error:\n{e}")
                time.sleep(3)

        with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_historical_prices", 'a', encoding="utf8") as f:
            f.write(f'{logging_time()} {TRADE_SYMBOL} price at [{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] is [{candle_close_price}]\n')

        if len(closed_candles) < 11:
            print(f"\n#####################################################################################################################################")
            print(f"#####################  Bot is gathering data for technical analysis. Currently at min [{len(closed_candles):2} of 10] of processing  #####################")
            print(f"#####################################################################################################################################\n")
        print(f"\n{logging_time()} History of target prices is {closed_candles}")

        if len(closed_candles) > 30:
            closed_candles = closed_candles[10:]
                
        if len(closed_candles) > RSI_PERIOD:
            np_candle_closes = numpy.array(closed_candles)
            rsi = talib.RSI(np_candle_closes, RSI_PERIOD)

            latest_rsi = round(rsi[-1], 2)

            print(f"\n\n{logging_time()} Latest RSI indicates {latest_rsi}")

            if subsequent_valid_rsi_counter == 1:
                print(f"\n\n{logging_time()} Invalidating one RSI period, as a buy / sell action just occured.\n")
                subsequent_valid_rsi_counter = 0
            else:
                if latest_rsi < RSI_FOR_BUY:
                    print("\n\n\n==============================")
                    print("==============================")
                    print(f"{logging_time()} BUY SIGNAL!")
                    print("==============================")
                    print("==============================\n")

                    if RYBKA_MODE == "LIVE":
                        for i in range(0,10):
                            try:
                                account_balance_update()
                                print(f"\n{logging_time()} Account Balance Sync. - Successful")
                                break
                            except Exception as e:
                                print(f"\n{logging_time()} Account Balance Sync. - Failed as:\n{e}")
                                all_errors_file_update(f"Account Balance Sync. - Failed as:\n{e}")
                                time.sleep(3)

                    with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                        f.write(f'\n\n\n{logging_time()} Within BUY (part I):\n')
                        f.write(f'{logging_time()} {"Latest RSI (latest_rsi) is":90} {latest_rsi:40}\n')
                        f.write(f"{logging_time()} {'BNB balance (balance_bnb) is':90} {balance_bnb:40}\n")
                        f.write(f"{logging_time()} {'USDT balance (balance_usdt) is':90} {balance_usdt:40}\n")
                        f.write(f"{logging_time()} {'EGLD balance (balance_egld) is':90} {balance_egld:40}\n")
                        f.write(f"{logging_time()} {'BNB commision (bnb_commission) is':90} {bnb_commission:40}\n")
                        f.write(f"{logging_time()} {'Total USDT profit (total_usdt_profit) is':90} {total_usdt_profit:40}\n")
                        f.write(f"{logging_time()} {'Multiple sells (multiple_sells) set to':90} {multiple_sells:40}\n")
                        f.write(f"{logging_time()} {'TRADE_QUANTITY (BEFORE processing) (TRADE_QUANTITY) is':90} {TRADE_QUANTITY:40}\n")
                        f.write(f"\n{logging_time()} {'Closed candles (str(closed_candles)) are':90} {str(closed_candles)}\n")
                        f.write(f"\n{logging_time()} {'KTBR config (BEFORE processing) (str(json.dumps(ktbr_config))) is':90} \n {str(json.dumps(ktbr_config))}\n\n")

                    if balance_bnb / bnb_commission >= 100:
                        print(f"{logging_time()} BNB balance [{balance_bnb}] is enough for transactions.")

                        if balance_usdt / 12 > 1:

                            min_buy_share = candle_close_price / 12
                            min_order_quantity = round(float(1 / min_buy_share), 4)

                            TRADE_QUANTITY = AUX_TRADE_QUANTITY

                            if min_order_quantity > TRADE_QUANTITY:
                                print(f"{logging_time()} We can NOT trade at this quantity: [{TRADE_QUANTITY}]. Enforcing a min quantity (per buy action) of [{min_order_quantity}] EGLD coins.")
                                TRADE_QUANTITY = min_order_quantity
                            else:
                                print(f"{logging_time()} We CAN trade at this quantity: [{TRADE_QUANTITY}]. No need to enforce a higher min trading limit.")
                            
                            possible_nr_of_trades = math.floor(balance_usdt / (TRADE_QUANTITY * candle_close_price))
                            print(f"{logging_time()} Remaining possible nr. of buy orders: {possible_nr_of_trades}\n\n\n")

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

                                with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                    f.write(f'\n\n{logging_time()} Within BUY (part II):\n')
                                    f.write(f"{logging_time()} {'HEATMAP actions (BEFORE processing) (heatmap_actions) is':90} {heatmap_actions:40}\n")
                                    f.write(f"{logging_time()} {'HEATMAP size (BEFORE processing) (heatmap_size) is':90} {heatmap_size:40}\n")
                                    f.write(f"{logging_time()} {'HEATMAP limit (BEFORE processing) (heatmap_limit) is':90} {heatmap_limit:40}\n")

                                if heatmap_actions == heatmap_size:
                                    heatmap_actions += 2
                                elif heatmap_actions - heatmap_size < 2:
                                    heatmap_actions += 1
                                if heatmap_limit < 2:
                                    heatmap_limit = 2
                                if heatmap_size < 2:
                                    heatmap_size = 2

                                # TO BE RE-ADDED only for DEMO version
                                #if RYBKA_MODE == "DEMO":
                                print(f"{logging_time()} heatmap_actions is {heatmap_actions}")
                                print(f"{logging_time()} heatmap_size is {heatmap_size}")
                                print(f"{logging_time()} heatmap_limit is {heatmap_limit}")

                                current_price_rounded_down = math.floor(round(float(candle_close_price), 4))

                                heatmap_counter = 0
                                ktbr_config_array_of_prices = []

                                for v in ktbr_config.values():
                                    ktbr_config_array_of_prices.append(math.floor(float(v[1])))

                                for n in range(-round(float(heatmap_size/2)), round(float(heatmap_size/2))):
                                    if current_price_rounded_down + n in ktbr_config_array_of_prices:
                                        heatmap_counter += ktbr_config_array_of_prices.count(current_price_rounded_down + n)

                                heatmap_center_coin_counter = ktbr_config_array_of_prices.count(current_price_rounded_down)  

                                with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                    f.write(f'\n\n{logging_time()} Within BUY (part III):\n')
                                    f.write(f"{logging_time()} {'HEATMAP actions (AFTER processing) (heatmap_actions) is':90} {heatmap_actions:40}\n")
                                    f.write(f"{logging_time()} {'HEATMAP size (AFTER processing) (heatmap_size) is':90} {heatmap_size:40}\n")
                                    f.write(f"{logging_time()} {'HEATMAP limit (AFTER processing) (heatmap_limit) is':90} {heatmap_limit:40}\n")
                                    f.write(f"{logging_time()} {'HEATMAP counter (heatmap_counter) is':90} {heatmap_counter:40}\n")
                                    f.write(f"{logging_time()} {'HEATMAP center coin counter (heatmap_center_coin_counter) is':90} {heatmap_center_coin_counter:40}\n")
                                    f.write(f"{logging_time()} {'Min Buy share (min_buy_share) is':90} {min_buy_share:40}\n")
                                    f.write(f"{logging_time()} {'Min Order QTTY (min_order_quantity) is':90} {min_order_quantity:40}\n")
                                    f.write(f"{logging_time()} {'Current price rounded down (current_price_rounded_down) set to':90} {current_price_rounded_down:40}\n")
                                    f.write(f"{logging_time()} {'TRADE_QUANTITY (AFTER processing) (TRADE_QUANTITY) is':90} {TRADE_QUANTITY:40}\n")
                                    f.write(f"{logging_time()} {'Possible Nr. of trades (possible_nr_of_trades) is':90} {possible_nr_of_trades:40}\n")
                                    f.write(f"{logging_time()} KTBR array of prices (str(ktbr_config_array_of_prices)) is {str(ktbr_config_array_of_prices)}\n\n\n")

                                if heatmap_center_coin_counter >= heatmap_limit or heatmap_counter >= heatmap_actions:
                                    print(f"\n\n{logging_time()} HEATMAP DOES NOT ALLOW BUYING!")
                                    print(f"{logging_time()} heatmap_center_coin_counter [{heatmap_center_coin_counter}] is >= heatmap_limit [{heatmap_limit}] OR heatmap_counter [{heatmap_counter}] is >= heatmap_actions [{heatmap_actions}]\n\n\n\n")
                                    with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                        f.write(f'\n\n{logging_time()} Within BUY (part IV):\n')
                                        f.write(f"{logging_time()} HEATMAP DOES NOT ALLOW BUYING!")
                                        f.write(f"{logging_time()} heatmap_center_coin_counter [{heatmap_center_coin_counter}] is >= heatmap_limit [{heatmap_limit}] OR heatmap_counter [{heatmap_counter}] is >= heatmap_actions [{heatmap_actions}]")
                                else:
                                    print(f"\n\n{logging_time()} HEATMAP ALLOWS BUYING!\n")
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
                                        print(f'{logging_time()} BUY Order placed now at [{order_time}]\n')
                                        print("==============================")
                                        time.sleep(3)
                                        
                                        if RYBKA_MODE == "LIVE":
                                            order_status = client.get_order(symbol = TRADE_SYMBOL, orderId = order["orderId"])
                                        elif RYBKA_MODE == "DEMO":
                                            order_status = {'symbol': 'EGLDUSDT', 'orderId': 0, 'orderListId': -1, 'clientOrderId': 'TXgNl8RNNipASGTrleH6ZY', 'price': '0.00000000', 'origQty': '0.19000000', 'executedQty': '0.19000000', 'cummulativeQuoteQty': '10.20300000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1661098548719, 'updateTime': 1661098548719, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
                                            order_status['orderId'] = order_id_tmp
                                            
                                        if order_status['status'] == "FILLED":
                                            print(f"{logging_time()} ✅ BUY Order filled successfully!\n")
                                            # avoid rounding up on quantity & price bought
                                            print(f"{logging_time()} Transaction ID [{order['orderId']}] - Bought [{int(float(order['executedQty']) * 10 ** 4) / 10 ** 4}] EGLD at price per 1 EGLD of [{int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4}] $")

                                            bnb_commission = float(order['fills'][0]['commission'])
                                            with open(f"{RYBKA_MODE}/most_recent_commission", 'w', encoding="utf8") as f:
                                                f.write(str(order['fills'][0]['commission']))

                                            ktbr_config[order['orderId']] = [int(float(order['executedQty']) * 10 ** 4) / 10 ** 4, int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4]
                                            with open(f"{RYBKA_MODE}/ktbr", 'w', encoding="utf8") as f:
                                                f.write(str(json.dumps(ktbr_config)))
                                            
                                            nr_of_trades += 1

                                            with open(f"{RYBKA_MODE}/number_of_buy_trades", 'w', encoding="utf8") as f:
                                                f.write(str(nr_of_trades))

                                            with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                                f.write(f'\n\n{logging_time()} Within BUY (part V):\n')
                                                f.write(f"{logging_time()} HEATMAP ALLOWS BUYING!\n")
                                                f.write(f"{logging_time()} {'Order time (order_time) is':90} {str(order_time):40}")
                                                f.write(f"{logging_time()} Transaction ID [{str(order['orderId'])}] - Bought [{str(int(float(order['executedQty']) * 10 ** 4) / 10 ** 4)}] EGLD at price per 1 EGLD of [{str(int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4)}] $\n")
                                                f.write(f"{logging_time()} {'Order (order) is':90} {str(json.dumps(order))}\n")
                                                f.write(f"{logging_time()} {'Order status (order_status) is':90} {str(json.dumps(order_status))}\n")
                                                f.write(f"{logging_time()} {'Order commision is':90} {str(order['fills'][0]['commission']):40}\n")
                                                f.write(f"{logging_time()} KTBR config (AFTER processing) (str(json.dumps(ktbr_config))) is {str(json.dumps(ktbr_config)):40}\n")
                                            
                                            back_up()
                                            
                                            if RYBKA_MODE == "LIVE":
                                                for i in range(0,10):
                                                    try:
                                                        account_balance_update()
                                                        print(f"\n{logging_time()} Account Balance Sync. - Successful")
                                                        break
                                                    except Exception as e:
                                                        print(f"\n{logging_time()} Account Balance Sync. - Failed as:\n{e}")
                                                        all_errors_file_update(f"Account Balance Sync. - Failed as:\n{e}")
                                                        time.sleep(3)

                                            print(f"\n\n{logging_time()} USDT balance is [{balance_usdt}]")
                                            print(f"{logging_time()} EGLD balance is [{balance_egld}]")
                                            print(f"{logging_time()} BNB  balance is [{balance_bnb}]")

                                            ktbr_integrity()

                                            print("==============================\n\n\n\n")
                                            with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_order_history", 'a', encoding="utf8") as f:
                                                f.write(f'{logging_time()} Buy order done now at [{str(order_time)}]\n')
                                                f.write(f"{logging_time()} Transaction ID [{str(order['orderId'])}] - Bought [{str(int(float(order['executedQty']) * 10 ** 4) / 10 ** 4)}] EGLD at price per 1 EGLD of [{str(int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4)}] $\n\n\n")
                                            with open(f"{RYBKA_MODE}/full_order_history", 'a', encoding="utf8") as f:
                                                f.write(f'{logging_time()} Buy order done now at [{str(order_time)}]\n')
                                                f.write(f"{logging_time()} Transaction ID [{str(order['orderId'])}] - Bought [{str(int(float(order['executedQty']) * 10 ** 4) / 10 ** 4)}] EGLD at price per 1 EGLD of [{str(int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4)}] $\n\n\n")
                                            
                                            subsequent_valid_rsi_counter = 1

                                            re_sync_time()
                                        else:
                                            print(f"{logging_time()} ❌ Buy order was NOT filled successfully! Please check the cause!")
                                            print("==============================")
                                            with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                                f.write(f'\n\n{logging_time()} Within BUY (part VI):\n')
                                                f.write(f'{logging_time()}  ❌ Buy order was NOT filled successfully! Please check the cause!\n')
                                                f.write(f"{logging_time()} Order (order) is {str(json.dumps(order))}\n")
                                                f.write(f"{logging_time()} Order status (order_status) is {str(json.dumps(order_status))}\n")
                                            exit(7)
                                    except Exception as e:
                                        print(f"\n\n{logging_time()} Make sure the API_KEY and API_SECRET have valid values and time server is synced with NIST's!")
                                        print(f"{logging_time()} Order could NOT be placed due to an error:\n{e}")
                                        all_errors_file_update(f"Order could NOT be placed due to an error:\n{e}")
                                        with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                            f.write(f'\n\n{logging_time()} Within BUY (part VII):\n')
                                            f.write(f'{logging_time()} Order could NOT be placed due to an error:\n{e}\n')
                                        exit(7)
                            else:
                                print(f"\n{logging_time()} Bot might still be able to buy some crypto, but only at a [{min_order_quantity}] EGLD trading quantity, not at the current one set of [{TRADE_QUANTITY}] EGLD per transaction!\n")
                                with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                    f.write(f'\n\n{logging_time()} Within BUY (part VIII):\n')
                                    f.write(f'{logging_time()} Bot might still be able to buy some crypto, but only at a [{min_order_quantity}] EGLD trading quantity, not at the current one set of [{TRADE_QUANTITY}] EGLD per transaction!\n')
                        else:
                            print(f'{logging_time()} Not enough [USDT] to set other BUY orders! Wait for SELLS, or fill up the account with more [USDT].')
                            print(f"\n{logging_time()} Notifying user (via email) that bot might need more money for buy actions, if possible.")
                            email_sender(f"[RYBKA MODE - {RYBKA_MODE}] Bot might be able to buy more, but doesn't have enought USDT in balance [{balance_usdt}]$\n\nTOP UP if possible!")
                            with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                f.write(f'\n\n{logging_time()} Within BUY (part IX):\n')
                                f.write(f'{logging_time()} Not enough [USDT] to set other BUY orders! Wait for SELLS, or fill up the account with more [USDT].\n')
                    else:
                        print(f"{logging_time()} BNB balance [{balance_bnb}] is NOT enough to sustain many more transactions. Please TOP UP!")
                        email_sender(f"{logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot doesn't have enought BNB in balance [{balance_bnb}] to sustain many more trades.\n\nHence, it will stop at this point. Please TOP UP!")
                        with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                            f.write(f'\n\n{logging_time()} Within BUY (part X):\n')
                            f.write(f'{logging_time()} BNB balance [{str(balance_bnb)}] is NOT enough to sustain many more transactions. Please TOP UP!\n')
                        exit(7)

                if latest_rsi > RSI_FOR_SELL:

                    print("\n\n\n==============================")
                    print("==============================")
                    print(f"{logging_time()} SELL SIGNAL!")
                    print("==============================")
                    print("==============================\n")

                    if RYBKA_MODE == "LIVE":
                        for i in range(0,10):
                            try:
                                account_balance_update()
                                print(f"\n{logging_time()} Account Balance Sync. - Successful")
                                break
                            except Exception as e:
                                print(f"\n{logging_time()} Account Balance Sync. - Failed as:\n{e}")
                                all_errors_file_update(f"Account Balance Sync. - Failed as:\n{e}")
                                time.sleep(3)

                    with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                        f.write(f'\n\n\n{logging_time()} Within SELL (part I):\n')
                        f.write(f'{logging_time()} {"Latest RSI (latest_rsi) is":90} {latest_rsi:40}\n')
                        f.write(f"{logging_time()} {'BNB balance (balance_bnb) is':90} {balance_bnb:40}\n")
                        f.write(f"{logging_time()} {'USDT balance (balance_usdt) is':90} {balance_usdt:40}\n")
                        f.write(f"{logging_time()} {'EGLD balance (balance_egld) is':90} {balance_egld:40}\n")
                        f.write(f"{logging_time()} {'BNB commission (bnb_commission) is':90} {bnb_commission:40}\n")
                        f.write(f"{logging_time()} {'Total USDT profit (total_usdt_profit) is':90} {total_usdt_profit:40}\n")
                        f.write(f"{logging_time()} {'Multiple sells (multiple_sells) set to':90} {multiple_sells:40}\n")
                        f.write(f"\n{logging_time()} {'Closed candles (multiple_sells) are':90} {closed_candles}\n")
                        f.write(f"\n{logging_time()} KTBR config (BEFORE processing) (str(json.dumps(ktbr_config))) is \n {str(json.dumps(ktbr_config))}\n\n")

                    if balance_bnb / bnb_commission >= 100:
                        print(f"{logging_time()} BNB balance [{balance_bnb}] is enough for transactions.")
                        
                        eligible_sells = []

                        for k, v in ktbr_config.items():
                            if v[1] + MIN_PROFIT < candle_close_price:
                                print(f"{logging_time()} Identified buy ID [{k:11}], qtty [{v[0]:5}] bought at price of [{v[1]:5}] as being eligible for sell. Multiple sells set as [{multiple_sells}]")
                                eligible_sells.append(k)
                                if multiple_sells == "disabled":
                                    break

                        with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                            f.write(f'\n\n\n{logging_time()} Within SELL (part II):\n')
                            f.write(f"{logging_time()} {'Eligible sells (eligible_sells) is':90} {str(eligible_sells)}\n")

                        if eligible_sells:
                            for sell in eligible_sells:
                                print(f"{logging_time()} Selling buy [{sell:11}] of qtty [{ktbr_config[sell][0]:5}]")

                                try:
                                    back_up()
                                    if RYBKA_MODE == "LIVE":
                                        order = client.order_market_sell(symbol=TRADE_SYMBOL, quantity=ktbr_config[sell][0])
                                        pass
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
                                    print(f'{logging_time()} SELL Order placed now at [{order_time}]\n')
                                    print("==============================")
                                    time.sleep(3)
                                    
                                    if RYBKA_MODE == "LIVE":
                                        order_status = client.get_order(symbol = TRADE_SYMBOL, orderId = order["orderId"])
                                    elif RYBKA_MODE == "DEMO":
                                        order_status = {'symbol': 'EGLDUSDT', 'orderId': 953796254, 'orderListId': -1, 'clientOrderId': 'TXgNl8RNNipASGTrleH6ZY', 'price': '0.00000000', 'origQty': '0.19000000', 'executedQty': '0.19000000', 'cummulativeQuoteQty': '10.20300000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1661098548719, 'updateTime': 1661098548719, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
                                        order_status['orderId'] = str(sell)
                                    
                                    if order_status['status'] == "FILLED":
                                        print(f"{logging_time()} ✅ SELL Order filled successfully!\n")
                                        # avoid rounding up on quantity & price sold
                                        qtty_aux = int(float(order['executedQty']) * 10 ** 4) / 10 ** 4
                                        price_aux = int(float(order['fills'][0]['price']) * 10 ** 4) / 10 ** 4

                                        print(f"{logging_time()} Transaction ID [{order['orderId']}] - Sold [{qtty_aux}] EGLD at price per 1 EGLD of [{price_aux}] $")

                                        total_usdt_profit = int((total_usdt_profit + (price_aux - ktbr_config[sell][1]) * ktbr_config[sell][0]) * 10 ** 4) / 10 ** 4
                                        with open(f"{RYBKA_MODE}/usdt_profit", 'w', encoding="utf8") as f:
                                            f.write(str(total_usdt_profit))

                                        bnb_commission = float(order['fills'][0]['commission'])
                                        with open(f"{RYBKA_MODE}/most_recent_commission", 'w', encoding="utf8") as f:
                                            f.write(str(order['fills'][0]['commission']))

                                        with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                            f.write(f'\n\n{logging_time()} Within SELL (part III):\n')
                                            f.write(f"{logging_time()} Selling buy [{str(sell):11}] {'of qtty':90} [{str(ktbr_config[sell][0]):5}]\n")
                                        
                                        previous_buy_info = f"What got sold: BUY ID [{str(sell):11}] of QTTY [{str(ktbr_config[sell][0]):5}] at bought PRICE of [{str(ktbr_config[sell][1]):5}] $"

                                        del ktbr_config[sell]
                                        with open(f"{RYBKA_MODE}/ktbr", 'w', encoding="utf8") as f:
                                            f.write(str(json.dumps(ktbr_config)))

                                        with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                            f.write(f'\n\n{logging_time()} Within SELL (part IV):\n')
                                            f.write(f"{logging_time()} {'Order time (order_time) is':90} {str(order_time):40}")
                                            f.write(f"{logging_time()} Transaction ID [{str(order['orderId'])}] - Sold [{qtty_aux}] EGLD at price per 1 EGLD of [{str(price_aux)}] $\n")
                                            f.write(f"{logging_time()} {'Order (order) is':90} {str(json.dumps(order))}\n")
                                            f.write(f"{logging_time()} {'Order status (order_status) is':90} {str(json.dumps(order_status))}\n")
                                            f.write(f"{logging_time()} {'Order commission is':90} {str(order['fills'][0]['commission']):40}\n")
                                            f.write(f"{logging_time()} KTBR config (AFTER processing) (str(json.dumps(ktbr_config))) is {str(json.dumps(ktbr_config)):40}\n")

                                        back_up()

                                        if RYBKA_MODE == "LIVE":
                                            for i in range(0,10):
                                                try:
                                                    account_balance_update()
                                                    print(f"\n{logging_time()} Account Balance Sync. - Successful")
                                                    break
                                                except Exception as e:
                                                    print(f"\n{logging_time()} Account Balance Sync. - Failed as:\n{e}")
                                                    all_errors_file_update(f"Account Balance Sync. - Failed as:\n{e}")
                                                    time.sleep(3)
                                        
                                        print(f"\n\n{logging_time()} USDT balance is [{balance_usdt}]")
                                        print(f"{logging_time()} EGLD balance is [{balance_egld}]")
                                        print(f"{logging_time()} BNB  balance is [{balance_bnb}]")

                                        ktbr_integrity()
                                        
                                        print("==============================\n\n\n\n")
                                        with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_order_history", 'a', encoding="utf8") as f:
                                            f.write(f'{logging_time()} Sell order done now at [{str(order_time)}]\n')
                                            f.write(f"{logging_time()} Transaction ID [{order['orderId']}] - Sold [{str(qtty_aux)}] EGLD at price per 1 EGLD of [{str(price_aux)}] $\n")
                                            f.write(f"{logging_time()} {previous_buy_info} \n\n\n")
                                        with open(f"{RYBKA_MODE}/full_order_history", 'a', encoding="utf8") as f:
                                            f.write(f'{logging_time()} Sell order done now at [{str(order_time)}]\n')
                                            f.write(f"{logging_time()} Transaction ID [{order['orderId']}] - Sold [{str(qtty_aux)}] EGLD at price per 1 EGLD of [{str(price_aux)}] $\n")
                                            f.write(f"{logging_time()} {previous_buy_info} \n\n\n")

                                        subsequent_valid_rsi_counter = 1
                                    else:
                                        print(f"{logging_time()} ❌ Sell order was NOT filled successfully! Please check the cause!")
                                        print("==============================")
                                        with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                            f.write(f'\n\n{logging_time()} Within SELL (part V):\n')
                                            f.write(f'{logging_time()}  ❌ Sell order was NOT filled successfully! Please check the cause!\n')
                                            f.write(f"{logging_time()} {'Order (order) is':90} {str(json.dumps(order))}\n")
                                            f.write(f"{logging_time()} {'Order status (order_status) is':90} {str(json.dumps(order_status))}\n")
                                        exit(7)
                                except Exception as e:
                                    print(f"\n\n{logging_time()} Make sure the API_KEY and API_SECRET have valid values and time server is synced with NIST's!")
                                    print(f"{logging_time()} Order could NOT be placed due to an error:\n{e}")
                                    all_errors_file_update(f"Order could NOT be placed due to an error:\n{e}")
                                    with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                        f.write(f'\n\n{logging_time()} Within SELL (part VI):\n')
                                        f.write(f'{logging_time()} Order could NOT be placed due to an error:\n{e}\n')
                                    exit(7)
                            re_sync_time()
                        else:
                            print(f"{logging_time()} No buy transactions are eligible to be sold at this moment!")
                            with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                                f.write(f'\n\n{logging_time()} Within SELL (part VII):\n')
                                f.write(f'{logging_time()} No buy transactions are eligible to be sold at this moment!\n')
                    else:
                        print(f"{logging_time()} BNB balance [{balance_bnb}] is NOT enough to sustain many more transactions. Please TOP UP!")
                        email_sender(f"[RYBKA MODE - {RYBKA_MODE}] Bot doesn't have enought BNB in balance [{balance_bnb}] to sustain many more trades.\n\nHence, it will stop at this point. Please TOP UP!")
                        with open(f"{os.environ.get('CURRENT_EXPORT_DIR')}/{TRADE_SYMBOL}_DEBUG", 'a', encoding="utf8") as f:
                            f.write(f'\n\n{logging_time()} Within SELL (part VIII):\n')
                            f.write(f'{logging_time()} BNB balance [{str(balance_bnb)}] is NOT enough to sustain many more transactions. Please TOP UP!\n')
                        exit(7)


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
            print("\n\n Please run the script with admin privileges as bot needs access to auto-update HOST's time with NIST servers!")
            exit(7)
    
    if RYBKA_MODE == "LIVE":
        print("\n\n====================================================================================================")
        print("====================================================================================================")
        print("=================================  ✅ RYBKA MODE   ---   LIVE ✅  =================================")
        print("====================================================================================================")
        print("====================================================================================================\n\n")

        time.sleep(3)
        clear_terminal()

        if not SET_DISCLAIMER == "disabled":
            disclaimer()
            clear_terminal()
    elif RYBKA_MODE == "DEMO":
        print("\n\n====================================================================================================")
        print("====================================================================================================")
        print("================================= 🛠️  RYBKA MODE   ---   DEMO 🛠️  =================================")
        print("====================================================================================================")
        print("====================================================================================================\n\n")
        time.sleep(3)
        clear_terminal()
    else:
        print(f" PLEASE be clear about the mode you want the bot to operate in! RYBKA MODE set to [{RYBKA_MODE}]!")
        exit(7)
    
    if RSI_PERIOD < 10:
        print("\n ⚠️ Please DO NOT set a value less than [10] for the [RYBKA_RSI_PERIOD] ENV var! To ensure a trustworthy tech. analysis at an RSI level  --->  defaulting to value [10].")
        RSI_PERIOD = 10

    def main_files():
        ktbr_configuration()
        profit_file()
        commission_file()
        nr_of_trades_file()
        full_order_history_file()
        back_up()

    re_sync_time()
    software_config_params()
    user_initial_config()
    email_engine_params()
    log_files_creation()
    binance_system_status()

    if RYBKA_MODE == "LIVE":
        for i in range(0,5):
            try:
                binance_account_status()
                binance_api_account_status()
                account_balance_update()
                ktbr_integrity()
                break
            except Exception as e:
                print(f"\nAccount-related functions failed to proceed successfully. Error:\n{e}")
                all_errors_file_update(f"Account-related functions failed to proceed successfully. Error:\n{e}")
                time.sleep(5)
    
    main_files()

    if RYBKA_MODE == "DEMO":
        if balance_usdt == 500:
            print(f"\nIn [DEMO] mode -> ⚠️  USDT Balance of [{balance_usdt:7}] $      --->  is set by default, by the bot. You can modify it by setting in ENV the var [RYBKA_BALANCE_USDT] and restart the terminal / bot.")
        if balance_egld == 100:
            print(f"\nIn [DEMO] mode -> ⚠️  EGLD Balance of [{balance_egld:7}] coins  --->  is set by default, by the bot. You can modify it by setting in ENV the var [RYBKA_BALANCE_EGLD] and restart the terminal / bot.")
        if balance_bnb == 0.02:
            print(f"\nIn [DEMO] mode -> ⚠️  BNB  Balance of [{balance_bnb:7}] coins  --->  is set by default, by the bot. You can modify it by setting in ENV the var [RYBKA_BALANCE_BNB] and restart the terminal / bot.")

    print("\n=====================================================================================================================================")
    print("=====================================================================================================================================")
    print(f"Account's AVAILABLE balance is:\n\tUSDT  ---  [{balance_usdt}]\n\tEGLD  ---  [{balance_egld}]\n\n\tBNB  ---  [{balance_bnb}] (for transaction fees)")
    print("=====================================================================================================================================")
    if RYBKA_MODE == "LIVE":
        print(f"Account's LOCKED balance in limit orders is:\n\tLOCKED USDT  ---  [{locked_balance_usdt}]\n\tLOCKED EGLD  ---  [{locked_balance_egld}]\n\n\tLOCKED BNB  ---  [{locked_balance_bnb}]")
        print("=====================================================================================================================================")
    print("=====================================================================================================================================")
    print(f"Rybka's historical registered PROFIT is:\n\tUSDT  ---  [{total_usdt_profit}]")
    print("=====================================================================================================================================")
    print("=====================================================================================================================================")

    email_sender(f"{logging_time()} [RYBKA MODE - {RYBKA_MODE}] Bot is starting up. Find logs into the local folder: \n\t[{os.environ.get('CURRENT_EXPORT_DIR')}]")
    bot_uptime()
    
    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message, on_error = on_error)
    ws.run_forever()


main()
