from slugify import slugify
import pandas as pd


class FactCheck:

    def __init__(self, id, claim_id, statement, description, published_at, url, rating, article_mappings, other_info):
        self.id = id
        self.claim_id = claim_id
        self.statement = capitalize(statement)
        self.description = description
        self.published_at = published_at
        self.url = url
        self.rating = capitalize(rating)
        self.article_mappings = article_mappings
        self.other_info = other_info

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

    def has_answers(self):
        return 'answers' in self.other_info and len(self.other_info['answers']) > 0

    def get_answers(self):
        if 'answers' in self.other_info:
            return [Answer(answer) for answer in self.other_info['answers']]
        return []

class Answer:

    def __init__(self, info):
        self.info = info
        self.description = info['description']
        self.created_at = pd.to_datetime(info['created_at'])
        self.author = f"{info['user']['first_name']} {info['user']['last_name']}, {info['user']['organisation']['full_name']}"

def capitalize(string):
    return string[0].capitalize() + string[1:]