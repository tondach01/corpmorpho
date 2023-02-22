#!/usr/bin/env python3
import os
import db_stats as dbs
import morph_database as md
from typing import Dict, List, TextIO


def guess_paradigm(segments: List[str], morph_db, frame, only_lemmas: bool = False) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given word and its sub-word segmentation,
    bigger matched suffixes are prioritized. Note: very slow for non-lemmatized word"""
    search_func = dbs.lemma_scores
    # TODO function for non-lemmatized
    return search_func(["".join(segments[-i:]) for i in range(1, len(segments) + 1)], frame)


def guess_paradigm_from_lemma(segments: List[str], frame) -> Dict[str, int]:
    """Guesses the probabilities of paradigms for given lemma and its segmentation,
    bigger matched suffixes are prioritized."""
    return guess_paradigm(segments, None, frame, only_lemmas=True)


def get_segment_method(segmenter: str):
    baseline = (lambda x: list(c for c in x))
    if "sentencepiece" in segmenter:
        import sentencepiece as sp
        params = segmenter.split("_")
        if len(params) != 3:
            return baseline
        sp.SentencePieceTrainer.train(f'--input=..{os.sep}desam{os.sep}prevert_desam'
                                      f' --model_prefix=m --model_type={params[1]} --vocab_size={params[2]}'
                                      f' --user_defined_symbols=<doc>,</doc>,<head>,</head>,<s>,</s>,<phr>,</phr>')
        m = sp.SentencePieceProcessor()
        m.load("m.model")
        return m.encode_as_pieces
    elif "morfessor" in segmenter:
        import morfessor as mo
        params = segmenter.split("_")
        max_epochs = 4
        if len(params) == 2 and params[1].isdigit():
            max_epochs = int(params[1])
        io = mo.MorfessorIO()
        train_data = list(io.read_corpus_file(f"..{os.sep}desam{os.sep}prevert_desam"))
        model = mo.BaselineModel()
        model.load_data(train_data, count_modifier=lambda x: 1)
        model.train_batch(algorithm="viterbi", max_epochs=max_epochs)
        return lambda x: model.viterbi_segment(x)[0]
    return baseline


def main(source: TextIO, lemmatized: bool = False, segmenter: str = ""):
    morph_db = md.MorphDatabase(f"..{os.sep}data{os.sep}current.dic", f"..{os.sep}data{os.sep}current.par")
    corpus = open(f"..{os.sep}desam{os.sep}desam", encoding="utf-8")
    frame = dbs.lemmas_to_dataframe(corpus, morph_db)
    corpus.close()
    segment = get_segment_method(segmenter)
    word = source.readline()
    word = word.strip()
    while word:
        scores = guess_paradigm(segment(word), morph_db, frame, lemmatized)
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
    source = sys.stdin if args.infile is None else open(args.infile, encoding="utf-8")
    main(source, args.lemma, args.use_segmenter)
    if args.infile is None:
        source.close()
    os.chdir("..")
