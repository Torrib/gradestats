from bs4 import BeautifulSoup
import requests


class Client:
    session = None

    def __init__(self):
        super().__init__()
        self.session = requests.session()

    def init_soup(self, page_text: str):
        return BeautifulSoup(page_text, "html5lib")
