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


def corpus_to_dataframe(corpus: str, morph_db: md.MorphDatabase) -> pd.DataFrame:
    frame = pd.DataFrame([x for x in lemmas(corpus)], columns=["lemma"])
    frame["paradigm"] = frame.lemma.apply(lambda x: morph_db.vocab.get(x, ""))
    frame["count"] = np.ones(len(frame))
    return frame[frame.paradigm != ""]


def suffix_scores(suffix: str, frame: pd.DataFrame) -> Dict[str, int]:
    filtered = frame[frame.lemma.apply(lambda x: x.endswith(suffix))].groupby(["paradigm"]).size().to_dict()
    return {paradigm: len(suffix) * count for paradigm, count in filtered.items()}


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
    from time import time
    from os import sep
    desam = f"desam{sep}desam"
    morph_db = md.MorphDatabase("current.dic", "current.par")
    word = "dlouhatánský"
    segments = [word[i:] for i in range(len(word))]
    df = corpus_to_dataframe(desam, morph_db)
    start = time()
    # p = suffix_frequencies(desam, md.MorphDatabase("current.dic", "current.par"), "čka")
    # p = paradigm_frequencies(desam, md.MorphDatabase("current.dic", "current.par"))
    # print_score(p)
    for suffix in segments:
        k = suffix_scores(suffix, df)
    checkpoint = time()
    print(f"pandas version finished in {round(checkpoint - start, 3)}s")
    lemma_scores(desam, morph_db, segments)
    print(f"classic version finished in {round(time() - checkpoint, 3)}s")


if __name__ == "__main__":
    main()
