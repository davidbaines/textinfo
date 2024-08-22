import argparse
import csv
import re
from pathlib import Path

def clean_text(text, replacements):
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    # Replace multiple whitespace characters with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def convert_sfm_to_csv(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split the content into rows based on the \ref marker, but keep the \ref
    rows = re.split(r'(?=\\ref)', content)
    
    # Define text cleaning patterns
    replacements = [
        (r'[«"""»]', ' '),  # Replace various quote marks
        (r'…|\.{3}', ' '),  # Replace ellipsis (character or three dots)
        (r'/refr.*', ' '),  # Replace "/refr" and anything after it
        (r':', ' '),  # Replace colons with space
        (r'[#\[\]]', ' '),  # Replace hashes and square brackets with a space
        # Add more patterns here as needed
    ]

    # Prepare the data for CSV
    csv_data = []
    for row in rows:
        if not row.strip():
            continue
        
        # Extract fields
        ref = re.search(r'\\ref\s*(.*?)(?=\n|$)', row)
        tx = re.search(r'\\tx\s*(.*?)(?=\n|$)', row)
        tf = re.search(r'\\tf\s*(.*?)(?=\n|$)', row)
        te = re.search(r'\\te\s*(.*?)(?=\n|$)', row)
        
        # Skip row if 'tx' is missing or both 'tf' and 'te' are missing
        if not tx or (not tf and not te):
            continue
        
        # Prepare row data and clean the text
        row_data = [
            clean_text(ref.group(1), replacements) if ref else '',
            clean_text(tx.group(1), replacements) if tx else '',
            clean_text(tf.group(1), replacements) if tf else '',
            clean_text(te.group(1), replacements) if te else ''
        ]
        
        csv_data.append(row_data)

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Reference', 'Text', 'Translation (French)', 'Translation (English)'])
        writer.writerows(csv_data)

def main():
    parser = argparse.ArgumentParser(
        description="Convert from sfm to csv."
    )
    parser.add_argument(
        "sfm", type=Path, help="Path to the sfm file."
    )
    args = parser.parse_args()
    sfm_file = Path(args.sfm)
    csv_file = sfm_file.with_suffix(".csv")
    convert_sfm_to_csv(sfm_file, csv_file)
    print(f"Conversion complete. Output saved to {csv_file}")

if __name__ == "__main__":
    main()