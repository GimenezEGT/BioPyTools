# BioPyTools

A collection of standalone bioinformatics helper scripts: BLAST wrappers,
FASTA/GenBank parsers, and a qPCR primer specificity/sensitivity pipeline.

## Requirements

- Python 3 (tested on 3.8+)
- Python packages: see [`requirements.txt`](requirements.txt)
  ```bash
  pip install -r requirements.txt
  ```
- External (not installable via pip), required by the BLAST scripts:
  - [NCBI BLAST+](https://www.ncbi.nlm.nih.gov/books/NBK279690/) (`blastn`, `blastp`)
  - A local `taxdb` (in the working directory or referenced from your shell
    profile) so BLAST can resolve scientific names (`sscinames`).

## Tools

### qPCR primer pipeline (`qPCR/`)
The flagship feature. Checks primer/probe specificity by BLASTing them against
`nt`, computing melting temperatures, and reporting sensitivity/specificity per
target species.

```bash
cd qPCR
python3 blastPrimers.py <primers.fasta> <output_prefix> <num_alignments>
```

This runs BLASTn (remote), adds a header, computes Tm
(`<output_prefix>.tm.tsv`), and writes a `report_<species>.tsv`. The target
species is inferred from the first BLAST hit. To batch-process a folder, use
`qPCR/run.sh`.

Supporting modules: `PrimerTm.py` (Tm + spec/sens), `putHeader.py` (adds the
column header to BLAST output), `fasta_handler.py` (IDT Excel → FASTA, multifasta
splitting).

### BLAST wrappers
- `blastn.py` — BLASTn of short sequences (primers) against `nt`.
- `blastp.py` — BLASTp of a protein FASTA against `nr`.

### FASTA / GenBank utilities
- `AcessionNumbers.py` — extract accession IDs from FASTA headers.
- `Exclue_multispecies.py` — split MULTISPECIES records out of a multifasta.
- `ExtractFirstSequence.py` — extract the first (consensus) sequence from each
  alignment file in a directory.
- `ExtractProteins.py` — extract CDS translations from a GenBank file.
- `removeAspas.py` — strip double quotes from a text file.

### Other
- `DataView/Orthofinder-venn.py` — Venn diagrams of OrthoFinder gene counts
  (work in progress).
- `RosalindProblems.py`, `testes.py`, `Teste_pandas.py`, `trasnlate.py` —
  personal scratch / learning files, not maintained tools.

## Notes

Generated outputs (`report_*.tsv`, `*.asn`, `__pycache__/`) are git-ignored.
Sample inputs (`*.fasta`, sample `*.tsv`) are kept for testing.
