from models.fact_check_source import FactCheckSource
from models.fact_checks_similarity import FactChecksSimilarity
from models.period import Period


class Domain:

    def __init__(self, fact_checks, articles, article_counts, fact_check_groups, fact_check_counts, fact_checks_by_id, similar_fact_checks, fact_check_similarities):
        self.fact_checks = fact_checks
        self.articles = articles
        self.article_counts = article_counts
        self.fact_check_groups = fact_check_groups
        self.fact_check_counts = fact_check_counts
        self.fact_checks_by_id = fact_checks_by_id
        self.similar_fact_checks = similar_fact_checks
        self.fact_check_similarities = fact_check_similarities

        sources = {f.domain() for f in self.fact_checks}
        self.fact_check_sources = list(reversed(sorted([
            FactCheckSource(source, [f for f in self.fact_checks if f.domain() == source])
            for source in sources
        ], key=lambda s: s.num_fact_checks)))

    def get_similar_fact_checks(self, fact_check, min_similarity=0.3):
        fact_check_similarities = self.fact_check_similarities.loc[self.fact_check_similarities >= min_similarity]
        fact_check_similarities = fact_check_similarities.loc[
            (fact_check_similarities.index.get_level_values(0) == fact_check.id) |
            (fact_check_similarities.index.get_level_values(1) == fact_check.id)
        ]
        similar_fact_check_ids = set(fact_check_similarities.index.get_level_values(0)).union(set(fact_check_similarities.index.get_level_values(1)))
        similar_fact_check_ids = similar_fact_check_ids - {fact_check.id}

        return [self.fact_checks_by_id[fid] for fid in similar_fact_check_ids]

    def get_fact_check_similarities(self, min_similarity=0.3):
        similarities = self.fact_check_similarities.loc[self.fact_check_similarities >= min_similarity]
        return [
            FactChecksSimilarity(
                fact_check_1=self.fact_checks_by_id[fact_check_1],
                fact_check_2=self.fact_checks_by_id[fact_check_2],
                similarity=similarity
            )
            for (fact_check_1, fact_check_2), similarity in similarities.sort_values(ascending=False).iteritems()
        ]

    def get_periods(self):
        period_freq = 'W'
        periods = {
            fact_check.published_at.to_period(period_freq)
            for fact_check in self.fact_checks
        }

        return [
            Period(
                period=period,
                fact_checks=[
                    fact_check for fact_check in self.fact_checks
                    if fact_check.published_at.to_period(period_freq) == period
                ],
                domain=self
            )
            for period in reversed(sorted(periods))
        ]
