#! usr/bin/python3.8
# -*-coding: utf-8 -*-

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

file_name = 'CMCP6.gb'


# stores all the CDS entries
all_entries = []


gb_record = SeqIO.read(open(file_name,"r"), "genbank")


gb_feature = gb_record.features


accession = gb_record.annotations['accessions'][0]+'.'+str(gb_record.annotations['sequence_version'])

# accession = gb_record.annotations['accessions']
# print(gb_record.annotations['accessions'])

for seq_feature in gb_feature:
    if seq_feature.type=="source":
            organism = str(seq_feature.qualifiers['organism'][0]).rsplit(" ", 1)[0]
            strain = seq_feature.qualifiers['strain'][0]
            chromosome = seq_feature.qualifiers['chromosome'][0]



for seq_feature in gb_feature:
    if seq_feature.type=="CDS":
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
                        complement = str(seq_feature.location).strip('[]').split('(-)')[0]
                        
                        
                        
                    pippo = SeqRecord(
                                Seq(seq_feature.qualifiers['translation'][0]),
                                
                                id = seq_feature.qualifiers['locus_tag'][0] ,
                                
                                description = ('|'+str(old_locus_tag)+'|'+str(gene)+'|'+str(product)\
                                                +'|'+str(complement)+'|'+str(protein_id) +'|Chromosome-'+str(chromosome)\
                                                +'|'+str(accession).strip("[]").replace("'", "")+'|'+str(organism)\
                                                    +'|'+str(strain))
                                )
                    all_entries.append(pippo)
                                
# print(all_entries)
# write file
SeqIO.write(all_entries, '{}.fasta'.format(file_name[:-3]), 'fasta')