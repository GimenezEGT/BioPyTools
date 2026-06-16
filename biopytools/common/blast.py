"""Single source of truth for the BLAST tabular output format.

The qPCR pipeline and the BLAST wrappers all parse the same tab-separated BLAST
table. Historically the field list was duplicated as an ``-outfmt '6 ...'``
string in the BLAST callers and again as a hardcoded header string in
``putHeader``; if the two drifted, pandas silently mis-aligned columns.

Defining the ordered field list **once** here and deriving both the ``outfmt``
argument and the TSV header from it makes that class of bug impossible
(FR-011).
"""

# Ordered BLAST output fields. The order is the column order of the produced
# table and therefore also the order of the inserted header.
OUTFMT_FIELDS = [
    "qseqid",       # query (primer/probe) id
    "sscinames",    # subject scientific name(s) - classification key
    "qcovs",        # query coverage %
    "pident",       # percent identity
    "evalue",       # expect value
    "staxids",      # subject taxonomy id(s)
    "qseq",         # aligned query sequence (used for Tm)
    "sblastnames",  # BLAST name group
    "salltitles",   # all subject titles
    "stitle",       # subject title
]


def outfmt_arg(fields=None):
    """Return the ``-outfmt`` argument string (``'6 field1 field2 ...'``)."""
    fields = OUTFMT_FIELDS if fields is None else fields
    return "6 " + " ".join(fields)


def header_line(fields=None):
    """Return the tab-separated header row matching :data:`OUTFMT_FIELDS`."""
    fields = OUTFMT_FIELDS if fields is None else fields
    return "\t".join(fields)
