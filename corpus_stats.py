from typing import Dict, List
from os import sep
from time import time


def attribute_stat(corpus: str, attr: str, subcategory: str = "") -> Dict[str, int]:
    """Computes frequencies of values of given attribute in corpus"""
    corp = open(corpus, encoding="utf-8")
    stats = dict()
    for line in corp:
        if line.startswith("<"):
            continue
        if len(line.split("\t")) != 3:
            continue
        tag = line.split("\t")[2]
        if subcategory not in tag:
            continue
        if attr in tag:
            val = tag[tag.index(attr)+1]
            stats[val] = stats.get(val, 0) + 1
    corp.close()
    return stats


def stat_tree(corpus: str, attrs: List[str], constraints: List[str]):
    """Computes a tree of frequencies, layers are defined by attrs."""
    corp = open(corpus, encoding="utf-8")
    if not attrs:
        return dict()
    tree = dict()
    for line in corp:
        if line.startswith("<"):
            continue
        if len(line.split("\t")) != 3:
            continue
        tag = line.split("\t")[2]
        if False in map(lambda x: x in tag, constraints):
            continue
        subtree = tree
        for attr in attrs:
            if attr not in tag:
                break
            val = tag[tag.index(attr)+1]
            subtree[attr+val] = subtree.get(attr+val, dict())
            subtree = subtree[attr + val]
            subtree["count"] = subtree.get("count", 0) + 1
            if subtree.get("sub", None) is None:
                subtree["sub"] = dict()
            subtree = subtree["sub"]
    corp.close()
    return tree


def tree_print(tree, level: int = 0) -> None:
    """Prints given frequency tree in human-readable format"""
    if not tree:
        return
    for atr_val, subtree in tree.items():
        print(level*"\t" + f"{atr_val}: {subtree['count']}")
        tree_print(subtree["sub"], level+1)


def main():
    start = time()
    desam = f"desam{sep}desam"
    tree = stat_tree(desam, ["g", "c", "n"], ["k2"])
    tree_print(tree)
    print(f"finished in {round(time()-start, 3)}s")


if __name__ == "__main__":
    main()
