#!/usr/bin/env python3
import morph_database as md
import guesser as g
from typing import Tuple
from os import sep


def baseline_guess(test_vocab: str, corpus: str, morph_db: md.MorphDatabase) -> None:
    """Tries to guess paradigm for each lemma in test_vocab and returns its success rate (all, correct)"""
    return segmented_guess(test_vocab, corpus, morph_db)


def segmented_guess(test_vocab: str, corpus: str, morph_db: md.MorphDatabase, segmenter: str = "") -> None:
    """Tries to guess paradigm for each lemma in test_vocab given its segmentation (if given segmenter)."""
    log_file = open(f"logs{sep}log_{segmenter}", "w", encoding="utf-8")
    segment = (lambda x: list(x[i] for i in range(len(x))))
    if "sentencepiece" in segmenter:
        import sentencepiece as sp
        m = sp.SentencePieceProcessor()
        m.load(f"sentencepiece{sep}{segmenter[14:]}.model")
        segment = m.encode_as_pieces
    elif "morfessor" in segmenter:
        import morfessor
        m = morfessor.MorfessorIO().read_binary_model_file(f"morfessor{sep}morfessor_model")
        segment = (lambda x: m.viterbi_segment(x)[0])
    with open(test_vocab, encoding="windows-1250") as test:
        for line in test:
            print(line.strip(), file=log_file)
            segments = segment(line.strip().split(":")[0])
            score = g.guess_paradigm_from_lemma_seg(corpus, morph_db, segments)
            paradigms = list(sorted(score, key=(lambda x: score[x]), reverse=True))
            print("\t" + ", ".join(paradigms), file=log_file)
    log_file.close()


def main():
    from time import time
    from sys import argv
    start = time()
    seg = "" if len(argv) < 2 else argv[1]
    train, test = md.MorphDatabase("current.dic", "current.par").split_vocabulary()
    train_md = md.MorphDatabase(train, "current.par")
    segmented_guess(test, f"desam{sep}desam", train_md, segmenter=seg)
    print(f"finished in {round(time() - start)}s")


if __name__ == "__main__":
    main()
