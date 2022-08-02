'''
Script to, from a protein FASTA file containing sequences, search them in the nr database.

Author: Enrico Giovanelli Tacconi Gimenez
e-mail: gimenezenrico@yahoo.com.br
Requisites: blast+; python3; taxdb in the same folder you run this code
'''

from Bio.Blast.Applications import *

path =  str(input("Type the path to your protein fasta file: "))
output_prefix = str(input("Type the prefix to you output file: "))
comand_blastp = NcbiblastpCommandline(query=path, db="nr", out="{}.blastProtein.out.tsv".format(output_prefix), \
outfmt='6 qseqid sscinames pident qcovs evalue', remote=True, num_alignments=5000)

print("Running BLASTp: {}".format(comand_blastp))

stdout, stderr = comand_blastp()

blast_result = open("{}.blastProtein.out.tsv".format(output_prefix), "r")

lines = blast_result.read()
print(lines)