#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# This script defines a Tm of your primer and the annealings returned from blastn, compares and say to you if the difference between your primer and the annealing returned isd more than 6ºC.
# This way you can choose the best set of primers based on Tm of the returned species

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
        print(df['qseq'])
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


def checkSpecSens(file):
    df = pd.read_csv(file, delimiter="\t", header=0)
    # target_taxid = df['staxids'][0]
    target_ssciname = (df['sscinames'][0].split(
    )[0] + df['sscinames'][0].split()[1]).lower()
    print(target_ssciname)
    false_positive, false_negative, true_positive, true_negative, total_true, total_false = 0, 0, 0, 0, 0, 0.000001
    species_false_positive, species_false_negative = [], []

    for index, row in df[['sscinames']].iterrows():
        if df['same_tm'][index] == True:
            total_true += 1
        else:
            total_false += 1
        try:
            if str(row['sscinames'].split()[0]+row['sscinames'].split()[1]).lower() not in target_ssciname and df['same_tm'][index] == True:
                false_positive += 1  # contar linhas nesta condição, dizer quais as espécies que pega
                species_false_positive.append(row['sscinames'])
            elif str(row['sscinames'].split()[0]+row['sscinames'].split()[1]).lower() not in target_ssciname and df['same_tm'][index] == False:
                true_negative += 1  # contar linhas nesta condição
            elif str(row['sscinames'].split()[0]+row['sscinames'].split()[1]).lower() in target_ssciname and df['same_tm'][index] == True:
                true_positive += 1  # contar linhas nesta condição, dizer quais as espécies que pega
            elif str(row['sscinames'].split()[0]+row['sscinames'].split()[1]).lower() in target_ssciname and df['same_tm'][index] == False:
                false_negative += 1  # contar linhas nesta condição, dizer quais as espécies que pega
                species_false_negative.append(row['sscinames'])
        except pd.errors as e:
            print(f'Error: {e}')

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
        if true_negative > 0:
            outfile.write("Sensitivity: {:.2f}% \nSpecifivity: {:.2f}% ".format(
                ((true_positive/total_true)*100), ((true_negative/total_false)*100)))
        else:
            outfile.write("Sensitivity: {:.2f}% \nSpecifivity: {}% ".format(((true_positive/total_true)*100),
                          "100%. No False negatives were found. Maybe you are analysing just a few alignments. Try to use +500 alignments."))
        outfile.write(
            f"""\n{total} sequences analysed.\nFalse positives: {false_positive}\nFalse negatives: {false_negative}\nPositives: {true_positive}\nNegatives: {true_negative}""")
    print(f"See your results in {outfile.name}")


checkSpecSens("./teste1.tsv")
