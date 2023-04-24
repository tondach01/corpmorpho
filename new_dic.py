#!/usr/bin/env python3
import morph_database as md
import guesser as g
import db_stats as dbs
from typing import List

DIC_FILE = "data/current.dic"
PAR_FILE = "data/current.par"
FREQ_LIST = "data/cstenten17_mj2.freqlist.cleaned.sorted_alpha"
FREQ_LIST_FILTERED = "data/cstenten17_mj2.freqlist.cleaned.sorted_alpha.filtered"
SEG_TOOL = "baseline"


def line_to_include(data: List[str], morph_db: md.MorphDatabase) -> bool:
    return int(data[1]) > 1 and not morph_db.form_present(data[0])


def main():
    morph_db = md.MorphDatabase(DIC_FILE, PAR_FILE, freq_list=FREQ_LIST_FILTERED)
    seg_method = g.get_segment_method(SEG_TOOL)
    node = dbs.FreqTreeNode().feed(FREQ_LIST, "a")
    start_letter = "a"
    with open(FREQ_LIST, encoding="utf-8") as fl:
        for line in fl:
            data = line.strip().split()
            if not line_to_include(data, morph_db):
                continue
            segments = dbs.uppercase_format("=".join(seg_method(data[0])))
            if segments[0] != start_letter:
                start_letter = segments[0]
                node = dbs.FreqTreeNode().feed(FREQ_LIST, start_letter)
            scores = g.tree_guess_paradigm_from_corpus(segments, node, morph_db, only_lemmas=True)
            dbs.print_scores(data[0], {par: score for score, par in scores[:min(5, len(scores))]})


if __name__ == "__main__":
    main()
