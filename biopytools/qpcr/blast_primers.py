"""Run BLASTn for qPCR primer/probe specificity checking.

From a nucleotide FASTA of primers/probes (short sequences), runs a remote
BLASTn against ``nt`` with primer-appropriate parameters and writes a tab-
separated table (with the shared column header inserted). The output feeds the
Tm and specificity/sensitivity steps in :mod:`primer_tm`.

The BLAST+ executables are invoked directly via :mod:`subprocess` (the old
``Bio.Blast.Applications`` command wrappers were removed in Biopython 1.85).

Author: Enrico Giovanelli Tacconi Gimenez (gimenezenrico@yahoo.com.br)
Requisites: BLAST+ (``blastn`` on PATH); a local ``taxdb`` (in the working
directory or referenced from your shell profile) so scientific names resolve;
network access for remote BLAST.
"""

import shutil
import subprocess

from ..common.blast import outfmt_arg
from .put_header import putHeader


def run_blast(query, output_prefix, num_alignments=1000, db="nt", remote=True):
    """Run BLASTn of short sequences and write ``<output_prefix>.tsv``.

    Uses the shared ``outfmt`` field list (FR-011) and inserts the matching
    header. Returns the path of the written ``.tsv``. Raises ``FileNotFoundError``
    with an understandable message if the ``blastn`` executable is missing, and
    ``RuntimeError`` if BLAST itself fails.
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
        "-evalue", "1000",
        "-word_size", "7",
        "-penalty", "-3",
        "-reward", "1",
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
