class Site:
    sites = []

    def __init__(self):
        self.sites.append(self)

    @staticmethod
    def add(site):
        Site.sites.append(site)

    @staticmethod
    def add_url(url):
        for site in Site.sites:
            if site.is_valid_url(url):
                site.add_url(url)
        return None
