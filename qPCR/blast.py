#! /usr/bin/python3.8
'''
Script to, from a nucleotide FASTA file containing sequences of primers and probes, that is, small sequences, check the
specificity of these sequences by blastn algorithm.

Author: Enrico Giovanelli Tacconi Gimenez
e-mail: gimenezenrico@yahoo.com.br
Requisites: blast+; python3; taxdb in the same folder you run this code
'''
from sys import stderr, stdout
from Bio.Blast.Applications import *
import pandas as pd
import argparse

print("*"*10 + "\n" +
      "WELCOME TO CHECK PRIMERS SOFTWARE. IT CHECKS PRIMERS WITH BLAST!\n"+"*"*10)
parser = argparse.ArgumentParser(
    description="Checks your primers specificity with BLASTn.")
parser.add_argument("query", help="Type the path to your query file.")
parser.add_argument(
    "output_name", help="Type the prefix of the out file (the out file is a .csv file", type=str)
parser.add_argument(
    "num_alignments", help="An integer of the number of alignments you want blast to return.", type=int)

args = parser.parse_args()

comando_blastn = NcbiblastnCommandline(query=args.query, evalue=1000, word_size=7, penalty=-3, reward=1, remote=True, db="nt",
                                       outfmt='6 qseqid sscinames qcovs pident evalue staxids qseq', out=args.output_name+".tsv", num_alignments=args.num_alignments)
print("Running BLASTn: {}\n".format(comando_blastn))

stdout, stderr = comando_blastn()

blast_result = open("{}.tsv".format(args.output_name), "r")
print("If there is any error, it will appear below:\n")
print(stderr)

lines = blast_result.read()
print("BLASTn results achieved! Check {}.tsv.".format(args.output_name))
print("*"*50, "\n Thank you for using this software! Feel free to share!\n", "*"*50)
