# CLI Contract: qPCR primer pipeline

Invocation: `python -m biopytools.qpcr <subcommand> ...` or console script
`biopytools-qpcr`.

## `run` (full pipeline)

```
biopytools-qpcr run QUERY OUTPUT_PREFIX NUM_ALIGNMENTS
```

| Arg | Required | Meaning |
|-----|----------|---------|
| `QUERY` | yes | Path to primer/probe FASTA |
| `OUTPUT_PREFIX` | yes | Prefix for output files |
| `NUM_ALIGNMENTS` | yes | Number of BLAST alignments to return |

**Behavior**:
- Runs remote BLASTn (`nt`, short-seq params: `word_size=7, penalty=-3,
  reward=1, evalue=1000`), writes `OUTPUT_PREFIX.tsv` (raw, header added).
- Computes Tm → `OUTPUT_PREFIX.tm.tsv` (raw input preserved).
- Writes `report_<target-slug>.tsv`; target species inferred from BLAST row 0.
- No interactive prompts. `--help` describes all of the above.

**Errors**: missing BLAST+/taxdb → understandable message on stderr, non-zero
exit. Invalid args → argparse usage error.

## `tm` (Tm only)

```
biopytools-qpcr tm BLAST_TSV [-o OUTPUT]
```
Adds `tm`/`same_tm` columns; writes `<prefix>.tm.tsv` (or `-o`). Returns/locates
the written path. Never overwrites the input.

## `specsens` (classification only)

```
biopytools-qpcr specsens TM_TSV
```
Reads a Tm-annotated table, writes `report_<slug>.tsv`. Exact-binomial matching;
rows without a two-token species name are skipped and the count reported.

## Batch

`run.sh` (or a `--glob` option) iterates files in a directory, quoting paths,
resolving the script dir, inferring target per file. No target argument passed.

## Acceptance (maps to spec)

- FR-001/SC-001: `specsens` counts use exact binomial equality.
- FR-002: one-token species rows skipped, not fatal.
- FR-003/SC-007: `run`/`tm` never destroy the raw BLAST `.tsv`.
- FR-004/SC-002/SC-003: runs non-interactively; `--help` present.
