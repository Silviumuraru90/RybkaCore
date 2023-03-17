#!/usr/bin/env python3

# Built-in and Third-Party Libs
import GPUtil
import json
import os
import psutil
import subprocess
import time

from termcolor import colored
from os.path import exists
from binance.client import Client
from telegram import ParseMode


# Custom Libs
from custom_modules.telegram import telegram_active_commands as R
from telegram.ext import *



####################################################
##############    Custom Functions    ##############
####################################################

def initialization():
    print(colored("""
    #########################################################
    #####        📡 Telegram listener activated!        #####
    #########################################################
    """, "magenta"), colored("""
    #########################################################
    #####                                               #####
    #####  1️⃣  Open `Telegram` app on your device        #####
    #####  2️⃣  Open your Rybka Telegram bot's chat       #####
    #####  3️⃣  Type `/help` for details on how to use    #####
    #####                                               #####
    #########################################################
    \n\n""", "cyan"))


def help_command(update, context):
    update.message.reply_text(f"""Available commands are ⤵️


👨‍💻 FUN commands:
    {'who are you?':20} - Who are you talking to?

👨‍💻 FUNds info on Binance commands:
    {'/withdrawals':20} - Withdrawal history
    {'/deposits':20}    - Deposit history
    {'/balances':20}    - Acc. balances
    {'/current_price':20}  - USDT/EGLD
    {'/current_uptime':20}- Bot's uptime

👨‍💻 FUNds handling history via Rybka:
    {'/current_buys':20} - Tracked buys
    {'/lifetime_buys_nr':20}- Total nr. of buys
    {'/profit':20}        - Lifetime profit

👨‍💻 FUNctional commands:
    {'/status':20}      - Bot's status
    {'/start_restarter':20}  - Starts Restarter
    {'/start_rybka':20}   - Starts Rybka
    {'/stop_software':20}- Stops Software
    {'/gpu':20}       - GPU temp

👨‍💻 FUNdamental SUBmenu(s):
    {'/weights_info':20}  - Bot's weights


    🔄 {'/help'}  -  Shows this help message


❕ These only apply to LIVE mode!
❕ Use with caution!
        """)


def weights_info_command(update, context):
    update.message.reply_text(f"""Available weights commands are ⤵️


👨‍💻 Hard-coded weights:
    {'/RYBKA_TRADE_SYMBOL'}
    {'/RYBKA_RSI_PERIOD'}

👨‍💻 Update-on-the-fly weights:
    {'/RYBKA_DEBUG_LVL'}
    {'/RYBKA_TRADING_BOOST_LVL'}
    {'/RYBKA_RSI_FOR_BUY'}
    {'/RYBKA_RSI_FOR_SELL'}
    {'/RYBKA_TRADE_QUANTITY'}
    {'/RYBKA_MIN_PROFIT'}
    {'/RYBKA_EMAIL_SWITCH'}
    {'/RYBKA_EMAIL_SENDER_EMAIL'}
    {'/RYBKA_EMAIL_RECIPIENT_EMAIL'}
    {'/RYBKA_EMAIL_RECIPIENT_NAME'}
    {'/RYBKA_TELEGRAM_SWITCH'}
    {'/RYBKA_DISCLAIMER'}


    🔄 {'/weights_info'}  -  Shows this help message


❕ Weights specific to DEMO mode are not included!
        """)



def status_command(update, context):
    try:
        with open("TEMP/pidTmp", 'r', encoding="utf8") as f:
            pID = int(f.read())
        if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
            update.message.reply_text("🟢 Bot is alive and well, no worries! \nGive yourself a pat on the back! \nRelax and stay hydrated!")
        else:
            update.message.reply_text("💤 Bot is stopped. Help it get back on track! \nC'mon! Results, not excuses!")
    except Exception as e:
        update.message.reply_text(f"The file for Rybka's PID does NOT exist! Exception raised:\n{e}")


def gpu_command(update, context):

    # Works for Nvidia GPUs
    # Need to find solutions for Intel, AMD and Broadcom
    try:
        if (GPUtil.getGPUs()[0].temperature, float):
            status = f"GPU Temp is {GPUtil.getGPUs()[0].temperature}" + u'\xb0' + "C"
            if float(GPUtil.getGPUs()[0].temperature) == 0:
                status = "Your PC does NOT seem to have a GPU-specific senzor!"
    except Exception:
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
        update.message.reply_text("No crypto withdrawal history found!")


