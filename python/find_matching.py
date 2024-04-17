import argparse
import os
from pathlib import Path


def matches(file, patterns):
    for pattern in patterns:
        if pattern in file.name:
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Search for files namein a directory")
    parser.add_argument("folder", type=str, help="Directory to search")
    parser.add_argument(
        "patterns", nargs="+", default=[], help="Patterns in file name to find."
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Search in subfolders."
    )

    args = parser.parse_args()
    folder = Path(args.folder)
    patterns = args.patterns
    recursive = args.recursive
    # patterns = ['BSB', 'CEVUK', 'CEVUS06', 'EASY', 'engLXXup', 'engULB', 'ESVUS16', 'GCN', 'GMTelSB', 'IRVAsm', 'IRVBen', 'IRVGuj', 'IRVHin', 'IRVKan', 'IRVMAL', 'IRVMar', 'IRVOry', 'IRVPun', 'IRVTam', 'IRVTel', 'IRVUrd', 'KANCLBSI', 'KANJVBSI', 'KEY_2024_02_05', 'KFA', 'KFI_2023_11_17', 'KJDP_2024_02_05', 'KONDANT2006', 'KUVBT_EN_2024_02_05', 'KUVI_2024_02_05', 'LSV', 'MAL10RO', 'malclBSI', 'malirv', 'MALOVBSI', 'MCV', 'muv', 'NASB', 'NET08', 'NIV11', 'NIV11R', 'NIV11R_Malayalam_600M', 'NLT', 'NLT07', 'NRSV', 'NTHaa20', 'NTNoo20', 'OKCV', 'OpenBible_Kannada', 'OpenBible_Kannada_Latn', 'OpenBible_Malayalam', 'OpenBible_Tamil', 'OpenBible_Tamil_Latn', 'RSV', 'TEL29OV', 'telirv', 'TELOV', 'TELUBSI', 'TLB', 'TND', 'Tulu', 'WEB', 'wsg', 'WSGlatin', 'YLT98']
    if recursive:
        matching_files = [
            file
            for file in folder.rglob("*")
            if file.is_file and matches(file, patterns)
        ]
    else:
        matching_files = [
            file
            for file in folder.glob("*")
            if file.is_file and matches(file, patterns)
        ]

    if matching_files:
        print("Matching files:")
        for matching_file in matching_files:
            if recursive:
                print(f"{matching_file}")
            else:
                print(f"{matching_file.name}")
    else:
        print("No matching files found.")


if __name__ == "__main__":
    main()
