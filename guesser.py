#!/usr/bin/env python3
import db_stats
from typing import Dict, List


def guess_paradigm(segments: List[str], morph_db, frame, only_lemmas: bool = False) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given word and its sub-word segmentation,
    bigger matched suffixes are prioritized. Note: very slow for non-lemmatized word"""
    search_func = db_stats.pandas_lemma_scores
    # TODO function for non-lemmatized
    return search_func(["".join(segments[-i:]) for i in range(1, len(segments) + 1)], frame)


def guess_paradigm_from_lemma(segments: List[str], frame) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given lemma and its segmentation,
    bigger matched suffixes are prioritized."""
    return guess_paradigm(segments, None, frame, only_lemmas=True)
