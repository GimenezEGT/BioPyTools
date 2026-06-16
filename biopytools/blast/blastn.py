"""BLASTn wrapper for short nucleotide queries (primers).

Runs BLASTn of short sequences against ``nt`` with primer-appropriate
parameters, writes a tab-separated table using the shared ``outfmt`` field list,
and inserts the matching column header (FR-011).

Author: Enrico Giovanelli Tacconi Gimenez (gimenezenrico@yahoo.com.br)
Requisites: NCBI BLAST+ (``blastn`` on PATH); a local ``taxdb`` so scientific
names resolve; network access for remote BLAST.
"""

import argparse
import shutil
import subprocess
import sys

from ..common.blast import outfmt_arg
from ..qpcr.put_header import putHeader


def run_blastn(query, output_prefix, num_alignments=1000, db="nt", remote=True):
    """Run BLASTn and write ``<output_prefix>.tsv`` (header inserted).

    Returns the path of the written ``.tsv``. Raises ``FileNotFoundError`` if
    ``blastn`` is missing and ``RuntimeError`` if BLAST fails.
    """
    if shutil.which("blastn") is None:
        raise FileNotFoundError(
            "The 'blastn' executable was not found on PATH. Install NCBI "
            "BLAST+ and ensure 'blastn' is reachable.")

    blast_output = f"{output_prefix}.tsv"
    command = [
        "blastn",
        "-query", query,
        "-db", db,
        "-out", blast_output,
        "-outfmt", outfmt_arg(),
        "-word_size", "7",
        "-penalty", "-3",
        "-reward", "1",
        "-evalue", "1000",
        "-num_alignments", str(num_alignments),
    ]
    if remote:
        command.append("-remote")
    print(f"Running BLASTn: {' '.join(command)}\n")

    result = subprocess.run(command, capture_output=True, text=True)
    if result.stderr:
        print("BLAST reported the following on stderr:\n")
        print(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(
            f"BLASTn failed (exit {result.returncode}). See stderr above.")

    putHeader(blast_output)
    print(f"BLASTn results achieved! Check {blast_output}.")
    return blast_output


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="BLASTn of short nucleotide sequences (primers) against a "
                    "database; writes a tab-separated table with a header.")
    parser.add_argument("query", help="Path to the query FASTA file.")
    parser.add_argument("output_prefix", help="Prefix of the output .tsv file.")
    parser.add_argument(
        "--num-alignments", type=int, default=1000,
        help="Number of alignments BLAST should return (default: 1000).")
    parser.add_argument(
        "--db", default="nt", help="BLAST database name (default: nt).")
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
        run_blastn(args.query, args.output_prefix,
                   num_alignments=args.num_alignments, db=args.db,
                   remote=args.remote)
    except (FileNotFoundError, RuntimeError) as exc:
        sys.exit(f"Error: {exc}")


if __name__ == "__main__":
    main()
