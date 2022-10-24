from utils import Reporter
from utils import Requester
from utils import Storage
from utils import Database
from utils import Config
from Parser import Parser


class Scraper:
    project1_url = "http://www.koeri.boun.edu.tr/scripts/lst4.asp"
    project_id = None

    def __init__(self, project_id):
        Config()
        self.project_id = 1

    def run(self):
        if self.project_id == 1:
            self.run_for_project1()

    def run_for_project1(self):
        Reporter.print_in_blue("Bot başlıyor.", f"1 nolu proje için bot başlıyor.")
        response = Requester.request(self.project1_url)
        data = Parser.parse_for_project1(response)
        i = 1
        for row in data:
            if False:  # TODO: Mükerrer Kontrolü
                Reporter.print_in_yellow(f"{i} / {len(data)} Güncellendi",
                                         f"{row.location} konumundaki deprem verisi veritabanında mevcut.")
                pass
            Reporter.print_in_green(f"{i} / {len(data)} Yeni Kayıt",f"{row.location} konumundaki deprem verisi veritabanına eklendi.")
            Database.p1_insert_data(row)
            i += 1
