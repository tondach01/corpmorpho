#!/usr/bin/env python3
import morph_database as md
import db_stats
from typing import Dict, List


def guess_paradigm(word: str, corpus: str, morph_db: md.MorphDatabase,
                   only_lemmas: bool = False, cache=None) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given word, bigger matched suffixes are prioritized.
    Note: very slow for non-lemmatized word"""
    return guess_paradigm_seg(word, corpus, morph_db, [word[i] for i in range(len(word))], only_lemmas, cache)


def guess_paradigm_seg(word: str, corpus: str, morph_db: md.MorphDatabase, segments: List[str],
                       only_lemmas: bool = False, cache=None) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given word and its sub-word segmentation,
    bigger matched suffixes are prioritized. Note: very slow for non-lemmatized word"""
    score = dict()
    search_func = db_stats.paradigm_frequencies if only_lemmas else db_stats.suffix_frequencies
    suffix = word
    if only_lemmas and cache is not None and suffix in cache.keys():
        for paradigm, freq in cache[suffix].items():
            score[paradigm] = freq
    else:
        for paradigm, freq in search_func(corpus, morph_db, suffix).items():
            score[paradigm] = max(freq * len(suffix), score.get(paradigm, 0))
    for i in range(len(segments) - 1):
        suffix = suffix[len(segments[i].strip("▁")):]
        if only_lemmas and cache is not None and suffix in cache.keys():
            for paradigm, freq in cache[suffix].items():
                score[paradigm] = max(freq, score.get(paradigm, 0))
            continue
        for paradigm, freq in search_func(corpus, morph_db, suffix).items():
            score[paradigm] = max(freq * len(suffix), score.get(paradigm, 0))
    return score


def guess_paradigm_from_lemma(lemma: str, corpus: str, morph_db: md.MorphDatabase, cache=None) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given lemma, bigger matched suffixes are prioritized."""
    return guess_paradigm(lemma, corpus, morph_db, only_lemmas=True, cache=cache)


def guess_paradigm_from_lemma_seg(lemma: str, corpus: str, morph_db: md.MorphDatabase,
                                  segments: List[str], cache=None) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given lemma and its segmentation,
    bigger matched suffixes are prioritized."""
    return guess_paradigm_seg(lemma, corpus, morph_db, segments, only_lemmas=True, cache=cache)


def main():
    from time import time
    from os import sep
    start = time()
    desam = f"desam{sep}desam"
    word = "pohrobkem"
    g = guess_paradigm(word, desam, md.MorphDatabase("current.dic", "current.par"))
    db_stats.print_score(g)
    print(f"finished in {round(time()-start, 3)}s")


if __name__ == "__main__":
    main()
