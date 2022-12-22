#!/usr/bin/env python3
import morph_database as md
import db_stats
from typing import Dict
from os import sep


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


def guess_paradigm_from_lemma(lemma: str, corpus: str, morph_db: md.MorphDatabase) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given lemma, bigger matched suffixes are prioritized."""
    return guess_paradigm(lemma, corpus, morph_db, True)


def print_score(score: Dict[str, int]) -> None:
    """Prints paradigms in descending order (by their values in score)"""
    for paradigm in sorted(score, key=(lambda x: score[x]), reverse=True):
        print(f"{paradigm}: {score[paradigm]}")


def main():
    desam = f"C:{sep}Users{sep}ondra{sep}Desktop{sep}MUNI{sep}PB106{sep}data{sep}desam_model{sep}desam"
    word = "pochybovač"
    g = guess_paradigm_from_lemma(word, desam, md.MorphDatabase("current.dic", "current.par"))
    print_score(g)


if __name__ == "__main__":
    main()
