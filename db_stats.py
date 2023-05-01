"""This file contains tools for handling queries on corpora."""
import morph_database as md
from typing import Dict, List, Set, Tuple


class FreqTreeNode:
    """Class representing a node in frequency list tree."""
    def __init__(self):
        self.value = 0
        self.children = dict()

    def add(self, word: str, freq: int):
        """Integrate word and its frequency into a tree."""
        if not word:
            self.value = freq
            return
        else:
            if word[0] not in self.children.keys():
                self.children[word[0]] = FreqTreeNode()
            self.children[word[0]].add(word[1:], freq)

    def __getitem__(self, item) -> int:
        if not isinstance(item, str):
            return 0
        if not item:
            return self.value
        if item[0] in self.children.keys():
            return self.children[item[0]].__getitem__(item[1:])
        elif item[0].upper() in self.children.keys():
            return self.children[item[0].upper()].__getitem__(item[1:])
        return 0

    def feed(self, freq_list: str, prefix: str = "") -> 'FreqTreeNode':
        """Integrate all lines <segmentation word frequency> from frequency list into a tree. Adding can
        be limited to words starting with given prefix."""
        with open(freq_list, encoding="utf-8") as fl:
            for line in fl:
                values = line.strip().split()
                if values[1].startswith(prefix):
                    self.add(uppercase_format(values[0]), int(values[2]))
        return self

    def suffixes(self, prefix: str, suffix: str = "") -> Dict[str, int]:
        """Returns all suffixes and their frequencies for given prefix. Suffix is auxiliary parameter
        used in recursion."""
        suffixes = dict()
        if prefix:
            if prefix[0] in self.children.keys():
                suffixes.update(self.children[prefix[0]].suffixes(prefix[1:]))
            if prefix[0].upper() in self.children.keys():
                suffixes.update(self.children[prefix[0].upper()].suffixes(prefix[1:]))
            return suffixes
        if not self.children:
            return {suffix: self.value}
        if self.value != 0:
            suffixes[suffix] = self.value
        for letter, node in self.children.items():
            if not suffix and letter.islower():
                continue
            suffixes.update(node.suffixes(prefix, suffix + letter.lower()))
        return suffixes


def uppercase_format(segmentation: str):
    """Converts '=' (segments separated with =) segmentation format into uppercase (starts of segments
    are in uppercase)."""
    clean = segmentation.strip("¦=▁")
    formatted = ""
    for i in range(len(clean)):
        if clean[i] == "=":
            continue
        if i > 0 and clean[i-1] == "=":
            formatted += clean[i].upper()
        else:
            formatted += clean[i]
    return formatted


def clean_freqlist(freq_list: str) -> None:
    import re
    cleaned = open(freq_list + ".cleaned", "w", encoding="utf-8")
    with open(freq_list, encoding="utf-8") as fl:
        for line in fl:
            if not re.fullmatch(r"\S+\s\d+\s\d+", line.strip()):
                continue
            values = line.split("\t")
            word, freq = values[0], values[1]
            if re.fullmatch(r"[a-záéíóúůýěžščřďťň]+", word) is None:
                continue
            print("\t".join([word, freq]), file=cleaned)
    cleaned.close()


def filter_freqlist(freq_list: str, all_forms: str) -> None:
    """Picks from alphabetically sorted frequency list only forms of words in morphological database."""
    out = open(f"{freq_list}.filtered", "w", encoding="utf-8")
    forms = open(all_forms, encoding="utf-8")
    form = forms.readline()
    with open(freq_list, encoding="utf-8") as fl:
        for line in fl:
            if not form:
                break
            print(line.strip())  # debug
            word = line.split()[0]
            data = form.strip().split(":")
            if str_gt(data[0], word):
                continue
            while str_gt(word, data[0]):
                form = forms.readline()
                if not form:
                    break
                data = form.strip().split(":")
            while data[0] == word:
                out.write(f"{data[2]}\t{data[1]}\t{line}")
                form = forms.readline()
                if not form:
                    break
                data = form.strip().split(":")
    out.close()
    forms.close()


def str_gt(this: str, other: str) -> bool:
    if this == other:
        return False
    for i in range(min(len(this), len(other))):
        if this[i] > other[i]:
            return True
        elif this[i] < other[i]:
            return False
    return len(this) > len(other)


def segment_dic_file(morph_db: md.MorphDatabase, seg_method, outfile: str, only_lemmas: bool = True) -> None:
    """Segments each word in vocabulary of morphological database with given method. If only_lemmas set
    to False, it first computes and includes all forms of given lemma. Result is saved to outfile."""
    with open(outfile, "w", encoding="utf-8") as out:
        for (lemma, paradigm) in morph_db.vocab:
            segments = "=".join(seg_method(lemma)).replace("_", "").replace("¦", "").replace("𐋇", "")\
                .replace("𐊣", "").replace("𐊼", "")
            print(f"{segments}:{lemma}:{paradigm}", file=out)
            if only_lemmas:
                continue
            for form in morph_db.lemma_forms(lemma, paradigm):
                segments = "=".join(seg_method(form)).replace("_", "").replace("¦", "").replace("𐋇", "") \
                    .replace("𐊣", "").replace("𐊼", "")
                print(f"{segments}:{lemma}:{paradigm}", file=out)


