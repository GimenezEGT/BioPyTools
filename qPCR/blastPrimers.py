#! /usr/bin/python3
'''
Script to, from a nucleotide FASTA file containing sequences of primers and
probes, that is, small sequences, check the
specificity of these sequences by blastn algorithm.

Author: Enrico Giovanelli Tacconi Gimenez
e-mail: gimenezenrico@yahoo.com.br
Requisites: blast+; python3; taxdb in the same folder you run this code or
referenced on your bashrc file
'''
from Bio.Blast.Applications import NcbiblastnCommandline
import argparse
from putHeader import putHeader
import PrimerTm


def parse_args():
    parser = argparse.ArgumentParser(
        description="Checks your primers specificity with BLASTn.")
    parser.add_argument("query", help="Type the path to your query file.")
    parser.add_argument(
        "output_name",
        help="Prefix of the output file (a .tsv file).", type=str)
    parser.add_argument(
        "num_alignments", type=int, default=1000,
        help="Number of alignments BLAST should return. Default=1000")
    return parser.parse_args()


def main():
    print("*" * 100 + "\n" +
          "WELCOME TO CHECK PRIMERS SOFTWARE. IT CHECKS PRIMERS WITH BLAST!\n"
          + "*" * 100 + "\n\n")
    args = parse_args()

    blast_output = f"{args.output_name}.tsv"
    comando_blastn = NcbiblastnCommandline(
        query=args.query, evalue=1000, word_size=7, penalty=-3, reward=1,
        remote=True, db="nt",
        outfmt='6 qseqid sscinames qcovs pident evalue staxids qseq '
               'sblastnames salltitles stitle',
        out=blast_output, num_alignments=args.num_alignments)
    print("Running BLASTn: {}\n".format(comando_blastn))

    _stdout, stderr = comando_blastn()
    print("If there is any error, it will appear below:\n\n")
    print(stderr)

    putHeader(blast_output)
    print(f"BLASTn results achieved! Check {blast_output}.")
    print("*" * 100,
          "\n Thank you for using this software! Feel free to share!\n",
          "*" * 100)

    # getTm writes an augmented copy (does not destroy the raw BLAST output)
    # and returns its path, which feeds the specificity/sensitivity step.
    tm_table = PrimerTm.getTm(blast_output)
    PrimerTm.checkSpecSens(tm_table)


if __name__ == "__main__":
    main()
