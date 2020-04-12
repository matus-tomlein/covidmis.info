import networkx as nx
from models.fact_check_group import FactCheckGroup


class Period:

    def __init__(self, period, fact_checks, domain):
        self.period = period
        self.fact_checks = fact_checks
        self.domain = domain
        self.groups = self._create_groups()

    def id(self):
        return self.period.start_time.date().isoformat()

    def format(self):
        return self.period.start_time.strftime('%-d %b %Y') + ' – ' + self.period.end_time.strftime('%-d %b %Y')

    def _create_groups(self):
        G=nx.Graph()

        fact_check_ids = {f.id for f in self.fact_checks}
        for fact_check in self.fact_checks:
            for similar in self.domain.get_similar_fact_checks(fact_check, min_similarity=0.5):
                if similar.id in fact_check_ids:
                    G.add_edge(fact_check.id, similar.id, weight=1)

        groups = [
            FactCheckGroup(fact_checks=[self.domain.fact_checks_by_id[f] for f in group])
            for group in nx.connected_components(G)
        ]
        group_fact_check_ids = {
            fact_check.id
            for group in groups
            for fact_check in group.fact_checks
        }
        groups = [
            FactCheckGroup([self.domain.fact_checks_by_id[fact_check_id]])
            for fact_check_id in fact_check_ids
            if fact_check_id not in group_fact_check_ids
        ] + groups
        return reversed(sorted(groups, key=lambda g: g.promoted_fact_check.published_at))