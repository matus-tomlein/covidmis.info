import json
import subprocess
from ratelimit import limits, sleep_and_retry


language = 'sk'
file_name = f'cache/translations_{language}.json'

translations = {}
try:
    with open(file_name) as f:
        translations = json.load(f)
except IOError:
    pass

@sleep_and_retry 
@limits(calls=1, period=1)
def fetch_translation(text):
    print('Translating')
    result = subprocess.run(['./translate.js', text], stdout=subprocess.PIPE)
    translation = result.stdout.decode('utf-8').strip()
    return translation

def translate(text, language='sk'):
    global translations

    if text.strip() == '':
        return text

    if text in translations and translations[text] != '':
        return translations[text]

    translation = fetch_translation(text)
    translations[text] = translation
    with open(file_name, 'w') as f:
        json.dump(translations, f)

    return translation
