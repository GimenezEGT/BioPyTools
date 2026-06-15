# Implementation Plan: Reorganize & Harden BioPyTools

**Branch**: `001-package-refactor` | **Date**: 2026-06-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-package-refactor/spec.md`

## Summary

Transform the flat collection of ~20 standalone scripts into a single
installable Python package (`biopytools`) with shared utilities, consistent
non-interactive CLIs, declared dependencies, separated scratch/examples, and a
pytest suite covering the scientifically critical computations. All existing tool
capabilities are preserved; defects identified in `code-review_v01.md` are fixed
as part of the move. The flagship qPCR pipeline is restructured into importable
functions behind `python -m biopytools.qpcr` while keeping target-species
inference from BLAST row 0 (per user decision).

## Technical Context

**Language/Version**: Python 3.9+ (drop the pinned `python3.8` shebang; use
`python3` / console entry points). Tested on the interpreter available locally.

**Primary Dependencies**: Biopython (SeqIO, Blast.Applications, SeqUtils.MeltingTemp),
pandas, numpy, openpyxl (Excel read), matplotlib + matplotlib-venn (DataView).

**External (non-pip) prerequisites**: NCBI BLAST+ executables (`blastn`,
`blastp`); a local `taxdb` for scientific-name resolution. Network access for
remote BLAST.

**Storage**: Plain files only — FASTA, GenBank, tab-separated BLAST tables,
text reports. No database.

**Testing**: pytest with small curated FASTA/TSV fixtures under `tests/fixtures/`.

**Target Platform**: Cross-platform CLI (developed on Windows; must also run on
Linux where the original `/usr/bin/python3.8` shebang and `run.sh` came from).

**Project Type**: Single Python package exposing multiple CLI tools (library + CLIs).

**Performance Goals**: Not performance-sensitive; correctness and clarity over
speed. BLAST itself dominates runtime and is external.

**Constraints**: Preserve all current functionality (FR-015); no destructive
in-place rewrites of input data (FR-003); no interactive prompts in maintained
tools (FR-004).

**Scale/Scope**: ~20 source files today → one package with ~5 sub-areas, a
shared `common` module, an examples folder, a scratch folder, and a test suite.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution (`.specify/memory/constitution.md`) is the unmodified
template with no ratified principles. There are therefore no enforced gates.
The plan nonetheless voluntarily adopts the template's spirit:

- **Library-first / CLI interface**: Each tool is a library function with a thin
  CLI wrapper (`argparse`) — satisfies FR-004, FR-011.
- **Test coverage for critical logic**: pytest suite for species classification,
  Tm, and FASTA parsing — satisfies FR-012.
- **Simplicity / YAGNI**: No web layer, no DB, no plugin system. Flat package.

**Result**: PASS (advisory). No violations to track in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/001-package-refactor/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI contracts)
│   ├── cli-qpcr.md
│   ├── cli-blast.md
│   └── cli-fasta-tools.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

```text
biopytools/                     # installable package
├── __init__.py
├── common/                     # shared utilities (single source of truth)
│   ├── __init__.py
│   ├── blast.py                # BLAST outfmt fields + header (one definition)
│   ├── fasta.py                # FASTA read / write / split helpers
│   └── io.py                   # path handling, slugify, atomic replace
├── blast/                      # blastn, blastp wrappers
│   ├── __init__.py
│   ├── blastn.py
│   └── blastp.py
├── fasta_tools/                # FASTA/GenBank parsing & extraction
│   ├── __init__.py
│   ├── accession_numbers.py    # was AcessionNumbers.py
│   ├── exclude_multispecies.py # was Exclue_multispecies.py
│   ├── extract_first_sequence.py
│   ├── extract_proteins.py     # was ExtractProteins.py
│   └── fasta_handler.py        # IDT Excel -> FASTA; multifasta split
├── qpcr/                       # qPCR primer pipeline
│   ├── __init__.py
│   ├── __main__.py             # `python -m biopytools.qpcr` CLI (replaces deleted main.py)
│   ├── blast_primers.py        # run_blast() refactored from blastPrimers.py
│   ├── primer_tm.py            # getTm + checkSpecSens (already bug-fixed)
│   └── put_header.py           # header insertion (already fixed)
├── text_tools/
│   ├── __init__.py
│   └── remove_quotes.py        # was removeAspas.py
└── dataview/
    ├── __init__.py
    └── orthofinder_venn.py     # finish or mark experimental

examples/                       # sample inputs only (tracked)
│   exemplo.fasta, primers_example.fasta, gcContent.fasta, teste.tsv,
│   qPCR/exemplo1.tsv, HPV11.fasta, ...
scratch/                        # NOT packaged, excluded from installable surface
│   rosalind_problems.py, testes.py, teste_pandas.py, trasnlate.py
tests/
├── fixtures/                   # curated tiny TSV/FASTA with known answers
├── test_spec_sens.py          # SC-001: exact classification counts
├── test_primer_tm.py          # Tm calculation ranges
└── test_fasta.py              # FASTA parse/split helpers
pyproject.toml                  # packaging + console_scripts entry points
requirements.txt                # already added (baseline)
README.md                       # already added; expand to full tool index
.gitignore                      # already added (baseline)
```

**Structure Decision**: Single installable package `biopytools/` with sub-area
subpackages and a shared `common/` module (eliminates the BLAST `outfmt`/header
and FASTA boilerplate duplication, FR-011). CLIs are exposed both as
`python -m biopytools.<area>` and via `console_scripts` entry points in
`pyproject.toml` (FR-010). Sample inputs move to `examples/` and scratch/learning
files to `scratch/` (FR-013, FR-014). The qPCR sub-area keeps its already-applied
bug fixes (exact matching, non-destructive Tm output) and adds a `__main__.py`
CLI to replace the deleted `main.py`.

## Migration Approach (functionality-preserving)

The reorganization is a series of `git mv` + light edits, not rewrites, so
history and behavior are preserved:

1. Create package skeleton (`biopytools/` + `__init__.py` files).
2. Move existing files to their new homes, renaming to snake_case; fix the
   import paths (`from putHeader import putHeader` → relative import).
3. Extract the duplicated BLAST `outfmt`/header into `common/blast.py` and the
   repeated FASTA boilerplate into `common/fasta.py`; update call sites.
4. Wrap every remaining top-level script body in a `main()` + argparse guard;
   replace `input()` prompts with arguments.
5. Apply the remaining script bug fixes (see research.md / Findings mapping).
6. Add `pyproject.toml` with entry points; expand README into a tool index.
7. Add the pytest suite + fixtures; make it green.
8. Move scratch files to `scratch/`, sample inputs to `examples/`.

## Complexity Tracking

> No constitution violations — section intentionally empty.
