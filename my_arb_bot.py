import logging
import os
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
from telegram import Bot

case_list = [1]
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

print (TELEGRAM_TOKEN)
print (CHAT_ID)

def update_case_list(bot, update):
    print (type(update))
    message = update.message
    print (message)
    case_list.append(message)
    print (case_list)
    return case_list

def delete_case_list(bot, update):
    case_list = []
    print (case_list)
    return case_list

def show_case_list(bot, update):
    bot.message.reply_text(case_list)



bot = Bot(token=TELEGRAM_TOKEN)
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler('del', delete_case_list))
updater.dispatcher.add_handler(CommandHandler('show', show_case_list))
updater.dispatcher.add_handler(MessageHandler(Filters.text, update_case_list))

print (case_list)

updater.start_polling()