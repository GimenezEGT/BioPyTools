#! /usr/bin/python3.8
# -*-coding: utf-8 -*-

#Este script foi utilizado para extrair os CDSs do GenBank file (full) das sequências NC_018019.1 e NC_018019.2, pois o NCBI não disponibiliza arquivos fasta de CDS de seuquências de versões antigas de um genoma 

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import argparse

parser = argparse.ArgumentParser(
    description="Extracts protein CDS from gb file.")
parser.add_argument("file_name", help="Type the path to your gb file.")
parser.add_argument(
    "output_name", help="Type the prefix of the out file (the out file is a .faa file", type=str)
args = parser.parse_args()

# stores all the CDS entries
all_entries = []


gb_record = SeqIO.read(open(args.file_name, "r"), "genbank")


gb_feature = gb_record.features


accession = gb_record.annotations['accessions'][0] + \
    '.'+str(gb_record.annotations['sequence_version'])

# accession = gb_record.annotations['accessions']
# print(gb_record.annotations['accessions'])

for seq_feature in gb_feature:
    if seq_feature.type == "source":
        organism = str(seq_feature.qualifiers['organism'][0]).rsplit(" ", 1)[0]
        strain = seq_feature.qualifiers['strain'][0]
        # chromosome = seq_feature.qualifiers['chromosome'][0]


for seq_feature in gb_feature:
    if seq_feature.type == "CDS":
        if 'translation' in seq_feature.qualifiers:
            if seq_feature.qualifiers['translation'][0] != '':
                if 'gene' in seq_feature.qualifiers:
                    gene = seq_feature.qualifiers['gene'][0]

                else:

                    gene = 'not defined'

                if 'product' in seq_feature.qualifiers:
                    product = seq_feature.qualifiers['product'][0]

                else:

                    product = 'not defined'

                if 'protein_id' in seq_feature.qualifiers:
                    protein_id = seq_feature.qualifiers['protein_id'][0]

                else:

                    protein_id = 'not defined'

                if 'old_locus_tag' in seq_feature.qualifiers:
                    old_locus_tag = seq_feature.qualifiers['old_locus_tag'][0]

                else:

                    old_locus_tag = 'not defined'

                if 'locus_tag' in seq_feature.qualifiers:
                    locus_tag = seq_feature.qualifiers['locus_tag'][0]

                else:

                    locus_tag = 'not defined'

                if seq_feature.location.strand == 1:
                    complement = 'no complement'

                if seq_feature.location.strand == -1:
                    complement = str(seq_feature.location).strip(
                        '[]').split('(-)')[0]

                pippo = SeqRecord(
                    Seq(seq_feature.qualifiers['translation'][0]),

                    id=f'lcl|{accession}_prot_{protein_id}',

                    description=f'[gene={gene}][locus_tag={locus_tag}[protein={product}] [gbkey=CDS]')
                all_entries.append(pippo)

# print(all_entries)
# write file
SeqIO.write(all_entries, '{}.faa'.format(args.output_name), 'fasta')
