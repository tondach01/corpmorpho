#!/usr/bin/env python3
import db_stats
import morph_database as md
import guesser as g
from typing import Tuple, Set, Dict
from os import sep


class SortedListCell:
    """This class represents one cell of (sorted) linked list"""
    def __init__(self, name, value):
        self.value = value
        self.name = name
        self.left = None
        self.right = None

    def __str__(self):
        return f"{'X' if self.left is None else self.left.name} <- [{self.name}: {self.value}]"\
               f" -> {'X' if self.right is None else self.right.name}"

    def __le__(self, other):
        if self.value == other.value:
            return len(self.name) >= len(other.name)
        return self.value <= other.value

    def __gt__(self, other):
        return not self <= other


class SortedList:
    """This class represents sorted list of cells"""
    def __init__(self):
        self.first = None
        self.last = None
        self.length = 0

    def __iter__(self):
        current = self.first
        while current is not None:
            yield current.name
            current = current.right

    def __getitem__(self, item):
        current = self.first
        while current is not None:
            if current.name == item:
                return current

    def __str__(self):
        out = ""
        current = self.first
        while current is not None:
            out += str(current) + "\n"
            current = current.right
        return out

    def add(self, cell: SortedListCell) -> None:
        """Adds new cell to sorted list"""
        self.length += 1
        if self.first is None:
            self.first = cell
            self.last = cell
            return
        if self.last > cell:
            self.last.right = cell
            cell.left = self.last
            self.last = cell
            return
        current = self.last
        while current is not None:
            if current > cell:
                cell.right = current.right
                cell.left = current
                current.right.left = cell
                current.right = cell
                return
            current = current.left
        cell.right = self.first
        self.first.left = cell
        self.first = cell

    def increase_value(self, name: str):
        """Increases value of cell with given name by 1 and moves it up the list if necessary"""
        current = self.first
        while current is not None:
            if current.name != name:
                current = current.right
                continue
            current.value += 1
            if current.left is not None:
                current.left.right = current.right
                if current.right is not None:
                    current.right.left = current.left
            new_left = current.left
            while new_left is not None:
                if new_left > current:
                    current.left = new_left
                    new_left.right.left = current
                    current.right = new_left.right
                    new_left.right = current
                    return
                new_left = new_left.left
            if current != self.first:
                current.right = self.first
                current.left = None
                self.first.left = current
                self.first = current
            return

    def pop(self) -> None:
        """Removes last cell of the sorted list. Does nothing if list is empty"""
        if self.length == 0:
            return
        self.length -= 1
        if self.length == 1:
            self.first = None
            self.last = None
        else:
            self.last = self.last.left

    def first_n(self, n: int) -> Set[str]:
        """Returns set of n most occurred suffixes in sorted list"""
        scores = set()
        current = self.first
        for _ in range(min(self.length, n)):
            scores.add(current.name)
            current = current.right
        return scores


def baseline_guess(test_vocab: str, corpus: str, morph_db: md.MorphDatabase,
                   top_n: int = 1, debug: bool = False) -> Tuple[int, int]:
    """Tries to guess paradigm for each lemma in test_vocab and returns its success rate (all, correct)"""
    return segmented_guess(test_vocab, corpus, morph_db, top_n=top_n, debug=debug)


def segmented_guess(test_vocab: str, corpus: str, morph_db: md.MorphDatabase, segmenter: str = "",
                    top_n: int = 1, debug: bool = False, cache=None) -> Tuple[int, int]:
    """Tries to guess paradigm for each lemma in test_vocab given its segmentation (if given segmenter)
    and returns its success rate (all, correct)"""
    segment = (lambda x: list(x[i] for i in range(len(x))))
    if segmenter == "sentencepiece":
        import sentencepiece as sp
        m = sp.SentencePieceProcessor()
        m.load(f"sentencepiece{sep}m.model")
        segment = m.encode_as_pieces
    elif segmenter == "morfessor":
        import morfessor
        m = morfessor.MorfessorIO().read_binary_model_file(f"morfessor{sep}morfessor_model")
        segment = (lambda x: m.viterbi_segment(x)[0])
    all_pars, correct = 0, 0
    with open(test_vocab, encoding="windows-1250") as test:
        for line in test:
            if debug:
                print(line.strip())
            lem_par = line.strip().split(":")
            segments = segment(lem_par[0])
            score = g.guess_paradigm_from_lemma_seg(lem_par[0], corpus, morph_db, segments, cache=cache)
            paradigms = list(sorted(score, key=(lambda x: score[x]), reverse=True))
            if debug:
                print("\t" + ", ".join(paradigms))
            if len(paradigms) < top_n and lem_par[1] in paradigms:
                correct += 1
            elif lem_par[1] in paradigms[:top_n]:
                correct += 1
            all_pars += 1
    return all_pars, correct


def most_common_suffixes(vocab_file: str, size: int = 100) -> Set[str]:
    """Finds <size> probably (not surely) most common suffixes for lemmas in vocabulary file
    (of format lemma:paradigm per each line)"""
    cache = SortedList()
    with open(vocab_file, encoding="windows-1250") as f:
        for line in f:
            lemma = line.split(":")[0]
            for suffix in [lemma[i:] for i in range(len(lemma))]:
                if suffix in cache:
                    cache.increase_value(suffix)
                elif cache.length >= 100 * size:
                    cache.pop()
                    cache.add(SortedListCell(suffix, 1))
                else:
                    cache.add(SortedListCell(suffix, 1))
    return cache.first_n(size)


def scores_of_most_common(common: Set[str], corpus: str, morph_db: md.MorphDatabase) -> Dict[str, Dict[str, int]]:
    scores = dict()
    for suffix in common:
        scores[suffix] = db_stats.paradigm_frequencies(corpus, morph_db, suffix)
    for suffix, paradigms in scores.items():
        for paradigm, freq in paradigms.items():
            scores[suffix][paradigm] = freq * len(suffix)
    return scores


def main():
    from time import time
    from sys import argv
    start = time()
    seg = "" if len(argv) < 2 else argv[1]
    train, test = md.MorphDatabase("current.dic", "current.par").split_vocabulary()
    train_md = md.MorphDatabase(train, "current.par")
    cache = scores_of_most_common(most_common_suffixes(test, 1000), f"desam{sep}desam", train_md)
    a, c = segmented_guess(test, f"desam{sep}desam", train_md, segmenter=seg, debug=True, cache=cache)
    # print(f"finished in {round(time() - start)}s")
    # print(f"{c} correct out of {a}")


if __name__ == "__main__":
    main()
