#!/usr/bin/env python3
from typing import Tuple, Dict, List, Set, Union


TAILS = Dict[str, List[Tuple[str, List[str]]]]
FORMS = Dict[str, Union[str, List[str]]]
PARADIGMS_TAIL_GROUPS = Dict[str, FORMS]
MORPH_DATABASE = Dict[str, Dict[str, Dict[str, int]]]
VOCABULARY = Dict[str, str]
SUFFICES_DATABASE = Dict[str, Dict[str, int]]


class MorphDatabase:
    def __init__(self, dic_file: str, par_file: str):
        self.vocab = vocabulary(dic_file)
        self.paradigms = translate_morph_db(par_file)
        self.paradigm_roots()

    def full_database(self) -> MORPH_DATABASE:
        database = dict()
        for lemma, paradigm in self.vocab.items():
            self.add_lemma_forms(lemma, paradigm, database)
        return database

    def add_lemma_forms(self, lemma: str, paradigm: str, database: MORPH_DATABASE) -> None:
        database[lemma] = dict()
        forms = self.all_forms_with_paradigm(lemma, paradigm)
        for form in forms.keys():
            database[lemma][form] = dict()
            for tag in forms[form]:
                database[lemma][form][tag] = 0

    def all_forms(self, lemma: str) -> FORMS:
        paradigm = self.find_paradigm(lemma) if lemma not in self.paradigms.keys() else lemma
        if paradigm:
            return self.all_forms_with_paradigm(lemma, paradigm)
        return dict()

    def all_forms_with_paradigm(self, lemma: str, paradigm: str) -> FORMS:
        forms = dict()
        root = self.word_root(lemma, paradigm)
        for form, tags in self.paradigms[paradigm].items():
            if form == "<suffix>":
                continue
            forms[root+form] = forms.get(root+form, [])
            forms[root+form].extend(tags)
        return forms

    def word_root(self, lemma: str, paradigm: str) -> str:
        if lemma.endswith("ný") or (lemma.endswith("cí") and not lemma.endswith("ící")) or lemma.endswith("tý") \
                or lemma.endswith("ový") or lemma.endswith("lý") \
                or (lemma.endswith("ní") and not lemma.endswith("ání") and not lemma.endswith("ení")):
            return lemma[:-1]
        common_suffix = len(self.paradigms[paradigm]["<suffix>"])
        if common_suffix == 0:
            return lemma
        return lemma[:-common_suffix]

    def word_form(self, lemma: str, tag_part: str) -> Set[str]:
        found_forms = set()
        for form in self.all_forms(lemma).keys():
            for tag in form:
                if tag_part in tag:
                    found_forms.add(form)
        return found_forms

    def lemma_tag(self, form: str) -> List[Dict[str, str]]:
        found_lt = []
        for lemma, paradigm in self.vocab.items():
            root = self.word_root(lemma, paradigm)
            if form.startswith(root):
                self.add_similar_forms(root, paradigm, form, found_lt)
        return found_lt

    def add_similar_forms(self, root: str, paradigm: str, form: str, found_lt: List[Dict[str, str]]) -> None:
        for paradigm_form, tags in self.paradigms[paradigm].items():
            if paradigm_form == "<suffix>":
                continue
            if root + paradigm_form == form:
                found_lt += [dict(lemma=(root + self.paradigms[paradigm]["<suffix>"]), tag=tag) for tag in tags]

    def find_paradigm(self, lemma: str) -> str:
        return self.vocab.get(lemma, "")

    def has_full_paradigm(self, lemma: str, k_tag: int) -> bool:
        all_tags = []
        for tags in self.all_forms(lemma).values():
            all_tags.extend(tags)
        if not all_tags:
            return False
        needed = []
        if k_tag == 1:
            for i in range(1, 8):
                needed.extend([f"nSc{i}", f"nPc{i}"])
            for tag in all_tags:
                if tag[-2] != "c":
                    continue
                t = tag[-4:]
                if t in needed:
                    needed.remove(t)
        elif k_tag == 2:
            for i in range(1, 8):
                needed.extend([f"gMnSc{i}", f"gMnPc{i}", f"gFnSc{i}", f"gFnPc{i}", f"gNnSc{i}", f"gNnPc{i}"])
            for tag in all_tags:
                if tag[-4] != "c":
                    continue
                t = tag[-8:-2]
                if t in needed:
                    needed.remove(t)
        elif k_tag == 5:
            for i in range(1, 4):
                needed.extend([f"p{i}nS", f"p{i}nP"])
            for tag in all_tags:
                if tag[-2] != "n":
                    continue
                t = tag[-4:]
                if t in needed:
                    needed.remove(t)
        else:
            return True
        return not needed

    def matching_paradigms(self, lemma: str) -> List[str]:
        matching = []
        for paradigm, suffices in self.paradigms.items():
            if lemma.endswith(suffices["<suffix>"]):
                matching.append(paradigm)
        return matching

    def paradigm_roots(self) -> None:
        for paradigm, suffices in self.paradigms.items():
            found = False
            for suffix, tags in suffices.items():
                for tag in tags:
                    if ("c1" in tag and "nS" in tag) or "mF" in tag:
                        self.paradigms[paradigm]["<suffix>"] = suffix
                        found = True
                        break
                if found:
                    break
            if not found:
                self.paradigms[paradigm]["<suffix>"] = longest_fitting_suffix(paradigm.split("_")[0], suffices)