def normalize_spread(spread: Dict[str, float]) -> Dict[str, float]:
    """Normalizes given frequency spread by dividing each frequency by greatest occurred frequency."""
    if not spread:
        return dict()
    norm = max(spread.values())
    if norm == 0.0:
        return {suf: 0.0 for (suf, _) in spread.items()}
    return {suf: freq / norm for (suf, freq) in spread.items()}


def spread_difference(paradigm: Dict[str, float], word: Dict[str, float]) -> float:
    """Computes difference of normalized spreads of given paradigm and word."""
    diff = 0
    for suf, freq in paradigm.items():
        diff += abs(freq - word.get(suf, 0.0))
    # for suf, freq in word.items():
    #     if suf not in paradigm.keys():
    #         diff += freq
    return diff  # / (1 if len(paradigm) == 0 else len(paradigm))


def tree_spread_scores(segments: str, tree: FreqTreeNode, morph_db: md.MorphDatabase, scoring,
                       only_lemmas: bool = False) -> Dict[str, float]:
    """Computes paradigm scores for given word based on its forms spread."""
    scores = dict()
    n_most_common = dict()
    normed = dict()
    prefix_frequencies = dict()
    all_suffixes = morph_db.all_suffixes()
    for i in range(len(segments)):
        if segments[i].islower():
            continue
        prefix = segments[:i].lower()
        if segments[len(prefix):].lower() in all_suffixes:
            prefix_frequencies[prefix] = tree.suffixes(prefix)
    prefix_frequencies[segments.lower()] = tree.suffixes(segments.lower())
    for prefix, word_suffixes in prefix_frequencies.items():
        suffix = segments[len(prefix):].lower()
        n_best = n_best_paradigms(set(word_suffixes.keys()), morph_db, suffix, only_lemmas=only_lemmas)
        for (common, paradigm) in n_best:
            if n_most_common.get(paradigm, (0, ""))[0] < common:
                if prefix not in normed.keys():
                    normed[prefix] = normalize_spread(word_suffixes)
                n_most_common[paradigm] = (common, prefix)
    for paradigm, (common, prefix) in n_most_common.items():
        scores[paradigm] = scoring(common,
                                   normed[prefix],
                                   normalize_spread(morph_db.paradigms[paradigm].get("spread", dict()))
                                   )
    return scores


def scoring_comm_square_spread(common_forms: int, guess_normed: Dict[str, float], par_normed: Dict[str, float]):
    # penalize lower-form paradigms
    return common_forms - square_spread_difference(par_normed, guess_normed)


def square_spread_difference(paradigm: Dict[str, float], word: Dict[str, float]) -> float:
    from math import pow
    diff = 0
    for suf, freq in paradigm.items():
        diff += pow(abs(freq - word.get(suf, 0.0)), 2)
    return diff


def n_best_paradigms(word_suffixes: Set[str], morph_db: md.MorphDatabase, suffix: str, n: int = 5,
                     only_lemmas: bool = False) -> List[Tuple[int, str]]:
    """Chooses n most suitable paradigms for given suffixes based on size of their intersection. Can return more than
    n paradigms if they have the same score as the n-th one."""
    i_sizes = list()
    for paradigm, data in morph_db.paradigms.items():
        par_affixes = set(data["affixes"].keys())
        if suffix not in par_affixes:
            continue
        if only_lemmas and suffix != data["<suffix>"].split("_")[0]:
            continue
        common = len(word_suffixes.intersection(par_affixes))
        i_sizes.append((common, paradigm))
    nth_score = 1
    result = []
    for i, (score, paradigm) in enumerate(sorted(i_sizes, reverse=True)):
        if i == (n - 1):
            nth_score = score
        elif i >= n and score < nth_score:
            return result
        result.append((score, paradigm))
    return result


def segment_freq_list(freq_list: str, seg_method, suffix: str) -> None:
    """Adds info about segmentation to frequency list and stores it."""
    outfile = open(f"{freq_list}.{suffix}", "w", encoding="utf-8")
    with open(freq_list, encoding="utf-8") as fl:
        for line in fl:
            print(f"{'='.join(seg_method(line.split()[0]))}\t{line.strip()}", file=outfile)
    outfile.close()


def test_forms(file: str = "data/current.dic.cleaned.utf8.sorted.forms", ratio: int = 50) -> None:
    out = open(file + ".filtered", "w", encoding="utf-8")
    with open(file, encoding="utf-8") as f:
        i = 0
        for line in f:
            if i % ratio == 0:
                out.write(line)
            i += 1
    out.close()


def print_scores(word: str, scores: Dict[str, float]) -> None:
    """Prints paradigms in descending order (by their frequency scores)"""
    print(word + ":", end="")
    for paradigm, score in scores.items():
        print(f" {paradigm} ({score})", end="")
    print()
