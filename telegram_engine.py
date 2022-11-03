#!/usr/bin/env python3

# Built-in and Third-Party Libs
import os
import GPUtil
import json
import psutil

from os.path import exists
from binance.client import Client


# Custom Libs
from custom_modules.telegram import telegram_active_commands as R
from telegram.ext import *



####################################################
##############    Custom Functions    ##############
####################################################

print("Telegram listener activated!")

def help_command(update, context):
    update.message.reply_text(f"""Available commands are:

FUN commands:
    {'who are you?':20} - Who are you talking to?

FUNds history on Binance commands:
    {'/withdrawals':20} - Withdrawal history
    {'/deposits':20}    - Deposit history

FUNctional commands:
    {'/status':20}      - Bot's status
    {'/gpu':20}       - GPU temp
    {'/current_buys':20} - Tracked buys
    {'/lifetime_buys_nr':20}- Total nr. of buys
    {'/profit':20}        - Lifetime profit
    {'/balances':20}    - Shows balances


    {'/help'}   -   Shows this help message
        """)


def status_command(update, context):
    a = "a"
    with open(f"TEMP/pidTmp", 'r', encoding="utf8") as f:
        pID = int(f.read())
    if psutil.pid_exists(pID):
        status = "🟢 Bot is alive and well, no worries! \nGive yourself a pat on the back! \nRelax and stay hydrated!"
    else:
        status = "💤 Bot is stopped. Help it get back on track! \nC'mon! Results, not excuses!"
    update.message.reply_text(status)


def gpu_command(update, context):

    # Works for Nvidia GPUs
    # Need to find solutions for Intel, AMD and Broadcom
    if (GPUtil.getGPUs()[0].temperature, float):
        status=f"GPU Temp is {GPUtil.getGPUs()[0].temperature}" + u'\xb0' + "C"
    else:
        status="GPU Temp currently supported for Nvidia GPUs only"
    update.message.reply_text(status)


def current_buys_command(update, context):

    if exists("LIVE/ktbr"):
        with open("LIVE/ktbr", 'r', encoding="utf8") as f:
            if os.stat("LIVE/ktbr").st_size == 0:
                update.message.reply_text(" ✅ [LIVE/ktbr] file exists and is empty")
            else:
                try:
                    ktbr_config = json.loads(f.read())
                    if not ktbr_config:
                        update.message.reply_text("There are no previous buys on Binance platform that need to be tracked for selling!")
                    for k, v in ktbr_config.items():
                        update.message.reply_text(f" 💳 Transaction [{k}]  ---  [{v[0]}] EGLD at [{v[1]}] USDT/EGLD")
                except Exception as e:
                    update.message.reply_text(f"[LIVE/ktbr] file contains wrong formatted content!\nFailing with error:\n{e}")
    else:
        update.message.reply_text("The file containing previous bot buys on Binance platform, does NOT exist!")


def lifetime_buys_nr_command(update, context):

    if exists("LIVE/number_of_buy_trades"):
        with open("LIVE/number_of_buy_trades", 'r', encoding="utf8") as f:
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

    if exists("LIVE/usdt_profit"):
        with open("LIVE/usdt_profit", 'r', encoding="utf8") as f:
            if os.stat("LIVE/usdt_profit").st_size == 0:
                update.message.reply_text(" ✅ [LIVE/usdt_profit] file exists and is empty")
            else:
                profit = float(f.read())
                if not profit or profit == 0:
                    update.message.reply_text("There is no previous recorded profit!")
                else:
                    update.message.reply_text(f"💰 Lifetime profit is [{profit}] USDT")
    else:
        update.message.reply_text("The file for lifetime profit does NOT exist!")


def balances_command(update, context):

    if exists("LIVE/real_time_balances"):
        with open("LIVE/real_time_balances", 'r', encoding="utf8") as f:
            if os.stat("LIVE/real_time_balances").st_size == 0:
                update.message.reply_text(" ✅ [LIVE/real_time_balances] file exists and is empty")
            else:
                balances = f.read()
                if not balances:
                    update.message.reply_text("There are no tracked balances!")
                else:
                    for elem in balances.split('\n'):
                        if '>' in elem:
                            elem = f'🟣 {elem.split(">")[1]}'
                        if elem:
                            update.message.reply_text(f"{elem}")
    else:
        update.message.reply_text("The file for balances does NOT exist!")


def user_initial_config():
    global client
    try:
        client = Client(os.environ.get("BIN_KEY"), os.environ.get("BIN_SECRET"))
    except Exception as e:
        print(f"Client config  -  FAILED\nError encountered at setting user config. via API KEY and API SECRET. Please check error below:\n{e}")





def binance_withdrawal_history_command(update, context):
    user_initial_config()

    binance_withdrawal_history = client.get_withdraw_history()
    if binance_withdrawal_history:
        for elem in binance_withdrawal_history:
            update.message.reply_text(f"""🟢 Withdrawal [{elem['applyTime']}]:\n
[{elem['amount']}] {elem['coin']} sent to:\n
Address [{elem['address']}]\n
☞ via [{elem['network']}] network
Fee applied was [{elem['transactionFee']}] {elem['coin']}\n
    """)
    else:
        update.message.reply_text("No withdrawal history found!")


def binance_deposit_history_command(update, context):
    user_initial_config()
    
    binance_deposits_history = client.get_deposit_history()
    if binance_deposits_history:
        for elem in binance_deposits_history:
            update.message.reply_text(f"""🟢 Deposit [{elem['applyTime']}]:\n
[{elem['amount']}] {elem['coin']} sent to:\n
Address [{elem['address']}]\n
☞ via [{elem['network']}] network
Fee applied was [{elem['transactionFee']}] {elem['coin']}\n
    """)
    else:
        update.message.reply_text("No deposit history found!")



####################################################
##############     CORE Functions     ##############
####################################################

def handle_message(update, context):
    text = str(update.message.text).lower()
    response = R.sample_responses(text)
    
    update.message.reply_text(response)
    
def error(update, context):
    print(f"Update {update} caused error {context.error}")
    
def main():
    updater = Updater(os.environ.get("RYBKA_TELEGRAM_API_KEY"), use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("help", help_command))

    dp.add_handler(CommandHandler("status", status_command))
    dp.add_handler(CommandHandler("gpu", gpu_command))
    dp.add_handler(CommandHandler("current_buys", current_buys_command))
    dp.add_handler(CommandHandler("lifetime_buys_nr", lifetime_buys_nr_command))
    dp.add_handler(CommandHandler("profit", profit_command))
    dp.add_handler(CommandHandler("balances", balances_command))

    dp.add_handler(CommandHandler("withdrawals", binance_withdrawal_history_command))
    dp.add_handler(CommandHandler("deposits", binance_deposit_history_command))


    dp.add_handler(MessageHandler(Filters.text, handle_message))
    
    dp.add_error_handler(error)
    
    updater.start_polling()
    
    updater.idle()
    
    print("Telegram listener stopped!")
    
    
main()
