import logging
import os
import time

from dotenv import load_dotenv
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
from telegram import Bot
from telegram.ext.dispatcher import run_async

from dbhelper import DBHelper
from arb_parser import Parser

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


class ArbitrBot:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_TOKEN)
        self.updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
        self.updater.dispatcher.add_handler(
            CommandHandler('del', self.delete_case_list))
        self.updater.dispatcher.add_handler(
            CommandHandler('show', self.show_case_list))
        self.updater.dispatcher.add_handler(
            CommandHandler('start', self.start))
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.text, self.update_case_list))
        self.updater.start_polling()
        self.db = DBHelper()
        self.stop = False

    @run_async
    def update_case_list(self, update, context):
        message = update.message.text.split("\n")
        for m in message:
            m = m.replace("А", "A")
            self.db.add_case(m)

    @run_async
    def delete_case_list(self, bot, update):
        self.db.delete_all_cases()

    @run_async
    def show_case_list(self, bot, update):
        case_list = self.db.get_cases()
        bot.message.reply_text(case_list)

    @run_async
    def start(self, bot, update):
        self.stop = False
        main()
        return self


def main():
    logging.info(f'Бот запущен')
    bot.bot.send_message(CHAT_ID, 'Бот запущен')
    parser = Parser()
    logger = logging.getLogger(__name__)
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)
    status = 1
    case_list = bot.db.get_cases()

    while case_list:
        case_list = bot.db.get_cases()
        for case in case_list:
            if status is None:
                logging.info(f'Прервал цикл')
                bot.bot.send_message(CHAT_ID, 'Прервал цикл')
                return
            try:
                session = parser.open_session()
                content = parser.get_content(session, case)
                status = parser.get_status(content)
                logging.info(f'Статус дела {case} = {status}')
                if 'завершено' in status:
                    message = f'Рассмотрение дела {case} завершено'
                    bot.bot.send_message(CHAT_ID, message)
                    logging.info(f'Сообщение отправлено: {message}')
                    bot.db.delete(case)
                time.sleep(1200)
            except Exception as e:
                error_text = f'Бот столкнулся с ошибкой: {e}'
                logging.exception(e)
                bot.bot.send_message(CHAT_ID, error_text)
                time.sleep(5)

    logging.info(f'Вышел из цикла')
    bot.bot.send_message(CHAT_ID, 'Вышел из цикла')


bot = ArbitrBot()
