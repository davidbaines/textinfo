#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read a text file and attempt to extract proper names.
Keep the names on the same line as they were found, write them to a file.

1) Simplest solution: Save every word that begins with an uppercase letter.
2) Find words that only appear capitalized at the start of a sentence. Remove those. 
3) Provide options for how to deal with punctuation.
4) Read a config file containing pairs of files. Create a comparison of title case words for each pair.
"""

import argparse
from collections import Counter
import csv
import unicodedata
from pathlib import Path
import re

"""
These are the Unicode Categories.
Code	Description
[Cc]	Other, Control
[Cf]	Other, Format
[Cn]	Other, Not Assigned (no characters in the file have this property)
[Co]	Other, Private Use
[Cs]	Other, Surrogate
[LC]	Letter, Cased
[Ll]	Letter, Lowercase
[Lm]	Letter, Modifier
[Lo]	Letter, Other
[Lt]	Letter, Titlecase
[Lu]	Letter, Uppercase
[Mc]	Mark, Spacing Combining
[Me]	Mark, Enclosing
[Mn]	Mark, Nonspacing
[Nd]	Number, Decimal Digit
[Nl]	Number, Letter
[No]	Number, Other
[Pc]	Punctuation, Connector
[Pd]	Punctuation, Dash
[Pe]	Punctuation, Close
[Pf]	Punctuation, Final quote (may behave like Ps or Pe depending on usage)
[Pi]	Punctuation, Initial quote (may behave like Ps or Pe depending on usage)
[Po]	Punctuation, Other
[Ps]	Punctuation, Open
[Sc]	Symbol, Currency
[Sk]	Symbol, Modifier
[Sm]	Symbol, Math
[So]	Symbol, Other
[Zl]	Separator, Line
[Zp]	Separator, Paragraph
[Zs]	Separator, Space

