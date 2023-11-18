import argparse
from pathlib import Path
from pprint import pprint
import shutil
from typing import List, Set, Union

ALL_BOOK_IDS = [
    "GEN",
    "EXO",
    "LEV",
    "NUM",
    "DEU",
    "JOS",
    "JDG",
    "RUT",
    "1SA",
    "2SA",  # 10
    "1KI",
    "2KI",
    "1CH",
    "2CH",
    "EZR",
    "NEH",
    "EST",
    "JOB",
    "PSA",
    "PRO",  # 20
    "ECC",
    "SNG",
    "ISA",
    "JER",
    "LAM",
    "EZK",
    "DAN",
    "HOS",
    "JOL",
    "AMO",  # 30
    "OBA",
    "JON",
    "MIC",
    "NAM",
    "HAB",
    "ZEP",
    "HAG",
    "ZEC",
    "MAL",
    "MAT",  # 40
    "MRK",
    "LUK",
    "JHN",
    "ACT",
    "ROM",
    "1CO",
    "2CO",
    "GAL",
    "EPH",
    "PHP",  # 50
    "COL",
    "1TH",
    "2TH",
    "1TI",
    "2TI",
    "TIT",
    "PHM",
    "HEB",
    "JAS",
    "1PE",  # 60
    "2PE",
    "1JN",
    "2JN",
    "3JN",
    "JUD",
    "REV",
    "TOB",
    "JDT",
    "ESG",
    "WIS",  # 70
    "SIR",
    "BAR",
    "LJE",
    "S3Y",
    "SUS",
    "BEL",
    "1MA",
    "2MA",
    "3MA",
    "4MA",  # 80
    "1ES",
    "2ES",
    "MAN",
    "PS2",
    "ODA",
    "PSS",
    "JSA",  # actual variant text for JOS, now in LXA text
    "JDB",  # actual variant text for JDG, now in LXA text
    "TBS",  # actual variant text for TOB, now in LXA text
    "SST",  # actual variant text for SUS, now in LXA text, 90
    "DNT",  # actual variant text for DAN, now in LXA text
    "BLT",  # actual variant text for BEL, now in LXA text
    "XXA",
    "XXB",
    "XXC",
    "XXD",
    "XXE",
    "XXF",
    "XXG",
    "FRT",  # 100
    "BAK",
    "OTH",
    "3ES",  # Used previously but really should be 2ES
    "EZA",  # Used to be called 4ES, but not actually in any known project
    "5EZ",  # Used to be called 5ES, but not actually in any known project
    "6EZ",  # Used to be called 6ES, but not actually in any known project
    "INT",
    "CNC",
    "GLO",
    "TDX",  # 110
    "NDX",
    "DAG",
    "PS3",
    "2BA",
    "LBA",
    "JUB",
    "ENO",
    "1MQ",
    "2MQ",
    "3MQ",  # 120
    "REP",
    "4BA",
    "LAO",
]

NON_CANONICAL_IDS = {
    "XXA",
    "XXB",
    "XXC",
    "XXD",
    "XXE",
    "XXF",
    "XXG",
    "FRT",
    "BAK",
    "OTH",
    "INT",
    "CNC",
    "GLO",
    "TDX",
    "NDX",
}

BOOK_NUMBERS = dict((id, i + 1) for i, id in enumerate(ALL_BOOK_IDS))

FIRST_BOOK = 1
LAST_BOOK = len(ALL_BOOK_IDS)


def book_number_to_id(number: int, error_value: str = "***") -> str:
    if number < 1 or number >= len(ALL_BOOK_IDS):
        return error_value
    index = number - 1
    return ALL_BOOK_IDS[index]


def book_id_to_number(id: str) -> int:
    return BOOK_NUMBERS.get(id.upper(), 0)


