#!/usr/bin/env python3
import sys

import morph_database as md
import guesser as g
import db_stats as dbs
from os import sep, path, mkdir


def baseline_guess(corpus: str, morph_db: md.MorphDatabase) -> None:
    """Tries to guess paradigm for each entry in test_vocab without explicit segmentation."""
    return segmented_tree_guess(corpus, morph_db)


def segmented_tree_guess(freq_list: str, morph_db: md.MorphDatabase, segmenter: str = "", only_lemmas: bool = False,
                         debug: bool = False) -> None:
    if debug:
        log_file = sys.stdout
    else:
        log_file = open(f"logs{sep}log_{segmenter}_{'lemmas' if only_lemmas else 'forms'}", "w", encoding="utf-8")
    if only_lemmas:
        test_vocab = f"data{sep}current.dic.cleaned.utf8.sorted"
    else:
        test_vocab = f"data{sep}current.dic.cleaned.utf8.sorted.forms.filtered"
    segment = g.get_segment_method(segmenter)
    start_letter = "a"
    node = dbs.FreqTreeNode().feed(freq_list, "a")
    with open(test_vocab, encoding="utf-8") as test:
        for line in test:
            print(line.strip(), file=log_file)
            segments = dbs.uppercase_format("=".join(segment(line.strip().split(":")[0])).lower())
            if segments[0] != start_letter:
                start_letter = segments[0]
                node = dbs.FreqTreeNode().feed(freq_list, start_letter)
            data = line.strip().split(":")
            for form in morph_db.lemma_forms(data[-2], data[-1]):
                morph_db.paradigms[data[-1]]["spread"][
                    data[0][len(morph_db.word_root(data[-2], data[-1])):]] -= node[form]
            scores = g.tree_guess_paradigm_from_corpus(segments, node, morph_db, dbs.scoring_comm_square_spread,
                                                       only_lemmas)
            print("\t" + ", ".join([par for _, par in scores]), file=log_file)
            for form in morph_db.lemma_forms(data[-2], data[-1]):
                morph_db.paradigms[data[-1]]["spread"][
                    data[0][len(morph_db.word_root(data[-2], data[-1])):]] += node[form]
    if not debug:
        log_file.close()


def substitus_segmented_tree_guess(morph_db: md.MorphDatabase, only_lemmas: bool = False, debug: bool = False) -> None:
    freq_list = f"data{sep}cstenten17_mj2.freqlist.cleaned.sorted_alpha.substitus"
    if debug:
        log_file = sys.stdout
    else:
        log_file = open(f"logs{sep}log_substitus_{'lemmas' if only_lemmas else 'forms'}", "w", encoding="utf-8")
    if only_lemmas:
        test_vocab = f"data{sep}current.dic.cleaned.utf8.sorted.substitus"
    else:
        test_vocab = f"data{sep}current.dic.cleaned.utf8.sorted.forms.filtered.substitus"
    start_letter = "a"
    node = dbs.FreqTreeNode().feed(freq_list, "a")
    with open(test_vocab, encoding="utf-8") as test:
        for line in test:
            data = line.strip().split(maxsplit=1)
            print(data[1], file=log_file)
            segments = dbs.uppercase_format(data[0].lower())
            if segments[0] != start_letter:
                start_letter = segments[0]
                node = dbs.FreqTreeNode().feed(freq_list, start_letter)
            data = data[1].strip().split(":")
            for form in morph_db.lemma_forms(data[-2], data[-1]):
                morph_db.paradigms[data[-1]]["spread"][
                    data[0][len(morph_db.word_root(data[-2], data[-1])):]] -= node[form]
            scores = g.tree_guess_paradigm_from_corpus(segments, node, morph_db, dbs.scoring_comm_square_spread,
                                                       only_lemmas)
            print("\t" + ", ".join([par for _, par in scores]), file=log_file)
            for form in morph_db.lemma_forms(data[-2], data[-1]):
                morph_db.paradigms[data[-1]]["spread"][
                    data[0][len(morph_db.word_root(data[-2], data[-1])):]] += node[form]
    if not debug:
        log_file.close()


def main():
    from time import time
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--segmenter", default="")
    parser.add_argument("-d", "--debug", action="store_true", default=False)
    parser.add_argument("-l", "--lemmas", action="store_true", default=False)
    args = parser.parse_args()
    if not path.exists(f".{sep}temp"):
        mkdir(f".{sep}temp")
    start = time()
    morph_db = md.MorphDatabase(f"data{sep}current.dic", f"data{sep}current.par",
                                freq_list=f"data{sep}cstenten17_mj2.freqlist.cleaned.sorted_alpha.filtered")
    fl = f"data{sep}cstenten17_mj2.freqlist.cleaned.sorted_alpha.{args.segmenter if args.segmenter else 'baseline'}"
    if not path.exists(fl):
        print(fl, " file not found")
        return
    if args.segmenter == "substitus":
        substitus_segmented_tree_guess(morph_db, only_lemmas=args.lemmas, debug=args.debug)
    else:
        segmented_tree_guess(fl, morph_db, segmenter=args.segmenter, only_lemmas=args.lemmas, debug=args.debug)
    print(f"finished in {round(time() - start)}s")


if __name__ == "__main__":
    main()
