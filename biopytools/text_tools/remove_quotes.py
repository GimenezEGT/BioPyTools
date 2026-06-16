"""Strip double quotes from a text file (``.txt``, ``.csv``, ...).

Either replaces the file atomically (``--in-place``) or writes the cleaned text
to a new path (``-o``). No per-line stdout noise.

Example:
    biopytools-remove-quotes data.csv -o data.clean.csv
    biopytools-remove-quotes data.csv --in-place
"""

import argparse
import sys

from ..common.io import atomic_write_text


def remove_quotes(text):
    """Return ``text`` with all double-quote characters removed."""
    return text.replace('"', "")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Strip double quotes from a text file.")
    parser.add_argument("input", help="Path to the input text file.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--in-place", action="store_true",
        help="Overwrite the input file atomically.")
    group.add_argument(
        "-o", "--output", help="Write the cleaned text to this path.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    with open(args.input, "r", encoding="utf-8") as handle:
        cleaned = remove_quotes(handle.read())

    destination = args.input if args.in_place else args.output
    atomic_write_text(destination, cleaned)
    print(f"Wrote cleaned text to {destination}.")


if __name__ == "__main__":
    main()
