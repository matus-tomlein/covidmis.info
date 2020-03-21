from jinja2 import Environment, FileSystemLoader
import pandas as pd

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

fact_checks = pd.read_pickle('cache/fact_checks.p')
fact_checks = fact_checks.loc[
    (fact_checks.claim.str.lower().str.contains('covid')) |
    (fact_checks.claim.str.lower().str.contains('corona'))
]
fact_checks = fact_checks.loc[fact_checks['num_articles'] > 0].sort_values('num_articles', ascending=False)
render_to_file(
    template='index.html',
    output_path='index.html',
    data={
        'page_name': 'covidmis.info',
        'fact_checks': fact_checks
    }
)