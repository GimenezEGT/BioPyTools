"""Command-line interface for the qPCR primer pipeline.

Subcommands (see ``--help`` on each):

  * ``run``      - full pipeline: BLASTn -> Tm -> specificity/sensitivity report.
  * ``tm``       - Tm annotation only, from an existing BLAST table.
  * ``specsens`` - specificity/sensitivity report only, from a Tm table.

Replaces the old interactive ``main.py``. Everything is argument-driven; the
target species is inferred from the first BLAST hit (no ``--target`` argument).
"""

import argparse
import sys

from . import blast_primers, primer_tm


def _cmd_run(args):
    blast_tsv = blast_primers.run_blast(
        args.query, args.output_prefix, num_alignments=args.num_alignments)
    tm_table = primer_tm.getTm(blast_tsv)
    primer_tm.checkSpecSens(tm_table)


def _cmd_tm(args):
    primer_tm.getTm(args.blast_tsv, output=args.output)


def _cmd_specsens(args):
    primer_tm.checkSpecSens(args.tm_tsv, out_dir=args.out_dir)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="biopytools-qpcr",
        description="qPCR primer specificity/sensitivity pipeline "
                    "(BLASTn -> Tm -> report).")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser(
        "run", help="Full pipeline: BLASTn, Tm, and spec/sens report.")
    p_run.add_argument("query", help="Path to the primer/probe FASTA.")
    p_run.add_argument("output_prefix", help="Prefix for the output files.")
    p_run.add_argument(
        "num_alignments", type=int,
        help="Number of BLAST alignments to return.")
    p_run.set_defaults(func=_cmd_run)

    p_tm = sub.add_parser(
        "tm", help="Add tm/same_tm columns to an existing BLAST table.")
    p_tm.add_argument("blast_tsv", help="Path to the BLAST .tsv (with header).")
    p_tm.add_argument(
        "-o", "--output", default=None,
        help="Output path (default: <prefix>.tm.tsv). The input is never "
             "overwritten.")
    p_tm.set_defaults(func=_cmd_tm)

    p_ss = sub.add_parser(
        "specsens", help="Write a spec/sens report from a Tm-annotated table.")
    p_ss.add_argument("tm_tsv", help="Path to the Tm-annotated .tsv.")
    p_ss.add_argument(
        "--out-dir", default=".",
        help="Directory for the report_<species>.tsv (default: current dir).")
    p_ss.set_defaults(func=_cmd_specsens)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except FileNotFoundError as exc:
        # Most often a missing BLAST+ executable or input file.
        sys.exit(f"Error: {exc}")


if __name__ == "__main__":
    main()
