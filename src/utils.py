import json
import logging

from fake_headers import Headers
import requests
from datetime import datetime
import datetime
from urllib.parse import urlparse
import random
import boto3
import pymysql.cursors


class Requester:
    __SECRET_IP__ = ''
    __REQUEST_LIMIT__ = False
    __REQUEST_IN_MIN__ = None
    __REQUEST_LIMITER_TURN_AT_SECOND__ = None
    __SENT_REQUEST_LAST_MIN__ = 0
    __RANDOM_HEADER__ = True
    __HEADERS__ = None
    __IP_API__ = 'https://api.ipify.org/?format=json'

    @staticmethod
    def request_limiter():
        if Requester.__REQUEST_LIMITER_TURN_AT_SECOND__ is None:
            Requester.__REQUEST_LIMITER_TURN_AT_SECOND__ = datetime.datetime.now().second
            Requester.__REQUEST_LIMITER_MINUTE__ = datetime.datetime.now().minute
        if Requester.__REQUEST_LIMITER_MINUTE__ != datetime.datetime.now().minute and datetime.datetime.now().second > Requester.__REQUEST_LIMITER_TURN_AT_SECOND__:
            Requester.__SENT_REQUEST_LAST_MIN__ = 0
        elif Requester.__SENT_REQUEST_LAST_MIN__ < Requester.__REQUEST_LIMIT__:
            Requester.__SENT_REQUEST_LAST_MIN__ += 1
            return True
        return False

    @staticmethod
    def request(url, method='GET', params=None, headers=None, check_ip=True):
        if check_ip and not Requester.__SECRET_IP__ != Requester.get_ip_address():
            Reporter.print_in_red("Program sonlandırılıyor.",
                                  "Gizlenmesini istediğiniz IP adresi ile internete çıkıyorsunuz. Güvenlik sebebiyle program sonlandırılıyor.")
            exit()
        else:
            if Requester.__REQUEST_LIMIT__:
                Requester.request_limiter()
            if Requester.__RANDOM_HEADER__:
                Requester.__HEADERS__ = Requester.generate_random_headers()
            try:
                response = requests.request(method=method, url=url, params=params, headers=headers)
                Reporter.print_in_cyan('İstek gönderildi.',
                                       f'{urlparse(url).netloc} isimli siteye istek gönderildi. Dönüş kodu : {response.status_code}')
                return response
            except Exception as ex:
                Reporter.print_in_red('Hata oluştu.', ex)

    @staticmethod
    def get_ip_address():
        response = Requester.request(Requester.__IP_API__, check_ip=False)
        return json.loads(response.text)['ip']

    @staticmethod
    def generate_random_headers(browser="chrome", os="win"):
        header = Headers(browser=browser, os=os, headers=True)
        Requester.__HEADERS__ = header.generate()
        return Requester.__HEADERS__


class Reporter:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    TELEGRAM_MESSAGES = False
    TELEGRAM_BOT_ID = "5538245636:AAGVTBsXD8nKc_UNozGiz2sa6srn6oOYrJM"
    TELEGRAM_CHAT_ID = "1346145789"

    @staticmethod
    def get_datetime():
        return datetime.datetime.now().strftime('%H:%M:%S.%f')

    @staticmethod
    def fill_the_blanks(text, length=30):
        return ' ' * (length - len(text))

    @staticmethod
    def print(header, text):
        print(f"{Reporter.get_datetime()}{' ' * 3}{Reporter.BOLD}{header}{Reporter.END}"
              f"{Reporter.fill_the_blanks(header)}{' ' * 3}{text}")

    @staticmethod
    def print_in_colored(color, header, text):
        print(f"{Reporter.get_datetime()}{' ' * 3}{color}{header}{Reporter.END}"
              f"{Reporter.fill_the_blanks(header)}{' ' * 3}{Reporter.BOLD}{text}{Reporter.END}")

    @staticmethod
    def print_in_pink(header, text):
        Reporter.print_in_colored(Reporter.PINK, header, text)

    @staticmethod
    def print_in_blue(header, text):
        Reporter.print_in_colored(Reporter.BLUE, header, text)

    @staticmethod
    def print_in_cyan(header, text):
        Reporter.print_in_colored(Reporter.CYAN, header, text)

    @staticmethod
    def print_in_green(header, text):
        Reporter.print_in_colored(Reporter.GREEN, header, text)

    @staticmethod
    def print_in_yellow(header, text):
        Reporter.print_in_colored(Reporter.YELLOW, header, text)

    @staticmethod
    def print_in_red(header, text):
        Reporter.print_in_colored(Reporter.RED, header, text)

    @staticmethod
    def send_with_telegram(text):
        params = {'chat_id': Reporter.TELEGRAM_CHAT_ID, 'text': text}
        Requester.request(f"https://api.telegram.org/bot{Reporter.TELEGRAM_BOT_ID}/sendMessage",
                          method='POST', params=params)


