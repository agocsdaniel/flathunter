import logging
import math
import re
import sys
import time
import requests
import shelve
import os
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

if os.environ.get('URL'):
    URLS = [os.environ.get('URL')]
elif os.path.exists('config/urls.txt'):
    with open('config/urls.txt', 'r') as f:
        URLS = [x for x in f.read().split('\n') if x.startswith('https://ingatlan.com/lista/')]
else:
    logging.error('No URLs defined')
    sys.exit(1)

GOTIFY_URL = os.environ.get('GOTIFY_URL')
GOTIFY_TOKEN = os.environ.get('GOTIFY_TOKEN')
SLEEP_INTERVAL = int(os.environ.get('SLEEP_INTERVAL') or 0)
FIRST_RUN = json.loads(os.environ.get('FIRST_RUN').lower()) if os.environ.get('FIRST_RUN') is not None else False

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

config = shelve.open(filename='config/config.db')
if 'seen' not in config:
    if os.path.exists('config/config.json'):
        with open('config/config.json', 'r') as f:
            conf: dict = config["seen"]
            conf |= json.load(f)
            config["seen"] = conf
    else:
        config['seen'] = {}

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0'
}


def scrape_new():
    ads = []
    ads_data = {}
    url_no = 0

    for url in URLS:
        page = 0
        max_page = -1
        url_no += 1

        while page < max_page or page == 0:
            doc = requests.get(url + '?page=' + str(page+1), headers=headers).content.decode('utf-8').split('\n')
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
            logging.info(f'Loaded page {str(page)} of {str(max_page)} at URL {str(url_no)} of {str(len(URLS))}')

    ads_data = {}
    count = 0
    ads = list(set(ads))
    unseen_ads = [str(ad) for ad in ads if str(ad) not in config['seen']]

    if FIRST_RUN:
        ads_data = {ad: {} for ad in unseen_ads}
        return ads_data

    for ad in unseen_ads:
        doc = requests.get('https://ingatlan.com/' + str(ad), headers=headers).content
        doc = BeautifulSoup(doc, 'html.parser')

        if not doc.find(id='listing'):
            continue

        data = json.loads(doc.find(id='listing').attrs['data-listing'])
        titles = doc.find_all(class_='card-title')
        data['title'] = titles[0].get_text()
        data['subtitle'] = titles[1].get_text()

        misc_infos = [x.find_next('span').find_next('span').get_text().strip() for x in doc.find_all(class_='listing-property')]
        data['price_pretty'] = misc_infos[0].split('\n')[0]
        data['rooms_pretty'] = misc_infos[2].split('\n')[0]

        ads_data[ad] = data
        count += 1
        logging.info(f'Loaded ad {ad}, {str(count)} of {str(len(unseen_ads))}')

    return ads_data


def notify(ad_data):
    message = f"### " \
              f"[{ad_data['title']}](https://ingatlan.com/{ad_data['id']})\n"

    message += f"#### " \
               f"{ad_data['price_pretty']}, " \
               f"{ad_data['property']['areaSize']} m2, " \
               f"{ad_data['rooms_pretty']} szoba\n"

    if 'photoUrl' in ad_data and ad_data['photoUrl'] != '':
        message += f"![]({ad_data['photoUrl']})\n\n"

    message += f"{ad_data['description']}\n\n"

    message += "##### \n"

    if 'seller' in ad_data and 'name' in ad_data['seller']:
        message += f"**👤 {ad_data['seller']['name']}"
        if 'office' in ad_data['seller']:
            message += f" ({ad_data['seller']['office']['name']})"
        message += "**  \n"

    try:
        message += f"**📱 [{ad_data['contactPhoneNumbers']['numbers'][0]}](tel:{ad_data['contactPhoneNumbers']['numbers'][0].replace(' ', '')})**"
    except:
        pass

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
        "message": message,
        "title": ad_data['subtitle']
    }
    requests.post(GOTIFY_URL + '/message', headers={'X-Gotify-Key': GOTIFY_TOKEN}, json=template)


def main():
    new_ads = scrape_new()
    new_ads_cnt = str(len(new_ads))
    logging.info(f'Found {new_ads_cnt} new ads')
    conf: dict = config['seen']
    i = 0
    for ad in new_ads:
        if not FIRST_RUN:
            notify(new_ads[ad])
            i += 1
            logging.info(f'Notified {ad}, {i} of {new_ads_cnt}')
        conf[ad] = new_ads[ad]
    config['seen'] = conf
    config.sync()


if __name__ == '__main__':
    while True:
        logging.info('Scrape started')
        main()
        logging.info('Scrape finished')
        if SLEEP_INTERVAL == 0 or FIRST_RUN:
            break

        logging.info(f'Waiting for {SLEEP_INTERVAL} seconds')
        time.sleep(SLEEP_INTERVAL)

    config.close()
