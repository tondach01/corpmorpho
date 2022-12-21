#!/usr/bin/env python3
import morph_database
from typing import List


def fit_suffices(word: str, suffices_db: morph_database.SUFFICES_DATABASE) -> List[str]:
    fitting = []
    for suffix in suffices_db.keys():
        if matches_suffix(word, suffix):
            fitting.append(suffix)
    return fitting


def matches_suffix(word: str, suffix: str) -> bool:
    return word.endswith(suffix.split("|")[1])


def lemma(word: str, suffix: str) -> str:
    return word.removesuffix(suffix.split("|")[1]) + suffix.split("|")[0]


def main():
    import group_word_forms
    import sentencepiece as sp

    word = "pochybovačem"
    m = sp.SentencePieceProcessor()
    m.load('sentencepiece\\m.model')
    print(m.encode_as_pieces(word))
    k = m.encode_as_pieces(word)[-1]

    md = group_word_forms.read_corpora(open("..\\..\\PB106\\data\\desam_model\\desam", "r", encoding="utf-8"))
    # md = morph_database.main()

    sd = morph_database.suffix_database(md)
    s = fit_suffices(word, sd)
    for suffix in s:
        if suffix.split("|")[1] in k:
            print(f"{lemma(word, suffix)}: {sum(sd[suffix].values())}")


if __name__ == "__main__":
    main()
