# Phase 0 Research: Reorganize & Harden BioPyTools

All "NEEDS CLARIFICATION" items from Technical Context were resolvable from the
existing code and `code-review_v01.md`; none required external research. Below are
the decisions, rationale, and alternatives considered.

## D1. Packaging & invocation

- **Decision**: Single `biopytools` package built with `pyproject.toml`
  (setuptools backend), exposing tools via `console_scripts` entry points and
  `python -m biopytools.<area>`.
- **Rationale**: Eliminates hardcoded `/usr/bin/python3.8` shebangs and absolute
  paths in `run.sh`; makes tools invokable from anywhere after `pip install -e .`;
  satisfies FR-010.
- **Alternatives**: (a) Keep flat scripts — rejected, this is the core problem.
  (b) Per-tool packages — rejected as over-engineered for ~20 small tools (YAGNI).

## D2. CLI convention

- **Decision**: `argparse` with a `main()` function under `if __name__ ==
  "__main__":` in every tool; no `input()` in maintained tools.
- **Rationale**: Half the scripts already use argparse cleanly (`blastn.py`,
  `ExtractProteins.py`) — standardize on the existing good pattern. Enables batch
  use and testing (FR-004, SC-002).
- **Alternatives**: `click`/`typer` — rejected to avoid adding a dependency for a
  simple need.

## D3. Shared BLAST output format

- **Decision**: Define the 10 BLAST `outfmt` fields once in `common/blast.py` as
  an ordered list; derive both the `-outfmt '6 ...'` string and the
  `putHeader` TSV header from it.
- **Rationale**: Today the field list and header are duplicated/coupled across
  `blastn.py`, `blastPrimers.py`, and `putHeader.py`; drift silently misaligns
  pandas columns (review L2). One definition prevents that (FR-011).
- **Alternatives**: Per-script constants — rejected (the current defect).

## D4. qPCR target-species source

- **Decision**: Keep inferring the target species from BLAST result **row 0**
  (no `target` CLI argument). Confirmed by the user.
- **Rationale**: Matches the user's stated workflow; `run.sh` no longer needs to
  pass a target (the extra args were the H4 bug).
- **Alternatives**: Explicit `--target` argument — considered and explicitly
  declined by the user.

## D5. Species matching correctness (already applied)

- **Decision**: Normalize each `sscinames` to lowercased `genus species` (first
  two tokens, single space) and compare with **equality**; skip rows with < 2
  tokens.
- **Rationale**: Substring `in` matching (review C2) misclassifies superstrings/
  truncations; verified failing cases now pass with equality (FR-001, FR-002,
  SC-001). Already implemented in `qPCR/PrimerTm.py` and unit-checked.
- **Alternatives**: Match on `staxids` (taxonomy id) — stronger but requires the
  taxid column to be reliably populated; deferred as a possible future
  enhancement, noted in data-model.

## D6. Non-destructive pipeline I/O (already applied)

- **Decision**: `getTm` writes `<prefix>.tm.tsv` (with `index=False`) and returns
  the path; `checkSpecSens` consumes that. Raw BLAST output is preserved.
- **Rationale**: The old in-place overwrite destroyed source data and corrupted
  re-runs with an unnamed index column (review M getTm) — FR-003, SC-007.
- **Alternatives**: Overwrite with `index=False` only — rejected; still
  destructive.

## D7. Tm column assignment

- **Decision**: Assign `df['tm'] = tm_values` directly (raises on length
  mismatch) instead of `np.resize`.
- **Rationale**: `np.resize` silently tiles values on mismatch, mis-associating
  Tm with sequences (review M np.resize). Loud failure is correct.

## D8. Directory-scanning tools

- **Decision**: Filter inputs by extension (e.g. `*.fasta`/`*.fa`), skip the
  tool's own output and non-files, and guard empty parses before indexing.
- **Rationale**: `ExtractFirstSequence.py` currently treats every directory entry
  as FASTA and can re-read its growing output / crash on `records[0]`
  (review M ExtractFirstSequence) — FR-007.

## D9. Robust record handling

- **Decision**: Guard optional GenBank qualifiers (`if 'strain' in qualifiers`),
  fix the malformed `[k=v]` description bracket, and slugify data-derived
  filenames.
- **Rationale**: `ExtractProteins.py` crashes on records without `strain` and
  emits unbalanced FASTA header brackets (review L ExtractProteins); report
  filenames with spaces break shell loops (review L report name) — FR-008, FR-016.

## D10. Scratch vs maintained

- **Decision**: Move `RosalindProblems.py`, `testes.py`, `Teste_pandas.py`,
  `trasnlate.py` to `scratch/` (not packaged); empty `qPCR/ExtractSequences.py`
  is deleted; `DataView/Orthofinder-venn.py` (commented-out body) is marked
  experimental under `dataview/`.
- **Rationale**: These are learning/scratch or incomplete; mixing them with tools
  is a top "hard to understand" driver (FR-013). Keeps the installable surface
  clean.

## D11. Testing strategy

- **Decision**: pytest with tiny hand-built fixtures: a TSV with a known mix of
  target/non-target/one-token species and `same_tm` flags asserting exact
  classification counts (SC-001); a Tm fixture asserting values within a
  tolerance; FASTA fixtures for parse/split round-trips.
- **Rationale**: The C2/Tm bugs would have been caught instantly by fixtures;
  provides the regression safety net for the migration (FR-012, SC-006).

## D12. Python version

- **Decision**: Target Python 3.9+, `#!/usr/bin/env python3`.
- **Rationale**: Drops the brittle 3.8 pin; 3.9+ is widely available. (Note: the
  earlier f-string-with-backslash pitfall is avoided by extracting regex to a
  variable, already done.)
