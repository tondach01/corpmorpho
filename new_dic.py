#!/usr/bin/env python3
import morph_database as md
import guesser as g
import db_stats as dbs
from typing import List
import re

DIC_FILE = "data/current.dic"
PAR_FILE = "data/current.par"
SEG_TOOL = "character"
FREQ_LIST_FILTERED = "data/cstenten17_mj2.freqlist.cleaned.sorted_alpha.filtered"


def line_to_include(data: List[str], morph_db: md.MorphDatabase) -> bool:
    return int(data[2]) > 100 and re.search("(.)\\1\\1", data[1]) is None and not morph_db.form_present(data[1])


def main():
    morph_db = md.MorphDatabase(DIC_FILE, PAR_FILE, freq_list=FREQ_LIST_FILTERED)
    outfile = open("new.dic", "w", encoding="utf-8")
    start_letter = ""
    with open(f"data/cstenten17_mj2.freqlist.cleaned.sorted_alpha.lowdrop.character", encoding="utf-8") as fl:
        for line in fl:
            data = line.strip().split()
            if not line_to_include(data, morph_db):
                continue
            segments = dbs.uppercase_format(data[0])
            if segments[0] != start_letter:
                start_letter = segments[0]
                node = dbs.FreqTreeNode().feed(f"data/cstenten17_mj2.freqlist.cleaned.sorted_alpha.lowdrop.character",
                                               start_letter)
            scores = g.tree_guess_paradigm_from_corpus(segments, node, morph_db, dbs.scoring_comm_square_spread_suf,
                                                       only_lemmas=False)
            if scores[0][0] > 5 and morph_db.lemmatize(segments.lower(), scores[0][1]) == segments.lower():
                dbs.print_scores(data[1], {par: score for score, par in scores[:min(5, len(scores))]}, outfile=outfile)
    outfile.close()


if __name__ == "__main__":
    main()
