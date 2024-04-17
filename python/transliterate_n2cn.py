#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import string
import unicodedata
from pathlib import Path
from pprint import pprint

import chardet
from tqdm import tqdm


def _count_generator(reader, file):
    b = reader(1024 * 1024)
    while b:
        yield b
        b = reader(1024 * 1024)

    with open(file, "rb") as fp:
        c_generator = _count_generator(fp.raw.read)
        # count each \n
        count = sum(buffer.count(b"\n") for buffer in c_generator)
        # print('Total lines:', count + 1)
    return count + 1


def count_lines(file):
    return sum(1 for line in open(file, "r"))


def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        rawdata = f.read()
    result = chardet.detect(rawdata)
    return result["encoding"]


def detect_delimiter(file, encoding):

    # Open the file with automatic encoding detection
    with open(file, "r", encoding=encoding) as f:
        first_line = f.readline()

    if len(first_line.strip()) != 3:
        print(
            f"Error: The first line '{first_line}' of the transliteration file {file} does not have exactly three characters."
        )
        exit()

    return first_line[1]  # The second character is the delimiter


def find_common_indices(keys, values):
    common_items = set(keys) & set(values)
    common_indices = []

    for item in common_items:
        item_indices_in_keys = [i for i, x in enumerate(keys) if x == item]
        item_indices_in_values = [i for i, x in enumerate(values) if x == item]

        common_indices.append((item, item_indices_in_keys, item_indices_in_values))

    return common_indices


def read_char_swaps_tsv(file_path, delimiter=None, encoding=None):

    if not encoding:
        encoding = detect_encoding(file_path)

    if not delimiter:
        delimiter = detect_delimiter(file_path, encoding=encoding)

    keys = []
    values = []
    ok = True

    with open(file_path, "r", encoding=encoding) as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            if len(row) == 2:
                keys.append(row[0])
                values.append(row[1])
            else:
                print("Warning: A line does not have exactly two fields.")
                ok = False
                continue

    if len(keys) != len(values):
        print("Warning: The keys and values lists are not of equal length.")
        ok = False

    for i in range(len(keys)):
        if keys[i] == values[i]:
            print(f"Warning: Key and value {keys[i]} at position {i+1} are identical.")
            ok = False

        for j in range(i + 1, len(keys)):
            if keys[i] == keys[j]:
                print(
                    f"Warning: Source character {keys[i]} at position {i+1} maps to {values[i]} and also to {values[j]} at position {j+1}."
                )
                ok = False

    common = set(keys) & set(values)
    if common:
        ok = False
        common_indices = find_common_indices(keys, values)
        for item, key_indices, value_indices in common_indices:
            print(f"The item '{item}' is common in both lists.")
            print(
                f"It appears at the following indices in the 'keys' list: {key_indices}"
            )
            print(
                f"It appears at the following indices in the 'values' list: {value_indices}"
            )

    if ok:
        return keys, values
    else:
        exit()

def get_transliteration(char_swaps_file, reverse):
    keys, values = read_char_swaps_tsv(char_swaps_file)

    forward_char_transliteration = {k: v for k, v in zip(keys, values)}
    reverse_char_transliteration = {v: k for k, v in zip(keys, values)}

    forward_transliteration = {
        ord(k): ord(v) for k, v in forward_char_transliteration.items()
    }
    reverse_transliteration = {
        ord(k): ord(v) for k, v in reverse_char_transliteration.items()
    }

    if reverse:
        transliteration = reverse_transliteration
    else:
        transliteration = forward_transliteration
    
    return transliteration


def transliterate(input_file, transliteration, output_file=None):

    with open(input_file, "r", encoding="utf-8", newline="") as file_in:
        if output_file:
            with open(output_file, "w", encoding="utf-8", newline="") as file_out:
                for line in file_in:
                    file_out.write(line.translate(transliteration))
            print(f"Wrote out the transliterated file to {output_file}")
        else:
            for line in file_in:
                print(line.translate(transliteration))


