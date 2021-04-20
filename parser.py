import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

SAMLResponse = os.getenv('SAMLResponse')
class Parser:
    def open_session(self):

        headers_for_session = {
            'accept': 'application/json, text/javascript, */*',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36',
        }

        form_data = {

            'RelayState': 'http://kad.arbitr.ru:80/account/LogOnViaEsia_v3?controllerName=https%3a%2f%2fkad.arbitr.ru%3a443%2f&isRemember=False',

            'SAMLResponse': SAMLResponse,
        }
        session = requests.Session()
        url = 'https://esia.arbitr.ru/login'
        session.post(url=url, data=form_data,
                     headers=headers_for_session).raise_for_status()

        return session


    def get_content(self, session, case_number):

        headers_for_get_content = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image'
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
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36',
        }

        url = f'https://kad.arbitr.ru/Card?number={case_number}'
        response = session.get(url=url, headers=headers_for_get_content)

        response_text = response.text
        return response_text

    def get_status (self, response_text):
        soup = BeautifulSoup(response_text, 'html.parser')
        case_status = soup.find('div', {'class': 'b-case-header-desc'}).text
        return case_status

# p = Parser()
# session = p.open_session()
# content = p.get_content(session, 'A40-123/2021')
# print (content)
# status = p.get_status(content)
# print (status)