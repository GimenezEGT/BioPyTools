# -*- coding: UTF-8 -*-
#!/usr/bin/python3.8

from Bio.SeqUtils import MeltingTemp as tm
from Bio.Seq import Seq
from numpy import array_equal
import pandas as pd


print('NN_3: {}'.format(tm.Tm_NN(myseq3, nn_table=tm.DNA_NN3, Mg=1.5, Tris=10, dnac1=500, dNTPs=0.8, Na=65)))

def getTm(archive, sequence):
    df = pd.read_csv(archive,sep="t")
    df.columns = ['qseqid', 'sscinames', 'qcovs', 'pident', 'evalue', 'staxids', 'qseq']
    hits = df[['qseq']]