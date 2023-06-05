import argparse
import re
from collections import Counter
from pathlib import Path

def clean_word(word):
    # remove punctuation at the start and end of the word, keep hyphens in the middle
    return re.sub(r'^[^a-zA-Z-]|[^a-zA-Z-]$', '', word)

def count_word_frequencies(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()
    words = text.split()
    cleaned_words = [clean_word(word) for word in words]
    return Counter(cleaned_words)

def process_files(folder, extension):
    path = Path(folder)
    files = path.glob(f'*.{extension}')

    summary_counts = Counter()

    for file in files:
        word_frequencies = count_word_frequencies(file)
        summary_counts += word_frequencies
        #print(f"Word frequencies for {file}:")
        #for word, count in word_frequencies.most_common():
        #    print(f"{word}: {count}")
        #print()

    #print("Summary counts across all files:")
    #for word, count in summary_counts.most_common():
    #    print(f"{word}: {count}")

    return summary_counts

def main():
    # Create parser and define command-line arguments
    parser = argparse.ArgumentParser(description='Count word frequencies in text files.')
    parser.add_argument('folder', help='Folder containing text files')
    parser.add_argument('extension', help='Extension of text files (e.g. txt)')
    parser.add_argument('output', help='Output file.')

    # Parse command-line arguments
    args = parser.parse_args()

    # Process files
    counts = process_files(args.folder, args.extension)
    with open(args.output, 'w', encoding='utf-8') as f_out:
        f_out.writelines([f"{word}\t{count}\n" for word, count in counts.most_common()]) 

if __name__ == "__main__":
    main()