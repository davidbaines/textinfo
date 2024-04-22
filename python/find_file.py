import multiprocessing as mp
import os
from   pathlib import Path
import glob

filename = "Luke.zip"
drive_letters = "CDE"
drives = [Path(f"{l}:/") for l in drive_letters]
print(drives)
print()

folder = Path(drives[0])
folders = []
i = 0
f_gen = [f for f in  folder.rglob(filename)]

exit()
for f in f_gen:
    i += 1
    try:
        if f.is_dir() and f.exists():
            folders.append(f)
            if i % 10000 == 0:
                print(f"Found the {i}th folder: {f}")
    except FileNotFoundError:
        pass

exit()

folders = sorted([Path(folder) for drive in drives for folder in glob.glob(f"{drive}**/") if Path(folder).is_dir()])
   

print(folders)

#no_of_cpu = 2
#print(f"Number of processors: {mp.cpu_count()} using {no_of_cpu}")
#pool = mp.Pool(no_of_cpu)
    
files_found = []

for folder in folders:
    for file in find_files(folder):
        files_found.append(file)

files = sorted(files)

# Iterate over folders with multiple processors.
#results = pool.map(find_files, [folder for folder in folders][:2])
    
#pool.close()

print(files)

