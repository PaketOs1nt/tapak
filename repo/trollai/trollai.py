import json
import sys
import zlib

import ngram

if sys.version_info.minor < 12:
    print("need 3.12 minimum version ")

file = "troll.model"


def load(file: str):
    with open(file, "rb") as f:
        compiled = json.loads(zlib.decompress(f.read()))
        data = {tuple(k.split("|")): v for k, v in compiled.items()}
        model = eval(
            "ngram.Model[str](len(list(data.keys())[0]))"
        )  # шоб без compile error
        model.data = data
        model.scorer = ngram.StrScorer()
        return model


def on_token(token: str):
    print(token, end=" ")


def main():
    model = load(file)

    while True:
        text = tuple(input(f"\nstart ({model.n} words) > ").split(" "))
        size = int(input("answer size > "))

        print()

        for t in text:
            on_token(t)

        model.sequence(text, size, on_token=on_token)
        print()


if __name__ == "__main__":
    main()
