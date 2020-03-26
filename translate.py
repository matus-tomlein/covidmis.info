import json
import subprocess


language = 'sk'
file_name = f'cache/translations_{language}.json'

translations = {}
try:
    with open(file_name) as f:
        translations = json.load(f)
except IOError:
    pass

def translate(text, language='sk'):
    global translations

    if text in translations: # and translation[text] != '':
        return translations[text]

    result = subprocess.run(['./translate.js', text], stdout=subprocess.PIPE)
    translation = result.stdout.decode('utf-8').strip()
    translations[text] = translation
    with open(file_name, 'w') as f:
        json.dump(translations, f)

    return translation