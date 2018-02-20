
from collections import Counter as Counter
import argparse

parser = argparse.ArgumentParser(description="Count the occurances of Characters in a file.")
parser.add_argument("-in", "--input",   help="Specify file to read in.")
parser.add_argument("-out", "--output",   help="Specify file to write.")
args = parser.parse_args()

charcount = Counter()
	
if not args.input:
	print("Use: CharCount -in <inputfile>")
else :
	with open(args.input, 'r', encoding='utf-8') as infile:
		for line in (infile):
			for character in line.strip('()[]0123456789\n'):
				charcount.update(character)

if args.output:
	with open(args.output, 'w', encoding='utf-8') as outfile:
		for character in charcount:
			outfile.write(character)

print()
for character in charcount.most_common():
	print(character)
print()

for character in charcount.most_common():				
	print(" {}  ,  {} ".format([character],charcount[character]))