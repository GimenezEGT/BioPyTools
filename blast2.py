'''
Script to, from a nucleotide FASTA file containing sequences of primers and probes, that is, small sequences, check the
specificity of these sequences by blastn algorithm.

Author: Enrico Giovanelli Tacconi Gimenez
e-mail: gimenezenrico@yahoo.com.br
Requisites: blast+; python3; taxdb in the same folder you run this code
'''

from sys import stderr, stdout
from Bio.Blast.Applications import *

path = str(input("Type the path to fasta file: "))
output_name = str(input("Please, name your output prefix: "))
search_strategy = str(input("Please, put the path to strategy file: "))
comando_blastn = NcbiblastnCommandline(query=path, import_search_strategy=search_strategy, remote=True, \
    outfmt='6 qseqid qcovs sscinames pident evalue', out="{}.out.txt".format(output_name))
print("Running BLASTn: {}".format(comando_blastn))

stdout, stderr = comando_blastn()

blast_result = open("{}.out.txt".format(output_name), "r")

lines = blast_result.read()
print(lines)
