from models.article import Article
from models.fact_check import FactCheck
from models.fact_check_group import FactCheckGroup
from models.domain import Domain
from models.article_mapping import ArticleMapping
import pandas as pd
import json


def create_domain():
    articles = pd.read_pickle('cache/articles.p')
    articles['published_at'] = pd.to_datetime(articles['published_at'], utc=True)
    article_counts = articles['published_at'].clip(pd.Timestamp(2019, 12, 1).tz_localize('UTC')).dt.floor('7d').dt.date.value_counts().sort_index().cumsum()
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
    fact_checks['published_at'] = pd.to_datetime(fact_checks['published_at'], utc=True)
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
    fact_checks_by_id = {
        fact_check.id: fact_check
        for fact_check in fact_checks
    }

    similar_fact_checks = pd.read_pickle('cache/similar_fact_checks.p')
    fact_check_similarities = pd.read_pickle('cache/fact_check_similarities.p')

    with open('cache/fact_groups.json') as f:
        fact_check_groups = json.load(f)

    fact_check_groups = list(reversed(sorted([
        FactCheckGroup(
            fact_checks=[
                fact_checks_by_id[fact_check]
                for fact_check in group['fact_checks']
            ]
        )
        for group in fact_check_groups
    ], key=lambda group: len(group.fact_checks))))

    domain = Domain(
        fact_checks=fact_checks,
        articles=articles,
        article_counts=article_counts,
        fact_check_groups=fact_check_groups,
        fact_check_counts=fact_check_counts,
        fact_checks_by_id=fact_checks_by_id,
        similar_fact_checks=similar_fact_checks,
        fact_check_similarities=fact_check_similarities
    )
    return domain