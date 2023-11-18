from nltk.translate.bleu_score import sentence_bleu
import argparse

def argparser():
    Argparser = argparse.ArgumentParser()
    Argparser.add_argument('--reference', type=str, default='summaries.txt', help='Reference File')
    Argparser.add_argument('--candidate', type=str, default='candidates.txt', help='Candidate file')

    args = Argparser.parse_args()
    return args

args = argparser()

reference = open(args.reference, 'r', encoding='utf-8').readlines()
candidate = open(args.candidate, 'r', encoding='utf-8').readlines()

if len(reference) != len(candidate):
    raise ValueError('The number of sentences in both files do not match.')

score = 0.
count = 0

for i in range(len(reference)):
    ref = reference[i].strip().split()
    cand = candidate[i].strip().split()
    bleu = sentence_bleu(ref,cand)
    if len(ref) >= 4 and len(cand) >= 4:
        count += 1
        score += bleu
        #print(f"{ref}")
        #print(f"{cand}")
        print(f"{len(ref)}, {len(cand)},  ***{bleu}***")

score /= count
print("The bleu score is: "+str(score))