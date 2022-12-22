import morph_database as md
from typing import Dict
from os import sep


def lemmas(corpus: str):
    """Generates all lemmas in given corpus"""
    corp = open(corpus, encoding="utf-8")
    for line in corp:
        if len(line.split("\t")) != 3:
            continue
        yield line.split("\t")[1]
    corp.close()


def paradigm_frequencies(corpus: str, morph_db: md.MorphDatabase, suffix: str = "") -> Dict[str, int]:
    """Computes frequencies of lemmas belonging to single paradigm in corpus. If given suffix,
    limits the search only to lemmas ending with it."""
    freqs = dict()
    for lemma in lemmas(corpus):
        if not lemma.endswith(suffix) or lemma not in morph_db.vocab.keys():
            continue
        paradigm = morph_db.vocab[lemma]
        freqs[paradigm] = freqs.get(paradigm, 0) + 1
    return freqs


def suffix_frequencies(corpus: str, morph_db: md.MorphDatabase, suffix: str) -> Dict[str, int]:
    """Computes frequencies of paradigms containing given suffix (not only in lemma)"""
    freqs = dict()
    non_matching = set()
    for lemma in lemmas(corpus):
        if lemma not in morph_db.vocab.keys():
            continue
        paradigm = morph_db.vocab[lemma]
        if paradigm in freqs.keys():
            freqs[paradigm] += 1
            continue
        elif paradigm in non_matching:
            continue
        found = False
        for form in morph_db.all_forms_with_paradigm(paradigm, paradigm).keys():
            if form.endswith(suffix) and not found:
                freqs[paradigm] = freqs.get(paradigm, 0) + 1
                found = True
        if not found:
            non_matching.add(paradigm)
    return freqs


def main():
    desam = f"C:{sep}Users{sep}ondra{sep}Desktop{sep}MUNI{sep}PB106{sep}data{sep}desam_model{sep}desam"
    p = suffix_frequencies(desam, md.MorphDatabase("current.dic", "current.par"), "čka")
    pass


if __name__ == "__main__":
    main()
