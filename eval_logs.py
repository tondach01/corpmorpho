#!/usr/bin/env python3
from typing import Tuple, List
from os import listdir
from sys import stdout
import morph_database as md


def top_n_check(log_file: str, top_n: int = 1) -> Tuple[List[int], int, int]:
    """Reads the given log file and evaluates its precision in 1 to <top_n> guesses.
    Returns (correct, all, total guesses)"""
    correct = [0 for _ in range(top_n)]
    entries, guess_count = 0, 0
    with open(log_file, encoding="utf-8") as log:
        line = log.readline()
        while line:
            entries += 1
            paradigm = line.strip().split(":")[-1]
            guesses = log.readline().strip().split(", ")
            if "" in guesses:
                guesses.remove("")
            guesses += [max(top_n - len(guesses), 0) * "_"]
            guess_count += len(guesses)
            for i in range(top_n - 1, -1, -1):
                if paradigm not in guesses[:i+1]:
                    break
                correct[i] += 1
            line = log.readline()
    return correct, entries, guess_count


def full_eval(fltr: str = "", top_n: int = 1, threshold: int = 5, debug: bool = False) -> None:
    morph_db = md.MorphDatabase("data/current.dic", "data/current.par")
    outfile = stdout
    if not debug:
        import datetime
        outfile = open(f"results/{datetime.date.today()}_all.txt", "w", encoding="utf-8")
    for log_file in listdir("logs"):
        if fltr not in log_file:
            continue
        correct, entries, guess_count = top_n_check(f"logs/{log_file}", top_n)
        print(f"{log_file}: {entries} examples, {round(guess_count, 3)} guesses at average", file=outfile)
        for i in range(len(correct)):
            print(f"\tsame_paradigms_top_{i + 1}: {correct[i]} (precision {round(correct[i] / entries, 3)})",
                  file=outfile)
        for crit in ["same_affixes", "common_forms", "common_tags", "same_lemma"]:
            correct, entries, guess_count = md_check(f"logs/{log_file}", crit, morph_db, threshold)
            print(f"\t{crit}{f'_{threshold}' if crit == 'common_forms' else ''}: {correct} "
                  f"(precision {round(correct / entries, 3)})", file=outfile)
    if not debug:
        outfile.close()


def classic_eval(fltr: str = "", top_n: int = 1, debug: bool = False) -> None:
    outfile = stdout
    if not debug:
        import datetime
        outfile = open(f"results/{datetime.date.today()}_top_n.txt", "w", encoding="utf-8")
    for log_file in listdir("logs"):
        if fltr not in log_file:
            continue
        correct, entries, guess_count = top_n_check(log_file, top_n)
        print(f"{log_file}: {entries} examples, {round(guess_count, 3)} guesses at average", file=outfile)
        for i in range(len(correct)):
            print(f"\ttop_{i + 1}: {correct[i]} (precision {round(correct[i] / entries, 3)})", file=outfile)
    if not debug:
        outfile.close()


def md_eval(crit: str, fltr: str = "", threshold: int = 5, debug: bool = False) -> None:
    morph_db = md.MorphDatabase("data/current.dic", "data/current.par")
    outfile = stdout
    if not debug:
        import datetime
        outfile = open(f"results/{datetime.date.today()}_{crit}.txt", "w", encoding="utf-8")
    for log_file in listdir("logs"):
        if fltr not in log_file:
            continue
        correct, entries, guess_count = md_check(f"logs/{log_file}", crit, morph_db, threshold)
        print(f"{log_file}: {correct}/{entries}, {round(guess_count/entries, 3)} guesses in average", file=outfile)
    if not debug:
        outfile.close()


def md_check(log_file: str, crit: str, morph_db, threshold: int = 5) -> Tuple[int, int, int]:
    correct = 0
    entries, guess_count = 0, 0
    with open(log_file, encoding="utf-8") as log:
        line = log.readline()
        while line:
            entries += 1
            paradigm = line.strip().split(":")[-1]
            form = line.strip().split(":")[0]
            guesses = log.readline().strip().split(", ")
            if "" in guesses:
                guesses.remove("")
            guess_count += len(guesses)
            if crit == "same_lemma":
                if guesses and morph_db.same_lemma(form, guesses[0], paradigm):
                    correct += 1
            elif guesses and morph_db.same_paradigms(guesses[0], paradigm, crit, threshold=threshold):
                correct += 1
            line = log.readline()
    return correct, entries, guess_count


def main():
    from time import time
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate logs in ./logs/ directory")
    parser.add_argument("-c", "--criterion", choices=["all", "same_paradigms", "same_affixes", "common_forms",
                                                      "common_tags", "same_lemma"],
                        help="how to evaluate", default="all")
    parser.add_argument("-f", "--filter", help="only log names containing this string will be evaluated", default="")
    parser.add_argument("-t", "--threshold", type=int, help="threshold for common_forms", default=5)
    parser.add_argument("-d", "--debug", action="store_true", help="print to standard output", default=False)
    parser.add_argument("-n", "--top_n", type=int, help="evaluate n best guesses", default=5)
    args = parser.parse_args()
    start = time()
    if args.criterion == "same_paradigms":
        classic_eval(args.filter, args.top_n, args.debug)
    elif args.criterion == "all":
        full_eval(args.filter, args.top_n, args.threshold, args.debug)
    else:
        md_eval(args.criterion, args.filter, args.threshold, args.debug)
    print(f"finished in {round(time() - start)}s")


if __name__ == "__main__":
    main()
