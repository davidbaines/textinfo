import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple
from tqdm import tqdm


def find_paths(top_level_dir: Path, folder_name: str) -> List[Path]:
    """
    Finds all paths in the given top level directory where one of the folders is named "infer".

    Args:
    - top_level_dir (Path): A pathlib.Path object representing the top-level directory.

    Returns:
    - List[Path]: A list of pathlib.Path objects for paths that contain a folder named "infer".
    """
    if not top_level_dir.is_dir():
        raise ValueError(f"The provided path {top_level_dir} is not a directory.")
    
    return [path for path in top_level_dir.glob(f"**/{folder_name}") if path.is_dir()]

def find_files_by_ext(paths: List[Path], ext: str) -> List[Path]:
    """
    Finds all files with a .SFM extension in the given list of infer paths.

    Args:
    - infer_paths (List[Path]): A list of pathlib.Path objects representing directories.

    Returns:
    - List[Path]: A list of pathlib.Path objects for files that end with .SFM.
    """
    ext = ext.lower()  # Normalize the extension to lowercase

    return [
        file
        for path in paths
        if path.is_dir()
        for file in path.glob("**/*")
        if file.is_file() and file.suffix.lower() == ext
    ]

def find_repeated_phrases(files: List[Path], min_dups: int) -> Dict[Path, List[Tuple[int, str, int, int, int]]]:
    """
    Finds lines with repeated phrases in the given list of .SFM files.

    Args:
    - files (List[Path]): A list of pathlib.Path objects representing .SFM files.
    - min_dups (int): The minimum number of repeated phrases to consider.

    Returns:
    - Dict[Path, List[Tuple[int, str, int, int, int]]]: A dictionary where the keys are file paths and the values
      are lists of tuples containing line number, line content, starting index of the repeating phrases,
      length of one phrase, and the number of times the phrase occurs.
    """
    repeated_phrases_dict = defaultdict(list)

    for file in tqdm(files):
        with file.open("r", encoding="utf-8") as f:
            lines = f.readlines()
            for line_number, line in enumerate(lines, start=1):
                words = line.split()
                n = len(words)
                found_repeated = False

                # Check for repeated phrases with lengths from 1 to n//2
                for phrase_length in range(1, n // 2 + 1):
                    for i in range(n - phrase_length):
                        phrase = words[i:i + phrase_length]
                        repeated_count = 1
                        
                        for j in range(i + phrase_length, n - phrase_length + 1, phrase_length):
                            if words[j:j + phrase_length] == phrase:
                                repeated_count += 1
                            else:
                                break
                        
                        if repeated_count >= min_dups:
                            start_index = line.index(" ".join(phrase))
                            phrase_str = " ".join(phrase)
                            repeated_phrases_dict[file].append((line_number, line.strip(), start_index, len(phrase_str), repeated_count))
                            found_repeated = True
                            break
                    if found_repeated:
                        break

    return repeated_phrases_dict

def write_vscode_friendly_output(repeated_phrases_dict: Dict[Path, List[Tuple[int, str, int, int, int]]], output_filepath: Path) -> None:
    """
    Writes the repeated phrases dictionary to a text file in a Visual Studio Code-friendly format.

    Args:
    - repeated_phrases_dict (Dict[Path, List[Tuple[int, str, int, int, int]]]): The dictionary containing repeated phrases information.
    - output_filepath (Path): The path of the text file where the output will be written.
    """
    with output_filepath.open("w", encoding="utf-8") as file:
        for path, lines in repeated_phrases_dict.items():
            for line_number, line_content, start_index, phrase_length, repeated_count in lines:
                file.write(f"{path}:{line_number}:{start_index + 1}: Repeated phrase starts here. Phrase length: {phrase_length}, Repeated count: {repeated_count}\n")


def remove_repeated_phrases(repeated_phrases_dict: Dict[Path, List[Tuple[int, str, int, int, int]]]) -> None:
    """
    Removes all repeating phrases from the lines, leaving only the first occurrence.

    Args:
    - repeated_phrases_dict (Dict[Path, List[Tuple[int, str, int, int, int]]]): The dictionary containing repeated phrases information.
    """

    for file, phrases_info in repeated_phrases_dict.items():
        file_out = file.with_name(f"{file.stem}_edit")

        lines = file.read_text(encoding="utf-8").splitlines()
        for line_number, line, start_index, phrase_length, repeated_count in phrases_info:
            end_index = start_index + phrase_length * repeated_count
            lines[line_number - 1] = lines[line_number - 1][:start_index + phrase_length] + lines[line_number - 1][end_index:]

        file_out.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote edited version to {file_out}")

# Example usage:
# remove_repeated_phrases(repeated_phrases)

def main():
    parser = argparse.ArgumentParser(
        description="Search for inferred files with stutters."
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path("E:/Stutters/"),
        help="Directory to search",
    )
    parser.add_argument(
        "--min_dups",
        type=int,
        default=3,
        help="Minimum number of repeated words to consider it a stutter.",
    )

    args = parser.parse_args()
    min_dups = args.min_dups
    directory = Path(args.directory)   
    text_file =  directory / "stutters_count.txt"

    infer_folders = find_paths(directory, "Infer")
    print(f"Found {len(infer_folders)} folders named 'Infer'.")

    sfm_files = find_files_by_ext(infer_folders, ".sfm")
    print(f"Found {len(sfm_files)} .SFM files.")

    repeated_phrases = find_repeated_phrases(sfm_files, min_dups)

    stutter_count = sum(len(lines) for lines in repeated_phrases.values())

    
    write_vscode_friendly_output(repeated_phrases, text_file)
    print(f"Saved to {text_file}")

    print(f"Found {len(repeated_phrases)} files with lines containing repeated phrases.")
    print(f"Found {stutter_count} lines containing at least {min_dups} repeated phrases.")
    
    remove_repeated_phrases(repeated_phrases)
    print(f"Removed repeated phrases.")

if __name__ == "__main__":
    main()
