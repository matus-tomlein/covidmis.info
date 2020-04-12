class Article:
    def __init__(self, id, title, url):
        self.id = id
        self.title = title
        self.url = url

    def domain(self):
        return self.url.split('/')[2].replace('www.', '')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'domain': self.domain()
        }