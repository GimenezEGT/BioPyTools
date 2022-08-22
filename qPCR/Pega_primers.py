#!/usr/bin/python3

#####
'''
Takes an excel from PrimerQuest(IDT) with primers designed and output them into a fasta file, so you can
check specificity with BLASTn

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

# Take input from user
path = str(input("Type the path to the excel file: "))
output = str(input('Type the prefix of your output file: '))

df = pd.read_excel(path)
df['AssaySet'] = df['AssaySet'].str.replace((" "),("_"))
print(df['AssaySet'])
print("Removing empty fasta...")

with open("primers.fas", "w+") as saida:
    for index, row in df.iterrows():
        #print(row['AssaySet'], row['Type'], row['Sequence'])
        #if 
        saida.write(">{}_{}\n{}\n".format(row['AssaySet'], row['Type'], row['Sequence']))

with open('{}.fas'.format(output), 'a+') as final:
    with open('./primers.fas', 'r') as entrada:
            for rec in SeqIO.parse('./primers.fas', 'fasta'):
                #print(rec)
                if 'nan' in rec.seq:
                    pass
                else:
                    SeqIO.write(rec, final, 'fasta')
remove('./primers.fas')
print("\n Done! Check {}.fas.".format(output))