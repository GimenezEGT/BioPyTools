# CLI Contract: BLAST wrappers

Console scripts `biopytools-blastn` / `biopytools-blastp`, or
`python -m biopytools.blast.blastn` / `.blastp`.

## `blastn`

```
biopytools-blastn QUERY OUTPUT_PREFIX [--num-alignments N] [--remote/--local] [--db nt]
```

- Runs BLASTn of short sequences with primer-appropriate params
  (`word_size=7, penalty=-3, reward=1`, high `evalue`).
- Uses the shared `outfmt` field list from `common/blast.py`; inserts the
  matching header via `common`/`put_header`.
- Writes `OUTPUT_PREFIX.tsv`. No dead read of the result file (review M dead I/O).
- `--help` describes purpose, inputs, outputs.

## `blastp`

```
biopytools-blastp QUERY OUTPUT_PREFIX [--num-alignments N] [--db nr]
```

- Runs BLASTp against `nr`. Imports only the needed Biopython command (no
  `import *`, review L). Does not dump the entire result to stdout (optional
  bounded preview only).

## Acceptance (maps to spec)

- FR-004: argument-driven, non-interactive, `--help` present.
- FR-011: outfmt/header come from the single shared definition.
- FR-009: documents the BLAST+/taxdb prerequisite; clear error if missing.
