import regex
import argparse
import sys
from pathlib import Path

# Define regular expressions
regex_patterns = {
    1: {
        "description": "Remove marks",
        "type": "deletion",
        "find": regex.compile(r'\pM'),
        "replace": ""
    },
    2: {
        "description": "Replace 'a' with 'b'",
        "type": "replacement",
        "find": regex.compile(r'a'),
        "replace": "b"
    },
    3: {
        "description": "Remove 'nd markers'",
        "type": "deletion",
        "find": regex.compile(r'\\nd\*'),
        "replace": ""        
    },
}

def list_expressions():
    for index, details in regex_patterns.items():
        print(f"{index}: {details['description']}")

def process_files(input_folder, output_folder, expressions, extensions=['.txt']):
    
    files = [file for file in input_folder.glob('*') if file.is_file() and file.suffix in extensions]
    for file in files:
        output_file = output_folder / f"{file.stem}{file.suffix}"
        with open(file, "r", encoding='utf-8') as infile, open(output_file, "w", encoding='utf-8') as outfile:        
            for line in infile:
                for exp_index in expressions:
                    if exp_index in regex_patterns:
                        find = regex_patterns[exp_index]["find"]
                        replace = regex_patterns[exp_index]["replace"]
                        line = find.sub(replace, line)
                outfile.write(line)

        print(f"Processed {file} and saved it in {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Process a file with regular expressions."
    )
    parser.add_argument("--input", help="The input folder to process")
    parser.add_argument(
        "-l", "--list", action="store_true", help="List available regular expressions"
    )
    parser.add_argument(
        "--re",
        nargs="+",
        type=int,
        help="Regular expressions to apply in order by index",
    )

    args = parser.parse_args()

    if args.list:
        list_expressions()
    elif args.re:
        input_folder = Path(args.input)
        output_folder = input_folder / "Processed"
        output_folder.mkdir(exist_ok=True)
        print(args.re)
        process_files(input_folder, output_folder, args.re)
    else:
        print(
            "Please specify the --list option or the --re option with the list of regular expressions to apply."
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
