import logging
import math
import requests
import json
from sites import Site
from bs4 import BeautifulSoup
from config import default_headers, config, FIRST_RUN, DEBUG


__name__ = 'Ingatlan.com'

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

    def scrape(self, notifier_callback=None):
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

                if DEBUG:
                    break

        ads_data = {}
        count = 0
        ads = list(set(ads))
        unseen_ads = [str(ad) for ad in ads if (self.__class__.__name__, str(ad)) not in config['seen']]

        if DEBUG:
            unseen_ads = unseen_ads[0:1]

        if FIRST_RUN:
            ads_data = {(self.__class__.__name__, ad): {} for ad in unseen_ads}
            return ads_data

        for ad in unseen_ads:
            doc = requests.get('https://ingatlan.com/' + str(ad), headers=default_headers).content
            doc = BeautifulSoup(doc, 'html.parser')

            if not doc.find(id='listing'):
                continue

            ad_data = {}
            ad_data['internal_data'] = json.loads(doc.find(id='listing').attrs['data-listing'])
            titles = doc.find_all(class_='card-title')
            ad_data['address'] = titles[0].get_text()
            ad_data['title'] = titles[1].get_text()

            misc_infos = [x.find_next('span').find_next('span').get_text().strip() for x in
                          doc.find_all(class_='listing-property')]
            ad_data['price'] = misc_infos[0].split('\n')[0]
            ad_data['rooms'] = misc_infos[2].split('\n')[0]

            ad_data['size'] = ad_data['internal_data']['property']['areaSize']
            ad_data['description'] = ad_data['internal_data']['description']
            ad_data['photoUrl'] = ad_data['internal_data']['photoUrl']

            if 'seller' in ad_data and 'name' in ad_data['seller']:
                ad_data['seller_name'] = ad_data['internal_data']['seller']['name']
                if 'office' in ad_data['internal_data']['seller']:
                    ad_data['seller_name'] += f" ({ad_data['internal_data']['seller']['office']['name']})"

            try:
                ad_data['tel_number'] = ad_data['internal_data']['contactPhoneNumbers']['numbers'][0].replace(' ', '')
                ad_data['tel_number_pretty'] = ad_data['internal_data']['contactPhoneNumbers']['numbers'][0]
            except:
                pass

            ad_data['url'] = f'https://ingatlan.com/{ad_data["internal_data"]["id"]}'

            ads_data[(self.__class__.__name__, ad)] = ad_data
            count += 1
            logging.info(f'Loaded ad {ad}, {str(count)} of {str(len(unseen_ads))}')

            if notifier_callback:
                notifier_callback(ad_data, key=(self.__class__.__name__, ad))

        return ads_data


ingatlan_com = Ingatlan_com()
Site.add(ingatlan_com)
