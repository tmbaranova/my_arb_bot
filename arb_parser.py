import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SAMLResponse = os.getenv('SAMLResponse')


def str_or_empty_str(str):
    if str is None:
        return ""
    else:
        return str

class Parser:
    def open_session(self):
        headers_for_session = {
            'accept': 'application/json, text/javascript, */*',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'user-agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/88.0.4324.146 Safari/537.36',
        }

        form_data = {
            'RelayState':
                'http://kad.arbitr.ru:80/account/'
                'LogOnViaEsia_v3?controllerName='
                'https%3a%2f%2fkad.arbitr.ru%3a443%2f&isRemember=False',
            'SAMLResponse': SAMLResponse,
        }
        session = requests.Session()
        url = 'https://esia.arbitr.ru/login'
        session.post(url=url, data=form_data,
                     headers=headers_for_session).raise_for_status()

        return session

    def get_content(self, session, case_number):

        headers_for_get_content = {
            'Accept': 'text/html,application/xhtml+xml,'
                      'application/xml;q=0.9,image'
                      '/avif,image/webp,image/apng,*/*;q=0.8,application/'
                      'signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip,deflate,br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'text/html;charset=utf-8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'kad.arbitr.ru',
            'sec-ch-ua': '"Chromium";v ="88", "Google Chrome";v = "88",'
                         '";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Referer': f'https://kad.arbitr.ru/Card?number={case_number}',
            'User-agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/88.0.4324.146 Safari/537.36',
        }

        url = f'https://kad.arbitr.ru/Card?number={case_number}'
        response = session.get(url=url, headers=headers_for_get_content)

        response_text = response.text
        return response_text

    def get_status(self, response_text):
        soup = BeautifulSoup(response_text, 'html.parser')
        case_status = soup.find('div', {'class': 'b-case-header-desc'}).text
        return case_status

    def get_case_id(self, response_text):
        soup = BeautifulSoup(response_text, 'html.parser')
        case_id = soup.find('input', {'id': 'caseId'})['value']
        return case_id

    def post_code(self, session, case_id, code):
        headers_for_post_code = {
            "accept": "application/json, text/javascript, */*",
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36',

        }
        url = f'https://kad.arbitr.ru/SimpleJustice/CheckCode/{case_id}'
        form_data = {'code': code}
        session.post(url=url, data=form_data, headers=headers_for_post_code)
        return session

    def get_json(self, session, case_id):
        headers_for_get_json = {
            "accept": "application/json, text/javascript, */*",
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'kad.arbitr.ru',
            'Referer': f'https://kad.arbitr.ru/Card/{case_id}',
            'X-Requested-With': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36',

        }
        date = datetime.now()
        date = datetime.timestamp(date)
        date_now = int(date * 1000)
        url = (f'https://kad.arbitr.ru/Kad/CaseDocumentsPage?_={date_now}&'
               f'caseId={case_id}&page=1&perPage=25')

        response = session.get(url, headers=headers_for_get_json)
        print (response)
        case_info = response.json()
        return case_info

    def check_organization(self, event):
        try:
            organisation = event.get('Declarers')[0].get('Organization')
            print(f'organization = {organisation}')
            if ('ЛОКОТРАНС' in organisation
                    or 'Локотранс' in organisation
                    or 'локотранс' in organisation):
                return False
            return True
        except Exception:
            return True

    def collect_message_text(self, event, case_id):
        try:
            organisation = event.get('Declarers')[0].get('Organization')
            doc_link = 'https://kad.arbitr.ru/Document/Pdf/'
        except Exception:
            organisation = 'Суд'
            doc_link = 'https://kad.arbitr.ru/SimpleJustice/Attachment/'
        document_id = event.get('Id')
        filename = event.get('FileName')
        date = event.get('DisplayDate')
        additional_info = event.get('AdditionalInfo')
        content = event.get('ContentTypes')
        document_type = event.get('DocumentTypeName')
        decision = event.get('DecisionTypeName')
        full_document_link = f'{doc_link}{case_id}/{document_id}/{filename}'
        info = (f'отправитель: {organisation}, дата: {date}, '
                f'{str_or_empty_str(additional_info)}, '
                f'документ: {content}, ссылка: {full_document_link}, ' 
                f'тип: {document_type}, {str_or_empty_str(decision)}')
        return info

    def collect_case_info(self, first_decision_date,
                          apell_decision_date, is_in_apell,
                          force_date_from_db, finished_date_from_db,
                          case_id, case):
        if first_decision_date:
            first = f'Решение первой инстанции вынесено {first_decision_date.date()}.'
        else:
            first = 'Решение первой инстанции еще не вынесено.'
        if apell_decision_date:
            apell = f'Постановление апелляции вынесено {apell_decision_date.date()}.'
        else:
            apell = ''
        if is_in_apell:
            in_apell = 'Решение сейчас обжалуется.'
        else:
            in_apell = ''
        if force_date_from_db:
            force_date = f'Дата вступления решения в силу: {force_date_from_db.date()}.'
        else:
            force_date = ''
        if finished_date_from_db:
            finished_date = f'Дата окончания работы с делом: {finished_date_from_db.date()}.'
        else:
            finished_date = ''

        case_link = f'[{case}](https://kad.arbitr.ru/Card/{case_id})'
        case_info_string = f'{case_link}\n{first} {in_apell} {apell} {force_date} {finished_date}'

        return case_info_string

    def date_convert(self, date):
        """Returns date in "%d.%m.%Y" format"""
        string_of_digits = ''
        for sumbol in date:
            if sumbol.isdigit():
                string_of_digits += sumbol

        sec = int(string_of_digits) / 1000
        converted_date = datetime.fromtimestamp(sec)

        return converted_date

    def date_convert_naoborot(self):
        date = datetime.now()
        date = datetime.timestamp(date)
        date = int(date*1000)
        return date

    def get_date(self, event):
        judges = event.get('Judges')
        if not judges:
            is_doc_from_court = False
        else:
            is_doc_from_court = True

        if is_doc_from_court:
            document_date = event.get('DisplayDate')
            print(document_date)
            date_converted = datetime.combine(datetime.strptime(document_date,
                                                                '%d.%m.%Y'),
                                              datetime.min.time())
            print(f'Документ из суда, дата документа {date_converted}')

        else:
            document_date = event.get('Date')
            print(f'Документ от стороны, дата документа {document_date}')
            if document_date is not None and document_date != 'null':
                date_converted = self.date_convert(document_date)
                print(date_converted)
        return date_converted
