"""Tm and specificity/sensitivity analysis for qPCR primers/probes.

Given a BLASTn result table (the ``.tsv`` produced by :mod:`blast_primers`, with
a header written by :mod:`put_header`), this module:

  * :func:`getTm`        - computes the melting temperature (Tm) of every
                           annealing sequence (``qseq``) and flags whether each
                           annealing has a Tm close enough (<= 6 degC difference)
                           to the primer's own Tm to realistically anneal.
  * :func:`classify`     - pure classification of a Tm-annotated table into
                           true/false positives/negatives by exact binomial
                           match (no I/O, so it is directly unit-testable).
  * :func:`checkSpecSens` - reads a Tm table, runs :func:`classify`, and writes a
                           per-target sensitivity/specificity report.

Inputs/outputs are plain tab-separated files so the steps can be chained.
"""

import os
from dataclasses import dataclass, field
from typing import List

import pandas as pd
from Bio.Seq import Seq
from Bio.SeqUtils import MeltingTemp as tm

from ..common.io import slugify

# Maximum tolerated difference (in degC) between the primer Tm and an annealing
# Tm for that annealing to be considered a real hybridisation.
MAX_TM_DIFFERENCE = 6


def _binomial(name):
    """Return the normalized ``genus species`` binomial of a scientific name.

    Lower-cased and reduced to the first two whitespace-separated tokens, with a
    single space kept between them so ``genus species`` can never collide with an
    unrelated concatenation. Returns ``None`` when the name has fewer than two
    tokens (e.g. ``"uncultured"``), so callers can skip those rows.
    """
    if not isinstance(name, str):
        return None
    tokens = name.split()
    if len(tokens) < 2:
        return None
    return f"{tokens[0]} {tokens[1]}".lower()


def getTm(archive, output=None):
    """Compute per-annealing Tm and the ``same_tm`` flag for a BLAST table.

    Reads ``archive`` (tab-separated, with header), adds ``tm`` and ``same_tm``
    columns and writes the result to ``output`` (defaults to
    ``<archive-without-.tsv>.tm.tsv``) without destroying the original BLAST
    output. Returns the path of the written file.
    """
    if output is None:
        base = archive[:-4] if archive.endswith(".tsv") else archive
        output = f"{base}.tm.tsv"

    df = pd.read_csv(archive, delimiter="\t", header=0)
    print("Sequences achieved!")

    # Calculate the Tm of every annealing sequence returned by BLAST.
    tm_values = []
    for position, (_, row) in enumerate(df.iterrows()):
        raw = str(row["qseq"]).strip()
        if not raw or raw.lower() == "nan":
            raise ValueError(
                f"Row {position} has an empty or missing 'qseq'; cannot compute "
                f"a melting temperature. Check the BLAST output for {archive}.")
        seq = Seq(raw)
        tm_values.append(tm.Tm_NN(seq, nn_table=tm.DNA_NN3,
                                  Mg=1.5, Tris=10, dnac1=500, dNTPs=0.8, Na=65))
    # Direct assignment: pandas raises if lengths differ (the failure we want
    # to surface), instead of np.resize silently recycling values.
    df["tm"] = tm_values

    # The primer's own Tm is the first row (the query against itself / best hit).
    tm_primer = df["tm"].iloc[0]
    print(f"Your primer has a melting temperature of {tm_primer} degC")

    anneals = [abs(tm_primer - value) <= MAX_TM_DIFFERENCE for value in df["tm"]]
    df["same_tm"] = anneals

    df.to_csv(output, sep="\t", encoding="utf-8", index=False)
    print(f"Tm table written to {output}")
    return output


