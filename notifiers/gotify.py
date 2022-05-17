import requests


class Gotify:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def notify(self, ad_data):
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
        requests.post(self.url + '/message', headers={'X-Gotify-Key': self.token}, json=template)

        return True