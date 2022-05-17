import logging
import math
import requests
import json
from sites import Site
from bs4 import BeautifulSoup
from config import default_headers, config, FIRST_RUN


class Ingatlan_com:
    def __init__(self, url_list=None):
        if url_list is None:
            url_list = []
        self.url_list = url_list

    @staticmethod
    def is_valid_url(url) -> bool:
        return url.startswith('https://ingatlan.com/lista/')

    def add_url(self, url):
        self.url_list.append(url)

    def scrape(self):
        ads = []
        ads_data = {}
        url_no = 0

        for url in self.url_list:
            page = 0
            max_page = -1
            url_no += 1

            while page < max_page or page == 0:
                doc = requests.get(url + '?page=' + str(page + 1), headers=default_headers).content.decode('utf-8').split('\n')
                if not doc[1].strip().startswith('dataLayer'):
                    logging.error('No JSON found, stopping scrape')
                    return ads_data
                data = json.loads(doc[1].strip().split('(')[1].split(')')[0])
                if not data['numberOfItems']:
                    break
                elif max_page == -1:
                    max_page = math.ceil(int(data['resultCount']) / data['numberOfItems'])
                ads.extend(data['itemId'])
                page += 1
                logging.info(f'Loaded page {str(page)} of {str(max_page)} at URL {str(url_no)} of {str(len(self.url_list))}')

        ads_data = {}
        count = 0
        ads = list(set(ads))
        unseen_ads = [str(ad) for ad in ads if (self.__class__, str(ad)) not in config['seen']]

        if FIRST_RUN:
            ads_data = {(self.__class__, ad): {} for ad in unseen_ads}
            return ads_data

        for ad in unseen_ads:
            doc = requests.get('https://ingatlan.com/' + str(ad), headers=default_headers).content
            doc = BeautifulSoup(doc, 'html.parser')

            if not doc.find(id='listing'):
                continue

            data = json.loads(doc.find(id='listing').attrs['data-listing'])
            titles = doc.find_all(class_='card-title')
            data['title'] = titles[0].get_text()
            data['subtitle'] = titles[1].get_text()

            misc_infos = [x.find_next('span').find_next('span').get_text().strip() for x in
                          doc.find_all(class_='listing-property')]
            data['price_pretty'] = misc_infos[0].split('\n')[0]
            data['rooms_pretty'] = misc_infos[2].split('\n')[0]

            ads_data[(self.__class__, ad)] = data
            count += 1
            logging.info(f'Loaded ad {ad}, {str(count)} of {str(len(unseen_ads))}')

        return ads_data


ingatlan_com = Ingatlan_com()
Site.add(ingatlan_com)
