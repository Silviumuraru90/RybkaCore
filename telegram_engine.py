#!/usr/bin/env python3

# Built-in and Third-Party Libs
import os

# Custom Libs
from custom_modules.telegram import telegram_active_commands as R
from telegram.ext import *



print("Telegram listener activated!")

def start_command(update, context):
    update.message.reply_text('Type something random to get started')
    
def help_command(update, context):
    update.message.reply_text('If you need help - Google')
    
def handle_message(update, context):
    text = str(update.message.text).lower()
    response = R.sample_responses(text)
    
    update.message.reply_text(response)
    
def error(update, context):
    print(f"Update {update} caused error {context.error}")
    
def main():
    updater = Updater(os.environ.get("RYBKA_TELEGRAM_API_KEY"), use_context=True)
    dp = updater.dispatcher
    
    #dp.add_handler(CommandHandler("start", start_command))
    #dp.add_handler(CommandHandler("help", help_command))
    
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    
    dp.add_error_handler(error)
    
    updater.start_polling()
    
    updater.idle()
    
    print("Telegram listener stopped!")
    
    
main()
