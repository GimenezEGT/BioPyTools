# BioPyTools

A small, installable toolkit of bioinformatics command-line utilities: BLAST
wrappers, FASTA/GenBank parsers, and a qPCR primer specificity/sensitivity
pipeline. All maintained tools are argument-driven and non-interactive, and
share a single source of truth for the BLAST output format.
I used Claude code to make it cleaner and readable.

## Install

```bash
git clone <repo> && cd BioPyTools
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -e .            # installs biopytools + the console scripts below
```

Or, without packaging:

```bash
pip install -r requirements.txt
python -m biopytools.qpcr --help
```

### External prerequisites (not installed by pip)

Required by the BLAST-backed tools (`biopytools-qpcr run`, `biopytools-blastn`,
`biopytools-blastp`):

- [NCBI BLAST+](https://www.ncbi.nlm.nih.gov/books/NBK279690/) — the `blastn` /
  `blastp` executables must be on your `PATH`.
- A local `taxdb` (in the working directory or referenced from your shell
  profile) so BLAST can resolve scientific names (`sscinames`).
- Network access for remote BLAST (`--remote`, the default).

## Tools

Every tool supports `--help`. Each can be run as `python -m <module>` or, after
`pip install -e .`, via its console script.

### qPCR primer pipeline — `biopytools-qpcr`

The flagship tool. Checks primer/probe specificity by BLASTing them against
`nt`, computing melting temperatures, and reporting sensitivity/specificity for
the target species (inferred from the first BLAST hit). The raw BLAST `.tsv` is
never overwritten.

```bash
biopytools-qpcr run primers.fasta my_run 5000   # BLASTn -> Tm -> report
biopytools-qpcr tm my_run.tsv                    # Tm annotation only
biopytools-qpcr specsens my_run.tm.tsv           # spec/sens report only
```

Outputs: `my_run.tsv` (raw BLAST + header), `my_run.tm.tsv` (Tm-annotated),
`report_<species>.tsv` (sensitivity/specificity). Batch a folder with
[`examples/run_qpcr_batch.sh`](examples/run_qpcr_batch.sh).

### BLAST wrappers

| Tool | Purpose |
|------|---------|
| `biopytools-blastn QUERY PREFIX [--num-alignments N] [--db nt] [--local]` | BLASTn of short sequences (primers) against `nt`; writes `PREFIX.tsv` with a header. |
| `biopytools-blastp QUERY PREFIX [--num-alignments N] [--db nr] [--local]` | BLASTp of a protein FASTA against `nr`; writes `PREFIX.blastProtein.out.tsv`. |

### FASTA / GenBank utilities

| Tool | Purpose |
|------|---------|
| `biopytools-accessions INPUT.fasta -o OUT.txt` | Extract accession IDs from FASTA headers. |
| `biopytools-exclude-multispecies INPUT.fasta --prefix OUT [--excluded multispecies.faa]` | Split MULTISPECIES records out of a multi-FASTA. |
| `biopytools-extract-first DIRECTORY -o consensos.fasta` | Extract the first (consensus) sequence from each FASTA in a directory. |
| `biopytools-extract-proteins GENOME.gb -o proteins.faa` | Extract CDS protein translations from a GenBank file. |
| `biopytools-fasta-handler excel-to-fasta IN.xlsx -o OUT.fasta` | Convert an IDT PrimerQuest Excel sheet to FASTA. |
| `biopytools-fasta-handler split IN.fasta --out-dir DIR` | Split a multi-FASTA into one file per record. |

### Text utilities

| Tool | Purpose |
|------|---------|
| `biopytools-remove-quotes INPUT [--in-place \| -o OUTPUT]` | Strip double quotes from a text file. |

### Experimental

- `python -m biopytools.dataview.orthofinder_venn` — Venn diagrams of
  OrthoFinder gene counts (work in progress; see the module docstring).

## Repository layout

- `biopytools/` — the installable package (`common/`, `blast/`, `fasta_tools/`,
  `qpcr/`, `text_tools/`, `dataview/`).
- `examples/` — sample inputs and the batch wrapper (tracked, not packaged).
- `scratch/` — personal learning/scratch scripts (not packaged, not maintained).
- `tests/` — pytest suite covering the scientifically critical computations.

## Tests

```bash
pip install pytest
pytest            # species classification (SC-001), Tm, FASTA round-trips
```

## Notes

Generated outputs (`report_*.tsv`, `*.asn`, `__pycache__/`) are git-ignored.
Sample inputs live under `examples/`.
