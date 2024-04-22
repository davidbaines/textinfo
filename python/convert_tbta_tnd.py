from pathlib import Path
import re
from pprint import pprint

book_name_from_code = {"GEN":"Genesis",
"EXO":"Exodus",
"LEV":"Leviticus",
"NUM":"Numbers",
"DEU":"Deuteronomy",
"JOS":"Joshua",
"JDG":"Judges",
"RUT":"Ruth",
"1SA":"1 Samuel",
"2SA":"2 Samuel",
"1KI":"1 Kings",
"2KI":"2 Kings",
"1CH":"1 Chronicles",
"2CH":"2 Chronicles",
"EZR":"Ezra",
"NEH":"Nehemiah",
"EST":"Esther",
"JOB":"Job",
"PSA":"Psalms",
"PRO":"Proverbs",
"ECC":"Ecclesiastes",
"SNG":"Song of Songs",
"ISA":"Isaiah",
"JER":"Jeremiah",
"LAM":"Lamentations",
"EZK":"Ezekiel",
"DAN":"Daniel",
"HOS":"Hosea",
"JOL":"Joel",
"AMO":"Amos",
"OBA":"Obadiah",
"JON":"Jonah",
"MIC":"Micah",
"NAM":"Nahum",
"HAB":"Habakkuk",
"ZEP":"Zephaniah",
"HAG":"Haggai",
"ZEC":"Zechariah",
"MAL":"Malachi",
"MAT":"Matthew",
"MRK":"Mark",
"LUK":"Luke",
"JHN":"John",
"ACT":"Acts",
"ROM":"Romans",
"1CO":"1 Corinthians",
"2CO":"2 Corinthians",
"GAL":"Galatians",
"EPH":"Ephesians",
"PHP":"Philippians",
"COL":"Colossians",
"1TH":"1 Thessalonians",
"2TH":"2 Thessalonians",
"1TI":"1 Timothy",
"2TI":"2 Timothy",
"TIT":"Titus",
"PHM":"Philemon",
"HEB":"Hebrews",
"JAS":"James",
"1PE":"1 Peter",
"2PE":"2 Peter",
"1JN":"1 John",
"2JN":"2 John",
"3JN":"3 John",
"JUD":"Jude",
"REV":"Revelation"}

book_code_from_name = {v:k for k,v in book_name_from_code.items()}
book_index = [code for code in book_name_from_code.keys()]


def get_book_name(filename):
    
    for book_name in book_code_from_name.keys():
        if book_name.lower() in filename.lower():
            book_code = book_code_from_name[book_name]
            return book_name, book_code
    return None, None

        
def format_bible_text(input_file, book_code):
    
    book_name = book_name_from_code[book_code]
    
    with open(input_file, 'r', encoding='utf-8') as f_in:
        lines = [line.strip() for line in f_in.readlines()]
    
    # Initialize output
    output = [f"\\id {book_code}\n"]
    # Initialize current chapter
    current_chapter = ""
    for line in lines:
        # If the line is empty, skip it
        if not line.strip():
            continue
        # Extract chapter and verse using regex
        match = re.match(rf'{book_name} (\d+):(\d+)', line)
        if match:
            chapter, verse = match.groups()
            # If the chapter has changed, add a chapter marker
            if chapter != current_chapter:
                output.append(f'\n\\c {chapter}\n')
                current_chapter = chapter
            # Add the verse marker and text
            verse_text = line[len(match.group(0)):].strip()
            output.append(f'\\v {verse} {verse_text}\n')
        else:
            # If the line doesn't start with 'Matthew', it's a continuation of the previous verse
            output.append(f'{line}\n')
    return output

folder = Path("E:/Work/Pilot_projects/TBTA/Files_without_tags2/")
#input_file = Path("E:/Work/Pilot_projects/TBTA/Files_without_tags2/Phase 1 text for Matthew(2).txt")
#output_file = Path("E:/Work/Pilot_projects/TBTA/Files_without_tags2/Phase 1 text for Matthew(2).sfm")

input_files = [file for file in folder.glob("*.txt")]

for input_file in input_files:
    book_name, book_code = get_book_name(input_file.name)
    if book_name and book_code:
        print(f"{input_file} looks like it is book {book_name} with code {book_code}")
        book_no = book_index.index(book_code) + 1
    else:
        print(f"Couldn't determine book from {input_file} name. Skipping")
        continue

    output_file = folder / f"{book_no:02}{book_code}TBTA_PH1.sfm"
    
    if output := format_bible_text(input_file, book_code):
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.writelines(output)

        print(f"Wrote output SFM file to {output_file}")