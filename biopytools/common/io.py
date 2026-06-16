"""Path and file helpers shared across tools.

Centralizes filename sanitisation (FR-008) and a non-destructive atomic file
replace so data-derived names can't break shell loops and in-place edits don't
corrupt a file if interrupted.
"""

import os
import re
import tempfile

# FASTA-ish extensions used to restrict directory scans (FR-007).
FASTA_EXTENSIONS = (".fasta", ".fa", ".fas", ".fna", ".faa", ".ffn")


def slugify(text):
    """Return ``text`` with every run of non-word characters collapsed to ``_``.

    Used for data-derived output filenames (e.g. ``report_<species>.tsv``) so a
    scientific name with spaces or punctuation can't produce a path that breaks
    shell loops (FR-008). Leading/trailing underscores are trimmed.
    """
    return re.sub(r"[^\w]+", "_", str(text)).strip("_")


def is_fasta_path(path, extensions=FASTA_EXTENSIONS):
    """True if ``path`` is an existing file with a FASTA-like extension."""
    return os.path.isfile(path) and path.lower().endswith(extensions)


def atomic_write_text(path, text, encoding="utf-8"):
    """Write ``text`` to ``path`` atomically via a temp file + ``os.replace``.

    The destination is only ever the complete new content or the untouched old
    content, never a half-written file.
    """
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as handle:
            handle.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
