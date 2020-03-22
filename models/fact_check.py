from slugify import slugify


class FactCheck:

    def __init__(self, id, claim_id, statement, description, url, rating, article_mappings):
        self.id = id
        self.claim_id = claim_id
        self.statement = capitalize(statement)
        self.description = description
        self.url = url
        self.rating = capitalize(rating)
        self.article_mappings = article_mappings

    def get_article_mappings(self):
        return reversed(sorted(self.article_mappings, key=lambda m: m.score))

    def domain(self):
        return self.url.split('/')[2].replace('www.', '')

    def num_articles(self):
        return len(self.article_mappings)

    def rating_style(self):
        if self.rating in {'False', 'Inaccurate', 'Unproven', 'Unsupported', 'Misleading'}:
            return 'text-error'
        elif self.rating in {'True', 'Affirmative', 'Correct', 'Accurate'}:
            return 'text-success'
        else:
            return 'text-warning'

    def short_description(self):
        if len(self.description) > 500:
            return self.description[:500] + '&hellip;'
        return self.description

    def file_name(self):
        return 'fact_checks/' + str(self.id) + '-' + slugify(self.statement, max_length=50) + '.html'

    def path(self):
        return '/' + self.file_name()

def capitalize(string):
    return string[0].capitalize() + string[1:]