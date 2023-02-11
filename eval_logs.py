#!/usr/bin/env python3
from typing import Tuple, List
from os import sep


def evaluate(log_file: str, top_n: int = 5) -> Tuple[List[int], int, int]:
    """Reads the given log file and evaluates its precision in 1 to <top_n> guesses.
    Returns (correct, all, total guesses)"""
    correct = [0 for _ in range(top_n)]
    entries, guess_count = 0, 0
    with open(log_file, encoding="utf-8") as log:
        line = log.readline()
        while line:
            entries += 1
            paradigm = line.strip().split(":")[1]
            guesses = log.readline().strip().split(", ")
            guess_count += len(guesses)
            for i in range(min(len(guesses), top_n) - 1, -1, -1):
                if paradigm not in guesses[:top_n]:
                    break
                correct[i] += 1
            line = log.readline()
    return correct, entries, guess_count


def full_eval(log_file: str, top_n: int = 5) -> None:
    correct, entries, guess_count = evaluate(log_file, top_n)
    for i, i_correct in enumerate(correct):
        print(f"top {i+1}: {i_correct}/{entries}, {round(guess_count/entries, 3)} guesses in average")


def eval_all_logs() -> None:
    from os import listdir
    for log_file in listdir("logs"):
        print(f"{log_file}:")
        full_eval(f"logs{sep}{log_file}")


def main():
    from time import time
    start = time()
    eval_all_logs()
    print(f"finished in {round(time() - start)}s")


if __name__ == "__main__":
    main()
