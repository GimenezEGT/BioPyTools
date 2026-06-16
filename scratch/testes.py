from Bio.Seq import Seq
from Bio import SeqIO

dna = Seq('ATGGCCATTCGCAAGGGTGCCCGATAG')

rna = dna.transcribe()
print("RNA: " + rna)

dna2 = rna.back_transcribe()
print("DNA: " + dna2)

prot = rna.translate()
print(prot)

for i in SeqIO.parse('arquivo.fasta', 'fasta'):
	print(i.id)
	print(i.seq)
	print(len(i))

entrada = open("arquivo.fasta","r")
saida = open("arquivo2.fasta", "w")

for i in SeqIO.parse(entrada,"fasta"):
	
	# Condicao 1 (> 10 pb) | Condicao 2 == 'C'
	if ( (len(i.seq) > 10) and (i.seq[0] == 'C')):
		SeqIO.write(i, saida, "fasta")

saida.close()


#BLAST

