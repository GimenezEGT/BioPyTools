# Tasks: Reorganize & Harden BioPyTools

**Input**: Design documents from `specs/001-package-refactor/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: INCLUDED — the spec explicitly requires a test suite (FR-012, US4, SC-006).

**Organization**: Tasks are grouped by user story (US1–US4) for independent
implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story the task belongs to (US1–US4)
- All paths are repo-relative.

## Migration note

Most moves should use `git mv` to preserve history, followed by light edits
(imports, argparse, bug fixes). The critical qPCR fixes already applied in the
working tree are carried over, not rewritten.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the package skeleton and packaging/test configuration.

- [x] T001 Create package skeleton with `__init__.py` in `biopytools/`, `biopytools/common/`, `biopytools/blast/`, `biopytools/fasta_tools/`, `biopytools/qpcr/`, `biopytools/text_tools/`, `biopytools/dataview/`
- [x] T002 [P] Create top-level `examples/`, `scratch/`, `tests/`, and `tests/fixtures/` directories (with a `.gitkeep` where empty)
- [x] T003 [P] Add `pyproject.toml` (setuptools backend, project metadata, Python >=3.9, dependencies from requirements.txt)
- [x] T004 [P] Configure pytest in `pyproject.toml` (`[tool.pytest.ini_options]` with `testpaths = ["tests"]`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared utilities every tool depends on (the single-source-of-truth modules).

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T005 Implement the BLAST output-format field list, the `-outfmt '6 ...'` string, and the TSV header (all derived from one list) in `biopytools/common/blast.py` (FR-011)
- [x] T006 [P] Implement FASTA read/write/split helpers in `biopytools/common/fasta.py` (FR-011)
- [x] T007 [P] Implement `slugify`, atomic file replace, and path helpers in `biopytools/common/io.py` (FR-008)

**Checkpoint**: Shared utilities importable — user stories can begin.

---

## Phase 3: User Story 1 - Trustworthy scientific output (Priority: P1) 🎯 MVP

**Goal**: The qPCR pipeline lives in the package, computes correct
sensitivity/specificity (exact binomial matching), and never destroys its input.

**Independent Test**: `pytest tests/test_spec_sens.py` reproduces hand-computed
counts; running the pipeline twice leaves the raw BLAST `.tsv` unchanged.

### Tests for User Story 1 ⚠️ (write first, ensure they FAIL before impl)

- [x] T008 [P] [US1] Curated fixture `tests/fixtures/spec_sens_known.tsv` + exact-count classification test in `tests/test_spec_sens.py` (covers exact match, superstring rejection, one-token skip — SC-001)
- [x] T009 [P] [US1] Tm-calculation test (value within tolerance, `same_tm` threshold) in `tests/test_primer_tm.py`

### Implementation for User Story 1

- [x] T010 [US1] `git mv qPCR/PrimerTm.py biopytools/qpcr/primer_tm.py`; keep applied fixes; update internal references
- [x] T011 [US1] `git mv qPCR/blastPrimers.py biopytools/qpcr/blast_primers.py`; extract BLAST call into `run_blast(...)`; import `common.blast` outfmt; use relative imports
- [x] T012 [US1] `git mv qPCR/putHeader.py biopytools/qpcr/put_header.py`; derive header from `common/blast.py` instead of a hardcoded string
- [x] T013 [US1] Create `biopytools/qpcr/__main__.py` with `argparse` subcommands `run` / `tm` / `specsens` per `contracts/cli-qpcr.md` (replaces the deleted `main.py`)
- [x] T014 [US1] Make `getTm`/`checkSpecSens`/`run_blast` cleanly importable (no top-level side effects) so tests can call them directly
- [x] T015 [US1] Run `pytest tests/test_spec_sens.py tests/test_primer_tm.py` and confirm green

**Checkpoint**: qPCR pipeline functional and verified inside the package (MVP).

---

## Phase 4: User Story 2 - Every tool is runnable and discoverable (Priority: P2)

**Goal**: Every maintained tool is argparse-driven, non-interactive, has `--help`,
and is listed in the README index.

**Independent Test**: each `biopytools-<tool> --help` prints purpose/inputs/outputs;
each runs to completion from args with no prompt; README lists all tools.

### Implementation for User Story 2

- [x] T016 [P] [US2] `git mv blastn.py biopytools/blast/blastn.py`; keep argparse, use `common.blast` outfmt/header, drop the dead result read (per `contracts/cli-blast.md`)
- [x] T017 [P] [US2] `git mv blastp.py biopytools/blast/blastp.py`; add argparse, remove `import *`, remove full-file stdout dump
- [x] T018 [P] [US2] `git mv AcessionNumbers.py biopytools/fasta_tools/accession_numbers.py`; replace `input()` with argparse `INPUT_FASTA -o OUTPUT_TXT`
- [x] T019 [P] [US2] `git mv Exclue_multispecies.py biopytools/fasta_tools/exclude_multispecies.py`; replace `input()` with argparse (keep context-manager fix)
- [x] T020 [P] [US2] `git mv ExtractFirstSequence.py biopytools/fasta_tools/extract_first_sequence.py`; argparse `DIRECTORY`, filter by FASTA extension, skip own output/non-files, guard empty parses (FR-007)
- [x] T021 [P] [US2] `git mv ExtractProteins.py biopytools/fasta_tools/extract_proteins.py`; guard optional `strain`/`organism` qualifiers, fix `[k=v]` bracket (FR-016)
- [x] T022 [P] [US2] `git mv qPCR/fasta_handler.py biopytools/fasta_tools/fasta_handler.py`; honor the path argument (remove internal `input()`), add `--out-dir`, sanitize record-id filenames (FR-004, FR-008)
- [x] T023 [P] [US2] `git mv removeAspas.py biopytools/text_tools/remove_quotes.py`; argparse `INPUT [--in-place | -o OUTPUT]`, drop per-line stdout
- [x] T024 [US2] Replace `qPCR/run.sh` batch wrapper to invoke `python -m biopytools.qpcr run` per file (already de-bugged; relocate alongside package or `examples/`)
- [x] T025 [US2] Expand `README.md` into a full tool index: one line + example invocation per tool (SC-004)

**Checkpoint**: All tools runnable non-interactively and discoverable via README.

---

## Phase 5: User Story 3 - Reproducible setup (Priority: P3)

**Goal**: One-command dependency install; tools invokable by name after install;
external prerequisites documented.

**Independent Test**: in a clean venv, `pip install -e .` then `biopytools-qpcr --help`
works; README documents BLAST+/taxdb.

### Implementation for User Story 3

- [x] T026 [US3] Finalize `console_scripts` entry points in `pyproject.toml` for every CLI (qpcr, blastn, blastp, accessions, exclude-multispecies, extract-first, extract-proteins, fasta-handler, remove-quotes)
- [x] T027 [P] [US3] Verify `requirements.txt` completeness (biopython, pandas, numpy, openpyxl, matplotlib, matplotlib-venn) and document BLAST+/taxdb + network needs in README (FR-009)
- [x] T028 [US3] In a clean venv, validate `pip install -e .` exposes all console scripts; run `quickstart.md` install steps (SC-005)

**Checkpoint**: Toolkit installs and runs from a documented setup.

---

## Phase 6: User Story 4 - Safe to change without breaking (Priority: P3)

**Goal**: Green test suite for critical computations; scratch/examples cleanly
separated from maintained tools.

**Independent Test**: `pytest` is green; repo browse shows distinct tool/example/scratch/output locations.

### Tests for User Story 4 ⚠️

- [x] T029 [P] [US4] FASTA parse/write/split round-trip tests in `tests/test_fasta.py` (SC-006)

### Implementation for User Story 4

- [x] T030 [P] [US4] `git mv` scratch files to `scratch/`: `RosalindProblems.py`→`rosalind_problems.py`, `testes.py`, `Teste_pandas.py`→`teste_pandas.py`, `trasnlate.py` (excluded from packaging via pyproject — FR-013)
- [x] T031 [P] [US4] Move sample inputs to `examples/` (`exemplo.fasta`, `primers_example.fasta`, `gcContent.fasta`, `teste.tsv`, `qPCR/exemplo1.tsv`, `HPV11.fasta`); delete empty `qPCR/ExtractSequences.py`
- [x] T032 [P] [US4] `git mv DataView/Orthofinder-venn.py biopytools/dataview/orthofinder_venn.py`; mark experimental in docstring (or implement venn) and document status
- [x] T033 [US4] Run full `pytest` suite and confirm green (SC-006)

**Checkpoint**: Regression safety net in place; repo cleanly organized.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T034 [P] Add a one-paragraph module docstring (purpose, inputs, outputs, example) to every maintained module that lacks one (FR-005)
- [x] T035 [P] Normalize all user-facing text to English (FR-006)
- [x] T036 Run `quickstart.md` end-to-end for the non-BLAST paths; confirm `git status` shows no generated outputs/artifacts (SC-007, SC-008)
- [x] T037 Update `CLAUDE.md` SPECKIT block and any references to the new module paths

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies — start immediately.
- **Foundational (Phase 2)**: depends on Setup — **BLOCKS all user stories** (every tool imports `common/`).
- **US1 (Phase 3)**: depends on Foundational. MVP.
- **US2 (Phase 4)**: depends on Foundational; independent of US1 (different files).
- **US3 (Phase 5)**: depends on the tools existing (US1/US2) to wire entry points.
- **US4 (Phase 6)**: tests depend on Foundational; the moves are independent.
- **Polish (Phase 7)**: after all desired stories.

### Within Each User Story

- Tests written first and FAIL before implementation (US1, US4).
- `common/` utilities before the tools that consume them.
- Core implementation before batch wrappers / README index.

### Parallel Opportunities

- T002–T004 (setup) in parallel.
- T006, T007 in parallel (after T005's interface is agreed).
- T008, T009 in parallel (US1 tests).
- T016–T023 are all `[P]` — each tool is a different file, no cross-dependencies once `common/` exists.
- T030–T032 (moves) in parallel.

---

## Parallel Example: User Story 2

```bash
# All tool migrations are independent files — run together:
Task: "Migrate blastn to biopytools/blast/blastn.py"
Task: "Migrate blastp to biopytools/blast/blastp.py"
Task: "Migrate AcessionNumbers to biopytools/fasta_tools/accession_numbers.py"
Task: "Migrate ExtractProteins to biopytools/fasta_tools/extract_proteins.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1 Setup → 2. Phase 2 Foundational (`common/`) → 3. Phase 3 US1 →
   **STOP & VALIDATE** the qPCR correctness tests. This alone delivers the
   highest-value outcome (trustworthy scientific output).

### Incremental Delivery

US1 (MVP) → US2 (all tools runnable) → US3 (installable) → US4 (tests + cleanup)
→ Polish. Each story is independently testable and adds value without breaking
the previous ones.

---

## Notes

- `[P]` = different files, no incomplete-task dependencies.
- Prefer `git mv` + light edits over rewrites to preserve history and behavior (FR-015).
- Commit after each task or logical group.
- Verify the US1/US4 tests fail before implementing the corresponding code.
- Total: 37 tasks — Setup 4, Foundational 3, US1 8, US2 10, US3 3, US4 5, Polish 4.
