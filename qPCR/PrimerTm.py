#!/usr/bin/python3.8
# -*- coding: UTF-8 -*-

from Bio.SeqUtils import MeltingTemp as tm
from Bio.Seq import Seq
import pandas as pd
import numpy as np


def getTm(archive):
    with open(archive, "r") as file:
        # Open file and determine dataframe
        df = pd.read_csv(file, delimiter="\t", header=0)
        # qseq = df[['qseq']]
        print('Sequences achieved!')
        Tm_values = list()
        aneal = list()  # Stores values for if the qseq hav a Tm very diferent from the primer tm. False not anel; True aneal

        # Get sequences that anealed with your primers and put them into a Seq data type,
        # so Biopython can calculate Tm.
        for index, row in df[['qseq']].iterrows():
            seq = Seq(row['qseq'])
            Tm_values.append(tm.Tm_NN(seq, nn_table=tm.DNA_NN3,
                             Mg=1.5, Tris=10, dnac1=500, dNTPs=0.8, Na=65))
        df['tm'] = np.resize(Tm_values, len(df))
        print(df)

        # Calculating diference between annealings and primer Tm
        tm_diference = []
        tm_primer = df['tm'][0]

        print(f'Your primer has a melting temperature of {tm_primer}ºC')
        for index, row in df[['tm']].iterrows():
            tm_annealing = row['tm']
            diference = tm_primer - tm_annealing
            tm_diference.append(diference)

            if diference > 6 or diference < (-6):
                aneal.append(False)
            else:
                aneal.append(True)
        df['same_tm'] = np.resize(aneal, len(df))
        print(df)

        # Overwrite file with Tm's
        with open(archive, 'w') as writable:
            df.to_csv(writable, sep="\t", encoding='utf-8')