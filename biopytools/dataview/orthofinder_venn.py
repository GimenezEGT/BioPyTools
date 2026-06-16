"""Venn diagrams of OrthoFinder gene counts (EXPERIMENTAL / work in progress).

Status: incomplete. The original script was a scratch draft with a hardcoded
absolute input path and a commented-out plotting body; it never produced a
diagram. It is kept here, importable and side-effect-free, as a starting point.

Intended behaviour (not yet implemented): read an OrthoFinder
``Orthogroups.GeneCount.tsv``, determine which orthogroups are unique to each
genome, and render a 2-/3-way Venn diagram with ``matplotlib-venn``.

Running it currently reports that it is unimplemented rather than crashing.
"""

import argparse
import sys

import pandas as pd


def load_gene_counts(path):
    """Load an OrthoFinder ``Orthogroups.GeneCount.tsv`` into a DataFrame."""
    return pd.read_csv(path, delimiter="\t")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="(EXPERIMENTAL) Venn diagrams of OrthoFinder gene counts.")
    parser.add_argument(
        "gene_count_tsv",
        help="Path to an OrthoFinder Orthogroups.GeneCount.tsv file.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    df = load_gene_counts(args.gene_count_tsv)
    print(f"Loaded {len(df)} orthogroups from {args.gene_count_tsv}.")
    sys.exit(
        "orthofinder_venn is experimental: the Venn rendering is not yet "
        "implemented. See the module docstring.")


if __name__ == "__main__":
    main()