class Config:
    __CONFIG_PATH__ = 'config.json'
    data = None

    def __init__(self):
        self.read_config()
        self.assign_config()

    def read_config(self):
        try:
            lines = open(Config.__CONFIG_PATH__, 'r').read()
            self.data = json.loads(lines)
        except Exception as ex:
            Reporter.print_in_red("Hata oluştu.", ex)

    def assign_config(self):
        Reporter.TELEGRAM_CHAT_ID = self.data['telegram_chat_id']
        Reporter.TELEGRAM_MESSAGES = self.data['send_telegram_messages']
        Reporter.TELEGRAM_BOT_ID = self.data['telegram_bot_id']
        Requester.__SECRET_IP__ = self.data['ip_address_to_hide']
        Requester.__REQUEST_LIMIT__ = self.data['request_limiter']
        Requester.__REQUEST_IN_MIN__ = self.data['send_max_request_per_minute']
        Requester.__RANDOM_HEADER__ = self.data['use_random_header']
        Storage.AWS_S3_ACCESS_KEY_ID = self.data['aws_s3_access_key_id']
        Storage.AWS_S3_SECRET_ACCESS_KEY = self.data['aws_s3_secret_key']
        Storage.AWS_S3_BUCKET_NAME = self.data['aws_s3_bucket_name']
        Database.__HOST__ = self.data['database_host']
        Database.__USER__ = self.data['database_user']
        Database.__PASSWORD__ = self.data['database_password']
        Database.__DATABASE__ = self.data['database_name']


class Storage:
    AWS_S3_ACCESS_KEY_ID = None
    AWS_S3_SECRET_ACCESS_KEY = None
    AWS_S3_BUCKET_NAME = None

    @staticmethod
    def get_media_id():
        return str(random.randint(1, 100000))

    @staticmethod
    def connect():
        session = boto3.Session(
            aws_access_key_id=Storage.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=Storage.AWS_S3_SECRET_ACCESS_KEY,
        )
        return session.resource('s3')

    @staticmethod
    def upload_file(source, target):
        s3 = Storage.connect()
        data = open(source, 'rb')
        s3.Bucket('web-scraping-media').put_object(Key=target, Body=data)

    @staticmethod
    def get_extension(path):
        return str(path).split('.')[-1]


class Database:
    __HOST__ = None
    __USER__ = None
    __PASSWORD__ = None
    __DATABASE__ = None
    connection = None
    cursor = None

    @staticmethod
    def connect():
        try:
            Database.connection = pymysql.connect(host=Database.__HOST__,
                                                  user=Database.__USER__,
                                                  password=Database.__PASSWORD__,
                                                  database=Database.__DATABASE__,
                                                  cursorclass=pymysql.cursors.DictCursor)
            Reporter.print_in_green('Veritabanına bağlanıldı.', f"{Database.__DATABASE__} veritabanına bağlanıldı.")
        except Exception as ex:
            Reporter.print_in_red('Hata oluştu.', 'Veritabanına bağlanırken hata oluştu.')
            logging.error(ex)

    @staticmethod
    def prepare_data(data):
        return 'NULL' if data is None else f"'{str(data).strip()}'"

    @staticmethod
    def p1_insert_data(data):
        if Database.connection is None:
            Database.connect()
        with Database.connection.cursor() as cursor:
            sql = f"INSERT INTO `p1_earthquakes` (`earthquake_time`, `latitude`, `longitude`, `depth`, `size_md`, `size_ml`, " \
                  f"`size_mw`, `location`) VALUES " \
                  f"({Database.prepare_data(data.datetime)}," \
                  f"{Database.prepare_data(data.latitude)}," \
                  f"{Database.prepare_data(data.longitude)}," \
                  f"{Database.prepare_data(data.depth)}," \
                  f"{Database.prepare_data(data.size_md)}," \
                  f"{Database.prepare_data(data.size_ml)}," \
                  f"{Database.prepare_data(data.size_mw)}," \
                  f"{Database.prepare_data(data.location)});"
            cursor.execute(sql)
            Database.connection.commit()

    @staticmethod
    def p1_get_row(earthquake_time, location):
        with Database.connection.cursor() as cursor:
            query = f"SELECT * FROM `p1_earthquakes` WHERE `earthquake_time`='{earthquake_time}' AND location='{location}'"
            cursor.execute(query)
            result = cursor.fetchone()
            if result is None:
                return result



