#!/usr/bin/env python
"""
Fast duplicate file finder.
Usage: duplicates.py <folder> [<folder>...]

Based on https://stackoverflow.com/a/36113168/300783
Modified for Python3 with some small code improvements.
"""
import hashlib
import os
import pickle
import string
import sys
from collections import defaultdict
from ctypes import windll
from pathlib import Path


def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_drives():
    return [
        f"{drive}" for drive in string.ascii_uppercase if os.path.exists(f"{drive}:")
    ]


def get_hash(filename, first_chunk_only=False, hash_algo=hashlib.sha1):
    hashobj = hash_algo()
    with open(filename, "rb") as f:
        if first_chunk_only:
            hashobj.update(f.read(1024))
        else:
            for chunk in chunk_reader(f):
                hashobj.update(chunk)
    return hashobj.digest()


def dump_pickle(data, pickle_file):
    with open(pickle_file, "wb") as f_pickle:
        pickle.dump(data, f_pickle)


def load_pickle(pickle_file):
    with open(pickle_file, "rb") as f_pickle:
        return pickle.load(f_pickle)


def check_for_duplicates(paths):
    # TODO Refactor to use {file: (size, small_hash, full_hash)} or class object.

    drives = ['C','D','E','F']
    print(drives)  # On my PC, this prints ['A', 'C', 'D', 'F', 'H']
    
    files_by_size = defaultdict(list)
    files_by_small_hash = defaultdict(list)
    files_by_full_hash = defaultdict(list)

    size_pickle = Path("sizes.pickle").resolve()
    small_hash_pickle = Path("small_hashes.pickle").resolve()
    full_hash_pickle = Path("file_hashes.pickle").resolve()

    if size_pickle.is_file():
        files_by_size = load_pickle(size_pickle)

    if small_hash_pickle.is_file():
        files_by_small_hash = load_pickle(small_hash_pickle)

    if full_hash_pickle.is_file():
        files_by_full_hash = load_pickle(full_hash_pickle)

    for path in paths:
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                try:
                    # if the target is a symlink (soft one), this will
                    # dereference it - change the value to the actual target file
                    full_path = os.path.realpath(full_path)
                    file_size = os.path.getsize(full_path)
                except OSError:
                    # not accessible (permissions, etc) - pass on
                    continue

                if full_path in files_by_size:
                    # Update the size and mark as updated

                    files_by_size[file_size].append(full_path)

    # For all files with the same file size, get their hash on the first 1024 bytes
    for file_size, files in files_by_size.items():
        if len(files) < 2:
            continue  # this file size is unique, no need to spend cpu cycles on it

        for filename in files:
            try:
                small_hash = get_hash(filename, first_chunk_only=True)
            except OSError:
                # the file access might've changed till the exec point got here
                continue
            files_by_small_hash[(file_size, small_hash)].append(filename)

    # For all files with the hash on the first 1024 bytes, get their hash on the full
    # file - collisions will be duplicates
    for files in files_by_small_hash.values():
        if len(files) < 2:
            # the hash of the first 1k bytes is unique -> skip this file
            continue

        for filename in files:
            try:
                full_hash = get_hash(filename, first_chunk_only=False)
            except OSError:
                # the file access might've changed till the exec point got here
                continue

            if full_hash in files_by_full_hash:
                duplicate = files_by_full_hash[full_hash]
                print("Duplicate found:\n - %s\n - %s\n" % (filename, duplicate))
            else:
                files_by_full_hash[full_hash] = filename


if __name__ == "__main__":
    if sys.argv[1:]:
        check_for_duplicates(sys.argv[1:])
    else:
        print("Usage: %s <folder> [<folder>...]" % sys.argv[0])
