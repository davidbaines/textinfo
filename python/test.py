#!/usr/bin/env python3
# -*- coding: utf-8 -*-

ranges = {1: [0,24], 5: [25,49], 10: [50,199], 20: [200,499], 50: [500, 1999], 100: [2000, 5000], 1000: [5000, 24999], 5000: [25000,499999], 10000: [500000,1999999] }


for files_found in range(0, 52):
    update_every = next((x for x, r in ranges.items() if r[0] <= files_found <= r[1]), 10000)
    print(f"Found {files_found} files will update every {update_every} files.")
    
for files_found in sorted([19999,20000,20001,20002,100000,1000000,25000,499999, 500000,1999999]):
    update_every = next((x for x, r in ranges.items() if r[0] <= files_found <= r[1]), 10000)
    print(f"Found {files_found} files will update every {update_every} files.")
