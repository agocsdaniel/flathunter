import logging
import math
import requests
import shelve
import os
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv


load_dotenv()

URL = os.environ.get('URL')
GOTIFY_URL = os.environ.get('GOTIFY_URL')
GOTIFY_TOKEN = os.environ.get('GOTIFY_TOKEN')


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

config = shelve.open(filename='config')
if 'seen' not in config:
    config['seen'] = {}


def scrape_new():
    page = 1
    ads = []
    while True:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0'
        }
        doc = requests.get(URL + '?page=' + str(page), headers=headers).content.decode('utf-8').split('\n')
        assert doc[1].strip().startswith('dataLayer')
        data = json.loads(doc[1].strip().split('(')[1].split(')')[0])
        ads.extend(data['itemId'])
        logging.info('Loaded page ' + str(page) + ' of ' + str(math.ceil(int(data['resultCount']) / data['numberOfItems'])))
        page += 1
        if page * data['numberOfItems'] > int(data['resultCount']):
            break

    ads_data = {}
    count = 0
    unseen_ads = [ad for ad in ads if ad not in config['seen']]
    for ad in unseen_ads:
        doc = requests.get('https://ingatlan.com/' + str(ad), headers=headers).content
        doc = BeautifulSoup(doc, 'html.parser')
        data = json.loads(doc.find(id='listing').attrs['data-listing'])
        titles = doc.find_all(class_='card-title')
        data['title'] = titles[0].get_text()
        data['subtitle'] = titles[1].get_text()
        misc_infos = [x.find_next('span').find_next('span').get_text().strip() for x in doc.find_all(class_='listing-property')]
        data['price_pretty'] = misc_infos[0].split('\n')[0]
        ads_data[ad] = data
        count += 1
        logging.info(f'Loaded ad {str(ad)}, {str(count)} of {str(len(unseen_ads))}')

    return ads_data


def notify(ad_data):
    template = {
        "extras": {
            "client::display": {
                "contentType": "text/markdown"
            },
            "client::notification": {
                "click": {"url": f"https://ingatlan.com/{ad_data['id']}"},
                "bigImageUrl": ad_data['photoUrl']
            }
        },
        "message": f"### [{ad_data['title']}](https://ingatlan.com/{ad_data['id']})\n"
                   f"#### "
                   f"{ad_data['price_pretty']}, "
                   f"{ad_data['property']['areaSize']} m2, "
                   f"{ad_data['property']['roomCount']} szoba\n"
                   f"![]({ad_data['photoUrl']})\n\n"
                   f"{ad_data['description']}",
        "title": ad_data['subtitle']
    }
    requests.post(GOTIFY_URL + '/message', headers={'X-Gotify-Key': GOTIFY_TOKEN}, json=template)


new_ads = scrape_new()
for ad in new_ads:
    notify(new_ads[ad])
    conf: dict = config['seen']
    conf[ad] = new_ads[ad]
    config['seen'] = conf

config.sync()
config.close()
