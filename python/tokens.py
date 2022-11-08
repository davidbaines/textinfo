import csv
from collections import Counter
import multiprocessing as mp
from pathlib import Path
import re
from sacremoses import MosesPunctNormalizer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from tqdm import tqdm
from typing import IO, Iterable, Iterator, List, Optional, Tuple, cast, Sequence
from unicodedata import name


detokenized_path = Path('C:/Gutenberg/MT/scripture')
tokenized_path = Path('C:/Gutenberg/MT/experiments/HuggingFace/NLLB_BT-English/tokenized')
report_path = Path('C:/Gutenberg/MT/experiments/HuggingFace/NLLB_BT-English/charfreq')
unknowns_summary  = "unknown_tokens.csv"
unknowns_report   = "unknown_token_by_file.csv"


def count_unknows(detok_file):
    
    unknowns = Counter()
    detok_lines = [mpn.normalize(line) for line in load_corpus(detok_file)]
    tok_file = tokenized_path /  get_simple_tokenized_filename(detok_file)
    tok_lines  = [line for line in load_corpus(tok_file)]

    for detok_line, tok_line in zip(detok_lines,tok_lines):

        if '<unk>' in tok_line:
            #print(f"Tokenizing {input_file.name} line {i+1}")
            #print(tokenized_line)
            #print(norm_line)
            tok_chars = ''.join(tokenized_line.split('unk'))
            unknown_chars = set(remove_chars(detok_line,tok_chars))
            #print(unknown_chars)
            for char in unknown_chars:
                unknowns[char] += norm_line.count(char)

    return {tok_file: unknowns}


def get_simple_tokenized_filename(input_file):
    return 'token__' + input_file.name

def load_corpus(corpus_path: Path) -> Iterator[str]:
    with corpus_path.open("r", encoding="utf-8-sig") as in_file:
        for line in in_file:
            line = line.strip()
            yield line


def char_name(char):

    if char == '':
        return 'Empty string'

    elif len(char) > 1:
        return "Multiple characters"

    elif len(char) == 1: 
        try:
           char_name = name(char)
        except:
           char_name = "No name found."
    else: 
        return "Unknown error getting name"
        
    return char_name

def remove_chars(line, chars):
    char_set = set(chars)
    return ''.join([c for c in line if c not in char_set])


def main():
    mpn = MosesPunctNormalizer()
    mpn.substitutions = [(re.compile(r), sub) for r, sub in mpn.substitutions]
    # Simplified tokenize, no src or target langs.

    detokenized_files = sorted([file for file in detokenized_path.glob("*.txt")])
    print(f"Found {len(detokenized_files)} detokenized files.")

    no_of_cpu = mp.cpu_count() - 2
    print(f"Number of processors available: {mp.cpu_count()} using {no_of_cpu}")
    pool = mp.Pool(no_of_cpu)

    results = pool.map(count_unknows, [file for file in detokenized_files])
    pool.close()

    made_by = "File produced by https://github.com/davidbaines/textinfo/tree/master/python/tokens.py\n"
    all_unknowns = Counter()
    for tokenized_file, unknowns in results.items():
        all_unknowns.update(unknowns)
        unk_report_lines = [f"{made_by}", "Char, Count, Unicode point, Unicode name, File\n"]
                
        if len(unknowns) > 0:
            for char,count in unknowns.most_common():
                unk_report_lines.append(f"{char},{count},{char_name(char)},{ord(char)},{tokenized_file.name}\n")
    
    unk_report_file   = report_path / unknowns_report
    with open(unk_report_file, 'w', encoding='utf-8', newline='\n') as unk_report:
        unk_report.writelines(unk_report_lines)
    print(f"Wrote the detailed report to {unk_report_file}")


    unk_summary_file  = report_path / unknowns_summary
    with open(unk_summary_file, 'w', encoding='utf-8') as unk_summary:
        unk_summary.write(f"{made_by}")
        unk_summary.write("Char,Count,Unicode name,Codepoint,In vocab,\n")
        for char, count in all_unknowns.most_common():
            unk_summary.write(f"{char},{count},{char_name(char)},{ord(char)},{char in vocab}")

    print(f"Wrote the summary report to {unk_summary_file}")


if __name__ == '__main__':
    main()