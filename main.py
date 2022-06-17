import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

import time
import requests
from config import config, GOTIFY_URL, GOTIFY_TOKEN, FIRST_RUN, URLS, SLEEP_INTERVAL, DEBUG
from sites import Site
from notifiers.gotify import Gotify
import scrapers


for url in URLS:
    Site.add_url(url)

notifier = Gotify(GOTIFY_URL, GOTIFY_TOKEN)


def mark_seen(key, ad_data):
    conf: dict = config['seen']
    conf[key] = ad_data
    config['seen'] = conf
    config.sync()


def main():
    new_ads = {}
    for scraper in Site.sites:
        new_ads |= (scraper.scrape(notifier_callback=notifier.notify, mark_seen_callback=mark_seen))
    new_ads_cnt = str(len(new_ads))
    logging.info(f'Found {new_ads_cnt} new ads')


if __name__ == '__main__':
    while True:
        logging.info('Scrape started')
        try:
            main()
            logging.info('Scrape finished')
        except requests.ConnectionError:
            logging.exception('Network problems, scrape failed')
        except Exception:
            logging.exception('Unkonwn error, scrape failed')

        if SLEEP_INTERVAL == 0 or FIRST_RUN:
            break

        logging.info(f'Waiting for {SLEEP_INTERVAL} seconds')
        time.sleep(SLEEP_INTERVAL)

    config.close()
