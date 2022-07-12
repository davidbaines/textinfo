#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read a text file and attempt to extract proper names.
Keep the names on the same line as they were found, write them to a file.

1) Simplest solution: Save every word that begins with an uppercase letter.
2) Find words that only appear capitalized at the start of a sentence. Remove those. 
3) Provide options for how to deal with punctuation.

"""

import argparse
from collections import Counter
import unicodedata
from pathlib import Path
from pprint import pprint
import re
import string

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

def simple_solution(file):

    names = []
    for line in file:
        line = line.strip("\r\n")
        
        words = strip_punct(line)
        names_on_line = [name for name in filter(is_name, words)]
        names.append(names_on_line)
        
        print(f"\nLine:  {line}")
        print(f"Words: {words}")
        print(f"Names: {names_on_line}")

    return names


def strip_punct(line):

    stripped = []
    words = line.split()
    for word in words:
        result = ''
        for char in word:
            if unicodedata.category(char)[0] == 'L':
                result = result + char
        if result:
            stripped.append(result)
    return stripped


def get_punctuation(file):

    punct = Counter()
    with open(file, 'r', encoding='utf-8', newline='') as file_in:
        for line in file_in:
            for char in line:
                # Count anything other than a letter as punctuation.
                if unicodedata.category(char)[0] != 'L':
                    punct.update(char)
    return punct


def find_names(line):

    names = [word for word in strip_punct(line) if word[0].isupper()]
    return names
    
    
def is_name(word):
    return word[0].isupper()
    

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
            print(f"{name}, {total_count[name]}, {first_count[name]}")
            ignored_names.add(name)
    
    print(f"Found {len(total_count)} title case words.\nFound {len(first_count)} words at the start. There are {len(ignored_names)} words which only appear at the start.")
    
    print(ignored_names,len(ignored_names))
    filtered_names = list()
    for namelist in names:
        filtered_names.append([name for name in namelist if name not in ignored_names])
   
    for namelist in filtered_names:
        if namelist:
            filtered_count.update(namelist)     
    print(f"There are {len(filtered_count)} names remaining.")    
    return  filtered_names
   
def main():

    parser = argparse.ArgumentParser(description="Write file that contains only certain words from the input file. Maintain lines")
    parser.add_argument('input_file',  type=Path, help="Input file to read.")
    parser.add_argument('--output_file', type=Path, help="Output file for words found.")
    parser.add_argument('--report_file', type=Path, help="Specify where to write a summary file.", required = False)
    
    args = parser.parse_args()
    input_file = args.input_file
    
#    print(input_file)  
#    print(output_file)
    
    with open(input_file, 'r', encoding='utf-8', newline='') as file_in:
        if args.output_file:
            output_file = Path(args.output_file)
            with open(output_file, 'w', encoding='utf-8', newline='') as file_out:
                for line in file_in:
                    file_out.write(find_names(line))
        else:
            #punct = get_punctuation(input_file)
            #punct_list = [p for p in get_punctuation(input_file).keys()]
            #punct_str = ''.join(punct_list)
                
            #print(punct_list)
            #print(punct_str)
            
            names = simple_solution(file_in)
            pprint(names[0:9])
            filtered_names = remove_first_only(names)
            for i, filtered_name in enumerate(filtered_names):
                if filtered_name:
                    print(f"{i+1}  {' '.join(filtered_name)}") 
                else:
                    pass

    
if __name__ == "__main__":
    main()