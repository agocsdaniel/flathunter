# _FlatHunter_

A tiny program to scrape ingatlan.com to get notified of new properties in the first place.

I use [Gotify](https://github.com/gotify/server) for notifications

### How to run it

1. Clone the repo
2. Install the requirements found in requirements.txt
3. Copy .env.dist into .env and fill the fields
4. Start main.py

Or you can use Docker, too. In this case the fourth step will be `docker-compose up`

### Final notes

Please do not abuse ingatlan.com with this script!
(For example: scraping within just seconds.)