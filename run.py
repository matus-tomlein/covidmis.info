import json
import pandas as pd
from models.article import Article
from models.article_mapping import ArticleMapping
from models.fact_check import FactCheck
from models.fact_check_group import FactCheckGroup
from helpers.create_graph import create_graph
from helpers.create_domain import create_domain
from helpers.html_output import render_to_file

domain = create_domain()

for page_title, language in [
    ('CovidMis.info', 'en'),
    ('CovidDez.info', 'sk')
]:
    for fact_check in domain.fact_checks:
        fact_check.translate(language)

    graph = create_graph(domain)

    render_to_file(
        template='index.html',
        output_path='index.html',
        data={
            'title': page_title,
            'domain': domain,
            'fact_checks': domain.fact_checks,
            'fact_checks_json': json.dumps([f.to_dict() for f in domain.fact_checks]),
            'data': json.dumps(graph.get_largest_component_data()),
            'fact_check_groups': domain.fact_check_groups,
            'fact_check_groups_json': json.dumps([g.to_dict(graph) for g in domain.fact_check_groups]),
            'fact_check_counts': domain.fact_check_counts,
            'language': language
        },
        language=language
    )

    render_to_file(
        template='about.html',
        output_path='about/index.html',
        data={
            'title': page_title,
            'domain': domain,
            'fact_checks': domain.fact_checks,
            'fact_check_counts': domain.fact_check_counts,
            'language': language
        },
        language=language
    )

    render_to_file(
        template='graph.html',
        output_path='graph/index.html',
        data={
            'title': page_title,
            'data': json.dumps(graph.get_complete_data()),
            'language': language
        },
        language=language
    )

    for fact_check in domain.fact_checks:
        render_to_file(
            template='fact_check.html',
            output_path=fact_check.file_name(),
            data={
                'title': page_title + ' – ' + fact_check.get_statement(),
                'fact_check': fact_check,
                'similar_fact_checks': domain.get_similar_fact_checks(fact_check),
                'language': language
            },
            language=language
        )

    for fact_check_group in domain.fact_check_groups:
        render_to_file(
            template='fact_check_group.html',
            output_path=fact_check_group.file_name(),
            data={
                'title': page_title + ' – ' + fact_check_group.promoted_fact_check.get_statement(),
                'fact_check_group': fact_check_group,
                'language': language
            },
            language=language
        )