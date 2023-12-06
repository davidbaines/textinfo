import argparse
#import boto3
from datetime import date
from pathlib import Path
from string import Template

def choose_yes_no(prompt: str) -> bool:

    choice: str = " "
    while choice == "" or choice not in ["n","y"]:
        choice: str = input(prompt).strip()[0].lower()
    if choice == "y":
        return True
    elif choice == "n":
        return False
    

def get_lines(file):

    # Extract from the text file the verse text as sfm and the BT as sfm
    with open(file, 'r', encoding='utf-8') as f_in:
        lines = [line for line in f_in.read().split('\n')]
    return lines

def save_file(file, lines):

    with open(file, 'w', encoding='utf-8') as f_out:
        for line in lines:
            f_out.write(line + "\n")

def get_id(lines):
    id = lines[0][4:7]
    return id

def get_description(lines):
    description = lines[0][7:] if len(lines[0]) > 8 else ""
    return description.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Add remark as second line of all sfm files in a folder.")
    # Folder is the location of the files to be modified. E.g: S:\MT\experiments\FT-Naxi\NLLB1.3_hak_zh_nxq_2\infer\23000
    # The model name will be extracted from this path.

    parser.add_argument("--folder", default=None, type=Path, help="The folder containing the sfm files.")
    parser.add_argument("--output", default=None, type=str, help="The subfolder for the modified sfm files. Will be created if it doesn't exist.", required=True)
    parser.add_argument("--source", default=None, type=str, help="The source Bible the model translated.")

    args = parser.parse_args()

    remark = Template("\\rem This draft of $book was machine translated on $today from the $description using model $experiment. It should be reviewed and edited carefully.")

    folder = Path(args.folder)

    if '\\' in str(folder):
        experiment_list = str(folder).split('\\')
    elif '/' in str(folder):
        experiment_list = str(folder).split('/')
    
    if experiment_list[-2] == 'infer':
           experiment = experiment_list[-4] + "/" + experiment_list[-3]
    else:
        raise RuntimeError(f"\nLooking for the two folders above the 'infer' directory as the experiment name.\nCouldn't find the experiment from the folder: {folder}")

    files = [file for file in folder.glob("*.sfm") if file not in folder.glob("*.rem.sfm")]
    
    if not args.source:
        first_file_lines = get_lines(files[0])
        first_book_id =  get_id(first_file_lines)
        description = get_description(first_file_lines)

        # Some ID lines also contain a remark.
        if "\\rem" in description:
            description = description.split("\\rem",1)[0]

        print(f"The source version has this description on the ID line:\n{description}\n")   

    elif len(args.source) < 5:
        print(f"The description of the source version is missing or very short: {args.source}")
        if not choose_yes_no(f"Continue y/n?"):
            exit()
        description = args.source
    
    first_remark = remark.substitute(book = first_book_id, today = date.today(), description = description, experiment = experiment).replace("  ", " ")
    #remark = f"\\rem This draft of {first_book_id} was machine translated on {today} from the {description} using model {experiment}.  It should be reviewed and edited carefully."
    
    output = folder / args.output

    print(f"The following line will be added to a copy of each of the {len(files)} sfm files in {folder}\n{first_remark}\n")
    if output:
        print(f"The modified files will be written to {output}")    
    else:
        print("The modified files will be written to the same folder and have the suffix .rem.sfm")
    
    if not choose_yes_no(f"Continue adding y/n?"):
        exit()
    
    
    output.mkdir(parents=True, exist_ok=True)
    file_pairs = [(file , output / file.name) for file in files]

    for file_in, file_out in file_pairs:
        if file_out.is_file():
            print(f"The output file {file_out} already exists. Skipping")
            continue
        lines = get_lines(file_in)
        book = get_id(lines)
        #remark = f"\\rem This draft of {book} was machine translated on {today} from the {source} using model {experiment}.  It should be reviewed and edited carefully."
        next_remark = remark.substitute(book = book, today = date.today(), description = description, experiment = experiment).replace("  ", " ")
        if lines[1] == next_remark:
            print(f"Remark already exists in the input file: {file_in}, making unchanged copy.")
            save_file(file_out,lines)
        else :
            lines.insert(1, next_remark)
            save_file(file_out,lines)
            print(f"Added {next_remark} to file {file_out}")

if __name__ == "__main__":
    main()
