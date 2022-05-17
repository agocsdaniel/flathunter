import logging
import shelve
import sys
import os
import json
from dotenv import load_dotenv


load_dotenv()

if os.environ.get('URL'):
    URLS = [os.environ.get('URL')]
elif os.path.exists('config/urls.txt'):
    with open('config/urls.txt', 'r') as f:
        URLS = [x for x in f.read().split('\n') if x.startswith('http')]
else:
    logging.error('No URLs defined')
    sys.exit(1)

GOTIFY_URL = os.environ.get('GOTIFY_URL')
GOTIFY_TOKEN = os.environ.get('GOTIFY_TOKEN')
SLEEP_INTERVAL = int(os.environ.get('SLEEP_INTERVAL', default=0))
FIRST_RUN = json.loads(os.environ.get('FIRST_RUN').lower()) if os.environ.get('FIRST_RUN') is not None else False
DEBUG = json.loads(os.environ.get('DEBUG').lower()) if os.environ.get('DEBUG') is not None else False

config = shelve.open(filename='config/config.db')
if 'seen' not in config:
    if os.path.exists('config/config.json'):
        with open('config/config.json', 'r') as f:
            conf: dict = config["seen"]
            conf |= json.load(f)
            config["seen"] = conf
    else:
        config['seen'] = {}

default_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0'
}
