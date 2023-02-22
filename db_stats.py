#!/usr/bin/env python3
import morph_database as md
from typing import Dict, List, TextIO
import pandas as pd
import numpy as np


def lemmas(corpus: TextIO):
    """Generates all lemmas in given corpus"""
    line = corpus.readline().strip()
    while line:
        if len(line.split("\t")) != 3:
            continue
        yield line.split("\t")[1]
        line = corpus.readline().strip()


def lemmas_to_dataframe(corpus: TextIO, morph_db: md.MorphDatabase) -> pd.DataFrame:
    frame = pd.DataFrame([x for x in lemmas(corpus)], columns=["lemma"])
    frame["paradigm"] = frame.lemma.apply(lambda x: morph_db.vocab.get(x, ""))
    frame["count"] = np.ones(len(frame))
    return frame[frame.paradigm != ""]


def freqlist_to_dataframe(freqlist: TextIO, limit: int = -1, threshold_function=None) -> pd.DataFrame:
    """Loads data from given frequency list to dataframe. The wordlist should be in format 'word lemma frequency'.
    Amount of loaded data can be limited (default -1 = unlimited). Rows to load can be filtered with threshold
    function List[str] -> bool."""
    data = []
    with open(freqlist) as fl:
        row = fl.readline()
        while row is not None:
            if len(data) == limit:
                break
            elements = row.split()
            if len(elements) >= 3 and (threshold_function is None or threshold_function(elements)):
                data.append([elements[0], elements[1], int(elements[2])])
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
