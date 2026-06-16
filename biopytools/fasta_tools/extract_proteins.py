"""Extract CDS protein translations from a GenBank file into a FASTA.

Originally written to extract CDSs from full GenBank records (e.g. old genome
versions for which the NCBI does not provide CDS FASTA downloads). Optional
qualifiers (``strain``, ``organism``, ``gene`` ...) are guarded with membership
checks so records missing them don't crash (FR-016), and the FASTA header
``[k=v]`` brackets are balanced.

Example:
    biopytools-extract-proteins genome.gb -o proteins.faa
"""

import argparse

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


def _qualifier(feature, key, default="not defined"):
    """Return the first value of ``feature.qualifiers[key]`` or ``default``."""
    values = feature.qualifiers.get(key)
    return values[0] if values else default


def extract_cds(genbank_path):
    """Return a list of ``SeqRecord`` protein translations from a GenBank file."""
    gb_record = SeqIO.read(genbank_path, "genbank")
    accession = (gb_record.annotations["accessions"][0] + "." +
                 str(gb_record.annotations.get("sequence_version", "")))

    entries = []
    for feature in gb_record.features:
        if feature.type != "CDS":
            continue
        translation = _qualifier(feature, "translation", default="")
        if not translation:
            continue

        gene = _qualifier(feature, "gene")
        product = _qualifier(feature, "product")
        protein_id = _qualifier(feature, "protein_id")
        locus_tag = _qualifier(feature, "locus_tag")

        entries.append(SeqRecord(
            Seq(translation),
            id=f"lcl|{accession}_prot_{protein_id}",
            description=(f"[gene={gene}] [locus_tag={locus_tag}] "
                         f"[protein={product}] [gbkey=CDS]")))
    return entries


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Extract CDS protein translations from a GenBank file into "
                    "a FASTA file.")
    parser.add_argument("genbank_file", help="Path to the input GenBank file.")
    parser.add_argument(
        "-o", "--output", required=True,
        help="Path to the output protein FASTA (.faa).")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    entries = extract_cds(args.genbank_file)
    SeqIO.write(entries, args.output, "fasta")
    print(f"Wrote {len(entries)} CDS translation(s) to {args.output}.")


if __name__ == "__main__":
    main()
