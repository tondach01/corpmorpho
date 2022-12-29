import morph_database as md
import guesser as g
from typing import Tuple


def baseline_guess(test_vocab: str, corpus: str, morph_db: md.MorphDatabase,
                   top_n: int = 1, debug: bool = False) -> Tuple[int, int]:
    """Tries to guess paradigm for each lemma in test_vocab and return its success rate (all, correct)"""
    all_pars, correct = 0, 0
    with open(test_vocab, encoding="windows-1250") as test:
        for line in test:
            if debug:
                print(line.strip())
            lem_par = line.strip().split(":")
            score = g.guess_paradigm_from_lemma(lem_par[0], corpus, morph_db)
            paradigms = list(sorted(score, key=(lambda x: score[x]), reverse=True))
            if debug:
                print("\t" + ", ".join(paradigms))
            if len(paradigms) < top_n and lem_par[1] in paradigms:
                correct += 1
            elif lem_par[1] in paradigms[:top_n]:
                correct += 1
            all_pars += 1
    return all_pars, correct


def main():
    from os import sep
    from time import time
    start = time()
    train, test = md.MorphDatabase("current.dic", "current.par").split_vocabulary()
    a, c = baseline_guess(test, f"desam{sep}desam", md.MorphDatabase(train, "current.par"), debug=True)
    print(f"finished in {round(time() - start)}s, {c} correct out of {a}")


if __name__ == "__main__":
    main()
