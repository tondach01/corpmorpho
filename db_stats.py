#!/usr/bin/env python3
import morph_database as md
from typing import Dict, List
import pandas as pd
import numpy as np


def lemmas(corpus: str):
    """Generates all lemmas in given corpus"""
    corp = open(corpus, encoding="utf-8")
    for line in corp:
        if len(line.split("\t")) != 3:
            continue
        yield line.split("\t")[1]
    corp.close()


def lemmas_to_dataframe(corpus: str, morph_db: md.MorphDatabase) -> pd.DataFrame:
    frame = pd.DataFrame([x for x in lemmas(corpus)], columns=["lemma"])
    frame["paradigm"] = frame.lemma.apply(lambda x: morph_db.vocab.get(x, ""))
    frame["count"] = np.ones(len(frame))
    return frame[frame.paradigm != ""]


def freqlist_to_dataframe(freqlist: str, morph_db: md.MorphDatabase, limit: int = -1) -> pd.DataFrame:
    """Loads data from given frequency list to dataframe. The wordlist should be in format 'word lemma frequency'.
    Amount of loaded data can be limited (default -1 = unlimited)."""
    data = []
    with open(freqlist) as fl:
        row = fl.readline()
        while row is not None:
            if len(data) == limit:
                break
            elements = row.split()
            if len(elements) >= 3:
                data.append(elements[:3])
            row = fl.readline()
    return pd.DataFrame(data=data, columns=["word", "lemma", "frequency"])


def pandas_lemma_scores(segments: List[str], frame: pd.DataFrame) -> Dict[str, int]:
    filtered = frame
    scores = dict()
    for suffix in segments:
        filtered = filtered[filtered.lemma.apply(lambda x: x.endswith(suffix))]
        if len(filtered) == 0:
            return scores
        for paradigm, count in filtered.groupby(["paradigm"]).size().to_dict().items():
            scores[paradigm] = max(scores.get(paradigm, 0), len(suffix) * count)
    return scores


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


def lemma_scores(corpus: str, morph_db: md.MorphDatabase, segments: List[str]) -> Dict[str, int]:
    """Computes frequency scores of whole segmented word from given corpora"""
    freqs = dict()
    for lemma in lemmas(corpus):
        if lemma not in morph_db.vocab.keys():
            continue
        paradigm = morph_db.vocab[lemma]
        for segment in segments:
            segment = segment.lstrip("\u2581")
            if not lemma.endswith(segment):
                break
            freqs[segment] = freqs.get(segment, dict())
            freqs[segment][paradigm] = freqs[segment].get(paradigm, 0) + 1
    final_freqs = dict()
    for segment, scores in freqs.items():
        for paradigm, score in scores.items():
            final_freqs[paradigm] = max(final_freqs.get(paradigm, 0), score * len(segment))
    return final_freqs


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
        for form in morph_db.all_forms_with_paradigm(paradigm, paradigm, informal=False).keys():
            if form.endswith(suffix) and not found:
                freqs[paradigm] = freqs.get(paradigm, 0) + 1
                found = True
        if not found:
            non_matching.add(paradigm)
    return freqs


def print_score(score: Dict[str, int]) -> None:
    """Prints paradigms in descending order (by their frequency scores)"""
    for paradigm in sorted(score, key=(lambda x: score[x]), reverse=True):
        print(f"{paradigm}: {score[paradigm]}")
    print()


def main():
    '''
    from time import time
    from os import sep
    desam = f"desam{sep}desam"
    morph_db = md.MorphDatabase("data/current.dic", "data/current.par")
    word = "kámen"
    segments = [word[- i:] for i in range(1, len(word) + 1)]
    df = lemmas_to_dataframe(desam, morph_db)
    start = time()
    # p = suffix_frequencies(desam, md.MorphDatabase("current.dic", "current.par"), "čka")
    # p = paradigm_frequencies(desam, md.MorphDatabase("current.dic", "current.par"))
    # print_score(p)
    pandas_lemma_scores(segments, df)
    checkpoint = time()
    print(f"pandas version finished in {round(checkpoint - start, 3)}s")
    lemma_scores(desam, morph_db, segments)
    print(f"classic version finished in {round(time() - checkpoint, 3)}s")
    '''
    from os import sep
    morph_db = md.MorphDatabase("data/current.dic", "data/current.par")
    k = freqlist_to_dataframe(f"data{sep}mu_theses_czech.freqlist", morph_db, limit=100)
    pass


if __name__ == "__main__":
    main()
