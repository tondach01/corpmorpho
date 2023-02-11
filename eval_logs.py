#!/usr/bin/env python3
from typing import Tuple, List, Dict, Any
from os import sep, listdir
import matplotlib as mpl
import matplotlib.pyplot as plt


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


def full_eval(log_file: str, top_n: int = 5) -> None:
    correct, entries, guess_count = evaluate(log_file, top_n)
    for i, i_correct in enumerate(correct):
        print(f"top {i+1}: {i_correct}/{entries}, {round(guess_count/entries, 3)} guesses in average")


def eval_all_logs() -> None:
    for log_file in listdir("logs"):
        print(f"{log_file}:")
        full_eval(f"logs{sep}{log_file}")


def plot_results():
    pass


def newest_res_file() -> str:
    from os import path
    return "results" + sep + max(listdir("results"), key=(lambda x: path.getctime(f"results{sep}{x}")))


def load_results() -> Dict[Tuple[str, str, int], Any]:
    loaded = dict()
    with open(newest_res_file(), encoding="utf-16le") as res:
        for line in res:
            if "log" in line:
                names = line.strip().split("_")
                tool, model, vocab_size = names[1], "" if len(names) < 3 else names[2], 0 if len(names) < 4 else names[3]
                loaded[(tool, model, vocab_size)] = dict(test_size=0, average_guesses=0.0, precisions=[])
            elif line.startswith("top"):
                data = line.split(" ")
                entry = loaded[(tool, model, vocab_size)]
                entry["precisions"].append(int(data[2].rstrip(",").split("/")[0]))
                entry["test_size"] = int(data[2].rstrip(",").split("/")[1])
                entry["average_guesses"] = float(data[3])
    return loaded


def main():
    from time import time
    start = time()
    eval_all_logs()
    print(f"finished in {round(time() - start)}s")


if __name__ == "__main__":
    # main()
    load_results()
