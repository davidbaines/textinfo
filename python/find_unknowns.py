# -*- coding: utf-8 -*-
# NLLB_missing_tokens.ipynb
# Compare two files and find the characters corresponding to <unk> tokens.

import multiprocessing as mp
import re
from collections import Counter, defaultdict
from csv import DictWriter
from pathlib import Path
from typing import IO, Iterable, Iterator, List, Optional, Sequence, Tuple, cast

import boto3
from sacremoses import MosesPunctNormalizer
from tqdm import tqdm


def read_s3_text_file(bucket, key):
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)
    data = response["Body"].read().decode("utf-8")  # decoding the bytes to string
    return data


mpn = MosesPunctNormalizer()
mpn.substitutions = [(re.compile(r), sub) for r, sub in mpn.substitutions]


def get_files_lines(tokenized_file, detokenized_file):
    with open(tokenized_file, "r", encoding="utf-8") as tok, open(
        detokenized_file, "r", encoding="utf-8"
    ) as detok:
        tok_lines = [line.strip() for line in tok.readlines()]
        detok_lines = [line.strip() for line in detok.readlines()]
    return tok_lines, detok_lines


def remove_chars(line, chars):
    char_set = set(chars)
    return "".join([c for c in line if c not in char_set])


def count_unknowns(tokenized_file, detokenized_file, token):

    unknowns = Counter()
    with open(tokenized_file, "r", encoding="utf-8") as tok, open(
        detokenized_file, "r", encoding="utf-8"
    ) as detok:
        tok_lines = tok.readlines()
        detok_lines = detok.readlines()

        for i, (tok_line, detok_line) in enumerate(zip(tok_lines, detok_lines)):
            tokens_found = re.findall(f"{token}", tok_line)

            if tokens_found:
                # Remove unnecessary characters.

                merged_tok_line = remove_chars(
                    mpn.normalize(tok_line), ["\n", " ", "▁"]
                )
                merged_detok_line = remove_chars(mpn.normalize(detok_line), ["\n", " "])

                unknown_tokens = merged_detok_line
                common_strings = merged_tok_line.split(token)

                for common_string in common_strings:
                    unknown_tokens = unknown_tokens.replace(common_string, "")
                # print(f"Unknown tokens are {unknown_tokens}")
                # print(f"{merged_detok_line}")
                # print(f"{merged_tok_line}")
                # print(f"Common strings are {common_strings}")

                unknowns.update(unknown_tokens)

    return unknowns


def alt_count_unknowns(tokenized_file, detokenized_file, token):

    unknowns = Counter()
    with open(tokenized_file, "r", encoding="utf-8") as tok, open(
        detokenized_file, "r", encoding="utf-8"
    ) as detok:
        tok_lines = tok.readlines()
        detok_lines = detok.readlines()

        for i, (tok_line, detok_line) in enumerate(zip(tok_lines, detok_lines)):
            tokens_found = re.findall(f"{token}", tok_line)

            if tokens_found:

                # Remove known characters from detok line:
                unknown_chars = remove_chars(mpn.normalize(detok_line), tok_line)
                if len(unknown_chars) == len(tokens_found):
                    unknowns.update(unknown_chars)
                else:
                    continue
                    print(f"\nIn line {i+1} of {tokenized_file.name}:")
                    print(
                        f"Found {len(tokens_found)} <unk> tokens in the tokenized line. Found {len(unknown_chars)} characters in the untokenized line that were not in the detokenized line."
                    )
                    print(f"Unknown tokens are {unknown_chars}")
                    print(f"{mpn.normalize(detok_line).strip()}")
                    print(f"{mpn.normalize(tok_line).strip()}")

    return unknowns


def second_alt_count_unknowns(arguments):
    tokenized_file, detokenized_file, token = arguments

    with open(tokenized_file, "r", encoding="utf-8") as tok, open(
        detokenized_file, "r", encoding="utf-8"
    ) as detok:
        tok_lines = tok.readlines()
        detok_lines = detok.readlines()

        tok_char = set()
        detok_char = set()

        for tok_line, detok_line in zip(tok_lines, detok_lines):
            tok_strings = tok_line.split(token)
            for tok_string in tok_strings:
                tok_char += tok_strings


def find_lines_with_tokens(tokenized_file, detokenized_file, tokens):

    tok_lines = []
    detok_lines = []
    tokenized_lines, detokenized_lines = get_files_lines(
        tokenized_file, detokenized_file
    )
    for tokenized_line, detokenized_line in zip(tokenized_lines, detokenized_lines):
        for token in tokens:
            if token in tokenized_line:
                tok_lines.append(tokenized_line)
                detok_lines.append(detokenized_line)

    return tok_lines, detok_lines


