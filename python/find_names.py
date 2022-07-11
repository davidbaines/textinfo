#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import unicodedata
from pathlib import Path
import string


def find_names(line):

    names = join(' ').[word for word in line.split() if word[0].isupper()]
    return names
   
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
            for line in file_in:
                print(find_names(line))
                
#        print(output_line)
#        if output_line != line:
#            print(line)
#            print(output_line)
    
if __name__ == "__main__":
    main()