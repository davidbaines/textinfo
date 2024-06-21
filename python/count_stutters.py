import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple
from tqdm import tqdm

def find_paths(top_level_dir: Path, folder_name: str) -> List[Path]:
    if not top_level_dir.is_dir():
        raise ValueError(f"The provided path {top_level_dir} is not a directory.")
    return [path for path in top_level_dir.glob(f"**/{folder_name}") if path.is_dir()]

def find_files_by_ext(paths: List[Path], ext: str) -> List[Path]:
    ext = ext.lower()
    return [
        file
        for path in paths
        if path.is_dir()
        for file in path.glob("**/*")
        if file.is_file() and file.suffix.lower() == ext
    ]

def remove_repeated_phrases(files: List[Path], min_dups: int) -> Dict[Path, List[Tuple[int, str]]]:
    changes_dict = defaultdict(list)

    for file in tqdm(files):
        with file.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        for line_number, line in enumerate(lines, start=1):
            words = line.split()
            n = len(words)
            modified_line = line

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
                        # Remove repeated phrases
                        modified_line = line.replace(" ".join(phrase) * repeated_count, phrase_str, 1)
                        changes_dict[file].append((line_number, line.strip()))
                        break

            new_lines.append(modified_line)

        # Write the modified content to a new file with "_edit" appended to the name
        edited_file_path = file.with_name(f"{file.stem}_edit{file.suffix}")
        with edited_file_path.open("w", encoding="utf-8") as f:
            f.writelines(new_lines)

    return changes_dict

def write_changes_log(changes_dict: Dict[Path, List[Tuple[int, str]]], output_filepath: Path) -> None:
    with output_filepath.open("w", encoding="utf-8") as file:
        for path, changes in changes_dict.items():
            file.write(f"File: {path}\n")
            file.write("Changed lines:\n")
            for line_number, line_content in changes:
                file.write(f"  Line {line_number}: {line_content}\n")
            file.write("\n")


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

    infer_folders = find_paths(directory, "Infer")
    print(f"Found {len(infer_folders)} folders named 'Infer'.")

    sfm_files = find_files_by_ext(infer_folders, ".sfm")
    print(f"Found {len(sfm_files)} .SFM files.")

    changes_dict = remove_repeated_phrases(sfm_files, min_dups)

    log_file = Path("E:/Work/stutters_changes_log.txt")
    write_changes_log(changes_dict, log_file)
    print(f"Saved changes log to {log_file}")

    print(f"Found {len(changes_dict)} files with lines containing repeated phrases.")

if __name__ == "__main__":
    main()
