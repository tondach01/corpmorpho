"""This is a script for dumping word paradigms from Internetová jazyková příručka (https://prirucka.ujc.cas.cz)"""
import pandas as pd
from typing import Dict, Any


CATEGORIES = {'jednotné číslo': 'nS', 'množné číslo': 'nP', '1. osoba': 'p1', '2. osoba': 'p2', '3. osoba': 'p3',
              'rozkazovací způsob': 'mR', 'příčestí činné': 'mA', 'příčestí trpné': 'mN',
              'přechodník přítomný, m.': 'mS', 'přechodník přítomný, ž. + s.': 'mS', 'přechodník minulý, m.': 'mD',
              'přechodník minulý, ž. + s.': 'mD', '1. pád': 'c1', '2. pád': 'c2', '3. pád': 'c3', '4. pád': 'c4',
              '5. pád': 'c5', '6. pád': 'c6', '7. pád': 'c7'}


def table_dump(word: str):
    """For given word, read corresponding entry in IJP and save its paradigm table to pandas dataframe"""
    import urllib.parse as p
    try:
        df = pd.read_html(f"https://prirucka.ujc.cas.cz/?slovo={p.quote(word)}")[0]
        for i, row in enumerate(df.values):
            for j, val in enumerate(row):
                if str(val)[-1].isdigit():
                    df[j][i] = val[:-1]
                elif str(val) in CATEGORIES.keys():
                    df[j][i] = CATEGORIES[str(val)]
        return df
    except ValueError:
        return None


def df2dict(df) -> Dict[str, Any]:
    """Converts dataframe with paradigm to simple dictionary"""
    if df is None:
        return dict()
    res = dict()
    header = None
    if str(df[0][0]) == "nan":
        header = df.values[0]
    for i in range(len(df.values)):
        if i == 0 and header is not None:
            continue
        for j in range(len(df.values[0])):
            if j == 0:
                continue
            if ',' in str(df[j][i]):
                val = str(df[j][i]).split(', ')
            else:
                val = [str(df[j][i])]
            if header is not None:
                res[header[j]] = res.get(header[j], dict())
                res[header[j]][df[0][i]] = val
            else:
                res[df[0][i]] = val
    return res


def main():
    print(df2dict(table_dump("silný")))


if __name__ == "__main__":
    main()
