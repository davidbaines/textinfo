#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Given a verse reference and extract file get the uppercase words that occur.
Print a line in the format vref, filename, uppercase words.

"""
import argparse
import csv
import unicodedata
from pathlib import Path
import re
import string_utils
#import has_sentence_ending

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

def get_names(line):

    stripped = []
    words = line.split()
    
    #The first word is always considered to start the sentence
    starts_sentence = True
    
    for word in words:
        result = ""
        
        for char in word:
            if unicodedata.category(char)[0] == "L":
                result = result + char
                
        if result and starts_sentence:
            result =  result + "@"
            
        if result:        
            stripped.append(result)

        if string_utils.has_sentence_ending(word) :
            starts_sentence = True
        else :
            starts_sentence = False
            
    names = [word for word in stripped if word[0].isupper()]
    # Move the @ to the start of the word.
    names = ['@' + name[:-1] if name[-1] is '@' else name for name in names]
    return names


def main():
    parser = argparse.ArgumentParser(
        description="Find names across extracted Bibles. Write to a file."
    )
    parser.add_argument("file", type=Path, help="Extract file to read.")
    parser.add_argument(
        "verse",
        type=str,
        help="Specify which verse in this format: GEN 12:14",
    )
    parser.add_argument(
        "--vref",
        type=Path,
        default="D:/GitHub/silnlp/silnlp/assets/vref.txt",
        help="vref.txt file.",
    )

    args = parser.parse_args()
    file_in = args.file
    verse = args.verse
    vref = args.vref
              
    # # Get lines without newlines.
    # lines1 = [line.strip() for line in f1.readlines()]
    # ref, filename, names

    with open(file_in, "r", encoding="utf-8") as f1, open(vref, "r", encoding="utf-8") as fref:
        # Read lines in.
        lines = f1.readlines()
        vrefs = [line.strip() for line in fref.readlines()]
            
    if not len(lines) == len(vrefs):
        print("\nWarning: Line counts don't match:")
        print(f"{file_in} : {len(lines)}")
        print(f"{vref}  : {len(vrefs)}\n")
        
    # Find the index of the verse reference.
    line_no = vrefs.index(verse)
    line = lines[line_no]
    
    print(f"{line}")
    print(f"{get_names(line)}")
    

if __name__ == "__main__":
    main()
