# textinfo

### charfreq.py
There are a few scripts in the python directory that report information about text files.

The first is charfreq.py it will take an input folder and read all the files in that folder counting every occurence of each character.
It writes two reports in csv format. character_summary.csv contains the total counts of all characters across all files. character_report.csv breaks down the 
counts by individual file.

To do:  
Would be better to replace the character_summary with a fixed Excel sheet that calculates the totals.

### transliterate.py
A hard coded transliteration table that converts Arabic characters whose unicode script is 'Inherited'  to other Arabic characters. This is in an attempt to overcome the bug (now fixed) in SentencePiece that breaks words when it encounters an inherited script character.

### findnames.py
Looks for words in a text file that begin with an uppercase letter. Looks at those which only occur first, and if they only occur in the first position they are removed.  The remaining words are a first approximation of proper nouns. These are written to a file on the same line as where they were found.
The hope is that this might help to improve the NLP processing of names which are not to be translated.  It might also be a help for post editing manually.

