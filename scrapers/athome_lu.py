import logging
import math
import requests
import json
from sites import Site
from scrapers.factory.property_site import PropertySite
from config import default_headers, config, FIRST_RUN, DEBUG
from model import Ad


class Athome_lu(PropertySite):
    @staticmethod
    def is_valid_url(url) -> bool:
        logging.debug('Checking url: ' + url)
        return url.startswith('https://www.athome.lu') and '/srp/' in url

    def _scrape(self, notifier_callback=None, mark_seen_callback=None):
        ads = []
        ads_data = {}
        url_no = 0

        for url in self.url_list:
            page = 0
            max_page = -1
            url_no += 1
            logging.debug('Loading url: ' + url)
            while page < max_page or page == 0:
                doc = requests.get(url + '&page=' + str(page + 1), headers=default_headers).content.decode('utf-8').split('\n')
                for line in doc:
                    if 'window.__INITIAL_STATE__' in line.strip():
                        break
                if 'window.__INITIAL_STATE__' not in line:
                    logging.error('No JSON found, stopping scrape')
                    return ads_data
                data = json.loads(line.split(' = ', maxsplit=1)[1].strip()[:-1])
                if max_page == -1:
                    max_page = data['search']['paginator']['totalPages']
                ads.extend(data['search']['list'])
                page += 1
                logging.info(f'Loaded page {str(page)} of {str(max_page)} at URL {str(url_no)} of {str(len(self.url_list))}')
                break
                if DEBUG:
                    break

        ads_data = {}
        count = 0
        unseen_ads = [ad for ad in ads if (self.__class__.__name__, str(ad['id'])) not in config['seen']]

        if DEBUG:
            unseen_ads = unseen_ads[0:1]

        for ad in unseen_ads:
            ad_data = Ad()

            if not FIRST_RUN:
                ad_data.internal_data = ad
                ad_data.title = ' '.join([ad['immotype'], 'for', ad['transactionType'], 'in', ad['geo']['city']])
                ad_data.address = ad_data.title
                ad_data.price = ad['price']
                ad_data.currency = '€'
                ad_data.rooms = ad['characteristic']['bedrooms_count']
                ad_data.size = ad['characteristic']['property_surface']
                ad_data.description = ad['description']
                
                try:
                    ad_data.photoUrl = ad['config']['urlPicture'] + ad['config']['layout']['path_picture'] + ad['media']['items'][0]['uri']
                except:
                    pass
                    
                try:
                    ad_data.geo.lat = ad['completeGeoInfos']['pin']['lat']
                    ad_data.geo.lon = ad['completeGeoInfos']['pin']['lon']
                    ad_data.geo.address = ' > '.join(ad['completeGeoInfos']['levels'].values())
                except:
                    pass
                    
                try:
                    ad_data.seller_name = ad['publisher']['name']
                except:
                    pass

                try:
                    ad_data.tel_number = ad['publisher']['phone1'].replace(' ', '')
                    ad_data.tel_number_pretty = ad['publisher']['phone1']
                except:
                    pass

                ad_data.url = f'https://{ad["domain"]}/{ad["locale"]}/{ad["meta"]["permalink"][ad["locale"]]}'

                ads_data[(self.__class__.__name__, ad['id'])] = ad_data
                count += 1
                logging.info(f'Loaded ad {str(ad["id"])}, {str(count)} of {str(len(unseen_ads))}')

                if notifier_callback:
                    if notifier_callback(ad_data, key=(self.__class__.__name__, ad['id'])):
                        mark_seen_callback((self.__class__.__name__, ad['id']), ad_data)

            else:
                mark_seen_callback((self.__class__.__name__, ad['id']), ad_data)

        return ads_data


athome_lu = Athome_lu()
Site.add(athome_lu)
