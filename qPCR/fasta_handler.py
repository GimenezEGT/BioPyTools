#!/usr/bin/python3

#####
'''
Takes an excel from PrimerQuest(IDT) with primers designed and output them into a fasta file, so you can
check specificity with BLASTn.
Also takes one file with several fastas and separate them in files containing only one fasta seq.

Author: Enrico Giovanelli Tacconi Gimenez
e-mail: gimenezenrico@yahoo.com.br
Requisites:
- biopython latest version
- python 3
- pandas latest version
'''
####


from os import remove
from Bio import SeqIO
import pandas as pd

def get_from_IDT(path, output):
# Take input from user
    df = pd.read_excel(path)
    df['AssaySet'] = df['AssaySet'].str.replace((" "), ("_"))
    print(df['AssaySet'])
    print("Removing empty fasta...")

    with open("primers.fas", "w+") as saida:
        for index, row in df.iterrows():
            #print(row['AssaySet'], row['Type'], row['Sequence'])
            # if
            saida.write(">{}_{}\n{}\n".format(
                row['AssaySet'], row['Type'], row['Sequence']))

    with open('{}.fas'.format(output), 'a+') as final:
        with open('./primers.fas', 'r') as entrada:
            for rec in SeqIO.parse('./primers.fas', 'fasta'):
                # print(rec)
                if 'nan' in rec.seq:
                    pass
                else:
                    SeqIO.write(rec, final, 'fasta')
    remove('./primers.fas')
    print("\n Done! Check {}.fas.".format(output))


def sep_seqs(arq):
    arq = input('Digite o caminho do arquivo: ')
    with open(str(arq), 'r') as entrada:
        for rec in SeqIO.parse(entrada, 'fasta'):
            id = rec.id
            with open(f"{id}.fasta", 'w') as output:
                SeqIO.write(rec, output, 'fasta')
