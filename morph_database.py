"""This file contains tools for creating and using morphological database."""
from typing import Tuple, Dict, List, Set, Any

AFFIXES = Dict[str, List[Tuple[str, List[str]]]]
PAR_DATA = Dict[str, Any]
DB_PARADIGMS = Dict[str, PAR_DATA]
DB_VOCABULARY = Dict[str, str]


class MorphDatabase:
    """This class represents morphological database obtained from dictionary and paradigm files. Holds
    attributes vocab (dictionary lemma:paradigm) and paradigms (paradigm:suffixes and tags)."""

    def __init__(self, dic_file: str, par_file: str, freq_list: str = "", only_formal: bool = False):
        self.vocab = dict()
        self.paradigms = paradigm_db(par_file, only_formal)
        self.paradigm_suffixes()
        if dic_file:
            self.vocab = vocabulary(dic_file)
        if freq_list:
            self.form_spread(freq_list)

    def productive_paradigms(self) -> DB_PARADIGMS:
        new_par = dict()
        for word, paradigm in self.vocab.items():
            if paradigm in new_par.keys() or word.split("_")[0] == paradigm.split("_")[0]:
                continue
            new_par[paradigm] = self.paradigms[paradigm]
        return new_par

    def form_present(self, word: str) -> bool:
        for paradigm, data in self.paradigms.items():
            root = paradigm[:len(paradigm) - len(data["<suffix>"])].lower()
            if not word.startswith(root):
                continue
            for suffix in data["affixes"].keys():
                if word == (root + suffix):
                    return True
        for lemma, paradigm in self.vocab.items():
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
        for paradigm, suffixes in self.paradigms.items():
            lemma = paradigm.split("_", 1)[0]
            # keys() iterates in insertion order
            self.paradigms[paradigm]["<suffix>"] = paradigm[lemma.rfind(list(suffixes["affixes"].keys())[0]):]

    def form_spread(self, freq_list: str) -> None:
        """Computes absolute spread of given forms in corpus characterized by its alphabetically sorted
        filtered frequency list."""
        for paradigm, data in self.paradigms.items():
            self.paradigms[paradigm]["spread"] = dict()
            for affix in data["affixes"].keys():
                self.paradigms[paradigm]["spread"][affix] = 0.0
        with open(freq_list, encoding="utf-8") as fl:
            for line in fl:
                values = line.strip().split()
                paradigm, word = values[0], values[1]
                if paradigm not in self.paradigms.keys():
                    continue
                self.paradigms[paradigm]["spread"][word[len(paradigm) -
                                                        len(self.paradigms[paradigm]["<suffix>"]):]] = float(values[2])

    def dic_file_all_forms(self, dic_file: str) -> None:
        outfile = open(f"{dic_file}.forms", "w", encoding="utf-8")
        for word, paradigm in self.vocab.items():
            for form in self.lemma_forms(word, paradigm):
                print(f"{form}:{word}:{paradigm}", file=outfile)
        outfile.close()

    def same_paradigms(self) -> None:
        for par, data in self.paradigms.items():
            for other_par, other_data in self.paradigms.items():
                if par <= other_par:
                    continue
                if data["affixes"] == other_data["affixes"]:
                    print(f"{par} == {other_par}")


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
    vocab = dict()
    d = open(dic_file, "r", encoding="windows-1250")
    for line in d:
        line = correct_encoding(line)
        if line.startswith(" ") or line.startswith("|") or not line.strip():
            continue
        lem_par = line.split("|")[0].split(":")
        vocab[lem_par[0]] = lem_par[1].rstrip("!%\n")
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
