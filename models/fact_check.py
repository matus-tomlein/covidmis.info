from slugify import slugify
from html.parser import HTMLParser
import pandas as pd
from helpers.translate import translate
import re


class FactCheck:

    def __init__(self, id, claim_id, statement, description, published_at, url, rating, article_mappings, other_info):
        self.id = id
        self.claim_id = claim_id
        self.statement = statement
        self.description = description
        self.published_at = published_at
        self.url = url
        self.rating = rating
        self.article_mappings = article_mappings
        self.other_info = other_info
        self.language = None

    def translate(self, language='sk'):
        self.language = language

    def get_statement(self):
        if self.language == 'sk':
            return capitalize(translate(self.statement, self.language))
        else:
            return capitalize(self.statement)

    def get_original_description(self):
        description = self.description
        if len(description) > 2000:
            return description[:2000] + '...'
        return description

    def get_description(self):
        if self.language == 'sk':
            description = translate(self.get_original_description(), self.language)
        else:
            description = self.get_original_description()

        description = re.sub('<[^<]+?>', '', description)
        parser = HTMLParser()
        description = parser.unescape(description)
        return description

    def get_rating(self):
        if self.language == 'sk':
            return capitalize(translate(self.rating, self.language))
        else:
            return capitalize(self.rating)

    def get_article_mappings(self):
        return list(reversed(sorted(self.article_mappings, key=lambda m: m.score)))[:10]

    def domain(self):
        return self.url.split('/')[2].replace('www.', '')

    def num_articles(self):
        return len(self.article_mappings)

    def rating_style(self):
        if self.rating.lower() in {'false', 'inaccurate', 'unproven', 'unsupported', 'misleading'}:
            return 'text-error'
        elif self.rating.lower() in {'true', 'affirmative', 'correct', 'accurate'}:
            return 'text-success'
        else:
            return 'text-warning'

    def rating_color(self):
        style = self.rating_style()
        if style == 'text-error':
            return '#e54c00'
        elif style == 'text-success':
            return '#2cad3b'
        else:
            return '#ffae00'

    def short_description(self):
        description = self.get_description()
        if len(description) > 500:
            return description[:500] + '&hellip;'
        return description

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

    def to_dict(self):
        return {
            'id': self.id,
            'statement': self.get_statement(),
            'description': self.get_description(),
            'published_at': self.published_at.isoformat(),
            'url': self.url,
            'domain': self.domain(),
            'rating': self.get_rating(),
            'rating_style': self.rating_style(),
            'article_mappings': [a.to_dict(self.language) for a in self.article_mappings],
            'path': self.path()
        }

class Answer:

    def __init__(self, info):
        self.info = info
        self.description = info['description']
        self.created_at = pd.to_datetime(info['created_at'])
        self.author = f"{info['user']['first_name']} {info['user']['last_name']}, {info['user']['organisation']['full_name']}"

def capitalize(string):
    if string == '':
        return string
    return string[0].capitalize() + string[1:]