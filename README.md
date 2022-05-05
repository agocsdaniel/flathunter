# _FlatHunter_

A tiny program to scrape ingatlan.com to get notified of new properties in the first place.

I use [Gotify](https://github.com/gotify/server) for notifications

### How to run it

1. Clone the repo
2. Install the requirements found in requirements.txt
3. Copy .env.dist into .env and fill the fields
4. Start main.py

Or you can use Docker, too. In this case the fourth step will be `docker-compose up`

For the first run you might define `FIRST_RUN=True` in the .env. Using this the script will not load all advertisements, only the search pages, and it saves the id-s, so you will not get notified for the existing ads. After a successful scrape, you restart the script with `FIRST_RUN=False`.

### Final notes

Please do not abuse ingatlan.com with this script!
(For example: scraping within just seconds.)