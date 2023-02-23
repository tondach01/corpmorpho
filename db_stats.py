"""This file contains tools for handling queries on corpora."""
import morph_database as md
from typing import Dict, List, TextIO, Set
import pandas as pd
import numpy as np


def lemmas(corpus: TextIO):
    """Generates all lemmas in given corpus"""
    line = corpus.readline()
    line = line.strip()
    while line:
        if len(line.split("\t")) == 3:
            yield line.split("\t")[1]
        line = corpus.readline()
        line = line.strip()


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
    row = freqlist.readline()
    row = row.strip()
    while row:
        if len(data) == limit:
            break
        elements = row.split()
        if len(elements) >= 3 and (threshold_function is None or threshold_function(elements)):
            data.append([elements[0], elements[1], int(elements[2])])
        row = freqlist.readline()
        row = row.strip()
    return pd.DataFrame(data=data, columns=["word", "lemma", "frequency"])


def lemma_scores(segments: List[str], frame: pd.DataFrame, morph_db: md.MorphDatabase) -> Dict[str, int]:
    filtered = frame
    scores = dict()
    for suffix in segments:
        filtered = filtered[filtered.lemma.apply(lambda x: x.endswith(suffix))]
        if len(filtered) == 0:
            return scores
        for paradigm, count in filtered.groupby(["paradigm"]).size().to_dict().items():
            scores[paradigm] = max(scores.get(paradigm, 0), len(suffix) * count)
    return scores


def word_scores(segments: List[str], frame: pd.DataFrame, morph_db: md.MorphDatabase) -> Dict[str, int]:
    # TODO
    pass


def occurring_forms(word_forms: Set[str], frame: pd.DataFrame) -> Set[str]:
    """From given forms of a word, returns those that occur in given dataframe."""
    found = set()
    for form in word_forms:
        if form in frame.word:
            found.add(form)
    return found


def word_similarity(word: str, other: str) -> int:
    """Finds similarity of two words based on longest common substring"""
    max_similarity = 0
    for start in range(len(word)):
        for end in range(start, len(word) + 1):
            if end - start > max_similarity and word[start:end] in other:
                max_similarity = end - start
    return max_similarity


def print_scores(scores: Dict[str, int]) -> None:
    """Prints paradigms in descending order (by their frequency scores)"""
    # TODO enhance
    for paradigm in sorted(scores, key=(lambda x: scores[x]), reverse=True):
        print(f"{paradigm}: {scores[paradigm]}")
    print()
