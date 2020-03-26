import json


language = 'sk'
file_name = f'cache/translations_{language}.json'

translations = {}
with open(file_name) as f:
    translations = json.load(f)

with open('translation_import_input.txt') as f:
    translations_input = f.read()

with open('translation_import_output.txt') as f:
    translations_output = f.read()

new_translations = {
    source: translation
    for source, translation in zip(translations_input.split('\n=====\n'), translations_output.split('\n=====\n'))
}

translations = {**translations, **new_translations}
with open(file_name, 'w') as f:
    json.dump(translations, f)

print(len(new_translations), 'translations imported')