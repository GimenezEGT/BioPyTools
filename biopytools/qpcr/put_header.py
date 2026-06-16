"""Insert the column header on the first line of a raw BLAST ``.tsv``.

The header is derived from the single shared field list in
:mod:`biopytools.common.blast`, so it can never drift out of sync with the
``-outfmt`` string used to produce the table (FR-011).
"""

import sys

from ..common.blast import header_line


def putHeader(file):
    """Prepend the BLAST header row to ``file`` in place."""
    with open(file, "r") as input_file:
        lines = input_file.readlines()
    lines.insert(0, header_line() + "\n")
    with open(file, "w") as output_file:
        output_file.writelines(lines)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        sys.exit("Usage: python -m biopytools.qpcr.put_header <blast_result.tsv>")
    putHeader(argv[0])


if __name__ == "__main__":
    main()
