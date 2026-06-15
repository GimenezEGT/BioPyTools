# Feature Specification: Reorganize & Harden BioPyTools

**Feature Branch**: `001-package-refactor`

**Created**: 2026-06-14

**Status**: Draft

**Input**: User description: "Reorganize and harden BioPyTools into an installable, documented, tested Python package preserving all existing bioinformatics functionality"

## Overview

BioPyTools is a personal collection of ~20 bioinformatics helper scripts (BLAST
wrappers, FASTA/GenBank parsers, a qPCR primer specificity/sensitivity pipeline,
and assorted scratch files) accumulated over time. The tools are scientifically
useful but disorganized, largely undocumented, inconsistently runnable, and a
few produce incorrect results. This feature reorganizes the collection into a
single coherent, documented, installable, and tested toolkit **without changing
what each tool fundamentally does for the researcher**.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Trustworthy scientific output (Priority: P1)

A researcher runs the qPCR primer checker on a set of primers and relies on the
reported sensitivity/specificity and per-species classification to decide which
primers to order. The numbers must be correct and reproducible.

**Why this priority**: Wrong specificity/sensitivity numbers lead to ordering the
wrong primers — real time and money lost in the lab. Correctness of scientific
output is the single most important property of the toolkit.

**Independent Test**: Run the qPCR analysis against a curated input with a known,
hand-computed expected outcome; the reported counts (true/false
positives/negatives), sensitivity, and specificity match the expected values
exactly, and re-running on the same input yields identical results.

**Acceptance Scenarios**:

1. **Given** a BLAST result containing the target species and unrelated species,
   **When** the specificity/sensitivity analysis runs, **Then** a hit is counted
   as the target only when its species name matches the target exactly (not as a
   substring or superstring of another name).
2. **Given** a result row whose species field has only one word (e.g.
   "uncultured"), **When** the analysis runs, **Then** that row is skipped and
   reported as skipped rather than crashing the run.
3. **Given** the same input file processed twice, **When** the pipeline runs
   each time, **Then** the original input is not destroyed and both runs produce
   identical reports.

### User Story 2 - Every tool is runnable and discoverable (Priority: P2)

A researcher (or a collaborator, or the author months later) wants to find the
right tool for a task and run it non-interactively, including in a batch over
many files, passing inputs and outputs as arguments.

**Why this priority**: Tools that block on interactive prompts or hide their
purpose cannot be scripted, batched, or rediscovered — this is the core
"disorganized and hard to understand" pain.

**Independent Test**: For each tool, invoking it with a help flag prints its
purpose and required inputs/outputs; invoking it with arguments runs to
completion with no interactive prompt; and a single index (README) lists every
tool with a one-line description and example invocation.

**Acceptance Scenarios**:

1. **Given** any tool in the toolkit, **When** the user requests its help,
   **Then** it describes what it does, its inputs, and its outputs.
2. **Given** any tool, **When** the user supplies inputs and outputs as
   arguments, **Then** it completes without pausing for keyboard input.
3. **Given** a folder of input files, **When** the user runs a tool in batch
   mode over the folder, **Then** each file is processed and outputs are written
   to predictable, non-colliding paths.

### User Story 3 - Reproducible setup (Priority: P3)

A researcher sets up the toolkit on a new machine and installs everything needed
to run the tools from a single declared list of dependencies.

**Why this priority**: Today nothing declares the required packages or external
tools, so a fresh setup fails with opaque errors. Reproducibility is essential
for sharing and for the author's future self.

**Independent Test**: On a clean environment, following the documented install
steps makes every non-external-dependent tool importable and runnable; the
external prerequisites (BLAST+, taxonomy database) are clearly documented.

**Acceptance Scenarios**:

1. **Given** a clean machine, **When** the user follows the documented setup,
   **Then** all declared dependencies install from one command.
2. **Given** a tool that needs an external program (BLAST) or database,
   **When** that prerequisite is missing, **Then** the documentation states the
   requirement clearly and the tool fails with an understandable message.

### User Story 4 - Safe to change without breaking (Priority: P3)

The author wants to keep improving the toolkit with confidence that existing
behavior is preserved, and wants experimental/scratch material separated from
the maintained tools.

**Why this priority**: Without a safety net and without separating scratch from
tools, every change risks silent regressions and the repository stays confusing.

**Independent Test**: An automated test suite runs green and covers the
scientifically critical computations; scratch/learning files live in a clearly
separate location and are excluded from the maintained, installable surface.

**Acceptance Scenarios**:

1. **Given** the maintained tools, **When** the automated test suite runs,
   **Then** the scientifically critical computations (species classification,
   melting-temperature calculation, FASTA parsing) are covered and pass.
2. **Given** the repository, **When** a user browses it, **Then** maintained
   tools, sample inputs, scratch/learning files, and generated outputs are in
   clearly distinct locations.

### Edge Cases

- A species name with only one token, or empty/missing, in a BLAST result row.
- An input directory containing non-FASTA files, subdirectories, or the tool's
  own output file.
- A GenBank record lacking optional qualifiers (e.g. "strain").
- Species or output names containing spaces or filesystem-unsafe characters.
- Re-running a pipeline step on a file it already produced (no double-processing
  or corruption).
