"""This file contains tools for creating and using morphological database."""
from typing import Tuple, Dict, List, Set, Any

AFFIXES = Dict[str, List[Tuple[str, List[str]]]]
PAR_DATA = Dict[str, Any]
DB_PARADIGMS = Dict[str, PAR_DATA]
DB_VOCABULARY = List[Tuple[str, str]]


class MorphDatabase:
    """This class represents morphological database obtained from dictionary and paradigm files. Holds
    attributes vocab (dictionary lemma:paradigm) and paradigms (paradigm:suffixes and tags)."""

    def __init__(self, dic_file: str, par_file: str, freq_list: str = "", only_formal: bool = False):
        self.vocab = []
        self.paradigms = paradigm_db(par_file, only_formal)
        self.paradigm_suffixes()
        if dic_file:
            self.vocab = vocabulary(dic_file)
        if freq_list:
            self.form_spread(freq_list)

    def form_present(self, word: str) -> bool:
        for paradigm, data in self.paradigms.items():
            root = paradigm[:len(paradigm) - len(data["<suffix>"])].lower()
            if not word.startswith(root):
                continue
            for suffix in data["affixes"].keys():
                if word == (root + suffix):
                    return True
        for (lemma, paradigm) in self.vocab:
            if word in self.lemma_forms(lemma.lower(), paradigm):
                return True
        return False

    def lemma_forms(self, lemma: str, paradigm: str) -> Set[str]:
        """Returns set of all forms for given lemma and paradigm."""
        forms = set()
        root = self.word_root(lemma, paradigm)
        for suffix in self.paradigms[paradigm]["affixes"].keys():
            forms.add(root + suffix)
        return forms

    def word_root(self, lemma: str, paradigm: str) -> str:
        """Returns the morphological root (resp. prefixes+root) for given lemma"""
        common_suffix = self.paradigms[paradigm]["<suffix>"].split("_")[0]
        return lemma if not common_suffix else lemma[:-len(common_suffix)]

    def paradigm_suffixes(self) -> None:
        """Assigns suffix (part of word to be cut when creating other forms) to each paradigm in database."""
        for paradigm, data in self.paradigms.items():
            lemma = paradigm.split("_", 1)[0].rstrip("1234567890")
            self.paradigms[paradigm]["<suffix>"] = ""
            # keys() iterates in insertion order
            for suffix in data["affixes"].keys():
                if lemma.endswith(suffix):
                    self.paradigms[paradigm]["<suffix>"] = paradigm[len(lemma) - len(suffix):]
                    break

    def form_spread(self, freq_list: str) -> None:
        """Computes absolute spread of given forms in corpus characterized by its alphabetically sorted
        filtered frequency list."""
        for paradigm, data in self.paradigms.items():
            self.paradigms[paradigm]["spread"] = dict()
            for affix in data["affixes"].keys():
                self.paradigms[paradigm]["spread"][affix] = 0
        with open(freq_list, encoding="utf-8") as fl:
            for line in fl:
                values = line.strip().split()
                paradigm, lemma, word = values[0], values[1], values[2]
                self.paradigms[paradigm]["spread"][word[len(lemma) -
                                                        len(self.paradigms[paradigm]["<suffix>"].split("_")[0]):]] \
                    += int(values[3])

    def all_suffixes(self) -> Set[str]:
        found = set()
        for data in self.paradigms.values():
            found |= data["affixes"].keys()
        return found

    def dic_file_all_forms(self, dic_file: str) -> None:
        outfile = open(f"{dic_file}.forms", "w", encoding="utf-8")
        for word, paradigm in self.vocab:
            for form in self.lemma_forms(word, paradigm):
                print(f"{form}:{word}:{paradigm}", file=outfile)
        outfile.close()

    def same_paradigms(self, this: str, other: str, criterion: str, threshold: int = -1) -> bool:
        if this not in self.paradigms.keys() or other not in self.paradigms.keys():
            return False
        if criterion == "same_paradigms":
            return this == other
        elif criterion == "same_affixes":
            return self.paradigms[this]["affixes"] == self.paradigms[other]["affixes"]
        elif criterion == "common_forms" and threshold != -1:
            return len(set(self.paradigms[this]["affixes"].keys())
                       .intersection(self.paradigms[other]["affixes"].keys())) >= threshold
        elif criterion == "common_tags":
            this_tag = list(self.paradigms[this]["affixes"].values())[0][0]
            other_tag = list(self.paradigms[other]["affixes"].values())[0][0]
            return this_tag[1] == other_tag[1] and \
                (True if this_tag[1] != "1" else ("g" in this_tag and "g" in other_tag
                                                  and this_tag[this_tag.index("g") + 1]
                                                  == other_tag[other_tag.index("g") + 1]))

    def same_lemma(self, word: str, this: str, other: str) -> bool:
        if this not in self.paradigms.keys() or other not in self.paradigms.keys():
            return False
        return self.lemmatize(word, this) == self.lemmatize(word, other)

    def lemmatize(self, form: str, paradigm: str, prefix: str = "") -> str:
        if prefix:
            return prefix + self.paradigms[paradigm]["<suffix>"].split("_")[0]
        longest_suffix = ""
        for suffix in self.paradigms[paradigm]["affixes"].keys():
            if form.endswith(suffix) and len(suffix) > len(longest_suffix):
                longest_suffix = suffix
        return form[:len(form) - len(longest_suffix)] + self.paradigms[paradigm]["<suffix>"].split("_")[0]