def binance_deposit_history_command(update, context):
    user_initial_config()
    
    binance_deposits_history = client.get_deposit_history()
    if binance_deposits_history:
        for elem in binance_deposits_history:
            update.message.reply_text(f"""🟢 Deposit [{elem['id']}]:\n
[{elem['amount']}] {elem['coin']} sent to:\n
Address [{elem['address']}]""")
    else:
        update.message.reply_text("No crypto deposit history found!")


def current_price_command(update, context):
    try:
        with open("TEMP/priceTmp", 'r', encoding="utf8") as f:
            with open("TEMP/pidTmp", 'r', encoding="utf8") as g:
                pID = int(g.read())
            if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
                current_price = float(f.read())
                update.message.reply_text(f"🩺 Current USDT / EGLD is [{current_price}]")
            else:
                update.message.reply_text("💤 Bot is stopped. Help it get back on track for an accurate price of EGLD!")
    except Exception as e:
        update.message.reply_text(f"The file for current price does NOT exist (most possible) or some other error occured! Exception raised:\n{e}")


def current_uptime_command(update, context):
    try:
        with open("TEMP/uptimeTmp", 'r', encoding="utf8") as f:
            with open("TEMP/pidTmp", 'r', encoding="utf8") as g:
                pID = int(g.read())
            if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
                current_uptime = str(f.read())
                update.message.reply_text(f"🔛 Current uptime is [{current_uptime}]")
            else:
                update.message.reply_text("💤 Bot is stopped. Help it get back on track for an accurate uptime!")
    except Exception as e:
        update.message.reply_text(f"The file for current uptime does NOT exist (most possible) or some other error occured! Exception raised:\n{e}")


def start_cmds_template(update, context, module):
    try:
        with open("TEMP/pidTmp", 'r', encoding="utf8") as f:
            pID = int(f.read())
        if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
            update.message.reply_text("🟢 Bot is already running! \nDo NOT start multiple instances, they'll corrupt each other's data!")
        else:
            update.message.reply_text("💤 Bot is indeed stopped at this moment.")
            update.message.reply_text(f"🚀 Starting bot via `{module}` module!\nPlease wait...")
            try:
                subprocess.Popen(["python", f"{module}.py", "-m", "live"])
                for i in range(0,10):
                    try:
                        time.sleep(2*i)
                        with open("TEMP/pidTmp", 'r', encoding="utf8") as f:
                            pID = int(f.read())
                            if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
                                update.message.reply_text("✅ Bot got successfully started remotely!")
                                break
                            elif i == 9:
                                update.message.reply_text("❌ Bot could NOT be started remotely!")
                    except Exception as e:
                        update.message.reply_text(f"Error occured while checking if bot got started or not via a remote command. Exception raised:\n{e}")
                        time.sleep(5)
            except Exception as e:
                update.message.reply_text(f"❌ Some error occured, bot could NOT be started remotely... Exception raised:\n{e}")
    except Exception as e:
        update.message.reply_text(f"The file for Rybka's PID does NOT exist! This needs to exist in order to check if software is already running! Exception raised:\n{e}")



def start_restarter_command(update, context):
    start_cmds_template(update, context, "restarter")


def start_rybka_command(update, context):
    start_cmds_template(update, context, "rybka")


def stop_software_command(update, context):
    try:
        with open("TEMP/pidTmp", 'r', encoding="utf8") as f:
            pID = int(f.read())
        if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
            update.message.reply_text("🟢 Bot is indeed currently running!")
            update.message.reply_text(f"🪓 Killing the process [pID:{str(pID)}]!\nPlease wait...")
            try:
                psutil.Process(pID).kill()
                time.sleep(5)
                if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
                    update.message.reply_text("❌ Bot could NOT be stopped remotely! Interesting, as the kill process cmd did complete just fine...")
                else:
                    update.message.reply_text(text=" ⚠️  Please check out <a href='https://gitlab.com/Silviu_space/rybka/-/issues/262'>[ISSUE NR 262]</a> for this command!", parse_mode=ParseMode.HTML)
                    update.message.reply_text("Too bad 🥺, go make profit somewhere else now!")
                    update.message.reply_text("🚮 Bot got successfully stopped remotely!")
            except Exception as e:
                update.message.reply_text(f"Could not kill process [pID:{str(pID)}]. Exception raised:\n{e}")
        else:
            update.message.reply_text(f"💤 Bot is already stopped at this moment. Last known [pID:{str(pID)}]")
            update.message.reply_text("🪓 No process to kill!")
    except Exception as e:
        update.message.reply_text(f"The file for Rybka's PID does NOT exist! This needs to exist in order to check if software is already running! Exception raised:\n{e}")


