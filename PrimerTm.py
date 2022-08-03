# -*- coding: UTF-8 -*-
#!/usr/bin/python3.8

from Bio.SeqUtils import MeltingTemp as tm
from Bio.Seq import Seq
from numpy import array_equal
import pandas as pd


# print('NN_3: {}'.format(tm.Tm_NN(myseq3, nn_table=tm.DNA_NN3,
#       Mg=1.5, Tris=10, dnac1=500, dNTPs=0.8, Na=65)))


def getTm(archive):
    file = open(archive, 'r')
    line = 0
    header = ('qseqid   sscinames   qcovs   pident  evalue  staxids qseq')
    lines = archive.readlines()
    file.close()

    lines.insert(line, header + "\n")
    file.writelines(lines)
    file.close()

    # with open(archive, "r"):
    #     df = pd.read_csv(archive, delimiter="t", error_bad_lines=False)
    #     print(df[[1]])
    # df.columns = ['qseqid', 'sscinames', 'qcovs',
    #   'pident', 'evalue', 'staxids', 'qseq']
    # print(df.columns)
    # qseq = df[['qseq']]
    # print(qseq)


getTm('./example_data.tsv')
