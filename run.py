from jinja2 import Environment, FileSystemLoader
import pandas as pd
from models.article import Article
from models.article_mapping import ArticleMapping
from models.fact_check import FactCheck

def render_template(file_name, data={}):
    with open(f'templates/{file_name}') as f:
        template_str = f.read()

    template = Environment(loader=FileSystemLoader('templates/')).from_string(template_str)
    html_str = template.render(**data)
    return html_str

def render_to_file(template, output_path, data, language):
    html = render_template(template, data)
    folder = f'docs/{output_path}'
    if language == 'sk':
        folder = f'docs_sk/{output_path}'

    with open(folder, 'w') as f:
        f.write(html)

articles = pd.read_pickle('cache/articles.p')
articles = [
    Article(id=article['id'], title=article['title'], url=article['url'])
    for _, article in articles.iterrows()
]
articles_by_id = {
    article.id: article
    for article in articles
}

mappings = pd.read_pickle('cache/mappings.p')
mappings = mappings.drop_duplicates(['source_entity_id', 'target_entity_id'])
mappings_by_claim_id = mappings.groupby('target_entity_id').apply(
    lambda claim_mappings: [
        ArticleMapping(article=articles_by_id[mapping['source_entity_id']], score=mapping['value']['score'])
        for _, mapping in claim_mappings.iterrows()
    ]
).to_dict()

fact_checks = pd.read_pickle('cache/fact_checks.p')
fact_checks = fact_checks.loc[
    (fact_checks.claim.str.lower().str.contains('covid')) |
    (
        (fact_checks.claim.str.lower().str.contains('corona')) &
        (fact_checks.claim.str.lower().str.contains('virus'))
    )
]
fact_checks['published_at'] = pd.to_datetime(fact_checks['published_at'])
fact_checks = fact_checks.sort_values('published_at', ascending=False)
fact_check_counts = (
    fact_checks['published_at'] - pd.to_timedelta(fact_checks['published_at'].dt.dayofweek, unit='d')
).dt.date.value_counts().sort_index().cumsum()
fact_checks = [
    FactCheck(
        id=fact_check['id'],
        claim_id=fact_check['claim_id'],
        statement=fact_check['claim'],
        published_at=fact_check['published_at'],
        description=fact_check['description'],
        url=fact_check['url'],
        rating=fact_check['rating']['overall_rating'],
        article_mappings=mappings_by_claim_id[fact_check['claim_id']] if fact_check['claim_id'] in mappings_by_claim_id else [],
        other_info=fact_check['other_info']
    )
    for _, fact_check in fact_checks.iterrows()
]

similar_fact_checks = pd.read_pickle('cache/similar_fact_checks.p')

page_title = 'CovidMis.info'
language = 'en'
render_to_file(
    template='index.html',
    output_path='index.html',
    data={
        'title': page_title,
        'fact_checks': fact_checks,
        'fact_check_counts': fact_check_counts,
        'language': language
    },
    language=language
)

for fact_check in fact_checks:
    similar_fact_check_ids = similar_fact_checks.loc[fact_check.id] if fact_check.id in similar_fact_checks.index else []

    render_to_file(
        template='fact_check.html',
        output_path=fact_check.file_name(),
        data={
            'title': page_title + ' – ' + fact_check.statement,
            'fact_check': fact_check,
            'similar_fact_checks': [f for f in fact_checks if f.id in similar_fact_check_ids],
            'language': language
        },
        language=language
    )

page_title = 'CovidDez.info'
language = 'sk'
for fact_check in fact_checks:
    fact_check.translate(language)

render_to_file(
    template='index.html',
    output_path='index.html',
    data={
        'title': page_title,
        'fact_checks': fact_checks,
        'fact_check_counts': fact_check_counts,
        'language': language
    },
    language=language
)

for fact_check in fact_checks:
    similar_fact_check_ids = similar_fact_checks.loc[fact_check.id] if fact_check.id in similar_fact_checks.index else []

    render_to_file(
        template='fact_check.html',
        output_path=fact_check.file_name(),
        data={
            'title': page_title + ' – ' + fact_check.statement,
            'fact_check': fact_check,
            'similar_fact_checks': [f for f in fact_checks if f.id in similar_fact_check_ids],
            'language': language
        },
        language=language
    )