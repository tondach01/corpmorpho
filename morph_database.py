"""This file contains tools for creating and using morphological database."""
from typing import Tuple, Dict, List, Union, Set

AFFIXES = Dict[str, List[Tuple[str, List[str]]]]
PAR_DATA = Dict[str, Union[str, Dict[str, List[str]], Dict[str, float]]]
PARADIGM_AFFIXES_GROUPS = Dict[str, PAR_DATA]
MORPH_DATABASE = Dict[str, Dict[str, Dict[str, int]]]
VOCABULARY = Dict[str, str]


class MorphDatabase:
    """This class represents morphological database obtained from dictionary and paradigm files. Holds
    attributes vocab (dictionary lemma:paradigm) and paradigms (paradigm:suffixes and tags)."""

    def __init__(self, dic_file: str, par_file: str, freq_list: str = ""):
        self.vocab = vocabulary(dic_file)
        self.paradigms = paradigm_db(par_file)
        self.paradigm_suffixes()
        if freq_list:
            self.form_spread(freq_list)

    def all_forms(self, lemma: str) -> PAR_DATA:
        """Constructs all forms for given lemma"""
        paradigm = self.find_paradigm(lemma) if lemma not in self.paradigms.keys() else lemma
        if paradigm:
            return self.all_forms_with_paradigm(lemma, paradigm)
        return dict()

    def only_forms(self, lemma: str, paradigm: str) -> Set[str]:
        """Returns set of all forms for given lemma and paradigm."""
        forms = set()
        root = self.word_root(lemma, paradigm)
        for suffix in self.paradigms[paradigm]["affixes"].keys():
            forms.add(root + suffix)
        return forms

    def all_forms_with_paradigm(self, lemma: str, paradigm: str) -> PAR_DATA:
        """Constructs all forms for given lemma when its paradigm is known"""
        forms = dict()
        root = self.word_root(lemma, paradigm)
        for form, tags in self.paradigms[paradigm]["affixes"].items():
            forms[root + form] = forms.get(root + form, []) + tags
        return forms

    def word_root(self, lemma: str, paradigm: str) -> str:
        """Returns the morphological root (resp. prefixes+root) for given lemma"""
        common_suffix = self.paradigms[paradigm]["<suffix>"].split("_")[0]
        return lemma if not common_suffix else lemma[:-len(common_suffix)]

    def add_similar_forms(self, root: str, paradigm: str, form: str, found_lt: List[Dict[str, str]]) -> None:
        """Searches through single paradigm and appends all lemma-tag pairs matching form"""
        for paradigm_form, tags in self.paradigms[paradigm]["affixes"].items():
            if root + paradigm_form == form:
                found_lt += [dict(lemma=(root + self.paradigms[paradigm]["<suffix>"]), tag=tag) for tag in tags]

    def find_paradigm(self, lemma: str) -> str:
        """Returns paradigm for given lemma or '' if lemma is not in vocabulary"""
        return self.vocab.get(lemma, "")

    def paradigm_suffixes(self) -> None:
        """Assigns suffix (part of word to be cut when creating other forms) to each paradigm in database."""
        for paradigm, suffixes in self.paradigms.items():
            lemma = paradigm.split("_", 1)[0]
            # keys() iterates in insertion order
            self.paradigms[paradigm]["<suffix>"] = paradigm[lemma.rfind(list(suffixes["affixes"].keys())[0]):]

    def split_vocabulary(self, ratio: int = 10, filename: str = "", path: str = "",
                         train_suffix: str = "_train.dic", test_suffix: str = "_test.dic") -> Tuple[str, str]:
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

    def matching_suffixes(self, word_suffixes: List[str]) -> Set[Tuple[str, str]]:
        """For given word segmented to suffixes, finds all paradigms containing form with common suffix and
        returns them with possible lemma of the word. Empty suffixes are counted in too."""
        matching = set()
        for paradigm, suffixes in self.paradigms.items():
            for suffix in suffixes["affixes"].keys():
                if suffix in word_suffixes or not suffix:
                    lemma = (word_suffixes[-1].lstrip("_") if not suffix else
                             word_suffixes[-1].lstrip("_")[:-len(suffix)]) \
                        + self.paradigms[paradigm]["<suffix>"].split("_")[0]
                    matching.add((paradigm, lemma))
        return matching

    def matching_suffixes_lemma(self, lemma_suffixes: List[str]) -> Set[str]:
        """For given lemma segmented to suffixes, finds all paradigms which lemma has common suffix. All others
        are possible too if using empty suffix, but this is handled elsewhere."""
        # TODO update according to matching_suffixes
        matching = set()
        for paradigm, suffixes in self.paradigms.items():
            if suffixes["<suffix>"].split("_")[0] in lemma_suffixes:
                matching.add(paradigm)
                continue
        return matching

    def suitable_paradigms(self, suffixes: Set[str]) -> Dict[str, Set[str]]:
        """Filters given set of suffixes for each paradigm in database."""
        par = dict()
        for paradigm, par_suffixes in self.paradigms.items():
            common = suffixes.intersection(par_suffixes["affixes"].keys())
            if common:
                par[paradigm] = common
        return par

    def form_spread(self, freq_list: str) -> None:
        """Computes relative spread of given forms in corpus characterized by its alphabetically sorted
        filtered frequency list."""
        with open(freq_list, encoding="utf-8") as fl:
            for line in fl:
                values = line.strip().split()
                paradigm, word = values[0], values[1]
                self.paradigms[paradigm]["spread"] = self.paradigms[paradigm].get("spread", dict())
                self.paradigms[paradigm]["spread"].update(
                    {word[len(paradigm) - len(self.paradigms[paradigm]["<suffix>"]):]: float(values[2])})


def paradigm_db(par_file: str) -> PARADIGM_AFFIXES_GROUPS:
    """Creates database from data in paradigm file."""
    translated = dict()
    paradigms, affixes = read_paradigms(par_file)
    for paradigm, forms in paradigms.items():
        translated[paradigm] = dict()
        translated[paradigm]["affixes"] = dict()
        for form, suffixes in forms.items():
            for alias in suffixes:
                for affix in affixes[alias]:
                    suffix = form + affix[0]
                    translated[paradigm]["affixes"][suffix] = translated[paradigm].get(suffix, [])
                    translated[paradigm]["affixes"][suffix].extend(affix[1])
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
    return line.replace("??", "??").replace("??", "??").replace("??", "??").replace("??", "??").replace("??", "??")
