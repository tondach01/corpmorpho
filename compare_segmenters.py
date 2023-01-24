#!/usr/bin/env python3
import db_stats
import morph_database as md
import guesser as g
from typing import Set, Dict, Tuple
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


def scores(common: Set[str], corpus: str, morph_db: md.MorphDatabase) -> Dict[str, Dict[str, int]]:
    """Precomputes frequency scores for given set of common suffixes"""
    score = dict()
    for suffix in common:
        score[suffix] = db_stats.paradigm_frequencies(corpus, morph_db, suffix)
    for suffix, paradigms in score.items():
        for paradigm, freq in paradigms.items():
            score[suffix][paradigm] = freq * len(suffix)
    return score


def evaluate(log_file: str, top_n: int = 1) -> Tuple[int, int, int]:
    """Reads the given log file and evaluates its success rate in <top_n> guesses.
    Returns (correct, all, total guesses)"""
    correct, entries, guess_count = 0, 0, 0
    with open(log_file, encoding="utf-16") as log:
        line = log.readline()
        while line:
            entries += 1
            paradigm = line.strip().split(":")[1]
            guesses = log.readline().strip().split(", ")
            guess_count += len(guesses)
            if len(guesses) < top_n and paradigm in guesses:
                correct += 1
            elif len(guesses) >= top_n and paradigm in guesses[:top_n]:
                correct += 1
            line = log.readline()
    return correct, entries, guess_count


def full_eval(log_file: str) -> None:
    for i in range(5):
        correct, entries, guess_count = evaluate(log_file, i+1)
        print(f"top {i+1}: {correct}/{entries}, {round(guess_count/entries, 3)} guesses in average")


def eval_all_logs() -> None:
    from os import listdir
    for log_file in listdir("logs"):
        print(f"{log_file}:")
        full_eval(f"logs{sep}{log_file}")


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
    # eval_all_logs()
