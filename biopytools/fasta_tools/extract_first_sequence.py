"""Extract the first (consensus) sequence from each FASTA in a directory.

Useful for NCBI Virus alignment exports, where the first record of each file is
the consensus. The scan is restricted to FASTA-extension files and skips the
tool's own output and non-files; empty parses are guarded so an unparseable file
can't crash the run (FR-007).

Example:
    biopytools-extract-first ./alignments -o consensos.fasta
"""

import argparse
import os

from Bio import SeqIO

from ..common.io import is_fasta_path


def extract_first_sequences(directory, output):
    """Write the first record of every FASTA in ``directory`` to ``output``.

    Returns the number of consensus records written. The ``output`` path is
    skipped if it lives inside ``directory`` so the growing result is never
    re-read.
    """
    output_abs = os.path.abspath(output)
    written = 0
    with open(output, "w") as out_handle:
        for name in sorted(os.listdir(directory)):
            path = os.path.join(directory, name)
            if os.path.abspath(path) == output_abs:
                continue
            if not is_fasta_path(path):
                continue
            records = list(SeqIO.parse(path, "fasta"))
            if not records:
                print(f"Skipping {name}: no FASTA records found.")
                continue
            SeqIO.write(records[0], out_handle, "fasta")
            written += 1
    return written


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Extract the first (consensus) sequence from each FASTA "
                    "file in a directory into a single multi-FASTA.")
    parser.add_argument(
        "directory", help="Directory containing the alignment FASTA files.")
    parser.add_argument(
        "-o", "--output", default="consensos.fasta",
        help="Output multi-FASTA path (default: consensos.fasta).")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    count = extract_first_sequences(args.directory, args.output)
    print(f"Wrote {count} consensus sequence(s) to {args.output}.")


if __name__ == "__main__":
    main()
