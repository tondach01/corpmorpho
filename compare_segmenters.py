#!/usr/bin/env python3
import os
import sys

import morph_database as md
import guesser as g
import db_stats as dbs
from os import sep


def baseline_guess(test_vocab: str, corpus: str, morph_db: md.MorphDatabase) -> None:
    """Tries to guess paradigm for each lemma in test_vocab and returns its success rate (all, correct)"""
    return segmented_guess(test_vocab, corpus, morph_db)


def get_segment_method(segmenter: str):
    baseline = (lambda x: list(c for c in x))
    if "sentencepiece" in segmenter:
        import sentencepiece as sp
        params = segmenter.split("_")
        if len(params) != 3:
            return baseline
        sp.SentencePieceTrainer.train(f'--input=..{sep}desam{sep}prevert_desam'
                                      f' --model_prefix=m --model_type={params[1]} --vocab_size={params[2]}'
                                      f' --user_defined_symbols=<doc>,</doc>,<head>,</head>,<s>,</s>,<phr>,</phr>')
        m = sp.SentencePieceProcessor()
        m.load("sp.model")
        return m.encode_as_pieces
    elif "morfessor" in segmenter:
        import morfessor as mo
        params = segmenter.split("_")
        max_epochs = 4
        if len(params) == 2 and params[1].isdigit():
            max_epochs = int(params[1])
        io = mo.MorfessorIO()
        train_data = list(io.read_corpus_file(f"..{sep}desam{sep}prevert_desam"))
        model = mo.BaselineModel()
        model.load_data(train_data, count_modifier=lambda x: 1)
        model.train_batch(algorithm="viterbi", max_epochs=max_epochs)
        return lambda x: model.viterbi_segment(x)[0]
    return baseline


def segmented_guess(test_vocab: str, corpus: str, morph_db: md.MorphDatabase,
                    segmenter: str = "", debug: bool = False) -> None:
    """Tries to guess paradigm for each lemma in test_vocab given its segmentation (if given segmenter)."""
    if debug:
        log_file = sys.stdout
    else:
        log_file = open(f"..{sep}logs{sep}log_{segmenter}", "w", encoding="utf-8")
    frame = dbs.lemmas_to_dataframe(corpus, morph_db)
    segment = get_segment_method(segmenter)
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
    from sys import argv
    if not os.path.exists(f".{sep}temp"):
        os.mkdir(f".{sep}temp")
    os.chdir(f".{sep}temp")
    start = time()
    debug = False
    if "-d" in argv:
        debug = True
        argv.remove("-d")
    seg = "" if len(argv) < 2 else argv[1]
    train, test = md.MorphDatabase(f"..{sep}data{sep}current.dic", f"..{sep}data{sep}current.par")\
        .split_vocabulary()
    train_md = md.MorphDatabase(train, f"..{sep}data{sep}current.par")
    segmented_guess(test, f"..{sep}desam{sep}desam", train_md, segmenter=seg, debug=debug)
    print(f"finished in {round(time() - start)}s")


if __name__ == "__main__":
    main()
