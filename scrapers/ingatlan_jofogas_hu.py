import logging
import math
import requests
import json
import re
from sites import Site
from bs4 import BeautifulSoup
from config import default_headers, config, FIRST_RUN, DEBUG


class Ingatlan_jofogas_hu:
    api_headers = default_headers | {
        'api_key': 'jofogas-web-eFRv9myucHjnXFbj'
    }

    def __init__(self, url_list=None):
        if url_list is None:
            url_list = []
        self.url_list = url_list

    @staticmethod
    def is_valid_url(url) -> bool:
        return url.startswith('https://ingatlan.jofogas.hu/')

    def add_url(self, url):
        self.url_list.append(url)

    def scrape(self, notifier_callback=None):
        ads = {}
        url_no = 0

        for url in self.url_list:
            page = 0
            max_page = -1
            url_no += 1
            region = url.split('https://ingatlan.jofogas.hu/')[1].split('/')[0]

            while page < max_page or page == 0:
                doc = requests.get(url + '&o=' + str(page + 1), headers=default_headers).content.decode('iso-8859-2').split('\n')
                for line in doc:
                    if line.startswith('acmh_items'):
                        data = json.loads(('[' + line.strip().split('[', maxsplit=1)[1][0:-2]).encode('iso-8859-2').decode('unicode_escape'))
                    if line.startswith('acmh_num_results'):
                        result_count = int(line.split('"')[1])
                    if line.startswith('<div data-jofogas-alert-container class="alert-container"></div>'):
                        break

                if max_page == -1:
                    max_page = math.ceil(result_count / int(len(data)))
                for ad in data:
                    ad['region'] = region
                    ads[(self.__class__.__name__, ad['contentId'])] = ad
                page += 1
                logging.info(f'Loaded page {str(page)} of {str(max_page)} at URL {str(url_no)} of {str(len(self.url_list))}')

                if DEBUG:
                    break

        count = 0
        unseen_ads = [ad for (cls, ad) in ads if (self.__class__.__name__, ad) not in config['seen']]
        ads_data = {}

        if DEBUG:
            unseen_ads = unseen_ads[0:1]

        if FIRST_RUN:
            return ads

        for ad in unseen_ads:
            ad_data = ads[(self.__class__.__name__, ad)]
            doc = requests.get(f'https://ingatlan.jofogas.hu/{ads_data[(self.__class__, ad)]["region"]}/{ad}.htm', headers=default_headers).content

            doc = BeautifulSoup(doc, 'html.parser')
            ad_data["title"] = doc.find(property='og:title').attrs['content']
            ad_data["description"] = doc.find(property='og:description').attrs['content'][6:].lstrip(ads_data[(self.__class__, ad)]["title"])[2:]
            ad_data["photoUrl"] = doc.find(property='og:image').attrs['content']
            ad_data["url"] = doc.find(property='og:url').attrs['content']
            ad_data["price"] = doc.find(class_="price-value").get_text(strip=True) + ' ' + doc.find(class_="price-unit").get_text(strip=True)
            ad_data["rooms"] = doc.find(class_="rooms").get_text(strip=True).rstrip(' szoba')
            ad_data["size"] = doc.find(class_="size").get_text(strip=True).rstrip('m2')
            ad_data["address"] = (', '.join([x.strip() for x in doc.find(class_='vi_map_line').text.replace('\n', '').split('>')])).split('Cím: ')[1]
            ad_data["seller_name"] = re.search('.*\\\'name\\\': \\\'(.*?)\\\'.*', [x.get_text(strip=True) for x in doc.find_all('script') if 'advertiser' in x.get_text()][0]).group(1)

            tel_doc = requests.get('https://apiv2.jofogas.hu/v2/items/getPhone?list_id=' + ad, headers=self.api_headers).json()
            if 'phone' in tel_doc:
                ad_data["tel_number"] = tel_doc['phone']
                ad_data["tel_number_pretty"] = tel_doc['phone']
            else:
                print(tel_doc)

            count += 1
            logging.info(f'Loaded ad {ad}, {str(count)} of {str(len(unseen_ads))}')

            if notifier_callback:
                notifier_callback(ad_data, key=(self.__class__.__name__, ad))

            ads_data[(self.__class__.__name__, ad)] = ad_data
        return ads_data


ingatlan_jofogas_hu = Ingatlan_jofogas_hu()
Site.add(ingatlan_jofogas_hu)
