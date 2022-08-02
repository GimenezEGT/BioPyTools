from importlib.resources import path
from os import pread
from Bio import SeqIO

caminho = str(input("Put the path to multifasta file: "))
prefix = str(input("Puth the prefix of the out file: "))
saida = open('{}.faa'.format(prefix), 'w+')
excluded = open('multispecies.faa', 'w+')

for rec in SeqIO.parse(open(caminho, 'r'), "fasta"):
    print (rec.description)
    if "MULTISPECIES" in rec.description:
        SeqIO.write(rec, excluded, 'fasta')
    else:
        SeqIO.write(rec, saida, 'fasta')

saida.close
excluded.close