import logging
import time
from configuration import config, GOTIFY_URL, GOTIFY_TOKEN, FIRST_RUN, URLS, SLEEP_INTERVAL
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
        new_ads |= (scraper.scrape())
    new_ads_cnt = str(len(new_ads))
    logging.info(f'Found {new_ads_cnt} new ads')
    conf: dict = config['seen']
    i = 0
    for x in new_ads:
        cls, ad = x
        if not FIRST_RUN:
            notifier.notify(new_ads[x])
            i += 1
            logging.info(f'Notified {ad}, {i} of {new_ads_cnt}')
        conf[x] = new_ads[x]
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
