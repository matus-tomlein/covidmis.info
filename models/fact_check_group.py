from slugify import slugify


class FactCheckGroup:

    def __init__(self, promoted_fact_check, fact_checks):
        self.promoted_fact_check = promoted_fact_check
        self.fact_checks = fact_checks

    def file_name(self):
        return 'fact_check_groups/' + str(self.promoted_fact_check.id) + '-' + slugify(self.promoted_fact_check.statement, max_length=50) + '.html'

    def path(self):
        return '/' + self.file_name()

    def get_article_mappings(self):
        return [
            article_mapping
            for fact_check in self.fact_checks
            for article_mapping in fact_check.article_mappings
        ]

    def num_articles(self):
        return len(self.get_article_mappings())