import pandas as pd
import urllib.request as req
from bs4 import BeautifulSoup as bs


class pagePhrase:

    def __init__(self, username):
        self.__mainURL = 'https://www.last.fm/user/'
        self.__pageToken = f'/library?page='
        self.__profile = username
        self.__records = pd.DataFrame(columns=['Artist', 'Album', 'Track', 'Time'])

    def read_page(self):
        pages = self.page_count()
        url = self.__mainURL + self.__profile

        for i in range(1, (pages + 1)):
            pageURL = url + self.__pageToken + f'{i}'
            records_in_page = self.track_lists(pageURL)
            formatted_record = self.extract_data(records_in_page)
            self.__records = self.__records.append(formatted_record)
            print(f'{i} pages done')

        return self.__records.reset_index()

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
        tds = [[td for td in tr.find_all('td')] for tr in data]
        df = pd.DataFrame(tds, index=None)
        df = df.drop([0, 2, 5, 6], axis=1)

        df['Artist'] = df[4].apply(lambda x: x.a.getText())
        df['Album'] = df[1].apply(lambda x: x.img['alt'])
        df['Track'] = df[3].apply(lambda x: x.a.getText())
        df['Time'] = df[7].apply(lambda x: x.span['title'])
        df = df.drop([1, 3, 4, 7], axis=1)

        return df