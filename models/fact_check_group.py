from slugify import slugify


class FactCheckGroup:

    def __init__(self, fact_checks):
        self.fact_checks = list(sorted(fact_checks, key=lambda fact_check: len(fact_check.get_statement())))
        self.promoted_fact_check = self.fact_checks[0]
        self.id = self.promoted_fact_check.id

    def file_name(self):
        return 'fact_check_groups/' + str(self.promoted_fact_check.id) + '-' + slugify(self.promoted_fact_check.statement, max_length=50) + '.html'

    def path(self):
        return '/' + self.file_name()

    def unpromoted_fact_checks(self):
        return [f for f in self.fact_checks if f.id != self.promoted_fact_check.id]

    def get_article_mappings(self):
        article_ids = {m.article.id for fact_check in self.fact_checks for m in fact_check.article_mappings}
        article_mappings = [
            max(
                [
                    article_mapping
                    for fact_check in self.fact_checks
                    for article_mapping in fact_check.article_mappings
                    if article_mapping.article.id == article_id
                ],
                key=lambda m: m.score
            )
            for article_id in article_ids
        ]
        return list(reversed(sorted(article_mappings, key=lambda m: m.score)))[:10]

    def num_articles(self):
        return len(self.get_article_mappings())

    def to_dict(self, graph):
        return {
            'id': self.id,
            'promoted_fact_check': self.promoted_fact_check.to_dict(),
            'fact_checks': [f.to_dict() for f in self.fact_checks],
            'path': self.path(),
            'graph_data': graph.get_component_data_for_factcheck(self.promoted_fact_check)
        }