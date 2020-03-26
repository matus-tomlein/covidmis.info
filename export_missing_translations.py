import json


language = 'sk'
file_name = f'cache/translations_{language}.json'

translations = {}
with open(file_name) as f:
    translations = json.load(f)

print('\n=====\n'.join([
    text
    for text, translation in translations.items()
    if translation == ''
]))