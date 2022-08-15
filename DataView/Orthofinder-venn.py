#!/usr/bin/python3.8

#import libraries
from ast import increment_lineno
from matplotlib_venn import venn2, venn2_circles, venn2_unweighted
from matplotlib_venn import venn3, venn3_circles
from matplotlib import pyplot as plt
import pandas as pd

arqui_Gene_Count = pd.DataFrame(pd.read_csv(
    "/home/enrico/Documentos/materialcp162/dados/CDSs/nucleotideos/OrthoFinder/Results_Aug15/Orthogroups/Orthogroups.GeneCount.tsv", delimiter="\t"))

# preciso iterar entre as linhas e descobrir qual grupo possui apenas em um dos genomas
for row in arqui_Gene_Count.iterrows():
    # Creating graphs
    # grafico = venn2(subsets=(30, 10, 5), set_labels=("Group A", "Group B"))

    # print(grafico)

    # plt.title("")
    # plt.show()
