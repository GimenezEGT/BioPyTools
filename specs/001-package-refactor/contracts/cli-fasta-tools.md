# CLI Contract: FASTA / GenBank tools

Console scripts under `biopytools-*`, or `python -m biopytools.fasta_tools.<mod>`.
All are argument-driven and non-interactive (FR-004); each provides `--help`.

## `accession-numbers` (was AcessionNumbers.py)
```
biopytools-accessions INPUT_FASTA -o OUTPUT_TXT
```
Extracts accession IDs from FASTA headers to a text file.

## `exclude-multispecies` (was Exclue_multispecies.py)
```
biopytools-exclude-multispecies INPUT_FASTA --prefix OUT [--excluded multispecies.faa]
```
Splits MULTISPECIES records out. Uses context managers (files always closed —
review H close()).

## `extract-first-sequence` (was ExtractFirstSequence.py)
```
biopytools-extract-first DIRECTORY -o consensos.fasta
```
Extracts the first sequence from each FASTA in DIRECTORY. **Filters by FASTA
extension**, skips its own output and non-files, guards empty parses (FR-007).

## `extract-proteins` (was ExtractProteins.py)
```
biopytools-extract-proteins GENBANK_FILE -o OUTPUT_FASTA
```
Extracts CDS translations as `lcl|`-style FASTA. Optional qualifiers (`strain`,
`organism`) are guarded (FR-016); FASTA header `[k=v]` brackets are balanced.

## `fasta-handler` (IDT Excel → FASTA; multifasta split)
```
biopytools-fasta-handler excel-to-fasta INPUT.xlsx -o OUT.fasta
biopytools-fasta-handler split INPUT.fasta --out-dir DIR
```
`split` honors the input-path argument (no internal `input()` override) and
writes to `--out-dir`, sanitizing record ids for filenames (FR-004, FR-008).

## `remove-quotes` (was removeAspas.py, text_tools)
```
biopytools-remove-quotes INPUT [--in-place | -o OUTPUT]
```
Strips double quotes; either replaces atomically (`--in-place`) or writes `-o`.
No per-line stdout noise.

## Acceptance (maps to spec)
- FR-004/SC-002/SC-003: all argument-driven, non-interactive, with `--help`.
- FR-007: directory scans restricted to intended inputs.
- FR-008: data-derived output filenames sanitized.
- FR-016: missing optional fields handled gracefully.
