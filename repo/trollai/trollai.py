import ngram

import zlib, json
file = "troll.model"

def load(file: str):
    with open(file, 'rb') as f:
