"""IDT PrimerQuest Excel -> FASTA, and multi-FASTA splitting.

Two subcommands:

  * ``excel-to-fasta`` - read an IDT PrimerQuest Excel sheet and write the
                         primer/probe sequences to a FASTA (empty/``nan``
                         sequences are skipped) so they can be BLASTed.
  * ``split``          - split a multi-FASTA into one file per record, written
                         to ``--out-dir`` with record ids sanitised for use as
                         filenames (FR-004, FR-008).

Author: Enrico Giovanelli Tacconi Gimenez (gimenezenrico@yahoo.com.br)

Example:
    biopytools-fasta-handler excel-to-fasta primers.xlsx -o primers.fasta
    biopytools-fasta-handler split primers.fasta --out-dir split_out
"""

import argparse

import pandas as pd

from ..common.fasta import split_records


def excel_to_fasta(path, output):
    """Convert an IDT PrimerQuest Excel sheet to a FASTA file.

    Returns the number of records written. Rows whose sequence is empty or
    ``nan`` are skipped.
    """
    df = pd.read_excel(path)
    required = ["AssaySet", "Type", "Sequence"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(
            f"Excel sheet {path} is missing required column(s): "
            f"{', '.join(missing)}. Expected an IDT PrimerQuest export with "
            f"columns {required}.")
    df["AssaySet"] = df["AssaySet"].astype(str).str.replace(" ", "_")

    written = 0
    with open(output, "w") as out_handle:
        for _, row in df.iterrows():
            sequence = str(row["Sequence"]).strip()
            if not sequence or sequence.lower() == "nan":
                continue
            out_handle.write(f">{row['AssaySet']}_{row['Type']}\n{sequence}\n")
            written += 1
    return written


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="IDT Excel -> FASTA conversion and multi-FASTA splitting.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_excel = sub.add_parser(
        "excel-to-fasta", help="Convert an IDT PrimerQuest Excel sheet to FASTA.")
    p_excel.add_argument("input_xlsx", help="Path to the IDT Excel file.")
    p_excel.add_argument(
        "-o", "--output", required=True, help="Output FASTA path.")

    p_split = sub.add_parser(
        "split", help="Split a multi-FASTA into one file per record.")
    p_split.add_argument("input_fasta", help="Path to the multi-FASTA file.")
    p_split.add_argument(
        "--out-dir", default=".",
        help="Directory for the per-record FASTA files (default: current dir).")

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.command == "excel-to-fasta":
        count = excel_to_fasta(args.input_xlsx, args.output)
        print(f"Wrote {count} sequence(s) to {args.output}.")
    elif args.command == "split":
        written = split_records(args.input_fasta, out_dir=args.out_dir)
        print(f"Wrote {len(written)} record file(s) to {args.out_dir}.")


if __name__ == "__main__":
    main()
