import pandas as pd
from models.fact_check_group import FactCheckGroup


def get_graph_data(articles, fact_checks, fact_checks_by_id):
    similar_fact_checks = pd.read_pickle('cache/fact_check_similarities.p')
    similar_fact_checks = similar_fact_checks.loc[similar_fact_checks > 0.5]

    fact_check_groups = []

    max_group_size = 10
    for (fact_check_1, fact_check_2), similarity in similar_fact_checks.sort_values(ascending=False).iteritems():
        fact_check_1_group_i = None
        fact_check_2_group_i = None

        for i, group in enumerate(fact_check_groups):
            if fact_check_1 in group:
                fact_check_1_group_i = i
            if fact_check_2 in group:
                fact_check_2_group_i = i

        if fact_check_1_group_i is not None and fact_check_2_group_i is not None:
            if (
                fact_check_1_group_i != fact_check_2_group_i and
                len(fact_check_groups[fact_check_1_group_i]) + len(fact_check_groups[fact_check_2_group_i]) <= max_group_size
            ):
                fact_check_groups[fact_check_1_group_i] = fact_check_groups[fact_check_1_group_i].union(fact_check_groups[fact_check_2_group_i])
                del fact_check_groups[fact_check_2_group_i]
        elif fact_check_1_group_i is not None:
            if len(fact_check_groups[fact_check_1_group_i]) < max_group_size:
                fact_check_groups[fact_check_1_group_i].add(fact_check_2)
        elif fact_check_2_group_i is not None:
            if len(fact_check_groups[fact_check_2_group_i]) < max_group_size:
                fact_check_groups[fact_check_2_group_i].add(fact_check_1)
        else:
            fact_check_groups.append({fact_check_1, fact_check_2})

    fact_check_groups = [
        FactCheckGroup([
            fact_checks_by_id[fact_check]
            for fact_check in group
        ])
        for group in fact_check_groups
    ]

    group_ids_for_fact_check_ids = {
        fact_check.id: group.id
        for group in fact_check_groups
        for fact_check in group.fact_checks
    }

    similarity_links = {
        (
            (f'gr_{group_ids_for_fact_check_ids[fact_check_1]}' if fact_check_1 in group_ids_for_fact_check_ids else f'fc_{fact_check_1}'),
            (f'gr_{group_ids_for_fact_check_ids[fact_check_2]}' if fact_check_2 in group_ids_for_fact_check_ids else f'fc_{fact_check_2}')
        )
        for (fact_check_1, fact_check_2), similarity in similar_fact_checks.iteritems()
    }

    fact_check_mappings = [
        (fact_check, mapping)
        for fact_check in fact_checks
        for mapping in fact_check.get_article_mappings()[:5]
    ]
    article_ids = {mapping.article.id for _, mapping in fact_check_mappings}
    data = {
        'nodes': [
            {'id': f'fc_{fact_check.id}', 'label': fact_check.get_statement(), 'group': fact_check.rating_color(), 'size': 5, 'type': 'fact_check', 'path': fact_check.path()}
            for fact_check in fact_checks
        ] + [
            {'id': f'ar_{article.id}', 'label': article.title, 'group': '#b4bbc7', 'size': 3, 'type': 'article', 'path': article.url}
            for article in articles
            if article.id in article_ids
        ] + [
            {'id': f'gr_{group.id}', 'label': group.promoted_fact_check.get_statement(), 'group': '#4d4bd4', 'size': 3, 'type': 'group', 'path': group.promoted_fact_check.path()}
            for group in fact_check_groups
        ],
        'links': [
            {'source': f'fc_{fact_check.id}', 'target': f'ar_{mapping.article.id}', 'value': 1, 'color': '#b4bbc7'}
            for fact_check, mapping in fact_check_mappings
        ] + [
            {'source': source, 'target': target, 'value': 2, 'color': '#4d4bd4'}
            for source, target in similarity_links
        ] + [
            {'source': f'gr_{group.id}', 'target': f'fc_{fact_check.id}', 'value': 3, 'color': '#4d4bd4'}
            for group in fact_check_groups
            for fact_check in group.fact_checks
        ]
    }
    return data
