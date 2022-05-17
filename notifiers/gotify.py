import requests
import logging
from config import config


class Gotify:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def notify(self, ad_data, key):
        message = f"### " \
                  f"[{ad_data['address']}]({ad_data['url']})\n"

        message += f"#### " \
                   f"{ad_data['price']}, " \
                   f"{ad_data['size']} m², " \
                   f"{ad_data['rooms']} szoba\n"

        if 'photoUrl' in ad_data and ad_data['photoUrl'] != '':
            message += f"![]({ad_data['photoUrl']})\n\n"

        message += f"{ad_data['description']}\n\n"

        message += "##### \n"

        if 'seller_name' in ad_data:
            message += f"**👤 {ad_data['seller_name']}**  \n"

        if 'tel_number' in ad_data:
            message += f"**📱 [{ad_data['tel_number_pretty']}](tel:{ad_data['tel_number']})**"

        template = {
            "extras": {
                "client::display": {
                    "contentType": "text/markdown"
                },
                "client::notification": {
                    "click": {"url": f"{ad_data['url']}"},
                    "bigImageUrl": ad_data['photoUrl']
                }
            },
            "message": message,
            "title": ad_data['title']
        }
        requests.post(self.url + '/message', headers={'X-Gotify-Key': self.token}, json=template)

        _, ad = key
        logging.info(f'Notified {ad}')

        conf: dict = config['seen']
        conf[key] = ad_data
        config['seen'] = conf
        config.sync()

        return True
