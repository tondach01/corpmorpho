"""This file contains tools for handling queries on corpora."""
import morph_database as md
from typing import Dict, List, Set, Tuple
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


def occurring_forms(word_forms: Set[str], frame: pd.DataFrame) -> Dict[str, int]:
    """From given forms of a word, returns those that occur in given dataframe."""
    found = dict()
    for form in word_forms:
        found[form] = frame[frame.word == form].frequency.sum()
    return found


def clean_freqlist(freq_list: str) -> None:
    import re
    cleaned = open(freq_list + ".cleaned", "w", encoding="utf-8")
    with open(freq_list, encoding="utf-8") as fl:
        for line in fl:
            if not re.fullmatch(r"\S+\s\d+\s\d+", line.strip()):
                continue
            values = line.split("\t")
            word, freq = values[0], values[1]
            if re.fullmatch(r"[a-záéíóúůýěžščřďťň]+", word) is None:
                continue
            print("\t".join([word, freq]), file=cleaned)
    cleaned.close()


def filter_freqlist(freq_list: str, morph_db: md.MorphDatabase) -> None:
    """Picks from alphabetically sorted frequency list only forms of paradigms in morphological database."""
    out = open(f"{freq_list}.filtered", "w", encoding="utf-8")
    with open(freq_list, encoding="utf-8") as fl:
        for line in fl:
            print(line.strip())  # debug
            word = line.split()[0]
            for paradigm, data in morph_db.paradigms.items():
                if word[0] != paradigm[0].lower() and data["<suffix>"] != paradigm:
                    continue
                if word in set(map(str.lower, morph_db.only_forms(paradigm, paradigm))):
                    out.write(f"{paradigm}\t{line}")


def segment_dic_file(morph_db: md.MorphDatabase, seg_method, outfile: str, only_lemmas: bool = True) -> None:
    """Segments each word in vocabulary of morphological database with given method. If only_lemmas set
    to False, it first computes and includes all forms of given lemma. Result is saved to outfile."""
    with open(outfile, "w", encoding="utf-8") as out:
        for lemma, paradigm in morph_db.vocab.items():
            segments = "=".join(seg_method(lemma)).replace("_", "").replace("¦", "").replace("𐋇", "")\
                .replace("𐊣", "").replace("𐊼", "")
            print(f"{segments}:{lemma}:{paradigm}", file=out)
            if only_lemmas:
                continue
            for form in morph_db.only_forms(lemma, paradigm):
                segments = "=".join(seg_method(form)).replace("_", "").replace("¦", "").replace("𐋇", "") \
                    .replace("𐊣", "").replace("𐊼", "")
                print(f"{segments}:{lemma}:{paradigm}", file=out)


def similar_words(segments: List[str], freq_list: str, seg_method) -> Dict[str, Dict[str, int]]:
    """Finds words similar to given segmented one, based on their common segmentation."""
    similar = dict()
    for i in range(len(segments)):
        similar["".join(segments[:i + 1])] = dict()
    with open(freq_list, encoding="utf-8") as fl:
        for line in fl:
            values = line.strip().split()
            corp_segments = seg_method(values[0])
            for i in range(min(len(segments), len(corp_segments))):
                if segments[:i + 1] == corp_segments[:i + 1]:
                    similar["".join(segments[:i + 1])]["" if i == len(corp_segments) - 1
                                                       else "".join(corp_segments[i + 1:])] = int(values[1])
    return similar


def word_similarity(word: str, other: str) -> int:
    """Finds similarity of two words based on longest common substring"""
    max_similarity = 0
    for start in range(len(word)):
        for end in range(start, len(word) + 1):
            if end - start > max_similarity and word[start:end] in other:
                max_similarity = end - start
    return max_similarity


def normalize_spread(spread: Dict[str, float]) -> Dict[str, float]:
    """Normalizes given frequency spread by dividing each frequency by greatest occurred frequency."""
    norm = max(spread.values())
    return {suf: freq / norm for (suf, freq) in spread}


def spread_difference(paradigm: Dict[str, float], word: Dict[str, float]) -> float:
    """Computes difference of normalized spreads of given paradigm and word."""
    diff = 0
    for suf, freq in paradigm.items():
        diff += abs(freq - word.get(suf, 0.0))
    for suf, freq in word.items():
        if suf not in paradigm.keys():
            diff += freq
    return diff / len(paradigm)


def spread_scores(word: Dict[str, float], morph_db: md.MorphDatabase) -> Dict[str, float]:
    """Computes paradigm scores for given word based on its forms spread."""
    word_normed = normalize_spread(word)
    scores = dict()
    for paradigm, data in morph_db.paradigms.items():
        if not set(word.keys()).intersection(set(data["affixes"].keys())):
            continue
        scores[paradigm] = spread_difference(normalize_spread(data["spread"]), word_normed)
    return scores


def print_scores(scores: Dict[str, int]) -> None:
    """Prints paradigms in descending order (by their frequency scores)"""
    # TODO enhance
    for paradigm in sorted(scores, key=(lambda x: scores[x]), reverse=True):
        print(f"{paradigm}: {scores[paradigm]}")
    print()
