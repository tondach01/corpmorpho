#!/usr/bin/env python3
import sentencepiece as sp
import guesser


def main():
    from time import time
    from os import sep
    import morph_database as md
    from db_stats import print_score
    start = time()
    sp.SentencePieceTrainer.train('--input=C:\\Users\\ondra\\Desktop\\MUNI\\BP\\corpmorpho\\desam\\prevert_desam'
                                  ' --model_prefix=m --model_type=bpe --vocab_size=8000'
                                  '--user_defined_symbols=<doc>,</doc>,<head>,</head>,<s>,</s>,<phr>,</phr>')
    m = sp.SentencePieceProcessor()
    m.load('m.model')
    word = "pohrobkem"
    desam = f"..{sep}desam{sep}desam"
    g = guesser.guess_paradigm(word, desam, md.MorphDatabase(f"..{sep}current.dic", f"..{sep}current.par"),
                               m.encode_as_pieces(word))
    print_score(g)
    print(f"finished in {round(time() - start, 3)}s")


if __name__ == "__main__":
    main()
