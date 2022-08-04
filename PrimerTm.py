# -*- coding: UTF-8 -*-
#!/usr/bin/python3.8

from Bio.SeqUtils import MeltingTemp as tm
from Bio.Seq import Seq
import pandas as pd
import numpy as np


# print('NN_3: {}'.format(tm.Tm_NN(myseq3, nn_table=tm.DNA_NN3, Mg=1.5, Tris=10, dnac1=500, dNTPs=0.8, Na=65)))


def getTm(archive):
    with open(archive, "r"):
        # Open file and determine dataframe
        df = pd.read_csv(archive, delimiter="\t", header=0)
        print(df.columns)
        qseq = df[['qseq']]
        print('Sequences achieved!')
        Tm_values = list()

        # Get sequences that anealed with your primers and put them into a Seq data type, so Biopython can calculate Tm
        for index, row in df[['qseq']].iterrows():
            seq = Seq(row['qseq'])
            Tm_values.append(tm.Tm_NN(seq, nn_table=tm.DNA_NN3, Mg=1.5, Tris=10, dnac1=500, dNTPs=0.8, Na=65))
            # print(seq)
        # print(Tm)
        df['tm'] = np.resize(Tm_values, len(df))
        # print(df[['tm']])
        print(df)


getTm('./example_data.tsv')