import pandas as pd
import pickle
import psycopg2
from sshtunnel import SSHTunnelForwarder
import os
from nltk.tokenize import sent_tokenize
from sentence_embedder import SentenceEmbedder
from sklearn.metrics.pairwise import cosine_similarity


def save_fact_checks():
    columns = ['id', 'url', 'source_id', 'description', 'rating', 'other_info', 'category', 'claim', 'published_at']
    cur.execute(f"""SELECT {', '.join(columns)}
        FROM fact_checking_articles
        WHERE is_deleted = FALSE""")
    rows = cur.fetchall()

    fact_checks = pd.DataFrame(rows, columns=columns)
    fact_checks.to_pickle('cache/fact_checks.p')
    print('Fetched fact checks')


def save_mappings():
    columns = ['id', 'method_id', 'annotation_type_id', 'source_entity_id', 'target_entity_id', 'value']
    cur.execute(f"""SELECT {', '.join(columns)}
    FROM relation_annotations
    WHERE method_id = 6 AND value->>'value' = 'yes' AND is_deleted = FALSE""")
    rows = cur.fetchall()

    mappings = pd.DataFrame(rows, columns=columns)
    mappings.to_pickle('cache/mappings.p')
    print('Fetched mappings')


def save_articles():
    columns = ['id', 'title', 'url', 'published_at']
    cur.execute(f"""SELECT {', '.join(columns)} FROM articles""")
    rows = cur.fetchall()

    articles = pd.DataFrame(rows, columns=columns)
    articles.to_pickle('cache/articles.p')
    print('Fetched articles')


def save_claims():
    columns = ['id', 'statement', 'description', 'rating', 'queries', 'category']
    cur.execute(f"""SELECT {', '.join(columns)}
        FROM claims
        WHERE is_deleted = FALSE""")
    rows = cur.fetchall()

    claims = pd.DataFrame(rows, columns=columns)
    claims.to_pickle('cache/claims.p')
    print('Fetched claims')


def save_fact_check_claim_transformations():
    columns = ['id', 'method_id', 'annotation_type_id', 'source_entity_id', 'target_entity_id', 'value']
    cur.execute(f"""SELECT {', '.join(columns)}
    FROM relation_annotations
    WHERE method_id = 5 AND is_deleted = FALSE""")
    rows = cur.fetchall()

    transformations = pd.DataFrame(rows, columns=columns)
    transformations.to_pickle('cache/fact_check_claims.p')
    print('Fetched fact-check claims')


def create_claim_to_articles():
    mappings = pd.read_pickle('cache/mappings.p')
    claim_to_articles = mappings.groupby('target_entity_id')['source_entity_id'].apply(set).to_dict()
    pickle.dump(claim_to_articles, open('cache/claim_to_articles.p', 'wb') )


def process_fact_checks():
    fact_check_claims = pd.read_pickle('cache/fact_check_claims.p')
    fact_check_to_claim = {
        row['source_entity_id']: row['target_entity_id']
        for _, row in fact_check_claims.iterrows()
    }
    fact_checks = pd.read_pickle('cache/fact_checks.p')
    fact_checks['claim_id'] = fact_checks['id'].apply(lambda fact_check_id: fact_check_to_claim[fact_check_id] if fact_check_id in fact_check_to_claim else None)

    claim_to_articles = pickle.load(open('cache/claim_to_articles.p', 'rb'))

    fact_checks['article_ids'] = fact_checks['claim_id'].apply(lambda claim_id: claim_to_articles[claim_id] if claim_id in claim_to_articles else [])
    fact_checks['num_articles'] = fact_checks['article_ids'].apply(len)

    fact_checks = fact_checks.loc[
        (fact_checks.claim.str.lower().str.contains('covid')) |
        (
            (fact_checks.claim.str.lower().str.contains('corona')) &
            (fact_checks.claim.str.lower().str.contains('virus'))
        )
    ]

    fact_checks = fact_checks.drop_duplicates('claim')

    fact_checks.to_pickle('cache/fact_checks.p')
    print('Processed fact checks')

def process_articles():
    mappings = pd.read_pickle('cache/mappings.p')
    article_ids = set(mappings['source_entity_id'])
    articles = pd.read_pickle('cache/articles.p')
    articles = articles.loc[articles['id'].isin(article_ids)]
    articles.to_pickle('cache/articles.p')
    print('Processed articles')


def find_similar_fact_checks():
    fact_checks = pd.read_pickle('cache/fact_checks.p')
    sentence_embedder = SentenceEmbedder()

    fact_check_sentences = [
        (fact_check['id'], sentence)
        for _, fact_check in fact_checks.iterrows()
        for sentence in sent_tokenize(fact_check['claim'])
    ]

    embeddings = sentence_embedder.embed_sentences([s[1] for s in fact_check_sentences])
    pairwise_similarities = cosine_similarity(embeddings)

    similarities = pd.DataFrame([
        (fact_check_id, other_fact_check_id,
         pairwise_similarities[sentence_i][other_sentence_i])
        for fact_check_id in fact_checks['id']
        for sentence_i in [
            i for i, (fid, _) in enumerate(fact_check_sentences)
            if fid == fact_check_id
        ]
        for other_sentence_i, other_fact_check_id in [
            (i, fid) for i, (fid, _) in enumerate(fact_check_sentences)
            if fid != fact_check_id
        ]
    ], columns=['fact_check_1', 'fact_check_2', 'similarity'])

    similarities = similarities.loc[similarities['similarity'] >= 0.3]
    similar_fact_checks = pd.Series({
        fact_check_id: list(row.sort_values(ascending=False).iloc[:5].index)
        for fact_check_id, row in similarities.groupby(['fact_check_1', 'fact_check_2'])['similarity'].max().unstack().iterrows()
    })
    similar_fact_checks.to_pickle('cache/similar_fact_checks.p')
    print('Found similar fact-checks')

with SSHTunnelForwarder(
    (os.environ['SSH_HOST'], 22),
    ssh_private_key='/Users/matus/.ssh/id_rsa',
    ssh_username=os.environ['SSH_USERNAME'],
    remote_bind_address=('localhost', 5433),
    local_bind_address=('localhost', 7543)
) as tunnel:

    tunnel.start()
    print('server connected')

    params = {
        'database': os.environ['DATABASE'],
        'user': os.environ['USER'],
        'password': os.environ['PASSWORD'],
        'host': tunnel.local_bind_host,
        'port': tunnel.local_bind_port
    }

    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    print('database connected')

    try:
        save_fact_checks()
        save_mappings()
        save_articles()
        save_claims()
        save_fact_check_claim_transformations()
        save_mappings()
        create_claim_to_articles()
        process_fact_checks()
        process_articles()
        find_similar_fact_checks()
    except Exception as inst:
        print(type(inst))
        print(inst.args)
        print(inst)

    conn.close()
    tunnel.stop()