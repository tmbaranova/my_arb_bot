import logging
import os
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
from telegram import Bot

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


class ArbitrBot:
    def __init__(self):
        self.case_list = [1]
        self.bot = Bot(token=TELEGRAM_TOKEN)
        self.updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
        self.updater.dispatcher.add_handler(CommandHandler('del', self.delete_case_list))
        self.updater.dispatcher.add_handler(CommandHandler('show', self.show_case_list))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.update_case_list))

        self.updater.start_polling()

    def update_case_list(self, update, context):
        message = update.message.text.split("\n")
        for m in message:
            self.case_list.append(m)
        string_cases = '\n '.join(map(str, self.case_list))
        context.bot.send_message(chat_id = update.message.chat.id, text= string_cases)
        return self.case_list

    def delete_case_list(self, bot, update):
        self.case_list = []
        bot.message.reply_text(self.case_list)
        return self.case_list

    def show_case_list(self, bot, update):
        bot.message.reply_text(self.case_list)
        return self.case_list


a = ArbitrBot()