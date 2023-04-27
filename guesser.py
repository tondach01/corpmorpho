#!/usr/bin/env python3
import os
import db_stats as dbs
import morph_database as md
from typing import List, TextIO, Tuple


def tree_guess_paradigm_from_corpus(segments: str, tree: dbs.FreqTreeNode, morph_db: md.MorphDatabase, scoring,
                                    only_lemmas: bool = False) -> List[Tuple[float, str]]:
    """Guesses paradigm of given word based on occurrences of similar words in given corpus and their spread.
    Returns sorted list of tuples (paradigm, score (greater the better))."""
    result = [(score, par) for par, score in dbs.tree_spread_scores(
        segments,
        tree,
        morph_db,
        scoring=scoring,
        only_lemmas=only_lemmas
    ).items()
              ]
    result.sort(reverse=True)
    return result


def get_segment_method(seg_tool: str):
    character = (lambda x: list(c for c in x))
    if "sentencepiece" in seg_tool:
        import sentencepiece as sp
        params = seg_tool.split("_")
        if len(params) != 3:
            return character
        if not os.path.exists(f'temp{os.sep}{params[1]}_{params[2]}.model'):
            sp.SentencePieceTrainer.train(f'--input=desam{os.sep}prevert_desam'
                                          f' --model_prefix=temp{os.sep}{params[1]}_{params[2]}'
                                          f' --model_type={params[1]} --vocab_size={params[2]}'
                                          f' --user_defined_symbols=<doc>,</doc>,<head>,</head>,<s>,</s>,<phr>,</phr>')
        m = sp.SentencePieceProcessor()
        m.load(f"temp{os.sep}{params[1]}_{params[2]}.model")
        return m.encode_as_pieces
    elif "morfessor" in seg_tool:
        import morfessor as mo
        params = seg_tool.split("_")
        max_epochs = 4
        if len(params) == 2 and params[1].isdigit():
            max_epochs = int(params[1])
        io = mo.MorfessorIO()
        train_data = list(io.read_corpus_file(f"desam{os.sep}prevert_desam"))
        model = mo.BaselineModel()
        model.load_data(train_data, count_modifier=lambda x: 1)
        model.train_batch(algorithm="viterbi", max_epochs=max_epochs)
        return lambda x: model.viterbi_segment(x, maxlen=5)[0]
    elif "hft" in seg_tool:
        import hftok.hftoks as hft
        vocab = hft.read_vocab(f"hftok{os.sep}desam.vocab")
        return lambda x: hft.tokenize_string(x.lower(), vocab)
    return character


def main(source: TextIO, only_lemmas: bool = False, seg_tool: str = ""):
    fl = "data/cstenten17_mj2.freqlist.cleaned.sorted_alpha"
    morph_db = md.MorphDatabase(f"data{os.sep}current.dic", f"data{os.sep}current.par",
                                freq_list=f"{fl}.filtered")
    segment = get_segment_method(seg_tool)
    fl = f"data{os.sep}cstenten17_mj2.freqlist.cleaned.sorted_alpha.{seg_tool if seg_tool else 'character'}"
    if not os.path.exists(fl):
        print(fl, ": file not found")
        return
    start_letter = "a"
    node = dbs.FreqTreeNode().feed(fl, "a")
    for line in source:
        segments = dbs.uppercase_format("=".join(segment(line.strip().lower())))
        if segments[0] != start_letter:
            start_letter = segments[0]
            node = dbs.FreqTreeNode().feed(fl, start_letter)
        scores = tree_guess_paradigm_from_corpus(segments, node, morph_db, only_lemmas)
        dbs.print_scores(line.strip(), {par: score for score, par in scores[:min(5, len(scores))]})


if __name__ == "__main__":
    import argparse
    import sys
    parser = argparse.ArgumentParser(description="Guesses the paradigm of given word")
    parser.add_argument("-l", "--lemma", action="store_true", help="word is given in its base form", default=False)
    parser.add_argument("-f", "--infile", help="file from which take the words for guessing (one per line), "
                                               "otherwise stdin is used")
    parser.add_argument("-s", "--use-segmenter", default="character",
                        help="use segmentation for words (if not specified, not using any)")
    args = parser.parse_args()

    if not os.path.exists(f".{os.sep}temp"):
        os.mkdir(f".{os.sep}temp")
    src = sys.stdin if args.infile is None else open(args.infile, encoding="utf-8")
    main(src, args.lemma, args.use_segmenter)
    if args.infile is None:
        src.close()
