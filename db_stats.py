import morph_database as md
from typing import Dict


def paradigm_frequencies(corpus: str, morph_db: md.MorphDatabase) -> Dict[str, int]:
    freqs = dict()
    corp = open(corpus, encoding="utf-8")
    for line in corp:
        if len(line.split("\t")) != 3:
            continue
        lemma = line.split("\t")[1]
        if lemma not in morph_db.paradigms.keys():
            continue
        paradigm = morph_db.paradigms[lemma]
        freqs[paradigm] = freqs.get(paradigm, 0) + 1
    corp.close()
    return freqs


def main():
    pass


if __name__ == "__main__":
    main()
