#!/usr/bin/env python3
import os
import sys

import morph_database as md
import guesser as g
import db_stats as dbs
from os import sep
from typing import TextIO


def baseline_guess(test_vocab: str, corpus: TextIO, morph_db: md.MorphDatabase) -> None:
    """Tries to guess paradigm for each lemma in test_vocab and returns its success rate (all, correct)"""
    return segmented_guess(test_vocab, corpus, morph_db)


def segmented_guess(test_vocab: str, corpus: TextIO, morph_db: md.MorphDatabase,
                    segmenter: str = "", debug: bool = False) -> None:
    """Tries to guess paradigm for each lemma in test_vocab given its segmentation (if given segmenter)."""
    if debug:
        log_file = sys.stdout
    else:
        log_file = open(f"..{sep}logs{sep}log_{segmenter}", "w", encoding="utf-8")
    frame = dbs.lemmas_to_dataframe(corpus, morph_db)
    segment = g.get_segment_method(segmenter)
    with open(test_vocab, encoding="windows-1250") as test:
        for line in test:
            print(line.strip(), file=log_file)
            segments = segment(line.strip().split(":")[0])
            score = g.guess_paradigm_from_lemma(segments, frame)
            paradigms = list(sorted(score, key=(lambda x: score[x]), reverse=True))
            print("\t" + ", ".join(paradigms), file=log_file)
    if not debug:
        log_file.close()


def main():
    from time import time
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--segmenter", default="")
    parser.add_argument("-d", "--debug", action="store_true", default=False)
    args = parser.parse_args()
    if not os.path.exists(f".{sep}temp"):
        os.mkdir(f".{sep}temp")
    os.chdir(f".{sep}temp")
    start = time()
    train, test = md.MorphDatabase(f"..{sep}data{sep}current.dic", f"..{sep}data{sep}current.par")\
        .split_vocabulary()
    train_md = md.MorphDatabase(train, f"..{sep}data{sep}current.par")
    corpus = open(f"..{sep}desam{sep}desam", encoding="utf-8")
    segmented_guess(test, corpus, train_md, segmenter=args.segmenter, debug=args.debug)
    corpus.close()
    os.chdir("..")
    print(f"finished in {round(time() - start)}s")


if __name__ == "__main__":
    main()
