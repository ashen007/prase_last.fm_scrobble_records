import json
import re
import numpy as np
import pandas as pd
import requests as r
import urllib.request as req
from bs4 import BeautifulSoup as bs


class pagePhrase:

    def __init__(self, username):
        self.__mainURL = 'https://www.last.fm/user/'
        self.__pageToken = f'/library?page='
        self.__profile = username
        self.__records = pd.DataFrame(columns=['Artist', 'Album', 'Track', 'Time'])
        self.__baseURL = 'http://ws.audioscrobbler.com/2.0/'
        self.__headers = {'user-agent': 'user listing trend analyzer'}
        self.__payload = {
            'api_key': '6954efc3b2ff0691fb109ce6f8dca9b6',
            'format': 'json'
        }

    def main(self):
        """read each page and return the data frame which contains artist, album, track, timestamp"""
        # page_count get pages has to read
        # track_lists extract track record from html code
        # extract_data reformat output data from track_lists
        # formatting_date reformat timestamp column to five columns
        pages = self.page_count()
        url = self.__mainURL + self.__profile

        for i in range(1, pages + 1):
            pageURL = url + self.__pageToken + f'{i}'
            records_in_page = self.track_lists(pageURL)
            formatted_record = self.extract_data(records_in_page)
            self.__records = self.__records.append(formatted_record)
            print(i, end='\r')

        self.__records.reset_index(inplace=True)
        self.__records = self.formatting_date()
        self.__records.drop('index', axis=1, inplace=True)
        self.combiner()

        return self.__records

    def lastfm_get(self, obj):
        """pull request to last.fm api artist method"""
        # make requests from last.fm api to get
        self.__payload = {**self.__payload, **obj}

        return r.get(url=self.__baseURL,
                     headers=self.__headers,
                     params=self.__payload).json()

    def get_tags(self, x):
        """returns tags, play count, duration, listener count for input track"""
        # get lastfm_get returns and reformat them
        artist, track = x[0]
        payload = {'method': 'track.getInfo',
                   'artist': artist,
                   'track': track
                   }

        getter = self.lastfm_get(payload)

        if 'error' in getter and getter['error'] == 6:
            result = [artist, track, np.nan, np.nan, np.nan, np.nan]
        else:
            result = [artist,
                      track,
                      getter['track']['duration'],
                      getter['track']['listeners'],
                      getter['track']['playcount'],
                      ','.join([t['name'] for t in getter['track']['toptags']['tag']])]

        return result

    def combiner(self):
        # create dataframe from get_tags returns
        i = 0
        df_temp = []
        attribute = self.__records.groupby(['Artist', 'Track'])[['Track']].count()
        print()

        for row in attribute.iterrows():
            i += 1
            temp = self.get_tags(row)
            df_temp.append(temp)
            print(i, '\r')

        df_temp = pd.DataFrame(df_temp, columns=['Artist', 'Track','Duration', 'Listeners', 'PlayCount', 'Tags'])
        self.__records = pd.merge(self.__records, df_temp, on=['Artist','Track'], how='left')

    def formatting_date(self):
        """clearly formatting time column to day, date, time, year, month"""
        patterns = {'Day': re.compile(r"(^[a-zA-Z]+)"),
                    'Month': re.compile(r"(\b[a-zA-Z]{3}\b)"),
                    'Date': re.compile(r"\s(\b[0-9]{1,}\b)\s"),
                    'Year': re.compile(r"([0-9]{4})"),
                    'TimeStamp': re.compile(r"([0-9]{1,}:[0-9]{2}[{a|p}]m)")
                    }

        for key, value in patterns.items():
            if key in ['Date', 'Year']:
                self.__records[key] = self.__records['Time'].str.extract(value).astype('int64')
            else:
                self.__records[key] = self.__records['Time'].str.extract(value)

        self.__records = self.__records.drop('Time', axis=1)
        self.__records = self.__records.rename(columns={'TimeStamp': 'Time'})
        self.__records['Time'] = self.__records['Time'].apply(lambda x: pd.to_datetime(x).strftime('%H:%M'))

        return self.__records

    def page_count(self):
        """detect how much pages attached to profile"""
        url = self.__mainURL + self.__profile + self.__pageToken + '1'
        html = req.urlopen(url)
        page = bs(html, 'lxml')
        pageLinks = page.find_all('nav')[-1]
        links = [[a.getText() for a in li.find_all('a')] for li in pageLinks.find_all('li') if
                 li['class'][0] == 'pagination-page']
        pageCount = int(links[-1][0])

        return pageCount

    def track_lists(self, page):
        """return <tr> tags which contain data about scrobble"""
        #  re form this function with error catching while reading page
        tries = 0
        response = r.get(page)

        if response.status_code == 200:
            # print('success', page)
            html = response.content.decode(response.encoding)
        else:
            while response.status_code != 200:
                tries += 1
                response = r.get(page)
                if response.status_code == 200:
                    # print(page, tries, response.status_code)
                    html = response.content.decode(response.encoding)
                    break

        DOM = bs(html, 'html.parser')
        trackList = DOM.find_all('tr', class_='chartlist-row')

        return trackList

    def extract_data(self, data):
        """formatting and extracting scrobble data from <tr> tags"""
        tds = [[td for td in tr.find_all('td')] for tr in data]
        df = pd.DataFrame(tds, index=None)
        df = df.drop([0, 2, 5, 6], axis=1)

        df['Artist'] = df[4].apply(lambda x: x.a.getText())
        df['Album'] = df[1].apply(lambda x: x.img['alt'])
        df['Track'] = df[3].apply(lambda x: x.a.getText())
        df['Time'] = df[7].apply(lambda x: x.span['title'])
        df = df.drop([1, 3, 4, 7], axis=1)

        return df
