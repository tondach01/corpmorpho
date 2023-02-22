#!/usr/bin/env python3
import os
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


def main(infile: str = None, lemmatized: bool = False, segment: str = ""):
    # TODO
    import sys
    if infile is None:
        source = sys.stdin
    elif not os.path.exists(infile):
        print(f"File {infile} not found, using stdin", file=sys.stderr)
        source = sys.stdin
    else:
        source = open(infile, "r")
    scores = guess_paradigm
    print(infile, lemmatized)
    pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Guesses the paradigm of given word")
    parser.add_argument("-l", "--lemma", action="store_true", help="word is given in its base form", default=False)
    parser.add_argument("-f", "--infile", help="file from which take the words for guessing (one per line), "
                                               "otherwise stdin is used")
    parser.add_argument("-s", "--use-segmenter", choices=["sentencepiece", "morfessor"], default="",
                        help="use segmentation for words (if not specified, not using any)")
    args = parser.parse_args()

    main(args.infile, args.lemma, args.use_segmenter)
