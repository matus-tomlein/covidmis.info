from jinja2 import Environment, FileSystemLoader
import pandas as pd
from slugify import slugify

def render_template(file_name, data={}):
    with open(f'templates/{file_name}') as f:
        template_str = f.read()

    template = Environment(loader=FileSystemLoader('templates/')).from_string(template_str)
    html_str = template.render(**data)
    return html_str

def render_to_file(template, output_path, data):
    html = render_template(template, data)
    with open(f'docs/{output_path}', 'w') as f:
        f.write(html)

def fact_check_file_name(fact_check):
    return 'fact_checks/' + str(fact_check['id']) + '-' + slugify(fact_check['claim'], max_length=50) + '.html'

def fact_check_path(fact_check):
    return '/' + fact_check_file_name(fact_check)

fact_checks = pd.read_pickle('cache/fact_checks.p')
fact_checks['domain'] = fact_checks['url'].str.split('/', expand=True)[2].apply(lambda domain: domain.replace('www.', ''))
fact_checks['path'] = fact_checks.apply(fact_check_path, axis=1)
fact_checks = fact_checks.loc[
    (fact_checks.claim.str.lower().str.contains('covid')) |
    (
        (fact_checks.claim.str.lower().str.contains('corona')) &
        (fact_checks.claim.str.lower().str.contains('virus'))
    )
]
fact_checks = fact_checks.sort_values('num_articles', ascending=False)

articles = pd.read_pickle('cache/articles.p')
articles['domain'] = articles['url'].str.split('/', expand=True)[2].apply(lambda domain: domain.replace('www.', ''))

render_to_file(
    template='index.html',
    output_path='index.html',
    data={
        'page_name': 'covidmis.info',
        'fact_checks': fact_checks
    }
)

for _, fact_check in fact_checks.iterrows():
    fact_check_articles = articles.loc[articles['id'].isin(fact_check['article_ids'])]
    render_to_file(
        template='fact_check.html',
        output_path=fact_check_file_name(fact_check),
        data={
            'fact_check': fact_check,
            'articles': fact_check_articles
        }
    )