- A tool invoked with missing or invalid arguments (clear error, not a crash).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The species classification in the qPCR analysis MUST match a hit
  to the target species only on exact normalized binomial (genus + species)
  equality, never by substring containment.
- **FR-002**: The qPCR analysis MUST skip and report result rows that lack a
  valid two-token species name instead of aborting the run.
- **FR-003**: Pipeline steps MUST NOT destroy their input; derived data MUST be
  written to distinct outputs, and re-running a step MUST be safe (idempotent
  with respect to the source input).
- **FR-004**: Every maintained tool MUST be runnable non-interactively with
  inputs and outputs supplied as arguments, and MUST provide help text
  describing its purpose, inputs, and outputs.
- **FR-005**: Every maintained tool MUST have a description of its purpose,
  inputs, outputs, and an example invocation discoverable from a single
  top-level index.
- **FR-006**: User-facing text across the maintained tools MUST use one
  consistent language.
- **FR-007**: File-reading tools that scan a directory MUST process only the
  intended input files and MUST NOT fail on unrelated files, subdirectories, or
  their own outputs.
- **FR-008**: Tools that derive output filenames from data (e.g. species names)
  MUST produce safe, non-colliding filenames.
- **FR-009**: The toolkit MUST declare all required software dependencies in one
  place and document external prerequisites (BLAST+, taxonomy database).
- **FR-010**: The toolkit MUST be installable such that its tools can be invoked
  by name (or as modules) after a documented install step.
- **FR-011**: Shared behavior used by multiple tools (e.g. the BLAST output
  column definition and its header, FASTA read/write helpers) MUST be defined in
  a single shared location so the definitions cannot drift apart.
- **FR-012**: An automated test suite MUST cover the scientifically critical
  computations (species classification, melting-temperature calculation, FASTA
  parsing) and MUST pass.
- **FR-013**: Experimental/learning/scratch material MUST be separated from the
  maintained tools and excluded from the installable surface.
- **FR-014**: Generated outputs and build artifacts MUST NOT be tracked in
  version control; sample inputs used for examples/tests MAY be tracked in a
  dedicated location.
- **FR-015**: All existing tool functionality MUST be preserved — no tool's core
  capability is removed by the reorganization (it may be renamed, relocated, or
  invoked differently, but it still performs its task).
- **FR-016**: Tools MUST handle missing optional input fields and malformed rows
  gracefully with understandable messages rather than uncaught crashes.

### Key Entities *(include if feature involves data)*

- **Primer/Probe sequence set**: Short nucleotide sequences (FASTA) submitted by
  the researcher to be checked for specificity.
- **BLAST result table**: Tab-separated alignment results with a defined set of
  columns (query id, scientific names, coverage, identity, e-value, taxonomy
  ids, aligned sequence, titles), used as the data backbone of the qPCR
  pipeline.
- **Tm-annotated table**: The BLAST result table augmented with a melting
  temperature per annealing and a flag indicating whether it can realistically
  anneal relative to the primer.
- **Specificity/Sensitivity report**: A per-target summary listing
  false-positive and false-negative species and the computed sensitivity and
  specificity.
- **Sequence records**: FASTA/GenBank records consumed and produced by the
  parsing/extraction tools (accessions, CDS translations, consensus sequences,
  multispecies splits).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a curated test input with a hand-computed expected result, the
  qPCR analysis reports the exact expected true/false positive/negative counts
  and sensitivity/specificity values (0 discrepancies).
- **SC-002**: 100% of maintained tools can be run end-to-end without any
  interactive keyboard prompt.
- **SC-003**: 100% of maintained tools expose help text describing purpose,
  inputs, and outputs.
- **SC-004**: A newcomer can identify the correct tool for a stated task and run
  it using only the top-level index/README, without reading source code.
- **SC-005**: On a clean environment, the full documented setup completes from a
  single dependency-install command with no manual dependency hunting.
- **SC-006**: The automated test suite passes and covers the three critical
  computations (species classification, Tm calculation, FASTA parsing).
- **SC-007**: Re-running any pipeline step on the same input never corrupts or
  destroys the original input (verified: original input unchanged after a
  second run).
- **SC-008**: Version-controlled files contain zero generated outputs or build
  artifacts.

## Assumptions

- The "users" are the author and fellow bioinformatics researchers/collaborators
  comfortable with a command line; there is no GUI or web interface in scope.
- All current scientific behavior is intended to be preserved; where current
  behavior is a defect (e.g. substring species matching), the corrected behavior
  is the intended one.
- External prerequisites (NCBI BLAST+ executables and a local taxonomy database)
  remain the user's responsibility to install; the toolkit documents but does not
  bundle them.
- Network access is required only for the tools that perform remote BLAST queries.
- English is the chosen consistent language for user-facing text.
- The critical-bug fixes already applied in the working tree (exact species
  matching, exception handling, non-destructive Tm output, dependency manifest,
  ignore rules) are part of this feature's baseline and are validated by the new
  test suite rather than re-derived.
- Supported Python is a currently maintained 3.x interpreter (not pinned to a
  single point release).
