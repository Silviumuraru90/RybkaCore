#!/usr/bin/env python3

# Built-in and Third-Party Libs
import fileinput
import json
import logging
import os
import random
import re
import string as string_str
import subprocess
import sys
import time
from datetime import datetime, timedelta
from os.path import exists

import colored as colored_2
import GPUtil
import psutil
import requests
import telepot
from binance.client import Client
from telegram import ParseMode

# Custom Libs
from telegram.ext import *
from termcolor import colored

from custom_modules.cfg import bootstrap
from custom_modules.telegram import telegram_active_commands as R

try:
    from custom_modules.graph_engine.graph import generate_graph
except:
    pass


####################################################
##############    Logging Handlers    ##############
####################################################

logging.getLogger().setLevel(logging.CRITICAL)


def ORANGE(message):
    print(colored_2.fg(202) + f"{message}")

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


###############################################
########      UNIQUE ID FUNCTION      #########
###############################################


def id_generator(size=10, chars=string_str.ascii_uppercase + string_str.digits):
    return "".join(random.choice(chars) for elem in range(size))


####################################################
##############     Initialization     ##############
####################################################


def initialization():

    print(
        colored(
            """
#########################################################
#####        📡 Telegram listener activated!        #####
#########################################################""",
            "magenta",
        ),
        "\n\n",
        colored(
            f"                                                       ",
            "blue",
            "on_grey",
        ),
        "\n   ",
        colored(
            f'{bcolors.BOLD}<<  Bot currently tracks the [{os.environ.get("TRADE_SYMBOL")}] pair  >>{bcolors.ENDC}',
            "blue",
            "on_grey",
        ),
        "\n",
        colored(
            f"                                                       ",
            "blue",
            "on_grey",
        ),
        "\n",
        colored(
            """
#########################################################
#####                                               #####
#####  1️⃣  Open `Telegram` app on your device        #####
#####  2️⃣  Open your RybkaCore Telegram bot's chat   #####
#####  3️⃣  Type `/help` for details on how to use    #####
#####                                               #####
#########################################################
    \n""",
            "cyan",
        ),
    )

    print(
        colored(
            f'🟢 Telegram Listener initialization finished successfully!\n',
            "green",
        )
    )

####################################################
##############        Main Menu       ##############
####################################################


def help_command(update, context):
    update.message.reply_text(
        f"""Available commands are ⤵️


🟣 FUN commands:
    {'who are you?':20} - Who are you talking to?

🟣 FUNds info on Binance commands:
    {'/deposits':20}    - Deposit History
    {'/withdrawals':20} - Withdrawal H.
    {'/balances':20}    - Acc. Balances
    {'/current_price':20}  - $/cryptocoin

🟣 FUNd handling history of RybkaCore:
    {'/current_buys':20} - Tracked Buys
    {'/lifetime_buys_nr':20}- Total Nr. of Buys
    {'/profit':20}        - Lifetime Profit

🟣 FUNctional commands:
    {'/status':20}       - Bot's Status
    {'/current_uptime':20}- Bot's Uptime
    {'/gpu':20}        - GPU Temp.

    {'/start_rybka':20}   - Starts bot
    {'/stop_rybka':20}   - Stops bot

🟣 FUNctor commands:
    {'/roadmap':20}   - Bot's Roadmap
    {'/stock_bot':20}    - Stockfish
    {'/contribute':20}    - Contribute

🟣 FUNdamental SUBmenu(s):
    {'/weights_info':20}  - Bot's Weights
    {'/modify_weights':20}- Modify Weights
    {'/graphs':20}      - Generate Graphs


❕ Reminder:
    🔄 {'/help'}  -  Shows this help message


❕ Some may only apply to LIVE mode!
❕ Use with caution!
        """
    )


####################################################
##############        Sub-menus       ##############
####################################################


def graphs_info_command(update, context):
    update.message.reply_text(
        f"""Available crypto-graphs are ⤵️

⚠️ Also, this does NOT support all the coins you may want to trade with (request its addition via an email);

⚠️ Please note this has a limitation and may not work for some users;
⚠️ Issue tracked in order to be solved, via:
https://gitlab.com/Silviu_space/rybka/-/issues/350

🟪 Cryptocurrency submenus:
    {'/EGLD'}
    {'/BTC'}
    {'/ETH'}
    {'/BNB'}
    {'/ADA'}
    {'/SOL'}
    {'/DOGE'}
    {'/DOT'}
    {'/DAI'}
    {'/OP'}
    {'/ARB'}
    {'/LINK'}
    {'/FIL'}
    {'/LTC'}
    {'/UNI'}
    {'/ATOM'}
    {'/BCH'}
    {'/ALGO'}
    {'/XMR'}
    {'/XRP'}


    🔄 {'/help'}  -  Back to parent menu
        """
    )


