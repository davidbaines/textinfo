import argparse
from pathlib import Path

def combine_files(file1_path, file2_path, output_path):
    with open(file1_path, 'r', encoding='utf-8') as file1, open(file2_path, 'r', encoding='utf-8') as file2, open(output_path, 'w', encoding='utf-8') as output:
        lines1 = file1.readlines()
        lines2 = file2.readlines()

        max_lines = max(len(lines1), len(lines2))

        for i in range(max_lines):
            if i < len(lines1) and lines1[i].isspace():
                output.write(lines2[i])
            else:
                output.write(lines1[i])
    print(f"Wrote file to {output_path}")

def combine_lines(file1_path, file2_path, output_path):
    with open(file1_path, 'r', encoding='utf-8') as file1, open(file2_path, 'r', encoding='utf-8') as file2, open(output_path, 'w', encoding='utf-8') as output:
        lines1 = file1.read().splitlines()
        lines2 = file2.read().splitlines()

        if not len(lines1) == len(lines2):
            print(f"{file1_path} has {len(lines1)} lines and {file2_path} has {len(lines2)}.\nPlease make these equal length and try again")
            exit()

        for line1, line2 in zip(lines1, lines2):
            output.write(f"{line1}{line2}\n")
    print(f"Wrote file to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Combine two extract files into one.")
    parser.add_argument("folder", type=Path, help="Path to files.")
    parser.add_argument("file1", type=str, help="First file name.")
    parser.add_argument("file2", type=str, help="Second file name.")
    parser.add_argument("--by-line", action="store_true", help="Combine files by concatenating lines.")
    parser.add_argument("--output_file_name", type=str, help="Output file name, default is concatenation of file1 and 2 with same suffix as file1.")
    
    args = parser.parse_args()
    #print(args)
    folder = args.folder
    file1 = folder / args.file1
    file2 = folder / args.file2
    output_file = folder / f"{file1.stem}_{file2.stem}{file1.suffix}"

    print(file1, file2, output_file)
    if args.by_line:
        print("Concatenating lines")
        combine_lines(file1, file2, output_file)    
    else:
        combine_files(file1, file2, output_file)


if __name__ == "__main__":
    main()

