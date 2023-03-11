#!/usr/bin/env python3
import os
import db_stats as dbs
import morph_database as md
from typing import Dict, List, TextIO, Tuple


def guess_paradigm_from_corpus(segments: List[str], freq_list: str, morph_db: md.MorphDatabase, seg_method)\
        -> List[Tuple[float, str]]:
    """Guesses paradigm of given word based on occurrences of similar words in given corpus and their spread.
    Returns sorted list of tuples (paradigm, diff (lower the better))."""
    scores = dict()
    for prefix, frequencies in dbs.get_suffixes(segments, freq_list, seg_method).items():
        print(f"{prefix}:\n\t{frequencies}")  # debug
        for paradigm, diff in dbs.spread_scores(frequencies, morph_db).items():
            scores[paradigm] = min(scores.get(paradigm, 100.0), diff)
    result = [(diff, par) for par, diff in scores.items()]
    result.sort()
    return result


def guess_paradigm(segments: List[str], morph_db, frame, only_lemmas: bool = False) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given word and its sub-word segmentation,
    bigger matched suffixes are prioritized. Note: very slow for non-lemmatized word"""
    # TODO update
    pass


def get_segment_method(seg_tool: str):
    baseline = (lambda x: list(c for c in x))
    if "sentencepiece" in seg_tool:
        import sentencepiece as sp
        params = seg_tool.split("_")
        if len(params) != 3:
            return baseline
        sp.SentencePieceTrainer.train(f'--input=..{os.sep}desam{os.sep}prevert_desam'
                                      f' --model_prefix=m --model_type={params[1]} --vocab_size={params[2]}'
                                      f' --user_defined_symbols=<doc>,</doc>,<head>,</head>,<s>,</s>,<phr>,</phr>')
        m = sp.SentencePieceProcessor()
        m.load("m.model")
        return m.encode_as_pieces
    elif "morfessor" in seg_tool:
        import morfessor as mo
        params = seg_tool.split("_")
        max_epochs = 4
        if len(params) == 2 and params[1].isdigit():
            max_epochs = int(params[1])
        io = mo.MorfessorIO()
        train_data = list(io.read_corpus_file(f"..{os.sep}desam{os.sep}prevert_desam"))
        model = mo.BaselineModel()
        model.load_data(train_data, count_modifier=lambda x: 1)
        model.train_batch(algorithm="viterbi", max_epochs=max_epochs)
        return lambda x: model.viterbi_segment(x)[0]
    elif "hft" in seg_tool:
        import hftok.hftoks as hft
        vocab = hft.read_vocab(f"..{os.sep}hftok{os.sep}desam.vocab")
        return lambda x: hft.tokenize_string(x.lower(), vocab)
    return baseline


def main(source: TextIO, lemma: bool = False, seg_tool: str = ""):
    morph_db = md.MorphDatabase(f"..{os.sep}data{os.sep}current.dic", f"..{os.sep}data{os.sep}current.par")
    corpus = f"..{os.sep}desam{os.sep}desam"
    frame = dbs.lemmas_to_dataframe(corpus, morph_db)
    segment = get_segment_method(seg_tool)
    word = source.readline()
    word = word.strip()
    while word:
        scores = guess_paradigm(segment(word), morph_db, frame, lemma)
        dbs.print_scores(scores)
        word = source.readline()
        word = word.strip()


if __name__ == "__main__":
    import argparse
    import sys
    parser = argparse.ArgumentParser(description="Guesses the paradigm of given word")
    parser.add_argument("-l", "--lemma", action="store_true", help="word is given in its base form", default=False)
    parser.add_argument("-f", "--infile", help="file from which take the words for guessing (one per line), "
                                               "otherwise stdin is used")
    parser.add_argument("-s", "--use-segmenter", choices=["sentencepiece", "morfessor"], default="",
                        help="use segmentation for words (if not specified, not using any)")
    args = parser.parse_args()

    if not os.path.exists(f".{os.sep}temp"):
        os.mkdir(f".{os.sep}temp")
    os.chdir(f".{os.sep}temp")
    src = sys.stdin if args.infile is None else open(args.infile, encoding="utf-8")
    main(src, args.lemma, args.use_segmenter)
    if args.infile is None:
        src.close()
    os.chdir("..")
