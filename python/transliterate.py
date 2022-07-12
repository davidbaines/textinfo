#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
                  
from pathlib import Path
from pprint import pprint
import string
from tqdm import tqdm
import unicodedata


"""
Transliterate:
ARABIC FATHATAN
ARABIC DAMMATAN
ARABIC KASRATAN
ARABIC FATHA
ARABIC DAMMA
ARABIC KASRA
ARABIC SHADDA
ARABIC SUKUN
ARABIC HAMZA ABOVE
ARABIC LETTER SUPERSCRIPT ALEF
ZERO WIDTH NON JOINER           
ZERO WIDTH JOINER             

# Added for ACW
ARABIC MADDAH ABOVE 1619
ARABIC HAMZA BELOW 1621
ARABIC WAVY HAMZA BELOW 1631

to:

ARABIC LETTER ALEF WITH EXTENDED ARABIC-INDIC DIGIT TWO ABOVE
ARABIC LETTER WAW WITH EXTENDED ARABIC-INDIC DIGIT TWO ABOVE
ARABIC LETTER FARSI YEH WITH EXTENDED ARABIC-INDIC DIGIT TWO ABOVE
ARABIC LETTER YU
ARABIC LETTER OE
ARABIC LETTER U
ARABIC LETTER TAH WITH THREE DOTS BELOW
ARABIC LETTER TAH WITH DOT BELOW
ARABIC TATWEEL WITH OVERSTRUCK HAMZA
ARABIC LETTER LOW ALEF
ARABIC TATWEEL WITH OVERSTRUCK WAW
ARABIC TATWEEL WITH TWO DOTS BELOW

# Added for ACW
ARABIC SMALL HIGH ZAIN 1559
ARABIC SMALL DAMMA 1561
ARABIC SMALL KASRA 1562

"""

source          = [1611,1612,1613,1614,1615,1616,1617,1618,1620,1648,8204,8205,1619,1621,1631]
destination     = [1907,1912,1909,1736,1734,1742,2188,2187,2179,2221,2180,2181,1559,1561,1562]
transliteration = {s:d for s,d in zip(source, destination)}

def _count_generator(reader,file):
    b = reader(1024 * 1024)
    while b:
        yield b
        b = reader(1024 * 1024)

    with open(file, 'rb') as fp:
        c_generator = _count_generator(fp.raw.read)
        # count each \n
        count = sum(buffer.count(b'\n') for buffer in c_generator)
        #print('Total lines:', count + 1)
    return count + 1
    
def count_lines(file):
    return sum(1 for line in open(file,'r'))
    
def main():

    parser = argparse.ArgumentParser(description="Write csv reports about the characters found in multiple files.")
    parser.add_argument('--input_file',  type=Path, help="Input file to transliterate.")
    parser.add_argument('--output_file', type=Path, help="Output file.")
    parser.add_argument('--show_map', default=False, action="store_true", help="Show transliteration map and exit.")
    
    args = parser.parse_args()
    if args.show_map:
        #name_lines = [f"{unicodedata.name(chr(key))} -> {unicodedata.name(chr(transliteration[key]))}" for key in transliteration.keys()]
        char_lines = [f"{chr(key)} -> {chr(transliteration[key])}" for key in transliteration.keys()]
        pprint(char_lines)
        exit(0)
    
    
    input_file = args.input_file
    
        
#    print(input_file)  
#    print(output_file)
    
    with open(input_file, 'r', encoding='utf-8', newline='') as file_in:
        if args.output_file:
            output_file = Path(args.output_file)
            with open(output_file, 'w', encoding='utf-8', newline='') as file_out:
                for line in file_in:
                    file_out.write(line.translate(transliteration))
        else:
            for line in file_in:
                print(line.translate(transliteration))
                
#        print(output_line)
#        if output_line != line:
#            print(line)
#            print(output_line)
    
if __name__ == "__main__":
    main()