from pathlib import Path
from tqdm import tqdm


def count_lines(file, include_empty=False):
    with open(file, "r", encoding="utf-8") as f_in:
        return len([line for line in f_in.readlines() if not line.strip() == ""])


file = Path(r"S:/Paratext/projects/RAWNFC/43LUKRAWNFC.SFM")
folder = Path("F:/GitHub/BibleNLP/ebible/corpus")

files = [(file.stem, count_lines(file)) for file in folder.glob("*.txt")]

# exit()
# for file in tqdm([file for file in folder.glob("*.txt")]) :
#     lines = [file.stem, count_lines(file)]
#     #file= Path(r"S:/Paratext/projects/RAWNFC/43LUKRAWNFC.SFM")
#     with open(file,'r',encoding='utf-8') as f_in:
#         line_len = {i: len(line) for i,line in enumerate(f_in.readlines(),1)}

#     #line_lengths = {k: v for k, v in reversed(sorted(line_len.items(), key=lambda item: item[1]))}

#     files[file] = sum(1 for k,v in line_len.items() if v > 0)
#     #break
# #print(line_lengths)
for file, lines in files:
    print(file, lines)