def weights_command(update, context):
    try:
        with open("TEMP/weightsTmp", 'r', encoding="utf8") as f:
            with open("TEMP/pidTmp", 'r', encoding="utf8") as g:
                pID = int(g.read())
            if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
                weights = json.loads(f.read())
                for weight_key, weight_value in weights.items():
                    if update['message']['text'][1:] == weight_key:
                        update.message.reply_text(f"⚖️ [{weight_key}] ➛ [{weight_value}]")
            else:
                update.message.reply_text("💤 Bot is stopped. Help it get back on track for an accurate representation of weights!")
    except Exception as e:
        update.message.reply_text(f"The file for Rybka's weights does NOT exist (most possible) or some other error occured! Exception raised:\n{e}")


def check_existing_bot_process():
    try:
        with open("TEMP/pidTmp", 'r', encoding="utf8") as f:
            pID = int(f.read())
        if psutil.pid_exists(pID) and "python" in psutil.Process(pID).name():
            print(colored(f"\n🟢 Telegram Listener started and connected to bot! Process [{str(pID)}]\n", "green"))
        else:
            print(colored("\n🔴 No bot process for the Telegram Listener to connect to! Running this would be unnecessary...\n", "red"))
            exit(0)
    except Exception as e:
        print(f"The file for Rybka's PID does NOT exist! This needs to exist in order to check if software is already running! Exception raised:\n{e}")



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
    dp.add_handler(CommandHandler("balances", balances_command))
    dp.add_handler(CommandHandler("current_price", current_price_command))
    dp.add_handler(CommandHandler("current_uptime", current_uptime_command))

    dp.add_handler(CommandHandler("withdrawals", binance_withdrawal_history_command))
    dp.add_handler(CommandHandler("deposits", binance_deposit_history_command))

    dp.add_handler(CommandHandler("start_restarter", start_restarter_command))
    dp.add_handler(CommandHandler("start_rybka", start_rybka_command))
    dp.add_handler(CommandHandler("stop_software", stop_software_command))

    dp.add_handler(CommandHandler("weights_info", weights_info_command))

    dp.add_handler(CommandHandler("RYBKA_TRADE_SYMBOL", weights_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_PERIOD", weights_command))
    dp.add_handler(CommandHandler("RYBKA_DEBUG_LVL", weights_command))
    dp.add_handler(CommandHandler("RYBKA_TRADING_BOOST_LVL", weights_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_BUY", weights_command))
    dp.add_handler(CommandHandler("RYBKA_RSI_FOR_SELL", weights_command))
    dp.add_handler(CommandHandler("RYBKA_TRADE_QUANTITY", weights_command))
    dp.add_handler(CommandHandler("RYBKA_MIN_PROFIT", weights_command))
    dp.add_handler(CommandHandler("RYBKA_EMAIL_SWITCH", weights_command))
    dp.add_handler(CommandHandler("RYBKA_EMAIL_SENDER_EMAIL", weights_command))
    dp.add_handler(CommandHandler("RYBKA_EMAIL_RECIPIENT_EMAIL", weights_command))
    dp.add_handler(CommandHandler("RYBKA_EMAIL_RECIPIENT_NAME", weights_command))
    dp.add_handler(CommandHandler("RYBKA_TELEGRAM_SWITCH", weights_command))
    dp.add_handler(CommandHandler("RYBKA_DISCLAIMER", weights_command))

    dp.add_handler(MessageHandler(Filters.text, handle_message))
    
    dp.add_error_handler(error)
    
    updater.start_polling()
    
    updater.idle()
    
    print("Telegram listener stopped!")
    
    
main()
