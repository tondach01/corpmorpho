#!/usr/bin/env python3
import sys
import os
import re


def main():
    args = sys.argv
    args.pop(0)
    if not args:
        return
    f = open(args[0], "r", encoding="utf-8")
    out = open(f"desam{os.sep}prevert_" + args[0].split('\\')[-1], "w", encoding="utf-8")
    buf = ""
    for line in f:
        if line.startswith("<"):
            if line.startswith("</"):
                buf = re.sub(r"\s([.,;?!)])", r"\1", buf)
                buf = re.sub(r"([(])\s", r"\1", buf)
                print(buf.strip(), file=out)
                out.write(line)
                buf = ""
            else:
                out.write(line.split()[0].lstrip(">") + ">\n")
            continue
        word = line.split()[0]
        buf += f" {word}"
    out.close()
    f.close()


if __name__ == "__main__":
    main()
