#!/usr/bin/python3.8
# -*- coding: UTF-8 -*-

from Bio.Seq import Seq
import pandas as pd
import numpy as np


def checkSpecSens(file):
    df = pd.read_csv(file, delimiter="\t", header=0)
    target_taxid = df[['taxid']][0]
    print(target_taxid)


checkSpecSens('./example_data.tsv')
