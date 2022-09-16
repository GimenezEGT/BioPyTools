#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from Bio.Seq import Seq
import pandas as pd
import numpy as np


def checkSpecSens(file):
    df = pd.read_csv(file, delimiter="\t", header=0)
    target_taxid = df['staxids'][0]
    target_ssciname = (df['sscinames'][0].split(
    )[0] + df['sscinames'][0].split()[1]).lower()
    print(target_ssciname)
    false_positive = 0
    false_negative = 0
    true_positive = 0
    true_negative = 0
    species_false_positive = []
    total_true = 0
    species_false_negative = []
    total_false = 0

    for index, row in df[['sscinames']].iterrows():
        if df['same_tm'][index] == True:
            total_true += 1
        else:
            total_false += 1
        try:
            if (row['sscinames'].split()[0]+row['sscinames'].split()[1]).lower() not in target_ssciname and df['same_tm'][index] == True:
                false_positive += 1  # contar linhas nesta condição, dizer quais as espécies que pega
                species_false_positive.append(row['sscinames'])
                false_positive_tm.append(row['tm'])
            elif (row['sscinames'].split()[0]+row['sscinames'].split()[1]).lower() not in target_ssciname and df['same_tm'][index] == False:
                true_negative += 1  # contar linhas nesta condição
            elif (row['sscinames'].split()[0]+row['sscinames'].split()[1]).lower() in target_ssciname and df['same_tm'][index] == True:
                true_positive += 1  # contar linhas nesta condição, dizer quais as espécies que pega
            elif (row['sscinames'].split()[0]+row['sscinames'].split()[1]).lower() in target_ssciname and df['same_tm'][index] == False:
                false_negative += 1  # contar linhas nesta condição, dizer quais as espécies que pega
                species_false_negative.append(row['sscinames'])
        except:
            continue

    total = false_negative + false_positive + true_negative + true_positive
    print(
        f"Falsos positivos: {false_positive}\nFalsos negativos: {false_negative}\nPositivos: {true_positive}\nNegativos: {true_negative}")
    print(
        f"Falsos positivos: {species_false_positive}\nFalsos negativos: {species_false_negative}")

    with open(f"report_{target_ssciname}.tsv", "w") as outfile:
        outfile.write("False positives:\n")
        for i in species_false_positive:
            outfile.writelines(f"{i}\n")
        outfile.write("False Negatives:\n")
        for i in species_false_negative:
            outfile.writelines(f"{i}\n")
        outfile.write("Sensitivity: {:.2f}% \nSpecifivity: {:.2f}% ".format(
            ((true_positive/total_true)*100), ((true_negative/total_false)*100)))


checkSpecSens('./example_data.tsv')
