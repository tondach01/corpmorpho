#!/usr/bin/env python3


def main():
    from os import sep
    from sentencepiece import SentencePieceTrainer as Trainer
    for model_type in ["bpe", "unigram"]:
        for vocab_size in range(1000, 16001, 1000):
            Trainer.train(f'--input=..{sep}desam{sep}prevert_desam'
                          f' --model_prefix={model_type + "_" + str(vocab_size)}'
                          f' --model_type={model_type} --vocab_size={vocab_size}'
                          ' --user_defined_symbols=<doc>,</doc>,<head>,</head>,<s>,</s>,<phr>,</phr>')


if __name__ == "__main__":
    main()
