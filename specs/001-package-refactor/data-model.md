# Phase 1 Data Model: Reorganize & Harden BioPyTools

The toolkit has no database; "entities" are file-based records and the in-memory
tables that flow through the qPCR pipeline. This document defines their shapes,
fields, validation rules, and transitions.

## E1. BLAST result table

Tab-separated output of `blastn`/`blastp`, the backbone of the qPCR pipeline.

| Field | Meaning | Notes |
|-------|---------|-------|
| `qseqid` | Query (primer/probe) id | from input FASTA |
| `sscinames` | Subject scientific name(s) | classification key; may be 1+ tokens |
| `qcovs` | Query coverage % | integer |
| `pident` | Percent identity | float |
| `evalue` | Expect value | float |
| `staxids` | Subject taxonomy id(s) | candidate stronger key (future) |
| `qseq` | Aligned query sequence | used for Tm calculation |
| `sblastnames` | BLAST name group | |
| `salltitles` | All subject titles | |
| `stitle` | Subject title | |

- **Single source of truth**: this ordered field list lives in
  `common/blast.py`; the `-outfmt '6 ...'` string and the `put_header` TSV
  header are both derived from it (FR-011).
- **Validation**: header row must match the field list; `sscinames` rows with
  fewer than two whitespace tokens are skipped during classification (FR-002).

**Transition**: produced by `blast_primers.run_blast()` → header inserted by
`put_header` → consumed by `getTm`.

## E2. Tm-annotated table

E1 augmented by `getTm`. Written to `<prefix>.tm.tsv` (never overwrites E1).

| Added field | Meaning | Rule |
|-------------|---------|------|
| `tm` | Melting temperature (°C) of `qseq` via nearest-neighbour (`Tm_NN`) | one value per row; assigned directly (raises on length mismatch) |
| `same_tm` | Whether the annealing can realistically hybridise | `True` iff `abs(tm_primer - tm_row) <= 6` |

- `tm_primer` is the `tm` of row 0 (the primer's self/best hit).
- **Validation**: written with `index=False` (no stray index column).

**Transition**: produced by `getTm(blast_table)` → consumed by `checkSpecSens`.

## E3. Specificity/Sensitivity report

Text/TSV summary written by `checkSpecSens` to `report_<slug>.tsv`.

| Element | Meaning |
|---------|---------|
| target binomial | `genus species` inferred from E2 row 0 (lowercased) |
| false positives | non-target species with `same_tm == True` (listed) |
| false negatives | target species with `same_tm == False` (listed) |
| true positives | target species with `same_tm == True` (count) |
| true negatives | non-target species with `same_tm == False` (count) |
| sensitivity | `true_positive / (true_positive + false_negative) * 100` |
| specificity | `true_negative / (true_negative + false_positive) * 100` |
| skipped | rows without a two-token species name |

- **Metric rule**: sensitivity and specificity use the classic diagnostic
  definitions and are computed **only over classified rows**. Skipped (one-token)
  rows do not contribute to either denominator. When a denominator is zero (no
  target, or no non-target rows) the metric is reported as `N/A`.

- **Classification rule (FR-001)**: a row is "target" iff its normalized binomial
  **equals** the target binomial (not substring containment).
- **Filename rule (FR-008)**: `<slug>` is the target binomial with non-word
  characters replaced by `_`.

## E4. Sequence records (FASTA / GenBank)

Consumed/produced by `fasta_tools` and `blast`:

- **FASTA record**: id + description + sequence. Helpers in `common/fasta.py`
  centralize parse/write/split (FR-011). Output filenames derived from `rec.id`
  are sanitized (FR-008).
- **GenBank record**: features with qualifiers. CDS extraction reads
  `translation`, `locus_tag`, and optional `strain`/`organism` — optional
  qualifiers are guarded with membership checks (FR-016). FASTA header `[k=v]`
  tags must be well-formed (balanced brackets).
- **Directory scans** (e.g. consensus extraction): restricted to FASTA
  extensions, skipping the tool's own output and non-files (FR-007).

## E5. IDT primer Excel → FASTA (fasta_handler)

- **Input**: an IDT-format Excel sheet (read via `openpyxl`).
- **Output**: a FASTA of primer/probe sequences; multifasta split writes one
  file per record to a caller-specified output directory (the `arq` parameter is
  honored, not overridden by `input()` — FR-004).

## Relationships

```text
primers.fasta ──run_blast──▶ E1 (blast.tsv)
                               │ put_header
                               ▼
                            E1 (+header)
                               │ getTm
                               ▼
                            E2 (<prefix>.tm.tsv)
                               │ checkSpecSens
                               ▼
                            E3 (report_<slug>.tsv)
```
