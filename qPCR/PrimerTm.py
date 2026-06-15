#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
Tm and specificity/sensitivity analysis for qPCR primers/probes.

Given a BLASTn result table (the .tsv produced by ``blastPrimers.py``, with a
header written by ``putHeader``), this module:

  * ``getTm``        - computes the melting temperature (Tm) of every annealing
                       sequence (``qseq``) and flags whether each annealing has a
                       Tm close enough (<= 6 degC difference) to the primer's own
                       Tm to realistically anneal.
  * ``checkSpecSens`` - using the target species (inferred from the first BLAST
                       row) and the ``same_tm`` flag, counts true/false
                       positives/negatives and writes a per-target report with
                       sensitivity and specificity.

Inputs/outputs are plain tab-separated files so the steps can be chained.
"""

from Bio.SeqUtils import MeltingTemp as tm
from Bio.Seq import Seq
import pandas as pd
import re

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
    for _, row in df.iterrows():
        seq = Seq(str(row["qseq"]))
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


def checkSpecSens(file):
    """Compute sensitivity/specificity from a Tm-annotated BLAST table.

    The target species is inferred from the first row of ``file``. Each row is
    classified by exact binomial match against the target and its ``same_tm``
    flag, and a ``report_<target>.tsv`` summary is written.
    """
    df = pd.read_csv(file, delimiter="\t", header=0)

    target_ssciname = _binomial(df["sscinames"].iloc[0])
    if target_ssciname is None:
        raise ValueError(
            f"Could not determine target species from first row: "
            f"{df['sscinames'].iloc[0]!r}")
    print(target_ssciname)

    false_positive = false_negative = true_positive = true_negative = 0
    # Seeded with a tiny value to avoid ZeroDivisionError when no negatives exist.
    total_true, total_false = 0, 0.000001
    species_false_positive, species_false_negative = [], []
    skipped = 0

    for index, row in df.iterrows():
        is_match_candidate = bool(row["same_tm"])
        if is_match_candidate:
            total_true += 1
        else:
            total_false += 1

        row_name = _binomial(row["sscinames"])
        if row_name is None:
            skipped += 1
            continue

        is_target = row_name == target_ssciname
        if not is_target and is_match_candidate:
            false_positive += 1
            species_false_positive.append(row["sscinames"])
        elif not is_target and not is_match_candidate:
            true_negative += 1
        elif is_target and is_match_candidate:
            true_positive += 1
        elif is_target and not is_match_candidate:
            false_negative += 1
            species_false_negative.append(row["sscinames"])

    total = false_negative + false_positive + true_negative + true_positive
    if skipped:
        print(f"Skipped {skipped} row(s) without a two-token species name.")
    print(f"Falsos positivos: {false_positive}\nFalsos negativos: {false_negative}\n"
          f"Positivos: {true_positive}\nNegativos: {true_negative}")
    print(f"Falsos positivos: {species_false_positive}\n"
          f"Falsos negativos: {species_false_negative}")

    slug = re.sub(r"[^\w]+", "_", target_ssciname)
    report_name = f"report_{slug}.tsv"
    with open(report_name, "w") as outfile:
        outfile.write("False positives:\n")
        for i in species_false_positive:
            outfile.write(f"{i}\n")
        outfile.write("False Negatives:\n")
        for i in species_false_negative:
            outfile.write(f"{i}\n")
        if true_negative > 0:
            outfile.write("Sensitivity: {:.2f}% \nSpecificity: {:.2f}% ".format(
                (true_positive / total_true) * 100,
                (true_negative / total_false) * 100))
        else:
            outfile.write(
                "Sensitivity: {:.2f}% \nSpecificity: {}".format(
                    (true_positive / total_true) * 100,
                    "100%. No False negatives were found. Maybe you are analysing "
                    "just a few alignments. Try to use +500 alignments."))
        outfile.write(
            f"\n{total} sequences analysed.\nFalse positives: {false_positive}\n"
            f"False negatives: {false_negative}\nPositives: {true_positive}\n"
            f"Negatives: {true_negative}")
    print(f"See your results in {report_name}")
