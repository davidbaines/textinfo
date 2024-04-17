""" Replace translations takes three files as input and creates a fourth file.
One original file is copied, then the lines from a source file 'equivalent lines' from a target file are read.
Each original line in the copy is replaced with its translation."""

import argparse
from bs4 import BeautifulSoup
import html
#import itertools
import os
from pathlib import Path
import re
from typing import Tuple, OrderedDict


def main():
    parser = argparse.ArgumentParser(description="Replace text in a file with a translation.")
    
    parser.add_argument("input", type=Path, help="The input file.")
    parser.add_argument("output", type=Path, help="The output file.")
    parser.add_argument("source", type=Path, help="The file with source language lines.")
    parser.add_argument("target", type=Path, help="The file with target language lines.")

    args = parser.parse_args()
    
    if not args.input.is_file:
        print(f"Can't find the input file: {args.input}")
        exit()
        
    if not args.source.is_file:
        print(f"Can't find the source file: {args.source}")
        exit()

    if not args.target.is_file:
        print(f"Can't find the target file: {args.target}")
        exit()

    

    with open(args.input, 'r', encoding='utf-8') as f_in:
        in_lines = f_in.readlines()

    escapes = ["&nbsp;", "&pound;"]
    for i, line in enumerate(in_lines,1):
        unescaped = html.unescape(line)
        if unescaped != line:
            print(i,line,"\n",i,html.escape(line))
            continue

        # for escape in escapes:
        #     if escape in line:
        #         print(line,"\n",html.escape(line))
        #         continue

    exit()

    line.replace("&pound;" , "")
    
    count = 0
    out_lines = []

    with open(args.source, 'r', encoding='utf-8') as f_source, open(args.target, 'r', encoding='utf-8') as f_target: 
        for s, t in zip(f_source, f_target):
            s_original = s.strip()
            t_original = t.strip()
            s = html.escape(s_original)
            t = html.escape(t_original)
            if s != s_original :
                print(f"s o: {s_original}")
                print(f"s e: {s}")
                exit()
            if t != t_original :
                print(f"t o: {t_original}")
                print(f"t e: {t}")

            for line in in_lines:
                new_line = re.sub(s, t, line)
                if new_line != line:
                    out_lines.append(new_line)
                    count += 1
                else:
                    out_lines.append(line)

    print(out_lines)
    print(f"Made {count} replacements.")
    with open(args.output, 'w', encoding='utf-8', newline='\n') as f_output:
        f_output.writelines(out_lines)


if __name__ == "__main__":
    main()