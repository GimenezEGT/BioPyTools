"""Extract accession IDs from the headers of a FASTA file.

Reads every ``>`` header line, takes the first whitespace-delimited token as the
accession, and writes one accession per line to the output file.

Example:
    biopytools-accessions sequences.fasta -o accessions.txt
"""

import argparse


def extract_accessions(input_fasta):
    """Return the list of accession IDs from a FASTA file's headers."""
    accessions = []
    with open(input_fasta, "r") as handle:
        for line in handle:
            if line.startswith(">"):
                accessions.append(line[1:].split()[0])
    return accessions


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Extract accession IDs from FASTA headers to a text file.")
    parser.add_argument("input_fasta", help="Path to the input FASTA file.")
    parser.add_argument(
        "-o", "--output", required=True,
        help="Path to the output text file (one accession per line).")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    accessions = extract_accessions(args.input_fasta)
    with open(args.output, "w") as handle:
        for accession in accessions:
            handle.write(f"{accession}\n")
    print(f"Wrote {len(accessions)} accession(s) to {args.output}.")


if __name__ == "__main__":
    main()
