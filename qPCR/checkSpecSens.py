#!/usr/bin/python3.8
# -*- coding: UTF-8 -*-

from Bio.Seq import Seq
import pandas as pd
import numpy as np


def checkSpecSens(file):
    df = pd.read_csv(file, delimiter="\t", header=0)
    target_taxid = df['staxids'][0]

    for index, row in df[['staxids']].iterrows():
        if row['staxids'] != target_taxid and df['same_tm'][index] == True:
            pass # contar linhas nesta condição, dizer quais as espécies que pega
        elif row['staxids'] != target_taxid and df['same_tm'][index] == False:
            pass # contar linhas nesta condição
        elif row['staxids'] == target_taxid and df['same_tm'][index] == True:
            pass # contar linhas nesta condição, dizer quais as espécies que pega
        elif row['staxids'] == target_taxid and df['same_tm'][index] == False:
            pass # contar linhas nesta condição, dizer quais as espécies que pega
        else:
            print('FATAL ERROR: ERR01 - NO CONDITIONS AVAILABLE')

checkSpecSens('./example_data.tsv')
