#!/usr/bin/env python3
import morph_database as md
import db_stats
from typing import Dict, List


def guess_paradigm(word: str, corpus: str, morph_db: md.MorphDatabase, only_lemmas: bool = False) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given word, bigger matched suffixes are prioritized.
    Note: very slow for non-lemmatized word"""
    score = dict()
    search_func = db_stats.paradigm_frequencies if only_lemmas else db_stats.suffix_frequencies
    for i in range(len(word)):
        suffix = word[i:]
        for paradigm, freq in search_func(corpus, morph_db, suffix).items():
            if paradigm not in score.keys() or score[paradigm] < freq*len(suffix):
                score[paradigm] = freq*len(suffix)
    return score


def guess_paradigm_seg(word: str, corpus: str, morph_db: md.MorphDatabase, segments: List[str],
                       only_lemmas: bool = False) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given word and its sub-word segmentation,
    bigger matched suffixes are prioritized. Note: very slow for non-lemmatized word"""
    score = dict()
    search_func = db_stats.paradigm_frequencies if only_lemmas else db_stats.suffix_frequencies
    suffix = word
    for paradigm, freq in search_func(corpus, morph_db, suffix).items():
        if paradigm not in score.keys() or score[paradigm] < freq * len(suffix):
            score[paradigm] = freq * len(suffix)
    for i in range(len(segments)):
        suffix = suffix.removeprefix(segments[i])
        for paradigm, freq in search_func(corpus, morph_db, suffix).items():
            if paradigm not in score.keys() or score[paradigm] < freq * len(suffix):
                score[paradigm] = freq * len(suffix)
    return score


def guess_paradigm_from_lemma(lemma: str, corpus: str, morph_db: md.MorphDatabase) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given lemma, bigger matched suffixes are prioritized."""
    return guess_paradigm(lemma, corpus, morph_db, True)


def guess_paradigm_from_lemma_seg(lemma: str, corpus: str, morph_db: md.MorphDatabase,
                                  segments: List[str]) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given lemma and its segmentation,
    bigger matched suffixes are prioritized."""
    return guess_paradigm_seg(lemma, corpus, morph_db, segments, True)


def main():
    from time import time
    from os import sep
    start = time()
    desam = f"C:{sep}Users{sep}ondra{sep}Desktop{sep}MUNI{sep}PB106{sep}data{sep}desam_model{sep}desam"
    word = "pohrobkem"
    g = guess_paradigm(word, desam, md.MorphDatabase("current.dic", "current.par"))
    db_stats.print_score(g)
    print(f"finished in {round(time()-start, 3)}s")


if __name__ == "__main__":
    main()
