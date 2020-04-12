import networkx as nx


class Graph:

    def __init__(self, fact_check_groups, domain):
        self.fact_check_groups = fact_check_groups
        self.domain = domain

        self.group_ids_for_fact_check_ids = {
            fact_check.id: group.id
            for group in self.fact_check_groups
            for fact_check in group.fact_checks
        }

        self.similarity_links = {
            (
                (f'gr_{self.group_ids_for_fact_check_ids[s.fact_check_1.id]}' if s.fact_check_1.id in self.group_ids_for_fact_check_ids else f'fc_{s.fact_check_1.id}'),
                (f'gr_{self.group_ids_for_fact_check_ids[s.fact_check_2.id]}' if s.fact_check_2.id in self.group_ids_for_fact_check_ids else f'fc_{s.fact_check_2.id}')
            )
            for s in self.domain.get_fact_check_similarities(0.5)
        }

        self.fact_check_mappings = [
            (fact_check, mapping)
            for fact_check in domain.fact_checks
            for mapping in fact_check.get_article_mappings()[:5]
        ]
        article_ids = {mapping.article.id for _, mapping in self.fact_check_mappings}

        self.nodes = [
            {'id': f'fc_{fact_check.id}', 'label': fact_check.get_statement(), 'group': fact_check.rating_color(), 'size': 5, 'type': 'fact_check', 'path': fact_check.path()}
            for fact_check in self.domain.fact_checks
        ] + [
            {'id': f'ar_{article.id}', 'label': article.title, 'group': '#b4bbc7', 'size': 3, 'type': 'article', 'path': article.url}
            for article in self.domain.articles
            if article.id in article_ids
        ] + [
            {'id': f'gr_{group.id}', 'label': group.promoted_fact_check.get_statement(), 'group': '#4d4bd4', 'size': 3, 'type': 'group', 'path': group.promoted_fact_check.path()}
            for group in self.fact_check_groups
        ]

        self.links = [
            {'source': f'fc_{fact_check.id}', 'target': f'ar_{mapping.article.id}', 'value': 1, 'color': '#b4bbc7'}
            for fact_check, mapping in self.fact_check_mappings
        ] + [
            {'source': source, 'target': target, 'value': 2, 'color': '#4d4bd4'}
            for source, target in self.similarity_links
        ] + [
            {'source': f'gr_{group.id}', 'target': f'fc_{fact_check.id}', 'value': 3, 'color': '#4d4bd4'}
            for group in self.fact_check_groups
            for fact_check in group.fact_checks
        ]

        self.G = nx.Graph()
        for link in self.links:
            self.G.add_edge(link['source'], link['target'], weight=link['value'])

    def get_largest_component_data(self):
        components = list(reversed(sorted(nx.connected_components(self.G), key=lambda c: len(c))))
        c = components[0]

        return {
            'nodes': [n for n in self.nodes if n['id'] in c],
            'links': [l for l in self.links if l['source'] in c or l['target'] in c]
        }

    def get_component_data_for_factcheck(self, fact_check):
        components = list(nx.connected_components(self.G))
        node_id = f'fc_{fact_check.id}'
        components = [c for c in components if node_id in c]
        c = components[0] if len(components) > 0 else []

        return {
            'nodes': [n for n in self.nodes if n['id'] in c],
            'links': [l for l in self.links if l['source'] in c or l['target'] in c]
        }

    def get_complete_data(self):
        return {
            'nodes': self.nodes,
            'links': self.links
        }