import argparse
import pickle
from collections import defaultdict
from pathlib import Path
from typing import Dict, List
from tqdm import tqdm
import json

CHECKPOINT_FILE = Path("checkpoint.json")

def save_checkpoint(data: dict) -> None:
    """
    Saves the checkpoint data to a JSON file.

    Args:
    - data (dict): The checkpoint data to save.
    """
    with CHECKPOINT_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file)

def load_checkpoint() -> dict:
    """
    Loads the checkpoint data from a JSON file.

    Returns:
    - dict: The loaded checkpoint data.
    """
    if CHECKPOINT_FILE.exists():
        with CHECKPOINT_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    return {}

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

def find_repeated_phrases(files: List[Path], min_dups: int) -> Dict[Path, List[int]]:
    """
    Finds lines with repeated phrases in the given list of .SFM files.

    Args:
    - files (List[Path]): A list of pathlib.Path objects representing .SFM files.
    - min_dups (int): The minimum number of repeated phrases to consider.

    Returns:
    - Dict[Path, List[int]]: A dictionary where the keys are file paths and the values are lists of line numbers with repeated phrases.
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
                            repeated_phrases_dict[file].append([line_number,line])
                            found_repeated = True
                            break
                    if found_repeated:
                        break

    return repeated_phrases_dict


def save_repeated_words_dict(repeated_words_dict: Dict[Path, List], filepath: Path) -> None:
    """
    Saves the repeated words dictionary to a file using pickle.

    Args:
    - repeated_words_dict (Dict[Path, List[int]]): The dictionary to save.
    - filepath (Path): The path of the file where the dictionary will be saved.
    """
    with filepath.open("wb") as file:
        pickle.dump(repeated_words_dict, file)

def load_repeated_words_dict(filepath: Path) -> Dict[Path, List]:
    """
    Loads the repeated words dictionary from a file using pickle.

    Args:
    - filepath (Path): The path of the file from which the dictionary will be loaded.

    Returns:
    - Dict[Path, List[int]]: The loaded dictionary.
    """
    with filepath.open("rb") as file:
        return pickle.load(file)

def write_vscode_friendly_output(repeated_words_dict: Dict[Path, List], output_filepath: Path) -> None:
    """
    Writes the repeated words dictionary to a text file in a VS Code friendly format.

    Args:
    - repeated_words_dict (Dict[Path, List[int]]): The dictionary containing repeated words information.
    - output_filepath (Path): The path of the text file where the output will be written.
    """
    with output_filepath.open("w", encoding="utf-8") as file:
        for path, lines in repeated_words_dict.items():
            for line_number, line in lines:
                #print(line_number, type(line_number), "\n", line, type(line))
                #continue
                file.write(f"{path}:{line_number}\t{line.rstrip()}\n")        
        file.write("\n")

def main():
    parser = argparse.ArgumentParser(description="Search for inferred files with stutters.")
    parser.add_argument("--directory", type=Path, default=Path("E:/Stutters/"), help="Directory to search")
    parser.add_argument("--min_dups", type=int, default=3, help="Minimum number of repeated words to consider it a stutter.")

    args = parser.parse_args()
    min_dups = args.min_dups
    directory = Path(args.directory)

    pickle_file = directory / "stutters.pkl"
    text_file =  directory / "stutters_count.txt"

    checkpoint_data = load_checkpoint()
    if "infer_folders" not in checkpoint_data:
        infer_folders = find_paths(directory, "Infer")
        checkpoint_data["infer_folders"] = [str(folder) for folder in infer_folders]
        checkpoint_data["infer_index"] = 0
        save_checkpoint(checkpoint_data)
    else:
        infer_folders = [Path(folder) for folder in checkpoint_data["infer_folders"]]

    print(f"Found {len(infer_folders)} folders named 'Infer'.")
    sfm_files = find_files_by_ext(infer_folders, ".sfm")
    print(f"Found {len(sfm_files)} sfm files.")

    repeated_phrases = find_repeated_phrases(sfm_files, min_dups)

    stutter_count = sum(len(lines) for lines in repeated_phrases.values())

    save_repeated_words_dict(repeated_phrases, pickle_file)
    print(f"Saved pickle to {pickle_file}")
    
    write_vscode_friendly_output(repeated_phrases, text_file)
    print(f"Saved to {text_file}")

    print(f"Found {len(repeated_phrases)} files with lines containing repeated phrases.")
    print(f"Found {stutter_count} lines containing at least {min_dups} repeated phrases.")

    # Cleanup checkpoint file on successful completion
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()

if __name__ == "__main__":
    main()