def paradigm_db(par_file: str, only_formal: bool = False) -> DB_PARADIGMS:
    """Creates database from data in paradigm file."""
    translated = dict()
    paradigms, affixes = read_paradigms(par_file)
    for paradigm, forms in paradigms.items():
        translated[paradigm] = dict()
        translated[paradigm]["affixes"] = dict()
        for form, suffixes in forms.items():
            for alias in suffixes:
                for affix in affixes[alias]:
                    tags = affix[1]
                    if only_formal:
                        tags = list(filter(lambda x: "wH" not in x, tags))
                    suffix = form + affix[0]
                    if tags:
                        translated[paradigm]["affixes"][suffix] = translated[paradigm].get(suffix, [])
                        translated[paradigm]["affixes"][suffix].extend(tags)
    return translated


def vocabulary(dic_file: str) -> DB_VOCABULARY:
    """Creates vocabulary from data in dictionary file"""
    vocab = []
    d = open(dic_file, "r", encoding="windows-1250")
    for line in d:
        line = correct_encoding(line)
        if line.startswith(" ") or line.startswith("|") or not line.strip():
            continue
        lem_par = line.split("|")[0].split(":")
        vocab.append((lem_par[0], lem_par[1].rstrip("!%\n")))
    d.close()
    return vocab


def read_paradigms(par_file: str) -> Tuple[DB_PARADIGMS, AFFIXES]:
    """Reads paradigms file to dictionaries which will be merged to paradigm database"""
    affixes = dict()
    database = dict()
    current = ""
    p = open(par_file, "r", encoding="windows-1250")
    for line in p:
        line = correct_encoding(line)
        if line.startswith("="):
            current = line.lstrip("=").rstrip()
            affixes[current] = list()
        elif line.startswith("\t{"):
            vals = line.lstrip("\t{").rstrip("}\n").split(",")
            affixes[current].append(("" if vals[0] == "_" else vals[0], [vals[1].strip()]))
        elif line.startswith("+"):
            current = line.lstrip("+").rstrip()
            database[current] = dict()
        elif line.startswith("\t<"):
            vals = line.strip().split()
            database[current][vals[0].lstrip("<").rstrip(">")] = [v.rstrip(",") for v in vals[1:]]
    p.close()
    return database, affixes


def correct_encoding(line: str) -> str:
    """Replaces wrongly encoded characters from dictionary and paradigm files"""
    return line.replace("ą", "š").replace("ľ", "ž").replace("»", "ť").replace("®", "Ž").replace("©", "Š")


def clean_dic_file(dic_file: str) -> None:
    """Removes unnecessary lines and information from dictionary and saves it in utf-8 encoding."""
    from re import fullmatch
    outfile = open(f"{dic_file}.cleaned.utf8", "w", encoding="utf-8")
    with open(dic_file, encoding="windows-1250") as dic:
        for line in dic:
            if not fullmatch(r"[\w_]+:[\w_]+\|?[\d.,]*", line.strip()):
                continue
            print(correct_encoding(line.strip().split("|")[0]), file=outfile)
    outfile.close()
