from collections import Counter as Counter
import argparse, io
import unicodedata

parser = argparse.ArgumentParser(description="Count occurrences of all characters in a file.")
parser.add_argument("-in", "--input",   help="Specify file to read in.")
parser.add_argument("-out" ,"--output", help="Specify the file name for the report.")
args = parser.parse_args()

column_names = "{0:>10s}  {1:<9} {2:}".format("Number","Character","Unicode name")
row_string_one_byte   = "{0:>10d} | {1:<9} |{2:}"
row_string_more_bytes = "{0:>10d} | {1:<9}|{2:}"

def count_bytes(character):
	return len(character.encode('utf8'))

char_count = Counter()
char_data = []

if not args.input:
	print("Use: CharCount -in <inputfile>")
	exit()
else:	
	with io.open(args.input, 'r', encoding='utf-8') as infile:
		for line in infile:
			char_count.update(line)

#Delete newline count.
del char_count['\n']

for character,count in char_count.most_common():
	try:
		name = unicodedata.name(character)
	except:
		name = "Couldn't find Unicode name"
	char_data.append((count,character,name))

print(column_names)

for count,character, name in char_data:
	if count_bytes(character) == 1 :
		print(row_string_one_byte.format(count,character, name))
	else :
		print(row_string_more_bytes.format(count,character, name))
		
if args.output:
	with open(args.output, 'w', encoding='utf-8') as outfile:
		outfile.write(column_names + '\n')
		for count, character, name in char_data:
			if count_bytes(character) == 1 :
				outfile.write(row_string_one_byte.format(count,character, name))
			else : 
				outfile.write(row_string_more_bytes.format(count,character, name))
			outfile.write("\n")
