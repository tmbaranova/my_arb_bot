import logging
import os
import time

from dotenv import load_dotenv
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
from telegram import Bot
from telegram.ext.dispatcher import run_async

from dbhelper import *
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
        create_table()


    @run_async
    def update_case_list(self, update, context):
        if int(update.message.chat_id) != int(CHAT_ID):
            update.message.reply_text(
                'Извините, для Вас этот бот недоступен')
            return
        message = update.message.text.split("\n")
        for m in message:
            m = m.replace("А", "A")
            add_case(m)

    @run_async
    def delete_case_list(self, update, context):
        if int(update.message.chat_id) != int(CHAT_ID):
            update.message.reply_text(
                'Извините, для Вас этот бот недоступен')
            return
        delete_all_cases()

    @run_async
    def show_case_list(self, update, context):
        if int(update.message.chat_id) != int(CHAT_ID):
            update.message.reply_text('Извините, для Вас этот бот недоступен')
            return
        case_list = get_cases()
        update.message.reply_text(case_list)

    @run_async
    def start(self, update, context):
        if int(update.message.chat_id) != int(CHAT_ID):
            update.message.reply_text(
                'Извините, для Вас этот бот недоступен')
            return
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
    case_list = get_cases()

    while case_list:
        case_list = get_cases()
        for case in case_list:
            try:
                session = parser.open_session()
                content = parser.get_content(session, case)
                case_id = get_case_id(case)[0][0]
                logging.info(f'Case_id дела {case} равен {case_id}')
                if case_id is None:
                    case_id_from_soup = parser.get_case_id(content)
                    update_case_id(case_id_from_soup, case[0])
                    case_id_new = get_case_id(case)
                    logging.info(f'Case_id дела {case} обновлен и равен {case_id_new}')
                    message = f'Case_id дела {case} обновлен и равен {case_id_new}'
                    bot.bot.send_message(CHAT_ID, message)

                status = parser.get_status(content)
                info = f'Статус дела {case} = {status}'
                bot.bot.send_message(CHAT_ID, info)
                logging.info(f'Статус дела {case} = {status}')

                if 'завершено' in status:
                    message = f'Рассмотрение дела {case} завершено'
                    bot.bot.send_message(CHAT_ID, message)
                    logging.info(f'Сообщение отправлено: {message}')
                    delete(case)
                time.sleep(1200)
            except Exception as e:
                error_text = f'Бот столкнулся с ошибкой: {e}'
                logging.exception(e)
                bot.bot.send_message(CHAT_ID, error_text)
                logging.info(f'Я прервал цикл')
                bot.bot.send_message(CHAT_ID, 'Я прервал цикл')
                return


    logging.info(f'Список дел пуст или кончился, я вышел из цикла')
    bot.bot.send_message(CHAT_ID, 'Список дел пуст или кончился, я вышел из цикла')


if __name__ == "__main__":
    bot = ArbitrBot()
    main()
