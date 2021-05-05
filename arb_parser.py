import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SAMLResponse = os.getenv('SAMLResponse')


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
        organisation = event.get('Declarers').get('Organization')
        if 'ЛОКОТРАНС' in organisation or 'Локотранс' in organisation or 'локотранс' in organisation:
            return False
        return True


    #
    # def json_parse(self, event):
    #     document_date = event_info.get('DisplayDate')
    #
    #     if document_date>last_event_date
    #
    #         if document_date is not None and document_date != '':
    #             date_norm = date_convert(document_date)
    #             if date_norm > date and (case_info[i]['Declarers'] == [] or
    #                                      case_info[i]['Declarers'][0][
    #                                          'OrganizationId'] != '5b608d8f-ecee-41cd-b14d-d8b2cf8127c2'):
    #                 date_norm = datetime.datetime.strftime(date_norm,
    #                                                        "%d.%m.%Y")
    #                 document_type_name = case_info[i]["DocumentTypeName"]
    #                 content_type = case_info[i]['ContentTypes']
    #                 file_id = case_info[i]['Id']
    #                 case_id = case_info[i]['CaseId']
    #                 file_name = case_info[i]['FileName']
    #                 link = (f'https://kad.arbitr.ru/Document/Pdf/{case_id}/'
    #                         f'{file_id}/{file_name}?isAddStamp=True')
    #
    #                 print(document_type_name)
    #                 print(content_type)
    #                 print(date_norm)
    #                 print(link)
    #


