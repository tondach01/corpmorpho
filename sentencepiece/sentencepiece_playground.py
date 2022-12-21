#!/usr/bin/env python3
import sentencepiece as sp


def main():
    test_text = open("C:\\Users\\ondra\\Desktop\\MUNI\\PB106\\data\\ud-treebanks-v2.10\\czech\\UD_Czech-PUD\\cs_pud-ud-test.txt", "r", encoding="utf-8").read()
    des = open("C:\\Users\\ondra\\Desktop\\MUNI\\BP\\corpmorpho\\desam\\prevert_desam", "r", encoding="utf-8").read().split()
    f = open("stats", "w", encoding="utf-8")
    total_tokens = len(test_text.split())
    print(f"{total_tokens} tokens total", file=f)
    for model_type in ["bpe", "unigram"]:
        for vocab_size in range(1000, 21000, 1000):
            sp.SentencePieceTrainer.train('--input=C:\\Users\\ondra\\Desktop\\MUNI\\BP\\corpmorpho\\desam\\prevert_desam'
                                          f' --model_prefix=sentencepiece\\m --model_type={model_type} --vocab_size={vocab_size} '
                                          '--user_defined_symbols=<doc>,</doc>,<head>,</head>,<s>,</s>,<phr>,</phr>')
            m = sp.SentencePieceProcessor()
            m.load('sentencepiece\\m.model')
            pieces = len(m.encode_as_pieces(test_text))
            print(f"vocab_size={vocab_size}, model_type={model_type}: {pieces} pieces, {round(pieces/total_tokens, 3)} pieces per token", file=f)
    f.close()


if __name__ == "__main__":
    main()
