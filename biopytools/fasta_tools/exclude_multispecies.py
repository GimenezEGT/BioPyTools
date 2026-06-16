"""Split a multi-FASTA file into MULTISPECIES and non-MULTISPECIES records.

Records whose description contains ``MULTISPECIES`` are written to the excluded
file (default ``multispecies.faa``); all others go to ``<prefix>.faa``. Files
are always closed via context managers (review H).

Example:
    biopytools-exclude-multispecies seqs.fasta --prefix clean
"""

import argparse

from Bio import SeqIO


def split_multispecies(input_fasta, prefix, excluded="multispecies.faa"):
    """Write non-MULTISPECIES records to ``<prefix>.faa`` and the rest to
    ``excluded``. Returns ``(kept_count, excluded_count)``."""
    kept = removed = 0
    kept_path = f"{prefix}.faa"
    with open(kept_path, "w") as keep_handle, open(excluded, "w") as excl_handle:
        for rec in SeqIO.parse(input_fasta, "fasta"):
            if "MULTISPECIES" in rec.description:
                SeqIO.write(rec, excl_handle, "fasta")
                removed += 1
            else:
                SeqIO.write(rec, keep_handle, "fasta")
                kept += 1
    return kept, removed


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Split MULTISPECIES records out of a multi-FASTA file.")
    parser.add_argument("input_fasta", help="Path to the input multi-FASTA.")
    parser.add_argument(
        "--prefix", required=True,
        help="Prefix for the kept (non-MULTISPECIES) output: <prefix>.faa.")
    parser.add_argument(
        "--excluded", default="multispecies.faa",
        help="Path for the MULTISPECIES records (default: multispecies.faa).")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    kept, removed = split_multispecies(
        args.input_fasta, args.prefix, excluded=args.excluded)
    print(f"Kept {kept} record(s) in {args.prefix}.faa; "
          f"moved {removed} MULTISPECIES record(s) to {args.excluded}.")


if __name__ == "__main__":
    main()
