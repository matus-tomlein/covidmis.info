import tensorflow as tf
import tensorflow_hub as hub
import nltk
import os

from nltk.tokenize import sent_tokenize
import time

from nltk.tokenize import sent_tokenize

ROOT_DIR = os.path.join(*(os.path.split(os.path.dirname(os.path.abspath(__file__)))[:1]))

class SentenceEmbedder:
    def __init__(self):
        tf.compat.v1.disable_eager_execution()
        self.embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/3")
        self.session = tf.compat.v1.Session()
        self.session.run([tf.compat.v1.global_variables_initializer(), tf.compat.v1.tables_initializer()])
        # nltk.data.path.append(os.path.join(ROOT_DIR, 'datasets'))
        # try:
        #     nltk.data.find('tokenizers/punkt')
        # except LookupError:
        #     nltk.download('punkt', download_dir=os.path.join(ROOT_DIR, 'datasets'))

    def embed_sentences(self, sentences):
        if not any(sentences):
            return []

        embeddings = self.embed(sentences)
        return self.session.run(embeddings)['outputs'].tolist()

    def embed_text(self, text):
        return self.embed_sentences(sent_tokenize(text))