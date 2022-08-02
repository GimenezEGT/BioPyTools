# -*- coding: UTF-8 -*-
#!/usr/bin/python3.8

from Bio.SeqUtils import MeltingTemp as tm
from Bio.Seq import Seq
from Bio.SeqUtils.MeltingTemp import make_table, DNA_NN2
from numpy import array_equal
import pandas as pd

table = DNA_NN2 # Sugimoto '96
table['init_A/T']
(0, 0)
newtable = make_table(oldtable=DNA_NN2, values={'init': (0, 0),'init_A/T': (2.3, 4.1),'init_G/C': (0.1, -2.8)})

# mystring, tm1 = 'TTGTTACTGTGGTAGA', 51.0
# print(f'\n{mystring} Tm no Tm Calculator Thermo: {float(tm1)}')
# myseq =  Seq(mystring)

# print('Wallace: {}'.format(tm.Tm_Wallace(myseq)))
# print('GC: {}'.format(tm.Tm_GC(myseq, Mg=1.5, Tris=10, dNTPs=0.8, Na=65)))
# print('NN_1: {}'.format(tm.Tm_NN(myseq, nn_table=tm.DNA_NN1, Mg=1.5, Tris=10, dnac1=500,dNTPs=0.8, Na=65)))
# print('NN_2: {}'.format(tm.Tm_NN(myseq, nn_table=tm.DNA_NN2, Mg=1.5, Tris=10, dnac1=500,dNTPs=0.8, Na=65)))
# print('NN_3: {}'.format(tm.Tm_NN(myseq, nn_table=tm.DNA_NN3, Mg=1.5, Tris=10, dnac1=500,dNTPs=0.8, Na=65)))
# print('NN_4: {}'.format(tm.Tm_NN(myseq, nn_table=tm.DNA_NN4, Mg=1.5, Tris=10, dnac1=500,dNTPs=0.8, Na=65)))
# print('NN_newtable: {}'.format(tm.Tm_NN(myseq, nn_table=newtable,Tris=10, Mg=1.5, dnac1=500,dNTPs=0.8, Na=65)))


# mystring2, tm2 = 'TGTTACTGTGGTAGAT', 50.7
# print(f'\n{mystring2} Tm no Tm Calculator Thermo: {float(tm2)}')
# myseq2 =  Seq(mystring2)

# print('Wallace: {}'.format(tm.Tm_Wallace(myseq2)))
# print('GC: {}'.format(tm.Tm_GC(myseq2, Mg=1.5, Tris=10, dNTPs=0.8, Na=65)))
# print('NN_1: {}'.format(tm.Tm_NN(myseq2, nn_table=tm.DNA_NN1, Mg=1.5, Tris=10, dnac1=500,dNTPs=0.8, Na=65)))
# print('NN_2: {}'.format(tm.Tm_NN(myseq2, nn_table=tm.DNA_NN2, Mg=1.5, Tris=10, dnac1=500,dNTPs=0.8, Na=65)))
# print('NN_3: {}'.format(tm.Tm_NN(myseq2, nn_table=tm.DNA_NN3, Mg=1.5, Tris=10, dnac1=500, dNTPs=0.8, Na=65)))
# print('NN_4: {}'.format(tm.Tm_NN(myseq2, nn_table=tm.DNA_NN4, Mg=1.5, Tris=10, dnac1=500,dNTPs=0.8, Na=65)))
# print('NN_newtable: {}'.format(tm.Tm_NN(myseq2, nn_table=newtable,dNTPs=0.8,Tris=10, Mg=1.5, dnac1=500, Na=65)))

# mystring3,tm3 = 'GTTACTGTGGTAGATA', 48.3
# print(f'\n{mystring3} Tm no Tm Calculator Thermo: {float(tm3)}')
# myseq3 =  Seq(mystring3)

# print('Wallace: {}'.format(tm.Tm_Wallace(myseq2)))
# print('GC: {}'.format(tm.Tm_GC(myseq3, Mg=1.5, Tris=10, dNTPs=0.8, Na=65)))
# print('NN_1: {}'.format(tm.Tm_NN(myseq3, nn_table=tm.DNA_NN1, Mg=1.5, Tris=10, dnac1=500,dNTPs=0.8, Na=65)))
# print('NN_2: {}'.format(tm.Tm_NN(myseq3, nn_table=tm.DNA_NN2, Mg=1.5, Tris=10, dnac1=500,dNTPs=0.8, Na=65)))
# print('NN_3: {}'.format(tm.Tm_NN(myseq3, nn_table=tm.DNA_NN3, Mg=1.5, Tris=10, dnac1=500, dNTPs=0.8, Na=65)))
#USE NN_3!!
# print('NN_4: {}'.format(tm.Tm_NN(myseq3, nn_table=tm.DNA_NN4, Mg=1.5, Tris=10, dnac1=500,dNTPs=0.8, Na=65)))
# print('NN_newtable: {}'.format(tm.Tm_NN(myseq3, nn_table=newtable,dNTPs=0.8,Tris=10, Mg=1.5, dnac1=500, Na=65)))


def getTm(archive, sequence):
    