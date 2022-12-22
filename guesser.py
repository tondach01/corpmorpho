#!/usr/bin/env python3
import morph_database as md
import db_stats
from typing import List, Dict
from os import sep


def guess_paradigm(word: str, corpus: str, morph_db: md.MorphDatabase) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given word, bigger matched suffixes are prioritized"""
    score = dict()
    for i in range(len(word)):
        suffix = word[i:]
        for paradigm, freq in db_stats.suffix_frequencies(corpus, morph_db, suffix).items():
            if paradigm not in score.keys() or score[paradigm] < freq*len(suffix):
                score[paradigm] = freq*len(suffix)
    return score


def fit_suffices(word: str, suffices_db: md.SUFFICES_DATABASE) -> List[str]:
    fitting = []
    for suffix in suffices_db.keys():
        if matches_suffix(word, suffix):
            fitting.append(suffix)
    return fitting


def matches_suffix(word: str, suffix: str) -> bool:
    return word.endswith(suffix.split("|")[1])


def lemma(word: str, suffix: str) -> str:
    return word.removesuffix(suffix.split("|")[1]) + suffix.split("|")[0]


def main():
    desam = f"C:{sep}Users{sep}ondra{sep}Desktop{sep}MUNI{sep}PB106{sep}data{sep}desam_model{sep}desam"
    word = "pochybovačem"
    g = guess_paradigm(word, desam, md.MorphDatabase("current.dic", "current.par"))
    pass


if __name__ == "__main__":
    main()
