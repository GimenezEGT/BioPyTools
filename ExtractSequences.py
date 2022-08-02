#! /usr/bin/python3.8
from Bio import SeqIO

arq = input('Digite o caminho do arquivo: ')

with open(str(arq), 'r') as entrada:
    for rec in SeqIO.parse(entrada, 'fasta'):
        id = rec.id
        with open(f"{id}.fasta",'w') as output:
            SeqIO.write(rec, output, 'fasta')
