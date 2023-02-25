"""This file contains tools for handling queries on corpora."""
import morph_database as md
from typing import Dict, List, Set
import pandas as pd
import numpy as np


def lemmas(corpus: str):
    """Generates all lemmas from given corpus."""
    for word in corpus_generator(corpus, lemmas=True):
        yield word


def corpus_generator(corpus: str, lemmas: bool):
    """Generates all desired features (words/lemmas) from given corpus."""
    c = open(corpus, encoding="utf-8")
    line = c.readline()
    line = line.strip()
    while line:
        if len(line.split("\t")) == 3:
            yield line.split("\t")[1 if lemmas else 0]
        line = c.readline()
        line = line.strip()
    c.close()


def words(corpus: str):
    """Generates all words from given corpus."""
    for word in corpus_generator(corpus, lemmas=False):
        yield word


def words_to_dataframe(corpus: str, morph_db: md.MorphDatabase) -> pd.DataFrame:
    """Converts all words from given corpus to dataframe."""
    frame = pd.DataFrame(data={"word": [x for x in words(corpus)], "lemma": [y for y in lemmas(corpus)]})
    frame["paradigm"] = frame.lemma.apply(lambda x: morph_db.vocab.get(x, ""))
    frame["count"] = np.ones(len(frame))
    return frame


def lemmas_to_dataframe(corpus: str, morph_db: md.MorphDatabase) -> pd.DataFrame:
    frame = pd.DataFrame([x for x in lemmas(corpus)], columns=["lemma"])
    frame["paradigm"] = frame.lemma.apply(lambda x: morph_db.vocab.get(x, ""))
    frame["count"] = np.ones(len(frame))
    return frame


def freqlist_to_dataframe(freqlist: str, limit: int = -1) -> pd.DataFrame:
    """Loads data from given frequency list to dataframe. The wordlist should be in format 'word lemma frequency'.
    Amount of loaded data can be limited (default -1 = unlimited)."""
    data = []
    with open(freqlist, encoding="utf-8") as fl:
        for row in fl:
            row = row.strip()
            if len(data) == limit:
                break
            elements = row.split()
            if len(elements) >= 2:
                data.append([elements[0], int(elements[1])])
    return pd.DataFrame(data=data, columns=["word", "frequency"])


def lemma_scores(segments: List[str], frame: pd.DataFrame, morph_db: md.MorphDatabase) -> Dict[str, int]:
    filtered = frame[frame.paradigm != ""]
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
        if not frame[frame.word == form].empty:
            found.add(form)
    return found


def clean_freqlist(freqlist: str) -> None:
    import re
    cleaned = open(freqlist + ".cleaned", "w", encoding="utf-8")
    with open(freqlist, encoding="utf-8") as fl:
        for line in fl:
            if not re.fullmatch(r"\S+\s\d+\s\d+", line.strip()):
                continue
            values = line.split("\t")
            word, freq = values[0], values[1]
            if re.fullmatch(r"[\w-]*[^\d\W-]+[\w-]*", word) is None:
                continue
            print("\t".join([word, freq]), file=cleaned)
    cleaned.close()


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