def cryptocoin_command(update, context):
    update.message.reply_text(
        f"""Available Egold graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/EGLD_price_in_the_last_year'}
    {'/EGLD_price_in_the_last_month'}
    {'/EGLD_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def btc_command(update, context):
    update.message.reply_text(
        f"""Available Bitcoin graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/BTC_price_in_the_last_year'}
    {'/BTC_price_in_the_last_month'}
    {'/BTC_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def eth_command(update, context):
    update.message.reply_text(
        f"""Available Ethereum graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/ETH_price_in_the_last_year'}
    {'/ETH_price_in_the_last_month'}
    {'/ETH_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def bnb_command(update, context):
    update.message.reply_text(
        f"""Available Binance Coin graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/BNB_price_in_the_last_year'}
    {'/BNB_price_in_the_last_month'}
    {'/BNB_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def ada_command(update, context):
    update.message.reply_text(
        f"""Available Cardano graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/ADA_price_in_the_last_year'}
    {'/ADA_price_in_the_last_month'}
    {'/ADA_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def sol_command(update, context):
    update.message.reply_text(
        f"""Available Solana graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/SOL_price_in_the_last_year'}
    {'/SOL_price_in_the_last_month'}
    {'/SOL_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def doge_command(update, context):
    update.message.reply_text(
        f"""Available Dogecoin graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/DOGE_price_in_the_last_year'}
    {'/DOGE_price_in_the_last_month'}
    {'/DOGE_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def dot_command(update, context):
    update.message.reply_text(
        f"""Available Polkadot graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/DOT_price_in_the_last_year'}
    {'/DOT_price_in_the_last_month'}
    {'/DOT_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def dai_command(update, context):
    update.message.reply_text(
        f"""Available Dai graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/DAI_price_in_the_last_year'}
    {'/DAI_price_in_the_last_month'}
    {'/DAI_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def op_command(update, context):
    update.message.reply_text(
        f"""Available Optimism graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/OP_price_in_the_last_year'}
    {'/OP_price_in_the_last_month'}
    {'/OP_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def arb_command(update, context):
    update.message.reply_text(
        f"""Available Arbitrum graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/ARB_price_in_the_last_year'}
    {'/ARB_price_in_the_last_month'}
    {'/ARB_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def link_command(update, context):
    update.message.reply_text(
        f"""Available Chainlink graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/LINK_price_in_the_last_year'}
    {'/LINK_price_in_the_last_month'}
    {'/LINK_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def fil_command(update, context):
    update.message.reply_text(
        f"""Available Filecoin graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/FIL_price_in_the_last_year'}
    {'/FIL_price_in_the_last_month'}
    {'/FIL_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def ltc_command(update, context):
    update.message.reply_text(
        f"""Available Litecoin graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/LTC_price_in_the_last_year'}
    {'/LTC_price_in_the_last_month'}
    {'/LTC_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def uni_command(update, context):
    update.message.reply_text(
        f"""Available Uniswap graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/UNI_price_in_the_last_year'}
    {'/UNI_price_in_the_last_month'}
    {'/UNI_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def atom_command(update, context):
    update.message.reply_text(
        f"""Available Cosmos graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/ATOM_price_in_the_last_year'}
    {'/ATOM_price_in_the_last_month'}
    {'/ATOM_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def bch_command(update, context):
    update.message.reply_text(
        f"""Available Bitcoin Cash graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/BCH_price_in_the_last_year'}
    {'/BCH_price_in_the_last_month'}
    {'/BCH_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def algo_command(update, context):
    update.message.reply_text(
        f"""Available Algorand graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/ALGO_price_in_the_last_year'}
    {'/ALGO_price_in_the_last_month'}
    {'/ALGO_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def xmr_command(update, context):
    update.message.reply_text(
        f"""Available Monero graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/XMR_price_in_the_last_year'}
    {'/XMR_price_in_the_last_month'}
    {'/XMR_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )


def xrp_command(update, context):
    update.message.reply_text(
        f"""Available Ripple graphs are ⤵️


🟪 Cryptocurrency submenus:
    {'/XRP_price_in_the_last_year'}
    {'/XRP_price_in_the_last_month'}
    {'/XRP_price_in_the_last_week'}


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/graphs'}  -  Back to parent menu
        """
    )



def weights_info_command(update, context):
    update.message.reply_text(
        f"""Available weights commands are ⤵️


🟪 Hard-coded weights:
    {'/RYBKA_TRADE_SYMBOL'}
    {'/RYBKA_RSI_PERIOD'}

🟪 Update-on-the-fly weights:
    {'/RYBKA_DEBUG_LVL'}
    {'/RYBKA_ALLOW_ONLY_BUYS'}
    {'/RYBKA_ALLOW_ONLY_SELLS'}
    {'/RYBKA_TRADING_BOOST_LVL'}
    {'/RYBKA_RSI_FOR_BUY'}
    {'/RYBKA_RSI_FOR_SELL'}
    {'/RYBKA_TRADE_QUANTITY'}
    {'/RYBKA_MIN_PROFIT'}
    {'/RYBKA_EMAIL_SWITCH'}
    {'/RYBKA_STABLECOIN_SAFETY_NET'}
    {'/RYBKA_EMAIL_SENDER_EMAIL'}
    {'/RYBKA_EMAIL_RECIPIENT_EMAIL'}
    {'/RYBKA_EMAIL_RECIPIENT_NAME'}
    {'/RYBKA_TELEGRAM_SWITCH'}
    {'/RYBKA_DISCLAIMER'}
    {'/RYBKA_ALL_LOG_TLG_SWITCH'}


    🔄 {'/help'}  -  Back to parent menu


❕ Weights specific to DEMO mode are not included!
        """
    )


def weight_modification_command(update, context):
    update.message.reply_text(
        f"""Available weight modification commands are ⤵️


🟪 Modify weights:
    {'/m_RYBKA_ALLOW_ONLY_BUYS'}
    {'/m_RYBKA_ALLOW_ONLY_SELLS'}
    {'/m_RYBKA_TRADING_BOOST_LVL'}
    {'/m_RYBKA_RSI_FOR_BUY'}
    {'/m_RYBKA_RSI_FOR_SELL'}
    {'/m_RYBKA_DEBUG_LVL'}
    {'/m_RYBKA_TRADE_QUANTITY'}
    {'/m_RYBKA_MIN_PROFIT'}
    {'/m_RYBKA_EMAIL_SWITCH'}
    {'/m_RYBKA_TELEGRAM_SWITCH'}
    {'/m_RYBKA_ALL_LOG_TLG_SWITCH'}
    {'/m_RYBKA_STABLECOIN_SAFETY_NET'}


    🔄 {'/help'}  -  Back to parent menu


❕ Weights specific to DEMO mode are not included!
        """
    )


def start_rybka_command(update, context):
    update.message.reply_text(
        f"""Available weight modification commands are ⤵️


❓ Are you sure ❓:
    {'/yes_start_it_in_DEMO_mode'}

    {'/yes_start_it_in_LIVE_mode'}


⚠️ Please note this has a limitation and will not work, if the bot was opened via the GUI, instead of the terminal;
⚠️ Issue tracked in order to be solved, via:
https://gitlab.com/Silviu_space/rybka/-/issues/301


    🔄 {'/help'}  -  Back to parent menu
        """
    )


def stop_rybka_command(update, context):
    update.message.reply_text(
        f"""Available weight modification commands are ⤵️


❓ Are you sure ❓:
    {'/yes_stop_it'}


    🔄 {'/help'}  -  Back to parent menu
        """
    )


####################################################
#########    Command-specific functions    #########
####################################################


def status_command(update, context):
    try:
        with open("TEMP/core_pidTmp", "r", encoding="utf8") as f:
            pID = int(f.read())
        if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
            update.message.reply_text(
                "🟢 Bot is alive and well, no worries! \nGive yourself a pat on the back! \nRelax and stay hydrated!"
            )
        else:
            update.message.reply_text(
                "💤 Bot is stopped. Help it get back on track! \nC'mon! Results, not excuses!"
            )
    except Exception as e:
        update.message.reply_text(
            f"The file for Rybka's PID does NOT exist! Exception raised:\n{e}"
        )


def gpu_command(update, context):
    # Works for Nvidia GPUs
    # Need to find solutions for Intel, AMD and Broadcom
    try:
        if (GPUtil.getGPUs()[0].temperature, float):
            status = f"GPU Temp is {GPUtil.getGPUs()[0].temperature}" + "\xb0" + "C"
            if float(GPUtil.getGPUs()[0].temperature) == 0:
                status = "Your PC does NOT seem to have a GPU-specific senzor!"
    except Exception:
        status = "GPU Temp currently supported for Nvidia GPUs only"
    update.message.reply_text(status)


def current_buys_command(update, context):
    if exists("LIVE/ktbr"):
        with open("LIVE/ktbr", "r", encoding="utf8") as f:
            if os.stat("LIVE/ktbr").st_size == 0:
                update.message.reply_text(" ✅ [LIVE/ktbr] file exists and is empty")
            else:
                try:
                    ktbr_config = json.loads(f.read())
                    if not ktbr_config:
                        update.message.reply_text(
                            "There are no previous buys on Binance platform that need to be tracked for selling!"
                        )
                    for k, v in ktbr_config.items():
                        update.message.reply_text(
                            f' 💳 Transaction [{k}]  ---  [{v[0]}] {os.environ.get("CRYPTOCOIN_SYMBOL")} at [{v[1]}] {os.environ.get("STABLECOIN_SYMBOL")}/{os.environ.get("CRYPTOCOIN_SYMBOL")}'
                        )
                except Exception as e:
                    update.message.reply_text(
                        f"[LIVE/ktbr] file contains wrong formatted content!\nFailing with error:\n{e}"
                    )
    else:
        update.message.reply_text(
            "The file containing previous bot buys on Binance platform, does NOT exist!"
        )


def lifetime_buys_nr_command(update, context):
    if exists("LIVE/number_of_buy_trades"):
        with open("LIVE/number_of_buy_trades", "r", encoding="utf8") as f:
            if os.stat("LIVE/number_of_buy_trades").st_size == 0:
                update.message.reply_text(" ✅ [LIVE/number_of_buy_trades] file exists and is empty")
            else:
                nr_of_buys = int(f.read())
                if not nr_of_buys or nr_of_buys == 0:
                    update.message.reply_text("There are no previous buys on Binance platform!")
                else:
                    update.message.reply_text(f"🗃 Lifetime nr. of buy trades is [{nr_of_buys}]")
    else:
        update.message.reply_text("The file for lifetime nr. of buy trades does NOT exist!")


def profit_command(update, context):
    if exists("LIVE/stablecoin_profit"):
        with open("LIVE/stablecoin_profit", "r", encoding="utf8") as f:
            if os.stat("LIVE/stablecoin_profit").st_size == 0:
                update.message.reply_text(" ✅ [LIVE/stablecoin_profit] file exists and is empty")
            else:
                profit = float(f.read())
                if not profit or profit == 0:
                    update.message.reply_text("There is no previous recorded profit!")
                else:
                    update.message.reply_text(f'💰 Lifetime profit is [{profit}] {os.environ["STABLECOIN_SYMBOL"]}')
    else:
        update.message.reply_text("The file for lifetime profit does NOT exist!")


def user_initial_config():
    global client
    try:
        client = Client(os.environ.get("RYBKA_BIN_KEY"), os.environ.get("RYBKA_BIN_SECRET"))
    except Exception as e:
        print(
            f"Client config  -  FAILED\nError encountered at setting user config. via API KEY and API SECRET. Please check error below:\n{e}"
        )


def binance_withdrawal_history_command(update, context):
    user_initial_config()

    binance_withdrawal_history = client.get_withdraw_history()
    if binance_withdrawal_history:
        for elem in binance_withdrawal_history:
            update.message.reply_text(
                f"""🟢 Withdrawal [{elem['applyTime']}]:\n
[{elem['amount']}] {elem['coin']} sent to:\n
Address [{elem['address']}]\n
☞ via [{elem['network']}] network
Fee applied was [{elem['transactionFee']}] {elem['coin']}\n
    """
            )
    else:
        update.message.reply_text("No crypto withdrawal history found!")


def binance_deposit_history_command(update, context):
    user_initial_config()

    binance_deposits_history = client.get_deposit_history()
    if binance_deposits_history:
        for elem in binance_deposits_history:
            update.message.reply_text(
                f"""🟢 Deposit [{elem['id']}]:\n
[{elem['amount']}] {elem['coin']} sent to:\n
Address [{elem['address']}]"""
            )
    else:
        update.message.reply_text("No crypto deposit history found!")


def current_price_command(update, context):
    try:
        with open("TEMP/priceTmp", "r", encoding="utf8") as f:
            with open("TEMP/core_pidTmp", "r", encoding="utf8") as g:
                pID = int(g.read())
            if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
                current_price = float(f.read())
                update.message.reply_text(f'🩺 Current {os.environ["STABLECOIN_SYMBOL"]} / {os.environ["CRYPTOCOIN_SYMBOL"]} is [{current_price}]')
            else:
                update.message.reply_text(
                    "💤 Bot is stopped. Help it get back on track for an accurate price of EGLD!"
                )
    except Exception as e:
        update.message.reply_text(
            f"The file for current price does NOT exist (most possible) or some other error occured! Exception raised:\n{e}"
        )


def current_uptime_command(update, context):
    try:
        with open("TEMP/uptimeTmp", "r", encoding="utf8") as f:
            with open("TEMP/core_pidTmp", "r", encoding="utf8") as g:
                pID = int(g.read())
            if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
                current_uptime = str(f.read())
                update.message.reply_text(f"🔛 Current uptime is [{current_uptime}]")
            else:
                update.message.reply_text(
                    "💤 Bot is stopped. Help it get back on track for an accurate uptime!"
                )
    except Exception as e:
        update.message.reply_text(
            f"The file for current uptime does NOT exist (most possible) or some other error occured! Exception raised:\n{e}"
        )


def yes_start_it(update, context):
    try:
        with open("TEMP/core_pidTmp", "r", encoding="utf8") as f:
            pID = int(f.read())
        if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
            update.message.reply_text(
                "🟢 Bot is already running! \nDo NOT start multiple instances, they'll corrupt each other's data!"
            )
        else:
            update.message.reply_text("💤 Bot is indeed stopped at this moment.")
            update.message.reply_text("🚀 Starting RybkaCore bot!\nPlease wait...")
            try:
                subprocess.Popen(
                    [
                        "python3",
                        "rybka.py",
                        "-m",
                        f"{str(update.message.text).lower().split('_')[4]}",
                    ]
                )
                for i in range(0, 10):
                    try:
                        time.sleep(2 * i)
                        with open("TEMP/core_pidTmp", "r", encoding="utf8") as f:
                            pID = int(f.read())
                            if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
                                update.message.reply_text(
                                    "✅ Bot got successfully started remotely!"
                                )
                                break
                            elif i == 9:
                                update.message.reply_text("❌ Bot could NOT be started remotely!")
                    except Exception as e:
                        update.message.reply_text(
                            f"Error occured while checking if bot got started or not via a remote command. Exception raised:\n{e}"
                        )
                        time.sleep(5)
            except Exception as e:
                update.message.reply_text(
                    f"❌ Some error occured, bot could NOT be started remotely... Exception raised:\n{e}"
                )
    except Exception as e:
        update.message.reply_text(
            f"The file for Rybka's PID does NOT exist! This needs to exist in order to check if software is already running! Exception raised:\n{e}"
        )


def yes_stop_it(update, context):
    try:
        with open("TEMP/core_pidTmp", "r", encoding="utf8") as f:
            core_pID = int(f.read())
        if psutil.pid_exists(core_pID) and "python" in psutil.Process(core_pID).name():
            update.message.reply_text("🟢 Bot is indeed currently running!")
            if exists("TEMP/pid_rybkaTmp"):
                with open("TEMP/pid_rybkaTmp", "r", encoding="utf8") as g:
                    rybka_pID = int(g.read())
            update.message.reply_text(
                f"🪓 Killing the process [pID:{str(core_pID)}]!\nPlease wait..."
            )
            if psutil.pid_exists(rybka_pID) and "python" in psutil.Process(rybka_pID).name():
                rybka_run = True
                update.message.reply_text(
                    f"🪓 Killing a secondary process [pID:{str(rybka_pID)}]!\nPlease wait..."
                )
            else:
                rybka_run = False
            try:
                if rybka_run:
                    psutil.Process(rybka_pID).kill()
                psutil.Process(core_pID).kill()
                time.sleep(5)
                if psutil.pid_exists(core_pID) and "python" in psutil.Process(core_pID).name():
                    update.message.reply_text(
                        "❌ Bot could NOT be stopped remotely! Interesting, as the kill process cmd did complete just fine..."
                    )
                else:
                    update.message.reply_text("Too bad 🥺, go make profit somewhere else now!")
                    update.message.reply_text("🚮 Bot got successfully stopped remotely!")
            except Exception as e:
                update.message.reply_text(f"Exception raised:\n{e}")
        else:
            update.message.reply_text(
                f"💤 Bot is already stopped at this moment. Last known [pID:{str(core_pID)}]"
            )
            update.message.reply_text("🪓 No process to kill!")
    except Exception as e:
        update.message.reply_text(
            f"The file for Rybka's PID does NOT exist! This needs to exist in order to check if software is already running! Exception raised:\n{e}"
        )


def weights_command(update, context):
    try:
        with open("TEMP/weightsTmp", "r", encoding="utf8") as f:
            with open("TEMP/core_pidTmp", "r", encoding="utf8") as g:
                pID = int(g.read())
            if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
                weights = json.loads(f.read())
                for weight_key, weight_value in weights.items():
                    if update["message"]["text"][1:] == weight_key:
                        update.message.reply_text(f"🟢 [{weight_key}] ➛ [{weight_value}]")
            else:
                update.message.reply_text(
                    "💤 Bot is stopped. Help it get back on track for an accurate representation of weights!"
                )
    except Exception as e:
        update.message.reply_text(
            f"The file for Rybka's weights does NOT exist (most possible) or some other error occured! Exception raised:\n{e}"
        )


def check_existing_bot_process():
    try:
        with open("TEMP/core_pidTmp", "r", encoding="utf8") as f:
            pID = int(f.read())
        if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
            print(
                colored(
                    "\n🟢 Telegram Listener started and connected to bot!\n",
                    "green",
                )
            )
        else:
            print(
                colored(
                    "\n🔴 No bot process for the Telegram Listener to connect to! Running this would be unnecessary...\n",
                    "red",
                )
            )
            sys.exit(0)
    except Exception as e:
        print(
            f"The file for Rybka's PID does NOT exist! This needs to exist in order to check if software is already running! Exception raised:\n{e}"
        )


def roadmap_command(update, context):
    update.message.reply_text(
        text=" 🎯 Please check out <a href='https://gitlab.com/Silviu_space/rybka/-/boards'>[ROADMAP]</a>",
        parse_mode=ParseMode.HTML,
    )


def stock_bot_command(update, context):
    update.message.reply_text(
        text=" 🎯 Please check out <a href='https://gitlab.com/Silviu_space/stockfish'>[STOCKFISH]</a>",
        parse_mode=ParseMode.HTML,
    )


def contribute_command(update, context):
    update.message.reply_text(
        text=" 🎯 Please check out <a href='https://silviu_space.gitlab.io/rybka/'>[CONTRIBUTORS]</a>",
        parse_mode=ParseMode.HTML,
    )


####################################################
##  Command-specific functions for sub-menus P.1  ##
####################################################


def modify_config_ini(weight, value):
    if weight == "RYBKA_TRADING_BOOST_LVL":
        pattern = r"RYBKA_TRADING_BOOST_LVL = \d+"
        replacement = f"RYBKA_TRADING_BOOST_LVL = {value}"

        for line in fileinput.input("config.ini", inplace=True):
            new_line = re.sub(pattern, replacement, line)
            print(new_line, end="")

    elif weight == "RYBKA_ALLOW_ONLY_BUYS":
        pattern = r"RYBKA_ALLOW_ONLY_BUYS = \d+"
        replacement = f"RYBKA_ALLOW_ONLY_BUYS = {value}"

        for line in fileinput.input("config.ini", inplace=True):
            new_line = re.sub(pattern, replacement, line)
            print(new_line, end="")

    elif weight == "RYBKA_ALLOW_ONLY_SELLS":
        pattern = r"RYBKA_ALLOW_ONLY_SELLS = \d+"
        replacement = f"RYBKA_ALLOW_ONLY_SELLS = {value}"

        for line in fileinput.input("config.ini", inplace=True):
            new_line = re.sub(pattern, replacement, line)
            print(new_line, end="")

    elif weight == "RYBKA_RSI_FOR_BUY":
        pattern = r"RYBKA_RSI_FOR_BUY = \d+"
        replacement = f"RYBKA_RSI_FOR_BUY = {value}"

        for line in fileinput.input("config.ini", inplace=True):
            new_line = re.sub(pattern, replacement, line)
            print(new_line, end="")

    elif weight == "RYBKA_BALANCES_AUX":
        pattern = r"RYBKA_BALANCES_AUX =.*"
        replacement = f"RYBKA_BALANCES_AUX = {value}"

        for line in fileinput.input("config.ini", inplace=True):
            new_line = re.sub(pattern, replacement, line)
            print(new_line, end="")

    elif weight == "RYBKA_RSI_FOR_SELL":
        pattern = r"RYBKA_RSI_FOR_SELL = \d+"
        replacement = f"RYBKA_RSI_FOR_SELL = {value}"

        for line in fileinput.input("config.ini", inplace=True):
            new_line = re.sub(pattern, replacement, line)
            print(new_line, end="")

    elif weight == "RYBKA_DEBUG_LVL":
        pattern = r"RYBKA_DEBUG_LVL =.*"
        replacement = f"RYBKA_DEBUG_LVL = {value}"

        for line in fileinput.input("config.ini", inplace=True):
            new_line = re.sub(pattern, replacement, line)
            print(new_line, end="")

    elif weight == "RYBKA_STABLECOIN_SAFETY_NET":
        pattern = r"RYBKA_STABLECOIN_SAFETY_NET =.*"
        replacement = f"RYBKA_STABLECOIN_SAFETY_NET = {value}"

        for line in fileinput.input("config.ini", inplace=True):
            new_line = re.sub(pattern, replacement, line)
            print(new_line, end="")

    elif weight == "RYBKA_TRADE_QUANTITY":
        pattern = r"RYBKA_TRADE_QUANTITY = \d+.*"
        replacement = f"RYBKA_TRADE_QUANTITY = {value}"

        for line in fileinput.input("config.ini", inplace=True):
            new_line = re.sub(pattern, replacement, line)
            print(new_line, end="")

    elif weight == "RYBKA_MIN_PROFIT":
        pattern = r"RYBKA_MIN_PROFIT = \d+.*"
        replacement = f"RYBKA_MIN_PROFIT = {value}"

        for line in fileinput.input("config.ini", inplace=True):
            new_line = re.sub(pattern, replacement, line)
            print(new_line, end="")

    elif weight == "RYBKA_EMAIL_SWITCH":
        pattern = r"RYBKA_EMAIL_SWITCH = .*"
        replacement = f"RYBKA_EMAIL_SWITCH = {value}"

        for line in fileinput.input("config.ini", inplace=True):
            new_line = re.sub(pattern, replacement, line)
            print(new_line, end="")

    elif weight == "RYBKA_TELEGRAM_SWITCH":
        pattern = r"RYBKA_TELEGRAM_SWITCH = .*"
        replacement = f"RYBKA_TELEGRAM_SWITCH = {value}"

        for line in fileinput.input("config.ini", inplace=True):
            new_line = re.sub(pattern, replacement, line)
            print(new_line, end="")

    elif weight == "RYBKA_ALL_LOG_TLG_SWITCH":
        pattern = r"RYBKA_ALL_LOG_TLG_SWITCH = .*"
        replacement = f"RYBKA_ALL_LOG_TLG_SWITCH = {value}"

        for line in fileinput.input("config.ini", inplace=True):
            new_line = re.sub(pattern, replacement, line)
            print(new_line, end="")

    time.sleep(1)


####################################################
##   RYBKA_TRADING_BOOST_LVL-specific functions   ##
####################################################


def modification_notice_log(update, context):
    update.message.reply_text(
        " 🟪 Modify signal sent\nPlease wait for confirmation from bot (< 1 min)!"
    )


def m_RYBKA_TRADING_BOOST_LVL_1_command(update, context):
    modify_config_ini("RYBKA_TRADING_BOOST_LVL", "1")
    modification_notice_log(update, context)


def m_RYBKA_TRADING_BOOST_LVL_2_command(update, context):
    modify_config_ini("RYBKA_TRADING_BOOST_LVL", "2")
    modification_notice_log(update, context)


def m_RYBKA_TRADING_BOOST_LVL_3_command(update, context):
    modify_config_ini("RYBKA_TRADING_BOOST_LVL", "3")
    modification_notice_log(update, context)


def m_RYBKA_TRADING_BOOST_LVL_4_command(update, context):
    modify_config_ini("RYBKA_TRADING_BOOST_LVL", "4")
    modification_notice_log(update, context)


def m_RYBKA_TRADING_BOOST_LVL_5_command(update, context):
    modify_config_ini("RYBKA_TRADING_BOOST_LVL", "5")
    modification_notice_log(update, context)


####################################################
##    RYBKA_ALLOW_ONLY_BUYS-specific functions    ##
####################################################


def m_RYBKA_ALLOW_ONLY_BUYS_0_command(update, context):
    modify_config_ini("RYBKA_ALLOW_ONLY_BUYS", "0")
    modification_notice_log(update, context)


def m_RYBKA_ALLOW_ONLY_BUYS_1_command(update, context):
    modify_config_ini("RYBKA_ALLOW_ONLY_BUYS", "1")
    modification_notice_log(update, context)


####################################################
##    RYBKA_ALLOW_ONLY_SELLS-specific functions   ##
####################################################


def m_RYBKA_ALLOW_ONLY_SELLS_0_command(update, context):
    modify_config_ini("RYBKA_ALLOW_ONLY_SELLS", "0")
    modification_notice_log(update, context)


def m_RYBKA_ALLOW_ONLY_SELLS_1_command(update, context):
    modify_config_ini("RYBKA_ALLOW_ONLY_SELLS", "1")
    modification_notice_log(update, context)


####################################################
##      RYBKA_RSI_FOR_BUY-specific functions      ##
####################################################


def m_RYBKA_RSI_FOR_BUY_20_command(update, context):
    modify_config_ini("RYBKA_RSI_FOR_BUY", "20")
    modification_notice_log(update, context)


def m_RYBKA_RSI_FOR_BUY_25_command(update, context):
    modify_config_ini("RYBKA_RSI_FOR_BUY", "25")
    modification_notice_log(update, context)


def m_RYBKA_RSI_FOR_BUY_28_command(update, context):
    modify_config_ini("RYBKA_RSI_FOR_BUY", "28")
    modification_notice_log(update, context)


def m_RYBKA_RSI_FOR_BUY_30_command(update, context):
    modify_config_ini("RYBKA_RSI_FOR_BUY", "30")
    modification_notice_log(update, context)


def m_RYBKA_RSI_FOR_BUY_32_command(update, context):
    modify_config_ini("RYBKA_RSI_FOR_BUY", "32")
    modification_notice_log(update, context)


def m_RYBKA_RSI_FOR_BUY_35_command(update, context):
    modify_config_ini("RYBKA_RSI_FOR_BUY", "35")
    modification_notice_log(update, context)


def m_RYBKA_RSI_FOR_BUY_40_command(update, context):
    modify_config_ini("RYBKA_RSI_FOR_BUY", "40")
    modification_notice_log(update, context)


####################################################
##     RYBKA_RSI_FOR_SELL-specific functions      ##
####################################################


def m_RYBKA_RSI_FOR_SELL_60_command(update, context):
    modify_config_ini("RYBKA_RSI_FOR_SELL", "60")
    modification_notice_log(update, context)


def m_RYBKA_RSI_FOR_SELL_65_command(update, context):
    modify_config_ini("RYBKA_RSI_FOR_SELL", "65")
    modification_notice_log(update, context)


def m_RYBKA_RSI_FOR_SELL_68_command(update, context):
    modify_config_ini("RYBKA_RSI_FOR_SELL", "68")
    modification_notice_log(update, context)


def m_RYBKA_RSI_FOR_SELL_70_command(update, context):
    modify_config_ini("RYBKA_RSI_FOR_SELL", "70")
    modification_notice_log(update, context)


def m_RYBKA_RSI_FOR_SELL_72_command(update, context):
    modify_config_ini("RYBKA_RSI_FOR_SELL", "72")
    modification_notice_log(update, context)


def m_RYBKA_RSI_FOR_SELL_75_command(update, context):
    modify_config_ini("RYBKA_RSI_FOR_SELL", "75")
    modification_notice_log(update, context)


def m_RYBKA_RSI_FOR_SELL_80_command(update, context):
    modify_config_ini("RYBKA_RSI_FOR_SELL", "80")
    modification_notice_log(update, context)


####################################################
##       RYBKA_DEBUG_LVL-specific functions       ##
####################################################


def m_RYBKA_DEBUG_LVL_unset_command(update, context):
    modify_config_ini("RYBKA_DEBUG_LVL", "")
    modification_notice_log(update, context)


def m_RYBKA_DEBUG_LVL_1_command(update, context):
    modify_config_ini("RYBKA_DEBUG_LVL", "1")
    modification_notice_log(update, context)


def m_RYBKA_DEBUG_LVL_2_command(update, context):
    modify_config_ini("RYBKA_DEBUG_LVL", "2")
    modification_notice_log(update, context)


def m_RYBKA_DEBUG_LVL_3_command(update, context):
    modify_config_ini("RYBKA_DEBUG_LVL", "3")
    modification_notice_log(update, context)


####################################################
##    RYBKA_STABLECOIN_SAFETY_NET-specific functions    ##
####################################################


def m_RYBKA_STABLECOIN_SAFETY_NET_0_command(update, context):
    modify_config_ini("RYBKA_STABLECOIN_SAFETY_NET", "0")
    modification_notice_log(update, context)


def m_RYBKA_STABLECOIN_SAFETY_NET_50_command(update, context):
    modify_config_ini("RYBKA_STABLECOIN_SAFETY_NET", "50")
    modification_notice_log(update, context)


def m_RYBKA_STABLECOIN_SAFETY_NET_100_command(update, context):
    modify_config_ini("RYBKA_STABLECOIN_SAFETY_NET", "100")
    modification_notice_log(update, context)


def m_RYBKA_STABLECOIN_SAFETY_NET_200_command(update, context):
    modify_config_ini("RYBKA_STABLECOIN_SAFETY_NET", "200")
    modification_notice_log(update, context)


def m_RYBKA_STABLECOIN_SAFETY_NET_350_command(update, context):
    modify_config_ini("RYBKA_STABLECOIN_SAFETY_NET", "350")
    modification_notice_log(update, context)


def m_RYBKA_STABLECOIN_SAFETY_NET_500_command(update, context):
    modify_config_ini("RYBKA_STABLECOIN_SAFETY_NET", "500")
    modification_notice_log(update, context)


def m_RYBKA_STABLECOIN_SAFETY_NET_750_command(update, context):
    modify_config_ini("RYBKA_STABLECOIN_SAFETY_NET", "750")
    modification_notice_log(update, context)


def m_RYBKA_STABLECOIN_SAFETY_NET_1000_command(update, context):
    modify_config_ini("RYBKA_STABLECOIN_SAFETY_NET", "1000")
    modification_notice_log(update, context)


def m_RYBKA_STABLECOIN_SAFETY_NET_1500_command(update, context):
    modify_config_ini("RYBKA_STABLECOIN_SAFETY_NET", "1500")
    modification_notice_log(update, context)


def m_RYBKA_STABLECOIN_SAFETY_NET_3000_command(update, context):
    modify_config_ini("RYBKA_STABLECOIN_SAFETY_NET", "3000")
    modification_notice_log(update, context)


def m_RYBKA_STABLECOIN_SAFETY_NET_5000_command(update, context):
    modify_config_ini("RYBKA_STABLECOIN_SAFETY_NET", "5000")
    modification_notice_log(update, context)


def m_RYBKA_STABLECOIN_SAFETY_NET_7500_command(update, context):
    modify_config_ini("RYBKA_STABLECOIN_SAFETY_NET", "7500")
    modification_notice_log(update, context)


####################################################
##     RYBKA_TRADE_QUANTITY-specific functions    ##
####################################################


def m_RYBKA_TRADE_QUANTITY_0_1_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "0.1")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_0_2_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "0.2")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_0_3_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "0.3")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_0_4_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "0.4")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_0_5_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "0.5")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_0_6_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "0.6")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_0_7_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "0.7")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_0_8_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "0.8")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_0_9_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "0.9")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_1_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "1")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_1_2_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "1.2")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_1_5_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "1.5")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_1_8_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "1.8")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_2_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "2")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_2_2_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "2.2")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_2_5_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "2.5")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_2_8_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "2.8")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_3_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "3")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_3_5_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "3.5")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_4_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "4")
    modification_notice_log(update, context)


def m_RYBKA_TRADE_QUANTITY_5_command(update, context):
    modify_config_ini("RYBKA_TRADE_QUANTITY", "5")
    modification_notice_log(update, context)


####################################################
##       RYBKA_MIN_PROFIT-specific functions      ##
####################################################


def m_RYBKA_MIN_PROFIT_0_1_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "0.1")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_0_2_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "0.2")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_0_3_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "0.3")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_0_4_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "0.4")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_0_5_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "0.5")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_0_6_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "0.6")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_0_7_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "0.7")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_0_8_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "0.8")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_0_9_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "0.9")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_1_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "1")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_1_2_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "1.2")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_1_5_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "1.5")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_1_8_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "1.8")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_2_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "2")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_2_2_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "2.2")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_2_5_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "2.5")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_2_8_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "2.8")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_3_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "3")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_3_5_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "3.5")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_4_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "4")
    modification_notice_log(update, context)


def m_RYBKA_MIN_PROFIT_5_command(update, context):
    modify_config_ini("RYBKA_MIN_PROFIT", "5")
    modification_notice_log(update, context)


####################################################
##     RYBKA_EMAIL_SWITCH-specific functions      ##
####################################################


def m_RYBKA_EMAIL_SWITCH_true_command(update, context):
    modify_config_ini("RYBKA_EMAIL_SWITCH", "True")
    modification_notice_log(update, context)


def m_RYBKA_EMAIL_SWITCH_false_command(update, context):
    modify_config_ini("RYBKA_EMAIL_SWITCH", "False")
    modification_notice_log(update, context)


####################################################
##    RYBKA_TELEGRAM_SWITCH-specific functions    ##
####################################################


def m_RYBKA_TELEGRAM_SWITCH_true_command(update, context):
    modify_config_ini("RYBKA_TELEGRAM_SWITCH", "True")
    modification_notice_log(update, context)


def m_RYBKA_TELEGRAM_SWITCH_false_command(update, context):
    modify_config_ini("RYBKA_TELEGRAM_SWITCH", "False")
    modification_notice_log(update, context)


####################################################
##  RYBKA_ALL_LOG_TLG_SWITCH-specific functions   ##
####################################################


def m_RYBKA_ALL_LOG_TLG_SWITCH_true_command(update, context):
    modify_config_ini("RYBKA_ALL_LOG_TLG_SWITCH", "True")
    modification_notice_log(update, context)


def m_RYBKA_ALL_LOG_TLG_SWITCH_false_command(update, context):
    modify_config_ini("RYBKA_ALL_LOG_TLG_SWITCH", "False")
    modification_notice_log(update, context)


####################################################
##      RYBKA_BALANCES_AUX-specific functions     ##
####################################################


def m_RYBKA_BALANCES_AUX_true_command(update, context):
    update.message.reply_text(
        " 🟪 Balances will be displayed in less than a minute.\n\nPlease wait..."
    )
    modify_config_ini("RYBKA_BALANCES_AUX", "True")


def m_RYBKA_BALANCES_AUX_false_command(update, context):
    modify_config_ini("RYBKA_BALANCES_AUX", "False")


####################################################
##  Command-specific functions for sub-menus P.2  ##
####################################################


def call_submenu_of_weight(update, context, weight):
    if weight == "RYBKA_TRADING_BOOST_LVL":
        update.message.reply_text(
            f"""Available [RYBKA_TRADING_BOOST_LVL] weight modification commands are ⤵️


❔ Firstly you may want to check the current value of this weight:
    {'/RYBKA_TRADING_BOOST_LVL'} - Checks current value

🟫 Choose the value you want to set for this weight:
    {'/RYBKA_TRADING_BOOST_LVL_1'} - Set value "1"
    {'/RYBKA_TRADING_BOOST_LVL_2'} - Set value "2"
    {'/RYBKA_TRADING_BOOST_LVL_3'} - Set value "3"
    {'/RYBKA_TRADING_BOOST_LVL_4'} - Set value "4"
    {'/RYBKA_TRADING_BOOST_LVL_5'} - Set value "5"


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/modify_weights'}  -  Back to parent menu


❕ Weights specific to DEMO mode are not included!
        """
        )

    elif weight == "RYBKA_ALLOW_ONLY_BUYS":
        update.message.reply_text(
            f"""Available [RYBKA_ALLOW_ONLY_BUYS] weight modification commands are ⤵️


❔ Firstly you may want to check the current value of this weight:
    {'/RYBKA_ALLOW_ONLY_BUYS'} - Checks current value

🟫 Choose the value you want to set for this weight:
    {'/RYBKA_ALLOW_ONLY_BUYS_0'} - Set value "0"
    {'/RYBKA_ALLOW_ONLY_BUYS_1'} - Set value "1"



    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/modify_weights'}  -  Back to parent menu


❕ Weights specific to DEMO mode are not included!
        """
        )

    elif weight == "RYBKA_ALLOW_ONLY_SELLS":
        update.message.reply_text(
            f"""Available [RYBKA_ALLOW_ONLY_SELLS] weight modification commands are ⤵️


❔ Firstly you may want to check the current value of this weight:
    {'/RYBKA_ALLOW_ONLY_SELLS'} - Checks current value

🟫 Choose the value you want to set for this weight:
    {'/RYBKA_ALLOW_ONLY_SELLS_0'} - Set value "0"
    {'/RYBKA_ALLOW_ONLY_SELLS_1'} - Set value "1"



    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/modify_weights'}  -  Back to parent menu


❕ Weights specific to DEMO mode are not included!
        """
        )

    elif weight == "RYBKA_RSI_FOR_BUY":
        update.message.reply_text(
            f"""Available [RYBKA_RSI_FOR_BUY] weight modification commands are ⤵️


❔ Firstly you may want to check the current value of this weight:
    {'/RYBKA_RSI_FOR_BUY'} - Checks current value

🟫 Choose the value you want to set for this weight:
    {'/RYBKA_RSI_FOR_BUY_20'} - Set value "20"
    {'/RYBKA_RSI_FOR_BUY_25'} - Set value "25"
    {'/RYBKA_RSI_FOR_BUY_28'} - Set value "28"
    {'/RYBKA_RSI_FOR_BUY_30'} - Set value "30"
    {'/RYBKA_RSI_FOR_BUY_32'} - Set value "32"
    {'/RYBKA_RSI_FOR_BUY_35'} - Set value "35"
    {'/RYBKA_RSI_FOR_BUY_40'} - Set value "40"



    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/modify_weights'}  -  Back to parent menu


❕ Weights specific to DEMO mode are not included!
        """
        )

    elif weight == "RYBKA_RSI_FOR_SELL":
        update.message.reply_text(
            f"""Available [RYBKA_RSI_FOR_SELL] weight modification commands are ⤵️


❔ Firstly you may want to check the current value of this weight:
    {'/RYBKA_RSI_FOR_SELL'} - Checks current value

🟫 Choose the value you want to set for this weight:
    {'/RYBKA_RSI_FOR_SELL_60'} - Set value "60"
    {'/RYBKA_RSI_FOR_SELL_65'} - Set value "65"
    {'/RYBKA_RSI_FOR_SELL_68'} - Set value "68"
    {'/RYBKA_RSI_FOR_SELL_70'} - Set value "70"
    {'/RYBKA_RSI_FOR_SELL_72'} - Set value "72"
    {'/RYBKA_RSI_FOR_SELL_75'} - Set value "75"
    {'/RYBKA_RSI_FOR_SELL_80'} - Set value "80"



    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/modify_weights'}  -  Back to parent menu


❕ Weights specific to DEMO mode are not included!
        """
        )

    elif weight == "RYBKA_DEBUG_LVL":
        update.message.reply_text(
            f"""Available [RYBKA_DEBUG_LVL] weight modification commands are ⤵️


❔ Firstly you may want to check the current value of this weight:
    {'/RYBKA_DEBUG_LVL'} - Checks current value

🟫 Choose the value you want to set for this weight:
    {'/RYBKA_DEBUG_LVL_unset'} - Unset the value
    {'/RYBKA_DEBUG_LVL_1'} - Set value "1"
    {'/RYBKA_DEBUG_LVL_2'} - Set value "2"
    {'/RYBKA_DEBUG_LVL_3'} - Set value "3"



    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/modify_weights'}  -  Back to parent menu


❕ Weights specific to DEMO mode are not included!
        """
        )

    elif weight == "RYBKA_STABLECOIN_SAFETY_NET":
        update.message.reply_text(
            f"""Available [RYBKA_STABLECOIN_SAFETY_NET] weight modification commands are ⤵️


❔ Firstly you may want to check the current value of this weight:
    {'/RYBKA_STABLECOIN_SAFETY_NET'} - Checks current value

🟫 Choose the value you want to set for this weight:
    {'/RYBKA_STABLECOIN_SAFETY_NET_0'} - Unset any value
    {'/RYBKA_STABLECOIN_SAFETY_NET_50'} - Set value "50"
    {'/RYBKA_STABLECOIN_SAFETY_NET_100'} - Set value "100"
    {'/RYBKA_STABLECOIN_SAFETY_NET_200'} - Set value "200"
    {'/RYBKA_STABLECOIN_SAFETY_NET_350'} - Set value "350"
    {'/RYBKA_STABLECOIN_SAFETY_NET_500'} - Set value "500"
    {'/RYBKA_STABLECOIN_SAFETY_NET_750'} - Set value "750"
    {'/RYBKA_STABLECOIN_SAFETY_NET_1000'} - Set value "1000"
    {'/RYBKA_STABLECOIN_SAFETY_NET_1500'} - Set value "1500"
    {'/RYBKA_STABLECOIN_SAFETY_NET_3000'} - Set value "3000"
    {'/RYBKA_STABLECOIN_SAFETY_NET_5000'} - Set value "5000"
    {'/RYBKA_STABLECOIN_SAFETY_NET_7500'} - Set value "7500"



    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/modify_weights'}  -  Back to parent menu


❕ Weights specific to DEMO mode are not included!
        """
        )

    elif weight == "RYBKA_TRADE_QUANTITY":
        update.message.reply_text(
            f"""Available [RYBKA_TRADE_QUANTITY] weight modification commands are ⤵️


❔ Firstly you may want to check the current value of this weight:
    {'/RYBKA_TRADE_QUANTITY'} - Checks current value

🟫 Choose the value you want to set for this weight:
    {'/RYBKA_TRADE_QUANTITY_0_1'} - Set value "0.1"
    {'/RYBKA_TRADE_QUANTITY_0_2'} - Set value "0.2"
    {'/RYBKA_TRADE_QUANTITY_0_3'} - Set value "0.3"
    {'/RYBKA_TRADE_QUANTITY_0_4'} - Set value "0.4"
    {'/RYBKA_TRADE_QUANTITY_0_5'} - Set value "0.5"
    {'/RYBKA_TRADE_QUANTITY_0_6'} - Set value "0.6"
    {'/RYBKA_TRADE_QUANTITY_0_7'} - Set value "0.7"
    {'/RYBKA_TRADE_QUANTITY_0_8'} - Set value "0.8"
    {'/RYBKA_TRADE_QUANTITY_0_9'} - Set value "0.9"
    {'/RYBKA_TRADE_QUANTITY_1'}   - Set value "1"
    {'/RYBKA_TRADE_QUANTITY_1_2'} - Set value "1.2"
    {'/RYBKA_TRADE_QUANTITY_1_5'} - Set value "1.5"
    {'/RYBKA_TRADE_QUANTITY_1_8'} - Set value "1.8"
    {'/RYBKA_TRADE_QUANTITY_2'}   - Set value "2"
    {'/RYBKA_TRADE_QUANTITY_2_2'} - Set value "2.2"
    {'/RYBKA_TRADE_QUANTITY_2_5'} - Set value "2.5"
    {'/RYBKA_TRADE_QUANTITY_2_8'} - Set value "2.8"
    {'/RYBKA_TRADE_QUANTITY_3'}   - Set value "3"
    {'/RYBKA_TRADE_QUANTITY_3_5'} - Set value "3.5"
    {'/RYBKA_TRADE_QUANTITY_4'}   - Set value "4"
    {'/RYBKA_TRADE_QUANTITY_5'}   - Set value "5"


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/modify_weights'}  -  Back to parent menu


❕ Weights specific to DEMO mode are not included!
        """
        )

    elif weight == "RYBKA_MIN_PROFIT":
        update.message.reply_text(
            f"""Available [RYBKA_MIN_PROFIT] weight modification commands are ⤵️


❔ Firstly you may want to check the current value of this weight:
    {'/RYBKA_MIN_PROFIT'} - Checks current value

🟫 Choose the value you want to set for this weight:
    {'/RYBKA_MIN_PROFIT_0_1'} - Set value "0.1"
    {'/RYBKA_MIN_PROFIT_0_2'} - Set value "0.2"
    {'/RYBKA_MIN_PROFIT_0_3'} - Set value "0.3"
    {'/RYBKA_MIN_PROFIT_0_4'} - Set value "0.4"
    {'/RYBKA_MIN_PROFIT_0_5'} - Set value "0.5"
    {'/RYBKA_MIN_PROFIT_0_6'} - Set value "0.6"
    {'/RYBKA_MIN_PROFIT_0_7'} - Set value "0.7"
    {'/RYBKA_MIN_PROFIT_0_8'} - Set value "0.8"
    {'/RYBKA_MIN_PROFIT_0_9'} - Set value "0.9"
    {'/RYBKA_MIN_PROFIT_1'}   - Set value "1"
    {'/RYBKA_MIN_PROFIT_1_2'} - Set value "1.2"
    {'/RYBKA_MIN_PROFIT_1_5'} - Set value "1.5"
    {'/RYBKA_MIN_PROFIT_1_8'} - Set value "1.8"
    {'/RYBKA_MIN_PROFIT_2'}   - Set value "2"
    {'/RYBKA_MIN_PROFIT_2_2'} - Set value "2.2"
    {'/RYBKA_MIN_PROFIT_2_5'} - Set value "2.5"
    {'/RYBKA_MIN_PROFIT_2_8'} - Set value "2.8"
    {'/RYBKA_MIN_PROFIT_3'}   - Set value "3"
    {'/RYBKA_MIN_PROFIT_3_5'} - Set value "3.5"
    {'/RYBKA_MIN_PROFIT_4'}   - Set value "4"
    {'/RYBKA_MIN_PROFIT_5'}   - Set value "5"


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/modify_weights'}  -  Back to parent menu


❕ Weights specific to DEMO mode are not included!
        """
        )

    elif weight == "RYBKA_EMAIL_SWITCH":
        update.message.reply_text(
            f"""Available [RYBKA_EMAIL_SWITCH] weight modification commands are ⤵️


❔ Firstly you may want to check the current value of this weight:
    {'/RYBKA_EMAIL_SWITCH'} - Checks current value

🟫 Choose the value you want to set for this weight:
    {'/RYBKA_EMAIL_SWITCH_true'} - Set value "True"
    {'/RYBKA_EMAIL_SWITCH_false'} - Set value "False"


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/modify_weights'}  -  Back to parent menu


❕ Weights specific to DEMO mode are not included!
        """
        )

    elif weight == "RYBKA_TELEGRAM_SWITCH":
        update.message.reply_text(
            f"""Available [RYBKA_TELEGRAM_SWITCH] weight modification commands are ⤵️


❔ Firstly you may want to check the current value of this weight:
    {'/RYBKA_TELEGRAM_SWITCH'} - Checks current value

🟫 Choose the value you want to set for this weight:
    {'/RYBKA_TELEGRAM_SWITCH_true'} - Set value "True"
    {'/RYBKA_TELEGRAM_SWITCH_false'} - Set value "False"


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/modify_weights'}  -  Back to parent menu


❕ Weights specific to DEMO mode are not included!
        """
        )

    elif weight == "RYBKA_ALL_LOG_TLG_SWITCH":
        update.message.reply_text(
            f"""Available [RYBKA_ALL_LOG_TLG_SWITCH] weight modification commands are ⤵️


❔ Firstly you may want to check the current value of this weight:
    {'/RYBKA_ALL_LOG_TLG_SWITCH'} - Checks current value

🟫 Choose the value you want to set for this weight:
    {'/RYBKA_ALL_LOG_TLG_SWITCH_true'} - Set value "True"
    {'/RYBKA_ALL_LOG_TLG_SWITCH_false'} - Set value "False"


    🔄 {'/help'}  -  Shows the `help` message

    🔄 {'/modify_weights'}  -  Back to parent menu


❕ Weights specific to DEMO mode are not included!
        """
        )


def modify_weights_command(update, context):
    if exists("config.ini"):
        call_submenu_of_weight(update, context, update["message"]["text"][3:])


####################################################
##########    Graph related Functions    ###########
####################################################


def local_pic(update, image):
    try:
        bot = telepot.Bot(bootstrap.TELE_KEY)
        bot.sendPhoto(
            bootstrap.TELE_CHAT_ID,
            photo=open(f"custom_modules/telegram/data/pics/{image}.png", "rb"),
        )
    except Exception:
        update.message.reply_text("Local image could not be sent via TELEGRAM!")


def generate_graph_command(update, context):
    usd_prices = []
    eur_prices = []

    currency = update["message"]["text"].split("_")[0][1:]
    timeframe = update["message"]["text"].split("_")[5]

    graph_image_name = f"graph_{currency}_{timeframe}_" + id_generator()

    def api_call(currency, date):
        r = ""

        if currency == "EGLD":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/elrond-erd-2/history?date={date}&localization=false"
            )
        elif currency == "BTC":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/bitcoin/history?date={date}&localization=false"
            )
        elif currency == "ETH":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/ethereum/history?date={date}&localization=false"
            )
        elif currency == "BNB":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/binancecoin/history?date={date}&localization=false"
            )
        elif currency == "ADA":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/cardano/history?date={date}&localization=false"
            )
        elif currency == "SOL":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/solana/history?date={date}&localization=false"
            )
        elif currency == "DOGE":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/dogecoin/history?date={date}&localization=false"
            )
        elif currency == "DOT":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/polkadot/history?date={date}&localization=false"
            )
        elif currency == "DAI":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/dai/history?date={date}&localization=false"
            )
        elif currency == "OP":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/optimism/history?date={date}&localization=false"
            )
        elif currency == "ARB":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/arbitrum/history?date={date}&localization=false"
            )
        elif currency == "LINK":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/chainlink/history?date={date}&localization=false"
            )
        elif currency == "FIL":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/filecoin/history?date={date}&localization=false"
            )
        elif currency == "LIT":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/litecoin/history?date={date}&localization=false"
            )
        elif currency == "UNI":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/uniswap/history?date={date}&localization=false"
            )
        elif currency == "ATOM":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/cosmos/history?date={date}&localization=false"
            )
        elif currency == "BCH":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/bitcoin-cash/history?date={date}&localization=false"
            )
        elif currency == "ALGO":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/algorand/history?date={date}&localization=false"
            )
        elif currency == "XMR":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/monero/history?date={date}&localization=false"
            )
        elif currency == "XRP":
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/ripple/history?date={date}&localization=false"
            )

        if r.status_code != 200:
            return "ratelimited"

        usd_price = r.json()["market_data"]["current_price"]["usd"]
        eur_price = r.json()["market_data"]["current_price"]["eur"]

        return [f"{usd_price:.2f}", f"{eur_price:.2f}"]

    def generate_dates(timeframe):
        today = datetime.now()

        date_list = []
        for i in range(timeframe):
            date = today - timedelta(days=i)
            formatted_date = date.strftime("%d-%m-%Y")
            date_list.append(formatted_date)

        return date_list

    if timeframe == "week":
        update.message.reply_text(
            " 🙏 RybkaCore might be getting queued for retrieving price data from Coin Gecko servers.\n\nPlease wait for the current 📈 to be generated!"
        )
        list_of_dates = generate_dates(7)
    elif timeframe == "month":
        update.message.reply_text(
            f" ⚗️ Your {timeframe} graph will be ready in ~2-3 mins.\n\n ⏰ RybkaCore is getting queued for retrieving price data from Coin Gecko servers.\n\nPlease wait for the current 📈 to be generated!"
        )
        list_of_dates = generate_dates(30)
    elif timeframe == "year":
        update.message.reply_text(
            f" ⚗️ Your {timeframe} graph will be ready in ~20-30 mins.\n\n ⏰ RybkaCore is getting queued for retrieving price data from Coin Gecko servers.\n\nPlease wait for the current 📈 to be generated!"
        )
        list_of_dates = generate_dates(365)

    list_of_dates = list_of_dates[::-1]

    for date in list_of_dates:
        prices = api_call(currency, date)
        while prices == "ratelimited":
            prices = api_call(currency, date)
            time.sleep(10)
        usd_prices.append(float(prices[0]))
        eur_prices.append(float(prices[1]))

    matplotlib_formatted_dates = []
    for date_str in list_of_dates:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        matplotlib_formatted_dates.append(date_obj)

    generate_graph(
        graph_image_name, currency, timeframe, matplotlib_formatted_dates, usd_prices, eur_prices
    )
    local_pic(update, graph_image_name)


####################################################
##############     CORE Functions     ##############
####################################################


def handle_message(update, context):
    text = str(update.message.text).lower()
    response = R.sample_responses(text)

    update.message.reply_text(response)


def error(update, context):
    if "make sure that only one bot instance is running" in str(context.error):
        with open("TEMP/uptimeTmp", "r", encoding="utf8") as f:
            with open("TEMP/core_pidTmp", "r", encoding="utf8") as g:
                pID = int(g.read())
            if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
                current_uptime = str(f.read())
                pattern = r"(\d+)h:\s*(\d+)m"

                match = re.search(pattern, current_uptime)
                hours = int(match.group(1))
                minutes = int(match.group(2))

                if exists("TEMP/telegram_pidTmp"):
                    with open("TEMP/telegram_pidTmp", "r", encoding="utf8") as f:
                        telegram_pID = int(f.read())
                        if (
                            psutil.pid_exists(telegram_pID)
                            and "python" in psutil.Process(telegram_pID).name()
                            and hours == 0
                            and minutes < 3
                        ):
                            ORANGE(
                                "\n=========================================================================================="
                            )
                            ORANGE(
                                " 🔀 There was identified another Telegram Listener already active. Perhaps on another PC?\n ⚠️  Shutting down the session in here, while keeping the other one alive!"
                            )
                            ORANGE(
                                "==========================================================================================\n"
                            )
                            try:
                                psutil.Process(telegram_pID).kill()
                            except Exception as e:
                                ORANGE(f"TELEGRAM PROCESS COULD NOT BE KILLED. ERROR BELOW:\n\n{e}")


def main():
    check_existing_bot_process()

    initialization()

    updater = Updater(os.environ.get("RYBKA_TELEGRAM_API_KEY"), use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help_command))

    dp.add_handler(CommandHandler("status", status_command))
    dp.add_handler(CommandHandler("gpu", gpu_command))
    dp.add_handler(CommandHandler("current_buys", current_buys_command))
    dp.add_handler(CommandHandler("lifetime_buys_nr", lifetime_buys_nr_command))
    dp.add_handler(CommandHandler("profit", profit_command))
    dp.add_handler(CommandHandler("balances", m_RYBKA_BALANCES_AUX_true_command))
    dp.add_handler(CommandHandler("current_price", current_price_command))
    dp.add_handler(CommandHandler("current_uptime", current_uptime_command))

    dp.add_handler(CommandHandler("withdrawals", binance_withdrawal_history_command))
    dp.add_handler(CommandHandler("deposits", binance_deposit_history_command))

    dp.add_handler(CommandHandler("start_rybka", start_rybka_command))
    dp.add_handler(CommandHandler("yes_start_it_in_DEMO_mode", yes_start_it))
    dp.add_handler(CommandHandler("yes_start_it_in_LIVE_mode", yes_start_it))
    dp.add_handler(CommandHandler("stop_rybka", stop_rybka_command))
    dp.add_handler(CommandHandler("yes_stop_it", yes_stop_it))

    dp.add_handler(CommandHandler("roadmap", roadmap_command))
    dp.add_handler(CommandHandler("stock_bot", stock_bot_command))
    dp.add_handler(CommandHandler("contribute", contribute_command))

    dp.add_handler(CommandHandler("weights_info", weights_info_command))

    dp.add_handler(CommandHandler("RYBKA_TRADE_SYMBOL", weights_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_PERIOD", weights_command))
    dp.add_handler(CommandHandler("RYBKA_DEBUG_LVL", weights_command))
    dp.add_handler(CommandHandler("RYBKA_ALLOW_ONLY_BUYS", weights_command))
    dp.add_handler(CommandHandler("RYBKA_ALLOW_ONLY_SELLS", weights_command))
    dp.add_handler(CommandHandler("RYBKA_TRADING_BOOST_LVL", weights_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_BUY", weights_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_SELL", weights_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY", weights_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT", weights_command))
    dp.add_handler(CommandHandler("RYBKA_STABLECOIN_SAFETY_NET", weights_command))
    dp.add_handler(CommandHandler("RYBKA_EMAIL_SWITCH", weights_command))
    dp.add_handler(CommandHandler("RYBKA_EMAIL_SENDER_EMAIL", weights_command))
    dp.add_handler(CommandHandler("RYBKA_EMAIL_RECIPIENT_EMAIL", weights_command))
    dp.add_handler(CommandHandler("RYBKA_EMAIL_RECIPIENT_NAME", weights_command))
    dp.add_handler(CommandHandler("RYBKA_TELEGRAM_SWITCH", weights_command))
    dp.add_handler(CommandHandler("RYBKA_ALL_LOG_TLG_SWITCH", weights_command))
    dp.add_handler(CommandHandler("RYBKA_DISCLAIMER", weights_command))

    # Modify weights
    dp.add_handler(CommandHandler("modify_weights", weight_modification_command))

    dp.add_handler(CommandHandler("m_RYBKA_TRADING_BOOST_LVL", modify_weights_command))
    dp.add_handler(CommandHandler("RYBKA_TRADING_BOOST_LVL_1", m_RYBKA_TRADING_BOOST_LVL_1_command))
    dp.add_handler(CommandHandler("RYBKA_TRADING_BOOST_LVL_2", m_RYBKA_TRADING_BOOST_LVL_2_command))
    dp.add_handler(CommandHandler("RYBKA_TRADING_BOOST_LVL_3", m_RYBKA_TRADING_BOOST_LVL_3_command))
    dp.add_handler(CommandHandler("RYBKA_TRADING_BOOST_LVL_4", m_RYBKA_TRADING_BOOST_LVL_4_command))
    dp.add_handler(CommandHandler("RYBKA_TRADING_BOOST_LVL_5", m_RYBKA_TRADING_BOOST_LVL_5_command))

    dp.add_handler(CommandHandler("m_RYBKA_ALLOW_ONLY_BUYS", modify_weights_command))
    dp.add_handler(CommandHandler("RYBKA_ALLOW_ONLY_BUYS_0", m_RYBKA_ALLOW_ONLY_BUYS_0_command))
    dp.add_handler(CommandHandler("RYBKA_ALLOW_ONLY_BUYS_1", m_RYBKA_ALLOW_ONLY_BUYS_1_command))

    dp.add_handler(CommandHandler("m_RYBKA_ALLOW_ONLY_SELLS", modify_weights_command))
    dp.add_handler(CommandHandler("RYBKA_ALLOW_ONLY_SELLS_0", m_RYBKA_ALLOW_ONLY_SELLS_0_command))
    dp.add_handler(CommandHandler("RYBKA_ALLOW_ONLY_SELLS_1", m_RYBKA_ALLOW_ONLY_SELLS_1_command))

    dp.add_handler(CommandHandler("m_RYBKA_RSI_FOR_BUY", modify_weights_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_BUY_20", m_RYBKA_RSI_FOR_BUY_20_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_BUY_25", m_RYBKA_RSI_FOR_BUY_25_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_BUY_28", m_RYBKA_RSI_FOR_BUY_28_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_BUY_30", m_RYBKA_RSI_FOR_BUY_30_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_BUY_32", m_RYBKA_RSI_FOR_BUY_32_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_BUY_35", m_RYBKA_RSI_FOR_BUY_35_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_BUY_40", m_RYBKA_RSI_FOR_BUY_40_command))

    dp.add_handler(CommandHandler("m_RYBKA_RSI_FOR_SELL", modify_weights_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_SELL_60", m_RYBKA_RSI_FOR_SELL_60_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_SELL_65", m_RYBKA_RSI_FOR_SELL_65_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_SELL_68", m_RYBKA_RSI_FOR_SELL_68_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_SELL_70", m_RYBKA_RSI_FOR_SELL_70_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_SELL_72", m_RYBKA_RSI_FOR_SELL_72_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_SELL_75", m_RYBKA_RSI_FOR_SELL_75_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_SELL_80", m_RYBKA_RSI_FOR_SELL_80_command))

    dp.add_handler(CommandHandler("m_RYBKA_DEBUG_LVL", modify_weights_command))
    dp.add_handler(CommandHandler("RYBKA_DEBUG_LVL_unset", m_RYBKA_DEBUG_LVL_unset_command))
    dp.add_handler(CommandHandler("RYBKA_DEBUG_LVL_1", m_RYBKA_DEBUG_LVL_1_command))
    dp.add_handler(CommandHandler("RYBKA_DEBUG_LVL_2", m_RYBKA_DEBUG_LVL_2_command))
    dp.add_handler(CommandHandler("RYBKA_DEBUG_LVL_3", m_RYBKA_DEBUG_LVL_3_command))

    dp.add_handler(CommandHandler("m_RYBKA_STABLECOIN_SAFETY_NET", modify_weights_command))
    dp.add_handler(CommandHandler("RYBKA_STABLECOIN_SAFETY_NET_0", m_RYBKA_STABLECOIN_SAFETY_NET_0_command))
    dp.add_handler(CommandHandler("RYBKA_STABLECOIN_SAFETY_NET_50", m_RYBKA_STABLECOIN_SAFETY_NET_50_command))
    dp.add_handler(CommandHandler("RYBKA_STABLECOIN_SAFETY_NET_100", m_RYBKA_STABLECOIN_SAFETY_NET_100_command))
    dp.add_handler(CommandHandler("RYBKA_STABLECOIN_SAFETY_NET_200", m_RYBKA_STABLECOIN_SAFETY_NET_200_command))
    dp.add_handler(CommandHandler("RYBKA_STABLECOIN_SAFETY_NET_350", m_RYBKA_STABLECOIN_SAFETY_NET_350_command))
    dp.add_handler(CommandHandler("RYBKA_STABLECOIN_SAFETY_NET_500", m_RYBKA_STABLECOIN_SAFETY_NET_500_command))
    dp.add_handler(CommandHandler("RYBKA_STABLECOIN_SAFETY_NET_750", m_RYBKA_STABLECOIN_SAFETY_NET_750_command))
    dp.add_handler(
        CommandHandler("RYBKA_STABLECOIN_SAFETY_NET_1000", m_RYBKA_STABLECOIN_SAFETY_NET_1000_command)
    )
    dp.add_handler(
        CommandHandler("RYBKA_STABLECOIN_SAFETY_NET_1500", m_RYBKA_STABLECOIN_SAFETY_NET_1500_command)
    )
    dp.add_handler(
        CommandHandler("RYBKA_STABLECOIN_SAFETY_NET_3000", m_RYBKA_STABLECOIN_SAFETY_NET_3000_command)
    )
    dp.add_handler(
        CommandHandler("RYBKA_STABLECOIN_SAFETY_NET_5000", m_RYBKA_STABLECOIN_SAFETY_NET_5000_command)
    )
    dp.add_handler(
        CommandHandler("RYBKA_STABLECOIN_SAFETY_NET_7500", m_RYBKA_STABLECOIN_SAFETY_NET_7500_command)
    )

    dp.add_handler(CommandHandler("m_RYBKA_TRADE_QUANTITY", modify_weights_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_0_1", m_RYBKA_TRADE_QUANTITY_0_1_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_0_2", m_RYBKA_TRADE_QUANTITY_0_2_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_0_3", m_RYBKA_TRADE_QUANTITY_0_3_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_0_4", m_RYBKA_TRADE_QUANTITY_0_4_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_0_5", m_RYBKA_TRADE_QUANTITY_0_5_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_0_6", m_RYBKA_TRADE_QUANTITY_0_6_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_0_7", m_RYBKA_TRADE_QUANTITY_0_7_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_0_8", m_RYBKA_TRADE_QUANTITY_0_8_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_0_9", m_RYBKA_TRADE_QUANTITY_0_9_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_1", m_RYBKA_TRADE_QUANTITY_1_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_1_2", m_RYBKA_TRADE_QUANTITY_1_2_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_1_5", m_RYBKA_TRADE_QUANTITY_1_5_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_1_8", m_RYBKA_TRADE_QUANTITY_1_8_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_2", m_RYBKA_TRADE_QUANTITY_2_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_2_2", m_RYBKA_TRADE_QUANTITY_2_2_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_2_5", m_RYBKA_TRADE_QUANTITY_2_5_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_2_8", m_RYBKA_TRADE_QUANTITY_2_8_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_3", m_RYBKA_TRADE_QUANTITY_3_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_3_5", m_RYBKA_TRADE_QUANTITY_3_5_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_4", m_RYBKA_TRADE_QUANTITY_4_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY_5", m_RYBKA_TRADE_QUANTITY_5_command))

    dp.add_handler(CommandHandler("m_RYBKA_MIN_PROFIT", modify_weights_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_0_1", m_RYBKA_MIN_PROFIT_0_1_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_0_2", m_RYBKA_MIN_PROFIT_0_2_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_0_3", m_RYBKA_MIN_PROFIT_0_3_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_0_4", m_RYBKA_MIN_PROFIT_0_4_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_0_5", m_RYBKA_MIN_PROFIT_0_5_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_0_6", m_RYBKA_MIN_PROFIT_0_6_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_0_7", m_RYBKA_MIN_PROFIT_0_7_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_0_8", m_RYBKA_MIN_PROFIT_0_8_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_0_9", m_RYBKA_MIN_PROFIT_0_9_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_1", m_RYBKA_MIN_PROFIT_1_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_1_2", m_RYBKA_MIN_PROFIT_1_2_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_1_5", m_RYBKA_MIN_PROFIT_1_5_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_1_8", m_RYBKA_MIN_PROFIT_1_8_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_2", m_RYBKA_MIN_PROFIT_2_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_2_2", m_RYBKA_MIN_PROFIT_2_2_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_2_5", m_RYBKA_MIN_PROFIT_2_5_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_2_8", m_RYBKA_MIN_PROFIT_2_8_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_3", m_RYBKA_MIN_PROFIT_3_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_3_5", m_RYBKA_MIN_PROFIT_3_5_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_4", m_RYBKA_MIN_PROFIT_4_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT_5", m_RYBKA_MIN_PROFIT_5_command))

    dp.add_handler(CommandHandler("m_RYBKA_EMAIL_SWITCH", modify_weights_command))
    dp.add_handler(CommandHandler("RYBKA_EMAIL_SWITCH_true", m_RYBKA_EMAIL_SWITCH_true_command))
    dp.add_handler(CommandHandler("RYBKA_EMAIL_SWITCH_false", m_RYBKA_EMAIL_SWITCH_false_command))

    dp.add_handler(CommandHandler("m_RYBKA_TELEGRAM_SWITCH", modify_weights_command))
    dp.add_handler(
        CommandHandler("RYBKA_TELEGRAM_SWITCH_true", m_RYBKA_TELEGRAM_SWITCH_true_command)
    )
    dp.add_handler(
        CommandHandler("RYBKA_TELEGRAM_SWITCH_false", m_RYBKA_TELEGRAM_SWITCH_false_command)
    )

    dp.add_handler(CommandHandler("m_RYBKA_ALL_LOG_TLG_SWITCH", modify_weights_command))
    dp.add_handler(
        CommandHandler("RYBKA_ALL_LOG_TLG_SWITCH_true", m_RYBKA_ALL_LOG_TLG_SWITCH_true_command)
    )
    dp.add_handler(
        CommandHandler("RYBKA_ALL_LOG_TLG_SWITCH_false", m_RYBKA_ALL_LOG_TLG_SWITCH_false_command)
    )

    # Graphs
    dp.add_handler(CommandHandler("graphs", graphs_info_command))

    dp.add_handler(CommandHandler("EGLD", cryptocoin_command))
    dp.add_handler(CommandHandler("EGLD_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("EGLD_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("EGLD_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("BTC", btc_command))
    dp.add_handler(CommandHandler("BTC_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("BTC_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("BTC_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("ETH", eth_command))
    dp.add_handler(CommandHandler("ETH_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("ETH_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("ETH_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("BNB", bnb_command))
    dp.add_handler(CommandHandler("BNB_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("BNB_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("BNB_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("ADA", ada_command))
    dp.add_handler(CommandHandler("ADA_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("ADA_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("ADA_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("SOL", sol_command))
    dp.add_handler(CommandHandler("SOL_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("SOL_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("SOL_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("DOGE", doge_command))
    dp.add_handler(CommandHandler("DOGE_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("DOGE_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("DOGE_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("DOT", dot_command))
    dp.add_handler(CommandHandler("DOT_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("DOT_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("DOT_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("DAI", dai_command))
    dp.add_handler(CommandHandler("DAI_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("DAI_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("DAI_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("OP", op_command))
    dp.add_handler(CommandHandler("OP_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("OP_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("OP_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("ARB", arb_command))
    dp.add_handler(CommandHandler("ARB_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("ARB_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("ARB_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("LINK", link_command))
    dp.add_handler(CommandHandler("LINK_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("LINK_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("LINK_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("FIL", fil_command))
    dp.add_handler(CommandHandler("FIL_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("FIL_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("FIL_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("LTC", ltc_command))
    dp.add_handler(CommandHandler("LTC_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("LTC_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("LTC_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("UNI", uni_command))
    dp.add_handler(CommandHandler("UNI_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("UNI_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("UNI_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("ATOM", atom_command))
    dp.add_handler(CommandHandler("ATOM_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("ATOM_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("ATOM_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("BCH", bch_command))
    dp.add_handler(CommandHandler("BCH_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("BCH_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("BCH_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("ALGO", algo_command))
    dp.add_handler(CommandHandler("ALGO_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("ALGO_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("ALGO_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("XMR", xmr_command))
    dp.add_handler(CommandHandler("XMR_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("XMR_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("XMR_price_in_the_last_week", generate_graph_command))

    dp.add_handler(CommandHandler("XRP", xrp_command))
    dp.add_handler(CommandHandler("XRP_price_in_the_last_year", generate_graph_command))
    dp.add_handler(CommandHandler("XRP_price_in_the_last_month", generate_graph_command))
    dp.add_handler(CommandHandler("XRP_price_in_the_last_week", generate_graph_command))

    dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

    print(colored("\n 🔴 Telegram listener stopped!\n", "red"))


main()
