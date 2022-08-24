#!/usr/bin/python3.8
'''
Simple blast. Returns a tsv file with main information about your hits.

Author: Enrico Giovanelli Tacconi Gimenez
e-mail: gimenezenrico@yahoo.com.br
Requisites: blast+; python3; taxdb in the same folder you run this code
'''
from qPCR.putHeader import putHeader
import argparse
from sys import stderr, stdout
from Bio.Blast.Applications import NcbiblastnCommandline
parser = argparse.ArgumentParser(
    description="Checks your primers specificity with BLASTn.")
parser.add_argument("query", help="Type the path to your query file.")
parser.add_argument(
    "output_name", help="Type the prefix of the out file (the out file is a .csv file", type=str)
parser.add_argument(
    "num_alignments", help="An integer of the number of alignments you want blast to return.", type=int)

args = parser.parse_args()

comando_blastn = NcbiblastnCommandline(query=args.query, db="nt", outfmt='6 qseqid sscinames qcovs pident evalue staxids qseq sblastnames salltitles stitle',
                                       out=args.output_name+".tsv", num_alignments=args.num_alignments, remote=True)
print("Running BLASTn: {}\n".format(comando_blastn))

stdout, stderr = comando_blastn()

blast_result = "{}.tsv".format(args.output_name)
print("If there is any error, it will appear below:\n\n")
print(stderr)
putHeader(blast_result)
with open(f'./{blast_result}', 'r') as saida:
    lines = saida.read()

print("BLASTn results achieved! Check {}.tsv.\n".format(args.output_name))
print("*"*100, "\n Thank you for using this software! Feel free to share!\n",
      "*"*100)
