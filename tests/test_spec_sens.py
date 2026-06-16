"""Exact-classification tests for the qPCR spec/sens step (SC-001, FR-001/002).

The fixture ``spec_sens_known.tsv`` has a hand-counted mix of target,
non-target, superstring, and one-token species rows. These tests pin the exact
counts so the substring-matching regression (review C2) can never come back.
"""

import os

import pandas as pd
import pytest

from biopytools.qpcr import primer_tm

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "spec_sens_known.tsv")


@pytest.fixture
def known_df():
    return pd.read_csv(FIXTURE, delimiter="\t", header=0)


def test_target_inferred_from_first_row(known_df):
    result = primer_tm.classify(known_df)
    assert result.target == "homo sapiens"


def test_exact_classification_counts(known_df):
    result = primer_tm.classify(known_df)
    # Row-by-row expectation (see fixture):
    #   Homo sapiens / True      -> true positive
    #   Homo sapiens / False     -> false negative
    #   Pan troglodytes / True   -> false positive
    #   Pan troglodytes / False  -> true negative
    #   Homo sapiensaa / True    -> false positive (exact match rejects superstring)
    #   uncultured / True        -> skipped (one token)
    assert result.true_positive == 1
    assert result.false_negative == 1
    assert result.false_positive == 2
    assert result.true_negative == 1
    assert result.skipped == 1
    assert result.total == 5


def test_sensitivity_specificity_values(known_df):
    """SC-001: classic diagnostic metrics over classified rows only.

    Skipped (one-token) rows must NOT affect the denominators.
    sensitivity = TP/(TP+FN) = 1/2 = 50.0%
    specificity = TN/(TN+FP) = 1/3 = 33.33%
    """
    result = primer_tm.classify(known_df)
    assert result.n_target == 2          # TP + FN, skipped row excluded
    assert result.n_non_target == 3      # TN + FP
    assert result.sensitivity == 50.0
    assert result.specificity == pytest.approx(100 / 3)


def test_superstring_is_not_a_target_match(known_df):
    """``Homo sapiensaa`` must NOT count as the target ``homo sapiens``."""
    result = primer_tm.classify(known_df)
    assert "Homo sapiensaa" in result.species_false_positive


def test_one_token_species_skipped_not_fatal(known_df):
    result = primer_tm.classify(known_df)
    assert result.skipped == 1


def test_report_written_and_input_preserved(known_df, tmp_path):
    before = open(FIXTURE, "rb").read()
    report = primer_tm.checkSpecSens(FIXTURE, out_dir=str(tmp_path))
    assert os.path.exists(report)
    # The Tm table fed in must be untouched (FR-003/SC-007).
    assert open(FIXTURE, "rb").read() == before