"""


def write_csv(outfile, row_data, column_headers=[], overwrite=False):
    """Write the data to a csv file.
    If column headers are defined overwrite any existing file, so that the column headings are only written once
    at the top of the file.
    If there are no column headers defined then append the rows to an(y) existing file.
    """

    if overwrite:
        with open(outfile, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_headers)
            writer.writerows(row_data)
    else:
        with open(outfile, "a", encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(row_data)
    print(f"Wrote csv file to {outfile}")
    return None


def get_titlecase_words(file_in):

    tc_words = []
    with open(file_in, "r", encoding="utf-8", newline="") as file:
        for line in file:
            line = line.strip("\r\n")
            words = line.split()
            tc_words.append([word for word in strip_punct(line) if word[0].isupper()])
    return tc_words


def get_words(file_in):

    words = []
    with open(file_in, "r", encoding="utf-8", newline="") as file:
        lines = [line.strip("\n") for line in file.readlines()]

        print(lines, len(lines))
        exit()
        for line in file:
            # line = line.strip("\r\n")
            words.append(line)
    return words


def move_punct(lines):

    """
    Split punctuation from the preceding word.
    """

    for line in lines:
        result = ""
        for char in word:
            if unicodedata.category(char)[0] == "L":
                result = result + char
        if result:
            stripped.append(result)
    return stripped


def strip_punct(line):

    stripped = []
    words = line.split()
    for word in words:
        result = ""
        for char in word:
            if unicodedata.category(char)[0] == "L":
                result = result + char
        if result:
            stripped.append(result)
    return stripped


def get_punctuation(file):

    punct = Counter()
    with open(file, "r", encoding="utf-8", newline="") as file_in:
        for line in file_in:
            for char in line:
                # Count anything other than a letter as punctuation.
                if unicodedata.category(char)[0] != "L":
                    punct.update(char)
    return punct


def get_names(lines):

    # Get list of words whose first letter is uppercase per line.
    names = []
    for line in lines:
        names_on_line = [word for word in line if word[0].isupper()]

        # Add a star to the start of the first word - indicate start of verse.
        if names_on_line:
            names_on_line[0] = "*" + names_on_line[0]
        names.append(names_on_line)
    return names


def remove_first_only(names):
    first_count = Counter()
    total_count = Counter()
    filtered_count = Counter()

    ignored_names = set()

    for namelist in names:
        if namelist:
            first_count.update([namelist[0]])
            total_count.update(namelist)
    for name in sorted(first_count):
        if total_count[name] == first_count[name]:
            # print(f"{name}, {total_count[name]}, {first_count[name]}")
            ignored_names.add(name)
    print(
        f"Found {len(total_count)} title case words.\nFound {len(first_count)} words at the start. There are {len(ignored_names)} words which only appear at the start."
    )

    # print(ignored_names,len(ignored_names))
    filtered_names = list()
    for namelist in names:
        filtered_names.append([name for name in namelist if name not in ignored_names])
    for namelist in filtered_names:
        if namelist:
            filtered_count.update(namelist)
    print(f"There are {len(filtered_count)} names remaining.")
    return filtered_names


def main():
    parser = argparse.ArgumentParser(
        description="Find names across extracted Bibles. Write to a file."
    )
    parser.add_argument("--input_folder", type=Path, help="Folder to search")
    parser.add_argument(
        "--output_folder",
        type=Path,
        help="Folder for the output results. The default is the current folder.",
        required=False,
    )
    parser.add_argument(
        "--extension",
        type=str,
        default="txt",
        help="Specify which files to read by extension. The default is 'txt'.",
    )
    parser.add_argument(
        "--book",
        type=str,
        default="txt",
        help="Specify which files to read by extension. The default is 'txt'.",
    )
    parser.add_argument(
        "--input_files",
        nargs="+",
        default=[],
        help="Files to read. Ignores input folder and extension argument.",
    )
    parser.add_argument(
        "--vref",
        type=Path,
        default="D:/GitHub/silnlp/silnlp/assets/vref.txt",
        help="vref.txt file.",
    )
    parser.add_argument(
        "--summary_csv",
        type=str,
        default="names_summary.csv",
        help="The filename for the summary csv file.",
    )
    parser.add_argument(
        "--full_csv",
        type=str,
        default="names_full.csv",
        help="The filename for the full csv file.",
    )

    args = parser.parse_args()
    
    vref = args.vref
    
    if args.output_folder:
        output_folder = Path(args.output_folder)
    else:
        output_folder = Path.cwd()
    summary_csv_file = output_folder / args.summary_csv
    detail_csv_file = output_folder / args.full_csv

    if len(args.input_files) > 0:
        files_found = sorted([Path(file) for file in args.input_files])
        print("\nFound the following files:")
        for file in files_found:
            print(file)
    elif args.input_folder:
        input_folder = args.input_folder
        extension = args.extension

        path_split = Path(input_folder).parts
        folder = path_split[-1]

        # root_Path = Path(root)
        pattern = "".join([r"*.", extension])
        files_found = sorted(input_folder.glob(pattern))
        print(
            f"Found {len(files_found)} files with .{extension} extension in {input_folder}"
        )
    else:
        print("Either --input_folder or --input_files must be specified.")
        exit(0)
          
    
    
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:

    # # Get lines without newlines.
    # lines1 = [line.strip() for line in f1.readlines()]
    # lines2 = [line.strip() for line in f2.readlines()]

    # Deal with any number of files.
    # Problem is that the output won't fit usefully in a single file.
    # If this is to compare all the names across all the extracts then we'd need a file per verse.
    # Each with ~1700 lines, one for each extract

    # How to reduce that?
    # 1 Only deal with Latin script.
    # 2 Report only verses containing names?
    # 3 Select by book at a time rather than whole Bible?
    # ref, filename, names

    with open(file1, "r", encoding="utf-8") as f1, open(
        file2, "r", encoding="utf-8"
    ) as f2, open(vref, "r", encoding="utf-8") as fref:
        # Get list of words per line.
        vrefs = [line.strip() for line in fref.readlines()]
        words1 = [strip_punct(line) for line in f1.readlines()]
        words2 = [strip_punct(line) for line in f2.readlines()]
    if not len(words1) == len(words2) == len(vrefs):
        print("\nWarning: Line counts don't match:")
        print(f"{file1} : {len(words1)}")
        print(f"{file2} : {len(words2)}")
        print(f"{vref}  : {len(vrefs)}\n")
    names1 = get_names(words1)
    names2 = get_names(words2)
    names_by_verse = [
        f"{ref},{names_1},{names_2}\n"
        for (ref, names_1, names_2) in zip(vrefs, names1, names2)
    ]
    print(names_by_verse[0:5])
    with open(data, "w", encoding="utf-8") as fdata:
        fdata.writelines(names_by_verse)
    #    for i in range(0,5):
    #        #print(f"{words1[i]}\n{names1[i]}\n")
    #        #print(f"{words2[i]}\n{names2[i]}\n\n")
    #        print(f"{names1[i]}\n{names2[i]}\n\n")

    name_pairs = Counter()
    for src_names, trg_names in zip(names1, names2):
        for (src_name, trg_name) in zip(src_names, trg_names):
            # print(src_name,trg_name)
            name_pairs.update([(src_name, trg_name)])
    print(f"{name_pairs.most_common(5)}")
    row_data = []
    for item, count in sorted(name_pairs.items()):
        src_name, trg_name = item
        row_data.append([src_name, trg_name, count])
    # print(row_data)

    write_csv(
        output_csv,
        row_data,
        column_headers=["Source name, Target name, Occurrences"],
        overwrite=True,
    )


if __name__ == "__main__":
    main()
