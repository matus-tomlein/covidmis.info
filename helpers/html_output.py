from jinja2 import Environment, FileSystemLoader


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
