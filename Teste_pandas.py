# teste tratamento de output do blast com pandas

from curses import flash
import pandas as pd
import numpy as np
import re
'''
with open('B1_primers.out.csv', 'r') as fin:
    with open('B1_primers_1.out.csv', 'w+') as fout:
        for line in fin:
            fout.write(line.replace(",", "_"))'''

headerList = ["qseqid", "sscinames", "qcovs", "pident", "evalue"]
df = pd.read_csv('B1_primers_blast.out.tsv', names=headerList, sep='\t')
print(df)
print("DataFrame created!")


a = df[df['sscinames'].str.contains('(.+gondii.+)',regex=True,na=False)]
print(a)