def count_original_tokens(tokenized_lines, detokenized_lines, token):

    token_count = Counter()
    for tokenized_line, detokenized_line in zip(tokenized_lines, detokenized_lines):
        # Remove unnecessary characters.
        merged_tok_line = tokenized_line.replace(" ", "").replace("▁", " ").strip()
        # print(detokenized_line)
        # print(tokenized_line)
        # print(merged_tok_line)
        reduced_tok_line = ""
        for character in detokenized_line:
            if character not in merged_tok_line:
                reduced_tok_line += character
        reduced_tok_line = reduced_tok_line.strip()
        token_count.update(reduced_tok_line)

        # print(reduced_tok_line.strip())
        # print(token_count)
        # exit()
    return token_count


def main():

    token = "<unk>"
    tokens = [token]
    all_unknowns = dict()

    # src_langs = ['eng_Latn']
    # trg_lang='eng_Latn'

    detokenized_path = Path(
        "E:/Work/Pilot_projects/Nepal/Thami/NLLB.1.3B.npi_NNRV-thf_THAMI.NT"
    )
    root_path = Path(
        "E:/Work/Pilot_projects/Nepal/Thami/NLLB.1.3B.npi_NNRV-thf_THAMI.NT"
    )
    tokenized_path = root_path  # / 'tokenized'
    output_path = root_path  # / 'unknown_tokens'
    summary_csv_file = output_path / "unk_summary.csv"
    detail_csv_file = output_path / "unk_details.csv"

    pairs = []
    splits = ["train", "val", "test"]
    for split in splits:
        for src_or_trg in ["src", "trg"]:
            pairs.append(f"{split}.{src_or_trg}")

    for pair in pairs:
        print(f"{pair}.txt", f"{pair}.detok.txt")
        tokenized_file = root_path / f"{pair}.txt"
        detokenized_file = root_path / f"{pair}.detok.txt"
        if tokenized_file.is_file() and detokenized_file.is_file():
            tok_lines, detok_lines = find_lines_with_tokens(
                tokenized_file, detokenized_file, tokens
            )
            token_count = count_original_tokens(tok_lines, detok_lines, token)
            print(tokenized_file)
            print(detokenized_file)
            print(token_count)

    #     if tokenized_file.is_file():
    #         #print(f"Finding unknown tokens in {tokenized_file.name}")
    #         unknowns = count_unknowns(tokenized_file,detokenized_file,token)
    #         all_unknowns[tokenized_file] = unknowns
    #     else:
    #         print(f"{tokenized_file.name} doesn't exist. Skipping")

    # summary_count = Counter()
    # summary_lines = [f"Unknown tokens of the form '{token}' found in files in {tokenized_path} and the corresponding charater from the untokenized file in {detokenized_path}.\n", \
    #     "Token, Count\n"]

    # detail_lines  = [f"Unknown tokens of the form '{token}' found in {tokenized_path} and their corresponding charater from the untokenized file in {detokenized_path}.\n",\
    #     "Token,Count,Filename\n"]

    # #print("These are the unknown tokens:\n")
    # for file, counts in all_unknowns.items():

    #     # Update the total unknown counts for all files.
    #     summary_count.update(counts)

    #     #print(f"{file}, {counts}\n")
    #     if len(counts) == 0:
    #         detail_lines.append(f"No unknown tokens,0,{file.name}\n")

    #     else:
    #         for token, count in counts.most_common():
    #             detail_lines.append(f"{token},{count},{file.name}\n")
    #             #print(f"This is a detailled line: {detail_lines[-1]}")

    # with open(detail_csv_file, 'w', encoding='utf-8', newline='\n') as detail_csv:
    #     detail_csv.writelines(detail_lines)

    # print(f'Wrote detailed csv file to {detail_csv_file}')

    # And write the data for the first file
    # with open(detail_csv_file, 'a', encoding='utf-8', newline='') as csvfile:
    #    writer = csv.DictWriter(csvfile, fieldnames=column_headers)
    #    for char_dict in chars_list:
    #        writer.writerow(char_dict)

    # for token,count in summary_count.most_common():
    #     summary_lines.append(f"{token},{count}\n")

    # with open(summary_csv_file, 'w', encoding='utf-8', newline='\n') as summary_csv:
    #     summary_csv.writelines(summary_lines)

    # print(f'Wrote summary csv file to {summary_csv_file}')

    # #print(all_unknowns)
    # #print(type(all_unknowns))


if __name__ == "__main__":
    main()
