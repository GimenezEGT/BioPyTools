"""Split a multi-FASTA file into MULTISPECIES and non-MULTISPECIES records.

Records whose description contains "MULTISPECIES" are written to
``multispecies.faa``; all others go to ``<prefix>.faa``.
"""
from Bio import SeqIO

caminho = input("Put the path to multifasta file: ")
prefix = input("Put the prefix of the out file: ")

with open(f"{prefix}.faa", "w") as saida, open("multispecies.faa", "w") as excluded:
    for rec in SeqIO.parse(caminho, "fasta"):
        print(rec.description)
        if "MULTISPECIES" in rec.description:
            SeqIO.write(rec, excluded, "fasta")
        else:
            SeqIO.write(rec, saida, "fasta")
