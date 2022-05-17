import logging
import time
from config import config, GOTIFY_URL, GOTIFY_TOKEN, FIRST_RUN, URLS, SLEEP_INTERVAL
from sites import Site
from notifiers.gotify import Gotify
import scrapers

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

for url in URLS:
    Site.add_url(url)

notifier = Gotify(GOTIFY_URL, GOTIFY_TOKEN)


def main():
    new_ads = {}
    for scraper in Site.sites:
        new_ads |= (scraper.scrape(notifier_callback=notifier.notify))
    new_ads_cnt = str(len(new_ads))
    logging.info(f'Found {new_ads_cnt} new ads')


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
