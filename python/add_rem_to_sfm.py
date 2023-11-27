import argparse
#import boto3
from datetime import date
from pathlib import Path


def choose_yes_no(prompt: str) -> bool:

    choice: str = " "
    while choice not in ["n","y"]:
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

    parser.add_argument("--folder", default=None, type=str, help="The folder containing the sfm files.")

    #parser.add_argument("--experiment", default=None, type=str, help="The experiment that drafted the book.")
    parser.add_argument("--source", default=None, type=str, help="The source Bible the model translated.")

    args = parser.parse_args()

    today = date.today()

    folder = Path(args.folder)

    if '\\' in str(folder):
        experiment_list = str(folder).split('\\')
    elif '/' in str(folder):
        experiment_list = str(folder).split('/')
    
    if experiment_list[-2] == 'infer':
           experiment = experiment_list[-4] + "/" + experiment_list[-3]
    else:
        raise RuntimeError(f"\nLooking for the two folders above the 'infer' directory as the experiment name.\nCouldn't find the experiment from the folder: {folder}")

    files = [file for file in folder.glob("*.sfm")]
    
    first_file_lines = get_lines(files[0])
    first_book_id =  get_id(first_file_lines)
    description = get_description(first_file_lines)

    source = args.source
    
    if source:
        description = source
    
    if len(description) < 5:
        print(f"The description of the source version is very short: {description}")
        if not choose_yes_no(f"Continue y/n?"):
            exit()

    if not source and description:
        print(f"The source version has this description on the ID line:\n{description}")

    remark = f"\\rem This draft of {first_book_id} was machine translated on {today} from the {source} using model {experiment}.  It should be reviewed and edited carefully."
    print(f"The following line will be added to each of the {len(files)} sfm files in {folder}\n{remark}\n")
    
    if not choose_yes_no(f"Continue adding y/n?"):
        exit()

    for file in files:
        lines = get_lines(file)
        book = get_id(lines)
        remark = f"\\rem This draft of {book} was machine translated on {today} from the {source} using model {experiment}.  It should be reviewed and edited carefully."
        lines.insert(1, remark)
        save_file(file,lines)
        print(remark)

if __name__ == "__main__":
    main()
