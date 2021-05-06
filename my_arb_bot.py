import logging
import os

from dotenv import load_dotenv
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
from telegram import Bot
from telegram.ext.dispatcher import run_async

from dbhelper import *
from arb_parser import Parser

import datetime

import time

from kalendar import *

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
    case_list = get_cases()

    while case_list:
        case_list = get_cases()
        for case in case_list:
            try:
                case = case[0]
                bot.bot.send_message(CHAT_ID, f'Проверяю дело {case}')
                today = date.today()
                print (f'СЕГОДНЯШНЯЯ ДАТА {today}')
                force_date_from_db = get_row('force_date', case)[0]
                finished_date_from_db = get_row('finished_date', case)[0]
                is_in_apell = get_row('is_in_apell', case)[0]

                print(f'ДАТА ВСТУПЛЕНИЯ В СИЛУ {force_date_from_db}')
                print(f'ДАТА ОКОНЧАНИЯ РАБОТЫ С ДЕЛОМ {finished_date_from_db}')

                if force_date_from_db and today >= force_date_from_db and not is_in_apell:
                    logging.info(
                        f'Решение по делу {case} вступило в силу {force_date_from_db}')
                    bot.bot.send_message(CHAT_ID,
                                         f'Решение по делу {case} вступило в силу {force_date_from_db}')

                if finished_date_from_db and today >= finished_date_from_db and not is_in_apell:
                    logging.info(
                        f'Работа с делом {case} окончена {finished_date_from_db}, дело удалено списка')
                    bot.bot.send_message(CHAT_ID,
                                         f'Работа с делом {case} окончена {finished_date_from_db}, дело удалено списка')
                    delete(case)

                first_decision_date = get_row('first_decision_date', case)[0]
                apell_decision_date = get_row('apell_decision_date', case)[0]
                message = f'Дата реш 1ой: {first_decision_date}, дата пост апелл: {apell_decision_date}, обжалуется ли: {is_in_apell}'
                bot.bot.send_message(CHAT_ID, message)

                session = parser.open_session()

                #Проверка, есть ли кейс айди в базе данных, скачать и занести в БД, если нет
                case_id = get_row('case_id', case)[0]
                logging.info(f'Case_id дела {case} равен {case_id}')
                if case_id is None:
                    content = parser.get_content(session, case)
                    case_id_from_soup = parser.get_case_id(content)
                    if case_id_from_soup is None:
                        logging.info(f'case_id_from_soup дела {case} is None, я вышел из цикла')
                        bot.bot.send_message(CHAT_ID, f'case_id_from_soup дела {case} is None, я вышел из цикла')
                        return

                    update_row('case_id', case_id_from_soup, case)
                    case_id = get_row('case_id', case)[0]
                    logging.info(f'Case_id дела {case} обновлен и равен {case_id}')

                # Получение списка событий из JSON-a
                case_info = parser.get_json(session, case_id)
                event_info = case_info.get('Result').get('Items')
                if event_info is None:
                    logging.info(
                        f'event_info дела {case} is None, я вышел из цикла')
                    bot.bot.send_message(CHAT_ID,
                                         f'event_info дела {case} is None, я вышел из цикла')
                    return
                # Получение из БД даты последнего события по делу
                last_event_date = get_row('last_event_date', case)[0]
                logging.info(
                    f'Last event date = {last_event_date}')

                #Для каждого события из списка событий
                for event in reversed(event_info):
                    #Получить дату события из JSON-a, перевести из строки в дататайм
                    document_date = event.get('DisplayDate')
                    date_convert = datetime.datetime.strptime(document_date,
                                                     '%d.%m.%Y').date()
                    #Если событие произошло позже, чем дата последнего события, которая есть в БД, то считать это событие новым
                    if date_convert > last_event_date:
                        info = f'Новое событие по делу {case}: {event}'
                        logging.info(info)
                        #Отправлять сообщение в телегу о новом событии, только если организация не моя
                        if parser.check_organization(event):
                            #Собрать человекочитаемую инфу о событии из JSON-a и отправить сообщение о новом событии в телегу
                            msg_text = parser.collect_message_text(event)
                            bot.bot.send_message(CHAT_ID, f'Новое событие:{msg_text}')
                        #Обновить дату последнего события в БД
                        update_row('last_event_date', date_convert, case)
                        last_event_date = get_row('last_event_date', case)[0]
                        logging.info(f'last_event_date дела {case} обновлена и равна {last_event_date}')

                        #Проверить, является ли новое событие решением или постановлением
                        document_type_name = event.get('DocumentTypeName')
                        content_types = event.get('ContentTypes')[0]
                        decision_type_name = event.get('DecisionTypeName')

                        # decision_type_name заполняется результатом рассмотрения только в суде 1ой инст
                        if (decision_type_name is not None or 'часть' in content_types or "Мотивированное" in content_types) and not is_in_apell:
                            force_date = force_date_runner(date_convert)
                            update_row('force_date', force_date, case)
                            update_row('first_decision_date', date_convert, case)
                            finished_date = force_date + datetime.timedelta(days=10)
                            update_row('finished_date', finished_date, case)
                            first_decision_date = get_row('first_decision_date', case)[0]
                            force_date_from_db = get_row('force_date', case)[0]
                            finished_date_from_db = get_row('finished_date', case)[0]
                            logging.info(
                               f'first_decision_date дела {case} обновлена и равна {first_decision_date}. Вст в силу {force_date_from_db}, окончание работы с делом {finished_date_from_db}')
                            bot.bot.send_message(CHAT_ID,
                               f'first_decision_date дела {case} обновлена и равна {first_decision_date}. Вст в силу {force_date_from_db}, окончание работы с делом {finished_date_from_db}')

                        if 'Постановление апелляционной инстанции' in document_type_name:
                            update_row('apell_decision_date', date_convert, case)
                            apell_decision_date = get_row('apell_decision_date', case)[0]
                            update_row('force_date', date_convert, case)
                            finished_date = force_date + datetime.timedelta(days=60)
                            update_row('finished_date', finished_date, case)
                            update_row('is_in_apell', False, case)
                            force_date_from_db = get_row('force_date', case)[0]
                            finished_date_from_db = get_row('finished_date', case)[0]
                            logging.info(
                                   f'apell_decision_date дела {case} обновлена и равна {apell_decision_date}, вст в силу {force_date_from_db}, окончание работы с делом {finished_date_from_db}')
                            bot.bot.send_message(CHAT_ID, f'apell_decision_date дела {case} обновлена и равна {apell_decision_date}, вст в силу {force_date_from_db}, окончание работы с делом {finished_date_from_db}')

                        #Проверка, подана ли жалоба в срок
                        if 'Жалоба' in document_type_name:
                            try:
                                if date_convert > force_date_from_db:
                                    logging.info(f'По делу {case} жалоба подана с нарушением срока!')
                                    bot.bot.send_message(CHAT_ID,
                                                 f'По делу {case} жалоба подана с нарушением срока!')
                                else:
                                    logging.info(
                                    f'По делу {case} жалоба подана в срок')
                                    bot.bot.send_message(CHAT_ID,
                                                     f'По делу {case} жалоба подана в срок')

                            except Exception as e:
                                logging.info(f'{e} По делу {case} подана жалоба, а дата вступления в силу не определена')
                                bot.bot.send_message(CHAT_ID,
                                                 f'{e} По делу {case} подана жалоба, а дата вступления в силу не определена')
                            update_row('force_date', None, case)
                            update_row('finished_date', None, case)
                            update_row('is_in_apell', True, case)


                        # Удалить дату вступления в силу и дату окончания работы над делом, если подано заявление о выдаче мот решения
                        if 'мотивированного' in content_types:
                            update_row('force_date', None, case)
                            update_row('finished_date', None, case)

                time.sleep(800)
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
