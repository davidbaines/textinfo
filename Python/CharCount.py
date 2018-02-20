from collections import Counter as Counter
import argparse, io
import unicodedata

parser = argparse.ArgumentParser(description="Count occurances of all characters in a file.")
parser.add_argument("-in", "--input",   help="Specify file to read in.")
parser.add_argument("-out" ,"--output", help="Specify the filename for the report.")
args = parser.parse_args()

char_count = Counter()
if not args.input:
	print("Use: CharCount -in <inputfile>")
	exit()
else:	
	with io.open(args.input, 'r', encoding='utf-8') as infile:
		for line in infile:
			char_count.update(line)

header_string = "{0:>10s} | {1:<s} | {2:}"
row_string = "{0:>10d} | {1:<s} | {2:}"
column1 = "Number"
column2 = "Character"
column3 = "Unicode name"

print(header_string.format(column1,column2, column3))

for character,count in char_count.most_common():
	try:
		name = unicodedata.name(character)
	except:
		name = ""
	print(row_string.format(count,character, name))

if args.output:
	with open(args.output, 'w', encoding='utf-8') as outfile:
		for character,count in char_count.most_common():
			try:
				name = unicodedata.name(character)
			except:
				name = ""
			outfile.write(row_string.format(count,character, name))
			outfile.write("\n")
