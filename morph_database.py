"""This file contains tools for creating and using morphological database."""
from typing import Tuple, Dict, List, Union

AFFIXES = Dict[str, List[Tuple[str, List[str]]]]
FORMS = Dict[str, Union[str, List[str]]]
PARADIGM_AFFIXES_GROUPS = Dict[str, FORMS]
MORPH_DATABASE = Dict[str, Dict[str, Dict[str, int]]]
VOCABULARY = Dict[str, str]


class MorphDatabase:
    """This class represents morphological database obtained from dictionary and paradigm files. Holds
    attributes vocab (dictionary lemma:paradigm) and paradigms (paradigm:suffixes and tags)."""

    def __init__(self, dic_file: str, par_file: str):
        self.vocab = vocabulary(dic_file)
        self.paradigms = paradigm_db(par_file)
        self.paradigm_suffixes()

    def full_database(self) -> MORPH_DATABASE:
        """Returns dictionary of words and all their forms and frequencies"""
        database = dict()
        for lemma, paradigm in self.vocab.items():
            self.add_lemma_forms(lemma, paradigm, database)
        return database

    def add_lemma_forms(self, lemma: str, paradigm: str, database: MORPH_DATABASE) -> None:
        """Constructs all forms for given lemma, assigns them frequency 0 and writes them to database"""
        database[lemma] = dict()
        forms = self.all_forms_with_paradigm(lemma, paradigm)
        for form in forms.keys():
            database[lemma][form] = dict()
            for tag in forms[form]:
                database[lemma][form][tag] = 0

    def all_forms(self, lemma: str) -> FORMS:
        """Constructs all forms for given lemma"""
        paradigm = self.find_paradigm(lemma) if lemma not in self.paradigms.keys() else lemma
        if paradigm:
            return self.all_forms_with_paradigm(lemma, paradigm)
        return dict()

    def all_forms_with_paradigm(self, lemma: str, paradigm: str, informal: bool = True) -> FORMS:
        """Constructs all forms for given lemma when its paradigm is known"""
        forms = dict()
        root = self.word_root(lemma, paradigm)
        for form, tags in self.paradigms[paradigm].items():
            if form == "<suffix>":
                continue
            if not informal:
                formal = []
                for tag in tags:
                    if "wH" not in tag:
                        formal.append(tag)
                if formal:
                    forms[root + form] = forms.get(root + form, []) + formal
            else:
                forms[root + form] = forms.get(root + form, []) + tags
        return forms

    def word_root(self, lemma: str, paradigm: str) -> str:
        """Finds the morphological root (resp. prefixes+root) for given lemma"""
        if lemma.endswith("ný") or (lemma.endswith("cí") and not lemma.endswith("ící")) or lemma.endswith("tý") \
                or lemma.endswith("ový") or lemma.endswith("lý") \
                or (lemma.endswith("ní") and not lemma.endswith("ání") and not lemma.endswith("ení")):
            return lemma[:-1]
        common_suffix = len(self.paradigms[paradigm]["<suffix>"])
        if common_suffix == 0:
            return lemma
        return lemma[:-common_suffix]

    def add_similar_forms(self, root: str, paradigm: str, form: str, found_lt: List[Dict[str, str]]) -> None:
        """Searches through single paradigm and appends all lemma-tag pairs matching form"""
        for paradigm_form, tags in self.paradigms[paradigm].items():
            if paradigm_form == "<suffix>":
                continue
            if root + paradigm_form == form:
                found_lt += [dict(lemma=(root + self.paradigms[paradigm]["<suffix>"]), tag=tag) for tag in tags]

    def find_paradigm(self, lemma: str) -> str:
        """Returns paradigm for given lemma or '' if lemma is not in vocabulary"""
        return self.vocab.get(lemma, "")

    def paradigm_suffixes(self) -> None:
        """Assigns suffix (part of word to be cut when creating other forms) to each paradigm in database."""
        for paradigm, suffices in self.paradigms.items():
            lemma = paradigm.split("_", 1)[0]
            # keys() iterates in insertion order
            self.paradigms[paradigm]["<suffix>"] = paradigm[lemma.rfind(list(suffices.keys())[0]):]

    def split_vocabulary(self, ratio: int = 10, filename: str = "", path: str = "",
                         train_suffix: str = "_train", test_suffix: str = "_test") -> Tuple[str, str]:
        """Split the database's vocabulary into two separate files of sizes
        approx. 1 : <ratio> - 1, returns their paths"""
        train = open(path + filename + train_suffix, "w", encoding="windows-1250")
        test = open(path + filename + test_suffix, "w", encoding="windows-1250")
        i = 0
        for lemma, paradigm in self.vocab.items():
            if (i % ratio != 0) or lemma == paradigm.split("_")[0]:
                print(f"{lemma}:{paradigm}", file=train)
            else:
                print(f"{lemma}:{paradigm}", file=test)
            i += 1
        train.close()
        test.close()
        return path + filename + train_suffix, path + filename + test_suffix

    def possible_paradigm(self, segments: List[str]):
        """
        For given segmented word, finds all paradigms containing form with common suffix. All others
        are possible too if using empty suffix, but this is handled elsewhere.
        """
        # TODO
        pass


def paradigm_db(par_file: str) -> PARADIGM_AFFIXES_GROUPS:
    """Creates database from data in paradigm file."""
    translated = dict()
    paradigms, affixes = read_paradigms(par_file)
    for paradigm, forms in paradigms.items():
        translated[paradigm] = dict()
        for form, suffixes in forms.items():
            for alias in suffixes:
                for affix in affixes[alias]:
                    suffix = form + affix[0]
                    translated[paradigm][suffix] = translated[paradigm].get(suffix, [])
                    translated[paradigm][suffix].extend(affix[1])
    return translated


def vocabulary(dic_file: str) -> VOCABULARY:
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


def read_paradigms(par_file: str) -> Tuple[PARADIGM_AFFIXES_GROUPS, AFFIXES]:
    """Reads paradigms file to dictionaries which wil be merged to paradigm database"""
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