def get_books(books: Union[str, List[str]]) -> Set[int]:
    if isinstance(books, str):
        books = books.split(",")
    book_set: Set[int] = set()
    for book_id in books:
        book_id = book_id.strip().strip("*").upper()
        if book_id == "NT":
            book_set.update(range(40, 67))
        elif book_id == "OT":
            book_set.update(range(40))
        else:
            book_num = book_id_to_number(book_id)
            if book_num is None:
                raise RuntimeError("A specified book Id is invalid.")
            book_set.add(book_num)
    return book_set


def is_nt(book_num: int) -> bool:
    return book_num >= 40 and book_num < 67


def is_ot(book_num: int) -> bool:
    return book_num < 40


def is_ot_nt(book_num: int) -> bool:
    return is_ot(book_num) or is_nt(book_num)


def is_book_id_valid(book_id: str) -> bool:
    return book_id_to_number(book_id) > 0


def is_canonical(book: Union[str, int]) -> bool:
    if isinstance(book, int):
        book = book_number_to_id(book)
    return is_book_id_valid(book) and book not in NON_CANONICAL_IDS


def choose_yes_no(prompt: str) -> bool:

    choice: str = " "
    while choice not in ["n","y"]:
        choice: str = input(prompt).strip()[0].lower()
    if choice == "y":
        return True
    elif choice == "n":
        return False


def get_destination_file_from_book(file):

    project_name = file.parent.name
    book = None
    for BOOK_ID in ALL_BOOK_IDS:
        if BOOK_ID in file.name:
            book = BOOK_ID
    if not book:
        return None
    else:

        book_number = book_id_to_number(book)
        #Add one to NT and DC book numbers:
        if not is_ot(book_number):
            book_number += 1 
        
        new_filename = f"{book_number:02}{book}{project_name}.usfm"
    
        return file.with_name(new_filename)


def rename_files(renames):
    for source_file, destination_file in renames:
        if destination_file.is_file(): 
            print(f"Didn't rename {source_file.name} to {destination_file.name} because the destination file aleady exists.")
        else:
            shutil.move(source_file, destination_file)
            print(f"Renamed {source_file.name} to {destination_file.name}")
        

# import machine.scripture.canon 
root_folder = Path("E:/Work/Pilot_projects/projects")

source_folders = [source_folder for source_folder in root_folder.iterdir()]
source_folders = [root_folder / "dzo"]

print(f"Found {len(source_folders)} source folders: {source_folders}")

for source_folder in source_folders:
    project_name = source_folder.name
    source_files = sorted([source_file for source_file in source_folder.glob("*") if source_file.is_file])
    filtered_files = [file for file in source_files if any(BOOK_ID.upper() in file.name.upper() for BOOK_ID in ALL_BOOK_IDS)]
    for filtered_file in filtered_files:
        print(filtered_file.name)

    renames = [(file, get_destination_file_from_book(file)) for file in filtered_files]

    # print matched files with corresponding name
    for src, dest in renames:
        print(f"{src.name}         ->    {dest.name}")

exit()
if renames:
    source, dest = renames[0]
    print(f"Will rename {len(renames)} files. E.g. {source} to {dest}")
    if not choose_yes_no("Continue with renaming? y/n?"):
        exit()
    rename_files(renames)
    print(f"Renamed {len(renames)} files.")


# Next step
for source_folder in source_folders:
    source_files = sorted([source_file for source_file in source_folder.glob('*.usfm') if source_file.name[2] == "-"])
    if source_files:
        renames = [(source_file, get_destination_file(source_file)) for source_file in source_files]       

        if renames:
            source_file, destination_file = renames[0]
            
           #print(f"Found {len(renames)} files to rename in {source_folder}.")
           #print(f"Example rename from :  {source_file.name}   to   {destination_file.name}")
           #if not choose_yes_no("Continue with renaming? y/n?"):
           #    exit()

            for source_file, destination_file in renames:
                shutil.move(source_file, destination_file)
            #    print(f"Renamed {source_file.name} to {destination_file.name}")
            print(f"Renamed {len(renames)} files in {source_folder}.")
            renames = []    
