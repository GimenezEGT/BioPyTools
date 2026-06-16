"""Shared FASTA read / write / split helpers (FR-011).

Thin wrappers over Biopython's ``SeqIO`` so the various FASTA tools don't each
re-implement parse/write boilerplate. Output filenames derived from a record id
are sanitised through :func:`biopytools.common.io.slugify` (FR-008).
"""

import os

from Bio import SeqIO

from .io import slugify


def read_records(path, fmt="fasta"):
    """Parse ``path`` and return a list of ``SeqRecord`` objects."""
    with open(path, "r") as handle:
        return list(SeqIO.parse(handle, fmt))


def write_records(records, path, fmt="fasta"):
    """Write ``records`` to ``path``; return the number written."""
    with open(path, "w") as handle:
        return SeqIO.write(records, handle, fmt)


def split_records(path, out_dir=".", fmt="fasta"):
    """Write each record of ``path`` to its own ``<slug(rec.id)>.fasta`` file.

    Returns the list of written paths. ``out_dir`` is created if needed; record
    ids are sanitised so ids with slashes/spaces can't escape the directory or
    break downstream loops (FR-008).
    """
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for rec in SeqIO.parse(path, fmt):
        name = slugify(rec.id) or "record"
        out_path = os.path.join(out_dir, f"{name}.fasta")
        write_records([rec], out_path, fmt)
        written.append(out_path)
    return written