def parse_args():

    parser = argparse.ArgumentParser(
        description="Transliterate from Yi to Chinese characters or the reverse."
    )
    parser.add_argument(
        "char_swaps_file",
        type=Path,
        help="Transliteration csv or tsv file with two columns of unique single characters.",
    )
    parser.add_argument(
        "--input_file",
        type=Path,
        help="Input file or folder to transliterate. If a folder specify a file extension.",
        required=False,
    )
    parser.add_argument(
        "--output_file",
        type=Path,
        help="Output file, if not specifed transliterated files will be saved in the same folder as the input file.",
        required=False,
    )
    parser.add_argument(
        "--input_folder",
        type=Path,
        help="Input folder, will transliterate all files with the given extension.",
        required=False,
    )
    parser.add_argument(
        "--output_folder",
        type=Path,
        help="Output folder, if not specifed transliterated files will be saved in the same folder as the input file.",
        required=False,
    )
    parser.add_argument(
        "--ext",
        type=Path,
        help="Filter input files to include only those with this extension.",
        default="txt",
    )
    parser.add_argument(
        "--show_map",
        default=False,
        action="store_true",
        help="Show transliteration map and exit.",
    )
    parser.add_argument(
        "--reverse",
        default=False,
        action="store_true",
        help="Transliterate in the reverse direction.",
    )

    args = parser.parse_args()

    char_swaps_file = Path(args.char_swaps_file)
    input_file = Path(args.input_file) if args.input_file else None
    output_file = Path(args.output_file) if args.output_file else None
    input_folder = Path(args.input_folder) if args.input_folder else None
    output_folder = Path(args.output_folder) if args.output_folder else None

    if not input_file and not input_folder:
        parser.error("Either an input_file or input_folder must be provided.")

    if input_file and input_folder:
        parser.error("Only an input_file or input_folder must be provided, but not both.")

    if input_file and output_file:
        files_to_process = zip([input_file], [output_file])

    if input_folder and output_folder:
        if not input_folder.is_dir():
            parser.error(f"Can't find --input_folder: {input_folder}.")
        if not output_folder.is_dir():
            parser.error(f"Can't find --output_folder: {output_folder}.")

        pattern = f"*.{args.ext}"
        input_files = [
            input_file
            for input_file in input_folder.rglob(pattern)
            if input_file.is_file()
        ]
        output_files = [
            output_folder / (input_file.stem + "_translit" + input_file.suffix)
            for input_file in input_files
        ]
        files_to_process = zip(input_files, output_files)

    if not input_folder and not input_file.is_file():
        parser.error(f"Can't find --input_file: {input_file}.")

    if not char_swaps_file.is_file():
        parser.error(f"Can't find the char_swaps_file: {char_swaps_file}.")

    keys, values = read_char_swaps_tsv(char_swaps_file)

    forward_char_transliteration = {k: v for k, v in zip(keys, values)}
    reverse_char_transliteration = {v: k for k, v in zip(keys, values)}

    forward_transliteration = {
        ord(k): ord(v) for k, v in forward_char_transliteration.items()
    }
    reverse_transliteration = {
        ord(k): ord(v) for k, v in reverse_char_transliteration.items()
    }

    if args.reverse:
        transliteration = reverse_transliteration
    else:
        transliteration = forward_transliteration

    if args.show_map:
        # name_lines = [f"{unicodedata.name(chr(key))} -> {unicodedata.name(chr(transliteration[key]))}" for key in transliteration.keys()]
        char_lines = [
            f"{chr(key)} -> {chr(transliteration[key])}"
            for key in transliteration.keys()
        ]
        pprint(char_lines)
        exit(0)

    return transliteration, files_to_process

def parse_args2():
    parser = argparse.ArgumentParser(
        description="Transliterate characters in either direction as specified."
    )
    
    # Group related arguments
    file_group = parser.add_argument_group('file arguments')
    option_group = parser.add_argument_group('optional arguments')

    file_group.add_argument(
        "char_swaps_file",
        type=Path,
        help="Transliteration csv or tsv file with two columns of unique single characters.",
    )
    file_group.add_argument(
        "--input_file",
        type=Path,
        help="Input file to transliterate.",
    )
    file_group.add_argument(
        "--output_file",
        type=Path,
        help="Output file, if not specified, transliterated files will be saved in the same folder as the input file.",
    )
    file_group.add_argument(
        "--input_folder",
        type=Path,
        help="Input folder, will transliterate all files with the given extension.",
    )
    file_group.add_argument(
        "--output_folder",
        type=Path,
        help="Output folder, if not specified, transliterated files will be saved in the same folder as the input file.",
    )
    file_group.add_argument(
        "--ext",
        type=str,
        help="Filter input files to include only those with this extension.",
        default="txt",
    )
    option_group.add_argument(
        "--show_map",
        default=False,
        action="store_true",
        help="Show transliteration map and exit.",
    )
    option_group.add_argument(
        "--reverse",
        default=False,
        action="store_true",
        help="Transliterate in the reverse direction.",
    )

    args = parser.parse_args()

    return args


def validate_args(args):

    if not args.input_file and not args.input_folder:
        raise ValueError("Either an input_file or input_folder must be provided.")

    if args.input_file and args.input_folder:
        raise ValueError("Only an input_file or input_folder must be provided, but not both.")

    if args.input_file and args.output_file:
        if not args.input_file.is_file():
            raise ValueError(f"Can't find --input_file: {args.input_file}.")

    if args.input_folder and args.output_folder:
        if not args.input_folder.is_dir():
            raise ValueError(f"Can't find --input_folder: {args.input_folder}.")
        if not args.output_folder.is_dir():
            raise ValueError(f"Can't find --output_folder: {args.output_folder}.")

    if not args.char_swaps_file.is_file():
        raise ValueError(f"Can't find the char_swaps_file: {args.char_swaps_file}.")

    return args


def prepare_files(args):
    files_to_process = []

    # If there's a single input file and a corresponding output file
    if args.input_file and args.output_file:
        files_to_process.append((args.input_file, args.output_file))

    # If there's an input folder and an output folder
    elif args.input_folder and args.output_folder:
        pattern = f"*.{args.ext}"
        input_files = [
            input_file
            for input_file in args.input_folder.rglob(pattern)
            if input_file.is_file()
        ]
        output_files = [
            args.output_folder / (input_file.stem + "_translit" + input_file.suffix)
            for input_file in input_files
        ]
        files_to_process.extend(zip(input_files, output_files))

    return files_to_process


def main():
    
    args = parse_args2()
    #print(args)
    validate_args(args)
    
    transliteration = get_transliteration(args.char_swaps_file, args.reverse)

    if args.show_map:
        char_lines = [
            f"{chr(key)} -> {chr(transliteration[key])}"
            for key in transliteration.keys()
        ]
        pprint(char_lines)
        exit(0)

    files_to_process = prepare_files(args)

    for input_file, output_file in files_to_process:
        print(f"Processing {input_file} to {output_file}")
        transliterate(input_file, transliteration, output_file)


if __name__ == "__main__":
    main()
