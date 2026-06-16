"""Tm-calculation tests (value within tolerance, ``same_tm`` threshold)."""

import pandas as pd

from biopytools.qpcr import primer_tm
from biopytools.common.blast import OUTFMT_FIELDS


def _blast_row(qseqid, sscinames, qseq):
    """Build a minimal BLAST-table row dict with the shared columns."""
    values = {field: "" for field in OUTFMT_FIELDS}
    values.update(qseqid=qseqid, sscinames=sscinames, qseq=qseq)
    return values


def _write_tsv(path, rows):
    pd.DataFrame(rows, columns=OUTFMT_FIELDS).to_csv(
        path, sep="\t", index=False)


def test_getTm_adds_columns_and_preserves_input(tmp_path):
    src = tmp_path / "blast.tsv"
    rows = [
        _blast_row("p1", "Homo sapiens", "ACGTACGTACGTACGTACGT"),
        _blast_row("p1", "Homo sapiens", "ACGTACGTACGTACGTACGT"),
    ]
    _write_tsv(src, rows)
    before = src.read_bytes()

    out = primer_tm.getTm(str(src))

    # Raw BLAST table preserved; a separate .tm.tsv produced (FR-003).
    assert src.read_bytes() == before
    assert out.endswith(".tm.tsv")

    df = pd.read_csv(out, sep="\t")
    assert "tm" in df.columns and "same_tm" in df.columns
    # A 20-mer of ACGT repeats has a Tm comfortably in the 40-80 degC band.
    assert 40 < df["tm"].iloc[0] < 80


def test_same_tm_threshold(tmp_path):
    """Identical sequences share a Tm, so ``same_tm`` is True for row 0's twin."""
    src = tmp_path / "blast.tsv"
    rows = [
        _blast_row("p1", "Homo sapiens", "ACGTACGTACGTACGTACGT"),
        _blast_row("p1", "Homo sapiens", "ACGTACGTACGTACGTACGT"),
    ]
    _write_tsv(src, rows)
    out = primer_tm.getTm(str(src))
    df = pd.read_csv(out, sep="\t")
    assert bool(df["same_tm"].iloc[0]) is True
    assert bool(df["same_tm"].iloc[1]) is True
