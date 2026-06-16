"""BLASTp wrapper: search a protein FASTA against a database (default ``nr``).

Writes a tab-separated table of the main hit information. Argument-driven and
non-interactive (FR-004); does not dump the entire result to stdout.

Author: Enrico Giovanelli Tacconi Gimenez (gimenezenrico@yahoo.com.br)
Requisites: NCBI BLAST+ (``blastp`` on PATH); network access for remote BLAST.
"""

import argparse
import shutil
import subprocess
import sys

# A focused output format for protein hits (distinct from the nucleotide one).
BLASTP_OUTFMT = "6 qseqid sscinames pident qcovs evalue"


def run_blastp(query, output_prefix, num_alignments=5000, db="nr", remote=True):
    """Run BLASTp and write ``<output_prefix>.blastProtein.out.tsv``.

    Returns the path of the written ``.tsv``. Raises ``FileNotFoundError`` if
    ``blastp`` is missing and ``RuntimeError`` if BLAST fails.
    """
    if shutil.which("blastp") is None:
        raise FileNotFoundError(
            "The 'blastp' executable was not found on PATH. Install NCBI "
            "BLAST+ and ensure 'blastp' is reachable.")

    blast_output = f"{output_prefix}.blastProtein.out.tsv"
    command = [
        "blastp",
        "-query", query,
        "-db", db,
        "-out", blast_output,
        "-outfmt", BLASTP_OUTFMT,
        "-num_alignments", str(num_alignments),
    ]
    if remote:
        command.append("-remote")
    print(f"Running BLASTp: {' '.join(command)}\n")

    result = subprocess.run(command, capture_output=True, text=True)
    if result.stderr:
        print("BLAST reported the following on stderr:\n")
        print(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(
            f"BLASTp failed (exit {result.returncode}). See stderr above.")

    print(f"BLASTp results achieved! Check {blast_output}.")
    return blast_output


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="BLASTp of a protein FASTA against a database (default nr); "
                    "writes a tab-separated hit table.")
    parser.add_argument("query", help="Path to the protein FASTA file.")
    parser.add_argument("output_prefix", help="Prefix of the output file.")
    parser.add_argument(
        "--num-alignments", type=int, default=5000,
        help="Number of alignments BLAST should return (default: 5000).")
    parser.add_argument(
        "--db", default="nr", help="BLAST database name (default: nr).")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--remote", dest="remote", action="store_true", default=True,
        help="Run against NCBI servers (default).")
    group.add_argument(
        "--local", dest="remote", action="store_false",
        help="Run against a local database instead of remotely.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        run_blastp(args.query, args.output_prefix,
                   num_alignments=args.num_alignments, db=args.db,
                   remote=args.remote)
    except (FileNotFoundError, RuntimeError) as exc:
        sys.exit(f"Error: {exc}")


if __name__ == "__main__":
    main()
