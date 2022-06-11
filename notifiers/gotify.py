import requests
import logging
from config import config, FIRST_RUN
from model import Ad


class Gotify:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def notify(self, ad_data: Ad, key):
        if not FIRST_RUN:
            message = f"### " \
                      f"[{ad_data.address}]({ad_data.url})\n"

            message += f"#### " \
                       f"{ad_data.price.pretty}, " \
                       f"{ad_data.size.pretty}, " \
                       f"{ad_data.rooms.pretty}\n"

            if ad_data.photoUrl != '':
                message += f"![]({ad_data.photoUrl})\n\n"

            message += f"{ad_data.description}\n\n"

            message += "##### \n"

            if ad_data.seller_name is not None:
                message += f"**👤 {ad_data.seller_name}**  \n"

            if ad_data.tel_number is not None:
                message += f"**📱 [{ad_data.tel_number_pretty}](tel:{ad_data.tel_number})**"

            template = {
                "extras": {
                    "client::display": {
                        "contentType": "text/markdown"
                    },
                    "client::notification": {
                        "click": {"url": f"{ad_data.url}"},
                        "bigImageUrl": ad_data.photoUrl
                    }
                },
                "message": message,
                "title": ad_data.title
            }
            requests.post(self.url + '/message', headers={'X-Gotify-Key': self.token}, json=template)

            _, ad = key
            logging.info(f'Notified {ad}')

        return True
