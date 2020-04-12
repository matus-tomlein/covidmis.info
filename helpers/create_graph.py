import pandas as pd
from models.fact_check_group import FactCheckGroup
from models.graph import Graph


def create_graph(domain):
    fact_check_groups = []
    max_group_size = 10

    for similarity in domain.get_fact_check_similarities(0.5):
        fact_check_1_group_i = None
        fact_check_2_group_i = None

        for i, group in enumerate(fact_check_groups):
            if similarity.fact_check_1.id in group:
                fact_check_1_group_i = i
            if similarity.fact_check_2.id in group:
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
                fact_check_groups[fact_check_1_group_i].add(similarity.fact_check_2.id)
        elif fact_check_2_group_i is not None:
            if len(fact_check_groups[fact_check_2_group_i]) < max_group_size:
                fact_check_groups[fact_check_2_group_i].add(similarity.fact_check_1.id)
        else:
            fact_check_groups.append({similarity.fact_check_1.id, similarity.fact_check_2.id})

    fact_check_groups = [
        FactCheckGroup([
            domain.fact_checks_by_id[fact_check]
            for fact_check in group
        ])
        for group in fact_check_groups
    ]

    return Graph(fact_check_groups=fact_check_groups, domain=domain)