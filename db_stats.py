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
                if word in set(map(str.lower, morph_db.lemma_forms(paradigm, paradigm))):
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
            for form in morph_db.lemma_forms(lemma, paradigm):
                segments = "=".join(seg_method(form)).replace("_", "").replace("¦", "").replace("𐋇", "") \
                    .replace("𐊣", "").replace("𐊼", "")
                print(f"{segments}:{lemma}:{paradigm}", file=out)


def normalize_spread(spread: Dict[str, float]) -> Dict[str, float]:
    """Normalizes given frequency spread by dividing each frequency by greatest occurred frequency."""
    if not spread:
        return dict()
    norm = max(spread.values())
    return {suf: freq / norm for (suf, freq) in spread.items()}


def spread_difference(paradigm: Dict[str, float], word: Dict[str, float]) -> float:
    """Computes difference of normalized spreads of given paradigm and word."""
    diff = 0
    for suf, freq in paradigm.items():
        diff += abs(freq - word.get(suf, 0.0))
    for suf, freq in word.items():
        if suf not in paradigm.keys():
            diff += freq
    return diff / (1 if len(paradigm) == 0 else len(paradigm))


def spread_scores(word_suffixes: Dict[str, float], morph_db: md.MorphDatabase, suffix: str) -> Dict[str, float]:
    """Computes paradigm scores for given word based on its forms spread."""
    word_normed = normalize_spread(word_suffixes)
    scores = dict()
    for paradigm in n_best_paradigms(set(word_suffixes.keys()), morph_db, suffix):
        scores[paradigm] = spread_difference(
            normalize_spread(morph_db.paradigms[paradigm].get("spread", dict())), word_normed)
    return scores


def n_best_paradigms(word_suffixes: Set[str], morph_db: md.MorphDatabase, suffix: str, n: int = 5,
                     threshold: float = 0.4) -> List[str]:
    """Chooses n most suitable paradigms for given suffixes based on size of their intersection. Can return more than
    n paradigms if they have the same score as the n-th one."""
    i_sizes = list()
    for paradigm, data in morph_db.paradigms.items():
        par_affixes = set(data["affixes"].keys())
        if suffix not in par_affixes:
            continue
        # penalize single-form paradigms
        rel_common = (len(word_suffixes.intersection(par_affixes)) + len(par_affixes)) / (len(par_affixes) + 1)
        if rel_common > threshold:
            i_sizes.append((rel_common, paradigm))
    result = []
    nth_score = 1.0
    for i, (score, paradigm) in enumerate(sorted(i_sizes, reverse=True)):
        if i == n:
            nth_score = score
        elif i > n and score < nth_score:
            break
        result.append(paradigm)
    return result


def freq_to_df(freq_list: str) -> pd.DataFrame:
    """Transforms frequency list with segmentations to dataframe."""
    df = pd.read_table(freq_list, names=["Word", "Segmented", "Frequency"])
    return df


def segment_freq_list(freq_list: str, seg_method, suffix: str) -> None:
    """Adds info about segmentation to frequency list and stores it."""
    outfile = open(f"{freq_list}.{suffix}", "w", encoding="utf-8")
    with open(freq_list, encoding="utf-8") as fl:
        for line in fl:
            print(f"{'='.join(seg_method(line.split()[0]))}\t{line.strip()}", file=outfile)
    outfile.close()


def get_suffixes(word: List[str], freq_list: str) -> Dict[str, Dict[str, float]]:
    """Lists through alphabetically sorted segmented frequency list and finds all words with prefixes
    obtained with segmentation method matching with some prefix of segmented word."""
    suffixes = {pref: dict() for pref in ["".join(word[:i + 1]) for i in range(len(word))]}
    fl = open(freq_list, encoding="utf-8")
    for line in fl:
        values = line.strip().split()
        if values[1][0] > word[0][0]:
            break
        if not line.startswith(word[0]):
            continue
        segments = values[0].strip("¦=▁").split("=")
        for segment in ["".join(segments[:i + 1]) for i in range(len(segments))]:
            if segment in suffixes.keys():
                suffixes[segment][values[1][len(segment):]] = float(values[2].strip())
    fl.close()
    return suffixes


def print_scores(scores: Dict[str, int]) -> None:
    """Prints paradigms in descending order (by their frequency scores)"""
    # TODO enhance
    for paradigm in sorted(scores, key=(lambda x: scores[x]), reverse=True):
        print(f"{paradigm}: {scores[paradigm]}")
    print()
