#!/usr/bin/env python3
# This script splits the tagged data to train/tune/test files in 7/1/2 ratio, the only format requirement is
# one token per line
# Ondra Metelka
import sys
import os


def main():
    args = sys.argv
    args.pop(0)
    if not args:
        print("use: train_tune_test.py tagged_data")
    name = args[0].split(os.sep)[-1]
    with open(args[0], "r", encoding="utf-8") as f:
        train = open(f"train_{name}", "w", encoding="utf-8")
        tune = open(f"tune_{name}", "w", encoding="utf-8")
        test = open(f"test_{name}", "w", encoding="utf-8")
        index = 0
        for line in f:
            if index % 10 == 0:
                tune.write(line)
            elif index % 10 < 3:
                test.write(line)
            else:
                train.write(line)
            index += 1
        train.close()
        tune.close()
        test.close()


if __name__ == "__main__":
    main()
