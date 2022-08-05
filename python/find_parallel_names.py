#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read a two extracted Bible files and extract words that begin with uppercase letters.

"""

import argparse
from collections import Counter
import csv
import unicodedata
from pathlib import Path
import re
import string_utils

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

def write_csv(outfile, row_data, column_headers = [], overwrite = False):
    '''Write the data to a csv file.
    If column headers are defined overwrite any existing file, so that the column headings are only written once
    at the top of the file.
    If there are no column headers defined then append the rows to an(y) existing file.
    '''
    
    if overwrite:
        with open(outfile, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_headers)
            writer.writerows(row_data)
    else:
        with open(outfile, 'a', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(row_data)
    print(f'Wrote csv file to {outfile}')
    return None


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

    parser = argparse.ArgumentParser(description="Write file that contains only certain words from the input file. Maintain lines")
    parser.add_argument('file1',  type=Path, help="First input file to read.")
    parser.add_argument('file2',  type=Path, help="Second input file to read.")
    parser.add_argument('--vref', type=Path, default="D:/GitHub/silnlp/silnlp/assets/vref.txt", help="vref.txt file.")
    
    parser.add_argument('--summary_csv', type=Path, help="The summary csv file for pairs found.")
    parser.add_argument('--detail_csv',  type=Path, help="A detailed csv file.", required = False)
    
    args = parser.parse_args()
    file1 = args.file1
    file2 = args.file2
    vref  = args.vref
    summary_csv = args.summary_csv
    detail_csv  = args.detail_csv
    
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2 , open(vref, 'r', encoding='utf-8') as fref:        
        # Read lines in.
        lines1 = f1.readlines()
        lines2 = f2.readlines()
        vrefs = [line.strip() for line in fref.readlines()]
            
    if not len(lines1) == len(lines2) == len(vrefs):
        print("\nWarning: Line counts don't match:")
        print(f"{file1} : {len(lines1)}")
        print(f"{file2} : {len(lines2)}")
        print(f"{vref}  : {len(vrefs)}\n")
        
    # Get the names from each verse.
    names1 = [get_names(line) for line in lines1]
    names2 = [get_names(line) for line in lines2]
    details = [(vref,names1,names2) for (vref,names1,names2) in zip(vrefs,names1,names2)]
    
    #print(details[0:3])
    if detail_csv:
        write_csv(detail_csv, details, column_headers = ["Reference", f"{file1}", f"{file2}"], overwrite = True)
    
    name_pairs = Counter()
    for src_names,trg_names in zip(names1,names2):
        for (src_name,trg_name) in zip(src_names,trg_names):
            #print(src_name,trg_name)
            name_pairs.update([(src_name,trg_name)])
            
    print(f"{name_pairs.most_common(5)}")
    row_data = []
    for item,count in sorted(name_pairs.items()):
        src_name,trg_name = item
        row_data.append([src_name,trg_name,count])
    
    print(row_data[0:3])
    
    if summary_csv:
        write_csv(summary_csv, row_data, column_headers = ["Source name, Target name, Occurrences"], overwrite = True)
                
if __name__ == "__main__":
    main()