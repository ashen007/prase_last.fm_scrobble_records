# import pandas as pd
import urllib.request as req
from bs4 import BeautifulSoup as bs


class pagePhrase:

    def __init__(self, username):
        self.__mainURL = 'https://www.last.fm/user/'
        self.__pageToken = f'/library?page='
        self.__profile = username

    def read_page(self):
        pages = self.page_count()
        url = self.__mainURL + self.__profile

        for i in range(1, (pages + 1)):
            pageURL = url + self.__pageToken + f'{i}'
            records_in_page = self.track_lists(pageURL)

    def page_count(self):
        url = self.__mainURL + self.__profile + self.__pageToken + '1'
        html = req.urlopen(url)
        page = bs(html, 'lxml')
        pageLinks = page.find_all('nav')[-1]
        links = [[a.getText() for a in li.find_all('a')] for li in pageLinks.find_all('li') if
                 li['class'][0] == 'pagination-page']
        pageCount = int(links[-1][0])

        return pageCount

    def track_lists(self, page):
        html = req.urlopen(page)
        DOM = bs(html, 'lxml')
        trackList = DOM.find_all('tr', class_='chartlist-row')

        return trackList

    def extract_data(self, data):

