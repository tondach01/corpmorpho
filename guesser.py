#!/usr/bin/env python3
import morph_database as md
import db_stats
from typing import Dict, List


def guess_paradigm(word: str, corpus: str, morph_db: md.MorphDatabase,
                   only_lemmas: bool = False) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given word, bigger matched suffixes are prioritized.
    Note: very slow for non-lemmatized word"""
    return guess_paradigm_seg(corpus, morph_db, [word[i] for i in range(len(word))], only_lemmas)


def guess_paradigm_seg(corpus: str, morph_db: md.MorphDatabase, segments: List[str],
                       only_lemmas: bool = False) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given word and its sub-word segmentation,
    bigger matched suffixes are prioritized. Note: very slow for non-lemmatized word"""
    search_func = db_stats.lemma_scores if only_lemmas else db_stats.suffix_frequencies
    return search_func(corpus, morph_db, ["".join(segments[-i:]) for i in range(1, len(segments) + 1)])


def guess_paradigm_from_lemma(lemma: str, corpus: str, morph_db: md.MorphDatabase) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given lemma, bigger matched suffixes are prioritized."""
    return guess_paradigm(lemma, corpus, morph_db, only_lemmas=True)


def guess_paradigm_from_lemma_seg(corpus: str, morph_db: md.MorphDatabase, segments: List[str]) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given lemma and its segmentation,
    bigger matched suffixes are prioritized."""
    return guess_paradigm_seg(corpus, morph_db, segments, only_lemmas=True)


def main():
    from time import time
    from os import sep
    start = time()
    desam = f"desam{sep}desam"
    word = "pohrobkem"
    g = guess_paradigm(word, desam, md.MorphDatabase("data/current.dic", "data/current.par"))
    db_stats.print_score(g)
    print(f"finished in {round(time()-start, 3)}s")


if __name__ == "__main__":
    main()
