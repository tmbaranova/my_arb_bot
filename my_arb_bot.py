import logging
import os
import time


from dotenv import load_dotenv
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
from telegram import Bot

from dbhelper import DBHelper
from parser import Parser

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


class ArbitrBot:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_TOKEN)
        self.updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
        self.updater.dispatcher.add_handler(CommandHandler('del', self.delete_case_list))
        self.updater.dispatcher.add_handler(CommandHandler('show', self.show_case_list))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.update_case_list))
        self.updater.start_polling()

    def update_case_list(self, update, context):
        message = update.message.text.split("\n")
        for m in message:
            db.add_case(m)

    def delete_case_list(self, bot, update):
        db.delete_all_cases()

    def show_case_list(self, bot, update):
        case_list = db.get_cases()
        bot.message.reply_text(case_list)




a = ArbitrBot()
db = DBHelper()
p = Parser()
