#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
#import csv
#import datetime as dt
import hanzidentifier
import multiprocessing as mp
import os
import sys
#import unicodedata
from collections import Counter, OrderedDict
#from operator import itemgetter
from pathlib import Path

def count_chars_mp(filename):
    ''' The main function of char_freq is to count the number of times each character appears in files.
        This function reads a single file and returns a Counter for the characters in the file.
        The function only reads utf-8 files. Any non UTF-8 files will throw an error.
        Characters in the lines containing only the "<range>" marker are not counted.
    '''
    
    #print("count_chars entered!\n")
    #print(f"Processing file: {filename}")
    char_count = Counter()
    with open(filename, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
        for line in lines:
            char_count.update(line)

    return {filename:char_count}


def unicode_data(character,count,file=""):
    ''' Count the number of characters that are chinese, simplified and traditional.
    '''
    # The data is stored in a dictionary:
    c = OrderedDict()

    c["char"] = character
    c["count"] = count
    c["simplified"] = ""
    c["traditional"] = ""
    if hanzidentifier.has_chinese(character):
        c["simplified"] = hanzidentifier.is_simplified(character)
        c["traditional"] = hanzidentifier.is_traditional(character)

    if not file == "" :
        c["filename"] = file.name
    return c

def write_csv(outfile, row_data, column_headers = [], overwrite = False):
    '''Write the data to a csv file.
    If column headers are defined overwrite any existing file, so that the column headings are only written once
    at the top of the file.
    If there are no column headers defined then append the rows if there is an existing file.
    '''
    if not column_headers:
        column_headers = row_data.keys()

    if overwrite:
        with open(outfile, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_headers)
            writer.writeheader()
            writer.writerows(row_data)
    else:
        with open(outfile, 'a', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_headers)
            writer.writerows(row_data)
    return None

def get_character_data(char_counts,file=""):
    """ Given a Counter that has counted the occurrences of characters, return a list of dictionaries with
    lots of data about the characters."""
    character_data = []
    for char, count in char_counts.most_common():
        c = unicode_data(char,count,file)
        character_data.append(c)
    return character_data

def main():
    
    parser = argparse.ArgumentParser(description="Write csv reports about the characters found in multiple files.")
    parser.add_argument('--output_folder', type=Path,                                                help="Folder for the output results. The default is the current folder.", required=False)
    parser.add_argument('--input_files',   nargs="+",           default=[],                          help="Files to read. Ignores input folder and extension argument.")
    parser.add_argument("--summary",       type=str,            default="character_summary.csv",     help="The filename for the summary csv file.")
    parser.add_argument("--full",          type=str,            default="character_report.csv",      help="The filename for the summary csv file.")
    
    args = parser.parse_args()
    if not args.output_folder:
        output_folder = Path(os.getcwd())
    else:
        output_folder = Path(args.output_folder)
    
    summary_csv_file = output_folder / args.summary
    detail_csv_file  = output_folder / args.full
    #csv.register_dialect('default')

    if len(args.input_files) > 0:
        files_found = sorted([Path(file) for file in args.input_files])

        print("Found the following files:")
        for file in files_found:
            print(file)
    else :
        print("Please us --input_files to specify files to scan.")
        exit(0)
          
    no_of_cpu = 20
    print(f"Number of processors: {mp.cpu_count()} using {no_of_cpu}")
    pool = mp.Pool(no_of_cpu)
    
    #Keep a running total of the characters seen across all files.
    all_chars = Counter()

    filecount = 0
    sys.stdout.flush()
    
    # Iterate over files_found with multiple processors.
    results = pool.map(count_chars_mp, [file for file in files_found])
    
    pool.close()
    #print(results, "\n" , type(results), "\n", len(results) )     
    #print(f"There are {len(results)} results\n")
    
    for result in results:
        #print("This is a single result:")
        #print(result)
        #print(f"result is a :{type(result)}")
        
        for item in result.items():
            file, char_counter = item
            total_characters = 0
            traditional_only = 0
            simple_only = 0
            both = 0
            neither = 0

            for char, count in char_counter.items():
                total_characters += count
                chinese = hanzidentifier.has_chinese(char)
                if chinese:
                    simple = hanzidentifier.is_simplified(char)
                    traditional = hanzidentifier.is_traditional(char)
                    if simple and traditional:
                        both += count
                    elif simple and not traditional:
                        simple_only += count
                    elif not simple and traditional:
                        traditional_only += count
                else:
                    neither += count
        
        print(f"File {file} contains {total_characters} charaters.")
        print(f"{neither} are not in Chinese script.")
        print(f"{both} are characters that occur in both the Traditional and the Simplified Chinese script.")
        print(f"{simple_only} are characters that occur only in the Simplified script.")
        print(f"{traditional_only} are characters that occur only in the Traditional script.")

                



if __name__ == "__main__":
    main()


    #         # print(f"{file}, {char_counter}\n")
    #         # Update the total character counts for all files.
    #         all_chars.update(char_counter)

    #         #List of dictionaries (one per char) with info.
    #         chars_list = get_character_data(char_counter,file)
    #         #print(chars_list)
            
    #         #Write out the data for this file to the detailled csv file
    #         filecount += 1
    #         if filecount == 1:          #If it is the first writing then write the column headers.
    #             # Set column headers
    #             #chars_list[0][input_folder] = ''
    #             column_headers = chars_list[0].keys()
                
    #             with open(detail_csv_file, 'w', encoding='utf-8', newline='') as csvfile:
    #                 writer = csv.DictWriter(csvfile, fieldnames=column_headers)
    #                 writer.writeheader()
                    
    #                 # And write the data for the first file
    #                 for char_dict in chars_list:
    #                     writer.writerow(char_dict)
                        
    #         else :                      #For subsequent files just write the data.
    #             with open(detail_csv_file, 'a', encoding='utf-8', newline='') as csvfile:
    #                 writer = csv.DictWriter(csvfile, fieldnames=column_headers)
    #                 for char_dict in chars_list:
    #                     writer.writerow(char_dict)
            
    # print(f'Wrote detailed csv file to {detail_csv_file}')

    # all_char_data = get_character_data(all_chars)
    # column_headers = all_char_data[0].keys()
    # write_csv(summary_csv_file, all_char_data, column_headers, overwrite=True)
    # print(f'Wrote summary csv file to {summary_csv_file}')
