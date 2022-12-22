import morph_database as md
from typing import Dict
from os import sep


def paradigm_frequencies(corpus: str, morph_db: md.MorphDatabase) -> Dict[str, int]:
    """Computes frequencies of words belonging to single paradigm in corpus"""
    freqs = dict()
    corp = open(corpus, encoding="utf-8")
    for line in corp:
        if len(line.split("\t")) != 3:
            continue
        lemma = line.split("\t")[1]
        if lemma not in morph_db.vocab.keys():
            continue
        paradigm = morph_db.vocab[lemma]
        freqs[paradigm] = freqs.get(paradigm, 0) + 1
    corp.close()
    return freqs


def main():
    desam = f"C:{sep}Users{sep}ondra{sep}Desktop{sep}MUNI{sep}PB106{sep}data{sep}desam_model{sep}desam"
    paradigm_frequencies(desam, md.MorphDatabase("current.dic", "current.par"))


if __name__ == "__main__":
    main()
