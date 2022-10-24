import datetime

from bs4 import BeautifulSoup

from Data import Data
from utils import Database


class Parser:
    @staticmethod
    def get_soup_for_parsing(response):
        return BeautifulSoup(response, 'lxml')

    @staticmethod
    def parse_for_project1(response):
        soup = Parser.get_soup_for_parsing(response.text)
        pre = soup.find('pre')
        return Parser.p1_parse_data(pre.text)


    @staticmethod
    def p1_parse_data(text):
        data = Parser.p1_delete_unnecessary_data(text.split('\r\n'))
        return Parser.p1_parse_table_data(data)

    @staticmethod
    def p1_delete_unnecessary_data(data):
        for i in range(7):
            del data[0]
        return data

    @staticmethod
    def p1_parse_table_data(scraped_data):
        result = []
        for row in scraped_data:
            tmp = str(row).split('  ')
            tmp = [str(x).strip() for x in tmp if x != '']
            if len(tmp) != 9:
                continue

            data = Data(1)
            data.datetime = Parser.p1_format_datetime(tmp[0])
            data.latitude = tmp[1]
            data.longitude = tmp[2]
            data.depth = tmp[3]
            data.size_md = Parser.p1_format_size(tmp[4])
            data.size_ml = Parser.p1_format_size(tmp[5])
            data.size_mw = Parser.p1_format_size(tmp[6])
            data.location = tmp[7]

            result.append(data)

        return result

    @staticmethod
    def p1_format_datetime(text):
        return str(text).replace('.', '-')

    @staticmethod
    def p1_format_size(text):
        return None if text == '-.-' else text
