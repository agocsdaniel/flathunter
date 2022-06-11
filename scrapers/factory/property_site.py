class PropertySite:
    def __init__(self, url_list=None):
        if url_list is None:
            url_list = []
        self.url_list = url_list

    @staticmethod
    def is_valid_url(url) -> bool:
        pass

    def add_url(self, url):
        self.url_list.append(url)

    def _scrape(self, notifier_callback=None, mark_seen_callback=None):
        pass

    def scrape(self, notifier_callback=None, mark_seen_callback=None):
        return self._scrape(notifier_callback, mark_seen_callback)
