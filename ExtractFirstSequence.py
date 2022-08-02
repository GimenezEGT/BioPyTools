# -*- coding: utf-8 -*-
# Este script pega um arquivo multifasta do NCBI Virus e criar um novo multifasta com os consensos de cada um
# É útil para extrair a sequência consenso de um arquivo de alinhamento feito no NCBI Virus

from Bio import SeqIO
from os import chdir, listdir


def ExtractConsensus():
    cam = input('Digite o caminho: ')
    chdir(cam)
    listaArquivos = listdir()
    print('Existem {} arquivos de alinhamento do NCBI Virus nesta pasta.'.format(
        len(listaArquivos)))
    print('A primeira sequência de cada arquivo é o consenso, por padrão.')
    print('Extraindo os consensos...')
    with open('consensos.fasta', '+a') as output_file:
        for arq in listaArquivos:
            with open(arq, 'r') as entrada:
                records = list(SeqIO.parse(entrada, 'fasta'))
                SeqIO.write(records[0], output_file, 'fasta')
