#!/usr/bin/env python3
import sys
import morph_database
from typing import TextIO, Dict, List


def read_corpora(corp: TextIO = sys.stdin) -> morph_database.MORPH_DATABASE:
    all_forms = dict()
    for line in corp:
        s = line.rstrip("\n").split("\t")
        if len(s) < 3:
            continue
        word, lemma, tag = s[0], s[1], s[2]
        if lemma == "#num#":
            continue
        if lemma[0].islower():
            word = word.lower()
        all_forms[lemma] = all_forms.get(lemma, dict())
        all_forms[lemma][word] = all_forms[lemma].get(word, dict())
        if tag not in all_forms[lemma][word].keys():
            all_forms[lemma][word][tag] = 0
        all_forms[lemma][word][tag] += 1
    return all_forms


def write_morph_db(morph_db: morph_database.MORPH_DATABASE, out: TextIO = sys.stdout) -> None:
    for lemma in sorted(morph_db.keys()):
        print(f"{lemma}:\n", file=out)
        for word in morph_db[lemma].keys():
            print(f"\t{morph_database.compress_word(lemma, word)}:{morph_db[lemma][word]}", file=out)


def db_stats(morph_db: morph_database.MORPH_DATABASE) -> None:
    unseen, total = 0, 0
    freqs = [0 for _ in range(20)]
    for lemma, forms in morph_db.items():
        for form, tags in forms.items():
            total += 1
            c = sum(tags.values())
            if c == 0:
                unseen += 1
            else:
                for i in range(19, -1, -1):
                    if c >= 2**i:
                        freqs[19-i] += 1
                        break
    print(f"{total} forms in total, {unseen} not present in desam")
    print(freqs)


def compress_tags(tags: Dict[str, int]) -> Dict[str, int]:
    new_tags = dict()
    common = extract_common_tags(tags.copy())
    new_tags["".join(common)] = -1
    for tag, count in tags.items():
        for sub_tag in common:
            tag = tag.replace(sub_tag, "")
        new_tags[tag] = count
    return new_tags


def extract_common_tags(tags: Dict[str, int]) -> List[str]:
    common = []
    sample = tags.popitem()[0]
    for sub_tag in split_by_two(sample):
        all_having = True
        for tag in tags.keys():
            if sub_tag not in tag:
                all_having = False
                break
        if all_having:
            common.append(sub_tag)
    return common


def split_by_two(tag: str) -> List[str]:
    slices = []
    for i in range(len(tag) // 2):
        slices.append(tag[2*i] + tag[2*i + 1])
    return slices


def add_morph_db(source: morph_database.MORPH_DATABASE, target: morph_database.MORPH_DATABASE) -> None:
    for lemma in target.keys():
        if lemma not in source.keys():
            source[lemma] = target[lemma]
            continue
        for word in target[lemma].keys():
            if word not in source[lemma].keys():
                source[lemma][word] = target[lemma][word]
                continue
            for tag in target[lemma][word].keys():
                if tag not in source[lemma][word].keys():
                    source[lemma][word][tag] = target[lemma][word][tag]
                    continue
                source[lemma][word][tag] += target[lemma][word][tag]


def main() -> None:
    from time import time
    start = time()
    args = sys.argv
    args.pop(0)
    print("Reading...")

    morph_db = morph_database.main().full_database()

    for corp in args[:-1]:
        print(corp)
        f = open(corp, "r", encoding="utf-8")
        add_morph_db(morph_db, read_corpora(f))
        f.close()

    print("Reading done, writing...")
    if len(args) > 1:
        out = open(args[-1], "w", encoding="utf-8")
        write_morph_db(morph_db, out)
        out.close()
    else:
        write_morph_db(morph_db)

    db_stats(morph_db)

    duration = round(time() - start)
    print(f"Writing done, finished in {duration // 60}min {duration % 60}s.")


def print_help() -> None:
    print("Usage:\n"
          "\t group_word_forms.py input_corpus (output is implicitly stdout)\n"
          "\t group_word_forms.py input_corpora (as much as you want, separated by space) output_file\n")


if __name__ == "__main__":
    main()