def longest_fitting_suffix(paradigm: str, suffices: FORMS) -> str:
    longest = ""
    for suffix in suffices.keys():
        if paradigm.endswith(suffix) and len(suffix) > len(longest):
            longest = suffix
    return longest


def translate_morph_db(par_file: str) -> PARADIGMS_TAIL_GROUPS:
    translated = dict()
    paradigm_db, tails = read_paradigms(par_file)
    for paradigm, forms in paradigm_db.items():
        translated[paradigm] = dict()
        for form, tail_groups in forms.items():
            for tg in tail_groups:
                for ending in tails[tg]:
                    suffix = form + ending[0]
                    translated[paradigm][suffix] = translated[paradigm].get(suffix, [])
                    translated[paradigm][suffix].extend(ending[1])
    return translated


def suffix_database(full_db: MORPH_DATABASE) -> SUFFICES_DATABASE:
    suffices = dict()
    for lemma, forms in full_db.items():
        for form, tags in forms.items():
            compressed_form = compress_word(lemma.split("_")[0], form)
            if compressed_form not in suffices:
                suffices[compressed_form] = dict()
            for tag, count in tags.items():
                if tag not in suffices[compressed_form]:
                    suffices[compressed_form][tag] = 0
                suffices[compressed_form][tag] += count
    return suffices


def compress_word(lemma: str, word: str) -> str:
    common = lemma
    while not word.startswith(common):
        common = common[:-1]
    return f"{lemma[len(common):]}|{word[len(common):]}"


def vocabulary(dic_file: str) -> VOCABULARY:
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


def read_paradigms(par_file: str) -> Tuple[PARADIGMS_TAIL_GROUPS, TAILS]:
    # tails -> koncovky
    tails = dict()
    database = dict()
    current = ""
    p = open(par_file, "r", encoding="windows-1250")
    for line in p:
        line = correct_encoding(line)
        if line.startswith("="):
            current = line.lstrip("=").rstrip()
            tails[current] = list()
        elif line.startswith("\t{"):
            vals = line.lstrip("\t{").rstrip("}\n").split(",")
            tails[current].append(("" if vals[0] == "_" else vals[0], [vals[1].strip()]))
        elif line.startswith("+"):
            current = line.lstrip("+").rstrip()
            database[current] = dict()
        elif line.startswith("\t<"):
            vals = line.strip().split()
            database[current][vals[0].lstrip("<").rstrip(">")] = [v.rstrip(",") for v in vals[1:]]
    p.close()
    return database, tails


def correct_encoding(line: str) -> str:
    return line.replace("ą", "š").replace("ľ", "ž").replace("»", "ť").replace("®", "Ž").replace("©", "Š")


def main() -> MorphDatabase:
    return MorphDatabase("current.dic", "current.par")


if __name__ == "__main__":
    import time
    start = time.time()
    md = main()
    # print(md.matching_paradigms("beránek"))
    x = md.full_database()
    print(f"{len(md.paradigms)} paradigms, {len(md.vocab)} words")
    print(f"finished in {round(time.time() - start, 3)}s")