@dataclass
class Classification:
    """Result of classifying a Tm-annotated BLAST table against its target."""

    target: str
    true_positive: int = 0
    true_negative: int = 0
    false_positive: int = 0
    false_negative: int = 0
    skipped: int = 0
    species_false_positive: List[str] = field(default_factory=list)
    species_false_negative: List[str] = field(default_factory=list)

    @property
    def total(self):
        """Number of classified (non-skipped) rows."""
        return (self.true_positive + self.true_negative +
                self.false_positive + self.false_negative)

    @property
    def n_target(self):
        """Target-species rows that were classified (the sensitivity base)."""
        return self.true_positive + self.false_negative

    @property
    def n_non_target(self):
        """Non-target rows that were classified (the specificity base)."""
        return self.true_negative + self.false_positive

    @property
    def sensitivity(self):
        """Classic sensitivity: ``TP / (TP + FN)`` as a percentage.

        Computed only over classified target rows; skipped (one-token) rows do
        not affect the denominator. Returns ``0.0`` when no target rows exist.
        """
        if self.n_target == 0:
            return 0.0
        return (self.true_positive / self.n_target) * 100

    @property
    def specificity(self):
        """Classic specificity: ``TN / (TN + FP)`` as a percentage.

        Computed only over classified non-target rows; skipped rows do not
        affect the denominator. Returns ``0.0`` when no non-target rows exist.
        """
        if self.n_non_target == 0:
            return 0.0
        return (self.true_negative / self.n_non_target) * 100


def classify(df, target=None):
    """Classify a Tm-annotated table by exact binomial match (FR-001/FR-002).

    The target species defaults to the binomial of the first row (the primer's
    own/best hit). A row is "target" iff its normalized binomial **equals** the
    target binomial (not substring containment). Rows whose ``sscinames`` lacks a
    two-token species name are skipped and counted, never fatal.
    """
    if target is None:
        target = _binomial(df["sscinames"].iloc[0])
        if target is None:
            raise ValueError(
                f"Could not determine target species from first row: "
                f"{df['sscinames'].iloc[0]!r}")

    result = Classification(target=target)
    for _, row in df.iterrows():
        is_match_candidate = bool(row["same_tm"])

        row_name = _binomial(row["sscinames"])
        if row_name is None:
            result.skipped += 1
            continue

        is_target = row_name == target
        if is_target and is_match_candidate:
            result.true_positive += 1
        elif is_target and not is_match_candidate:
            result.false_negative += 1
            result.species_false_negative.append(row["sscinames"])
        elif not is_target and is_match_candidate:
            result.false_positive += 1
            result.species_false_positive.append(row["sscinames"])
        else:  # not target, not match
            result.true_negative += 1

    return result


def _format_report(result):
    """Render a :class:`Classification` as the textual report body."""
    lines = ["False positives:"]
    lines += [str(s) for s in result.species_false_positive]
    lines.append("False Negatives:")
    lines += [str(s) for s in result.species_false_negative]

    if result.n_target > 0:
        lines.append(f"Sensitivity: {result.sensitivity:.2f}% ")
    else:
        lines.append(
            "Sensitivity: N/A (no target-species alignments were classified).")
    if result.n_non_target > 0:
        lines.append(f"Specificity: {result.specificity:.2f}% ")
    else:
        lines.append(
            "Specificity: N/A (no non-target alignments were found). Maybe you "
            "are analysing just a few alignments. Try to use +500 alignments.")

    lines.append("")
    lines.append(f"{result.total} sequences analysed.")
    lines.append(f"False positives: {result.false_positive}")
    lines.append(f"False negatives: {result.false_negative}")
    lines.append(f"Positives: {result.true_positive}")
    lines.append(f"Negatives: {result.true_negative}")
    return "\n".join(lines)


def checkSpecSens(file, out_dir="."):
    """Compute sensitivity/specificity from a Tm-annotated BLAST table.

    The target species is inferred from the first row of ``file``. Each row is
    classified by exact binomial match against the target and its ``same_tm``
    flag, and a ``report_<target>.tsv`` summary is written into ``out_dir``.
    Returns the path of the written report.
    """
    df = pd.read_csv(file, delimiter="\t", header=0)
    result = classify(df)
    print(result.target)

    if result.skipped:
        print(f"Skipped {result.skipped} row(s) without a two-token species name.")
    print(f"False positives: {result.false_positive}\n"
          f"False negatives: {result.false_negative}\n"
          f"Positives: {result.true_positive}\n"
          f"Negatives: {result.true_negative}")

    slug = slugify(result.target)
    report_name = os.path.join(out_dir, f"report_{slug}.tsv")
    with open(report_name, "w", encoding="utf-8") as outfile:
        outfile.write(_format_report(result))
    print(f"See your results in {report_name}")
    return report_name
