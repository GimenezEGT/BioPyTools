# Code Review v02

- **Date:** 2026-06-15
- **Feature / Scope:** `001-package-refactor` — post-implementation, spec-aligned review of the refactor that turned ~20 flat scripts into the installable `biopytools` package. Diff reviewed: `013af6e..HEAD` (commits `ec333ff`, `0c56b09`, `bef9454`, `5f65a4c`).
- **Specs referenced:** `spec.md` (FR-001..FR-016, SC-001..SC-008, US1..US4), `plan.md`, `research.md` (D1..D12), `data-model.md` (E1..E5), `contracts/cli-qpcr.md`, `contracts/cli-blast.md`, `contracts/cli-fasta-tools.md`, `quickstart.md`, `tasks.md`.
- **Trigger:** manual /code-reviewer (post /speckit.implement)

## Summary

The refactor is **largely successful and faithful to the spec**. The package skeleton, shared single-source-of-truth modules (`common/blast.py`, `common/fasta.py`, `common/io.py`), argparse-driven non-interactive CLIs, `pyproject.toml` with console scripts, the pytest suite, and the scratch/examples separation are all present and correct. The two v01 Critical bugs (the `main.py` stub and substring species matching) are genuinely fixed: classification now uses exact normalized-binomial equality, one-token rows are skipped (not fatal), and `getTm` writes a separate `.tm.tsv` with `index=False` so the raw BLAST table is preserved. The test suite is green (`10 passed`).

The Biopython 1.85 deviation (replacing the removed `Bio.Blast.Applications.Ncbiblast*Commandline` with direct `subprocess` calls) is implemented **safely**: argument lists are passed as a vector (no `shell=True`), so there is no shell-injection surface, and missing executables / non-zero exits are turned into understandable errors.

Findings by severity: **0 Critical, 1 High, 3 Medium, 5 Low, 3 Info.**

Headline items:
- **High — SC-008 violation:** the `separados/` directory (including a generated `report_humanpapillomavirus.tsv`) is still tracked in git. The `.gitignore` `report_*.tsv` rule does not untrack already-tracked files, so version control still contains generated outputs.
- **Medium — sensitivity/specificity denominator (E3 ambiguity):** skipped rows still increment `total_true`/`total_false`, so a one-token row with `same_tm=True` inflates the sensitivity denominator. Verified: the curated fixture yields `sensitivity = 25%` instead of the intuitive `TP/(TP+FN) = 50%`. Carried over from the original; the data-model E3 definition is itself ambiguous.
- **Medium — SC-001 test gap:** the spec/sens tests pin counts but never assert the computed `sensitivity`/`specificity` *values*, which is exactly what SC-001 calls for and is where the above ambiguity hides.

## Requirements Coverage Map

| Requirement | Source | Status | Notes |
|---|---|---|---|
| FR-001 exact binomial match | spec/D5 | Met | `_binomial` + `==` in `classify`; superstring `Homo sapiensaa` correctly rejected. |
| FR-002 skip one-token rows | spec | Met | `_binomial` returns `None`; counted in `skipped`, never fatal. |
| FR-003 non-destructive I/O | spec/D6 | Met | `getTm` writes `<prefix>.tm.tsv`, `index=False`; raw `.tsv` preserved (test asserts byte-equality). |
| FR-004 non-interactive + help | spec/D2 | Met | No `input()` anywhere in `biopytools/`; every CLI has argparse + `--help`. |
| FR-005 single index/README | spec | Met | README expanded into a tool index. |
| FR-006 one language | spec | Met | User-facing text normalized to English. |
| FR-007 directory-scan filtering | spec/D8 | Met | `extract_first_sequence` filters via `is_fasta_path`, skips own output, guards empty parses. |
| FR-008 safe filenames | spec/D9 | Met | `slugify` applied to report + split filenames; test covers `gi|123/abc\x`. |
| FR-009 declared deps + ext docs | spec | Met | `pyproject.toml` + `requirements.txt`; BLAST+/taxdb documented. See L4 (blastp omits taxdb note). |
| FR-010 installable / invokable | spec/D1 | Met | `[project.scripts]` defines all 9 console scripts. |
| FR-011 single source of truth | spec/D3 | Met | `outfmt_arg()`/`header_line()` both derive from `OUTFMT_FIELDS`; `put_header`, `blast_primers`, `blast/blastn` all import it. See L5 re blastp. |
| FR-012 tests for critical logic | spec/D11 | Partial | Classification counts, Tm, FASTA covered and green; sens/spec *values* not asserted (M2). |
| FR-013 scratch separated | spec/D10 | Met | scratch files moved; excluded via `[tool.setuptools.packages.find] exclude`. |
| FR-014 no tracked outputs/artifacts | spec | Partial | `.gitignore` correct, but `separados/` outputs remain tracked (H1). |
| FR-015 functionality preserved | spec | Met | All tools relocated and runnable; BLAST via subprocess preserves behavior. |
| FR-016 graceful malformed handling | spec/D9 | Met | `_qualifier` guards optional GenBank fields; balanced `[k=v]` brackets. |
| SC-001 exact counts + sens/spec values | spec | Partial | Counts pinned; sens/spec values not pinned (M2). |
| SC-002 no interactive prompts | spec | Met | Verified by grep + argparse design. |
| SC-003 help text | spec | Met | All CLIs expose `--help`. |
| SC-005 one-command install | spec | Met (not re-validated in clean venv here) | `pyproject.toml` complete. |
| SC-006 suite passes | spec | Met | `10 passed in 0.37s`. |
| SC-007 non-destructive re-run | spec | Met | Raw `.tsv` never overwritten. |
| SC-008 zero tracked generated outputs | spec | **Contradicts** | `separados/report_humanpapillomavirus.tsv` + sibling generated `.tsv` tracked (H1). |

## Findings

### [HIGH] `separados/` generated outputs remain tracked — violates SC-008 / FR-014
- **Location:** `separados/example_data.tsv`, `separados/exemplo1.tsv`, `separados/teste.tsv`, `separados/exemplo.fasta`, `separados/report_humanpapillomavirus.tsv` (all in `git ls-files`).
- **Category:** governance / data-integrity (hygiene)
- **What:** The whole `separados/` directory is still version-controlled, including `report_humanpapillomavirus.tsv` — a generated specificity/sensitivity report that matches the `.gitignore` pattern `report_*.tsv`. `.gitignore` only affects *untracked* files; a file already in the index keeps being tracked despite a matching ignore rule, so the rule gives a false sense of safety. `example_data.tsv` is ~1 MB of generated BLAST output.
- **Why it's a problem:** SC-008 states "Version-controlled files contain zero generated outputs or build artifacts" and FR-014 forbids tracking generated outputs. This is the project's original "messy, hard to tell inputs from outputs" pain, left half-addressed: examples were migrated to `examples/` but the `separados/` output dump was not removed. The tasks (T031/T036) claimed clean VCS, but `git status`/`git ls-files` contradict that.
- **Suggested fix:** `git rm -r --cached separados/` and either delete the directory or move any genuine *sample inputs* into `examples/` (none here appear to be unique inputs — `exemplo.fasta`/`exemplo1.tsv` already exist under `examples/`). Add `separados/` to `.gitignore` if it is a runtime output dir. Then re-verify `git ls-files | grep -iE 'report_|separados'` is empty to actually satisfy SC-008.

### [MEDIUM] Skipped rows inflate the sensitivity/specificity denominators (E3 ambiguity)
- **Location:** `biopytools/qpcr/primer_tm.py:139-149` (the `total_true`/`total_false` increment precedes the `skipped` `continue`); formulas at `:108-120`.
- **Category:** logic / spec-misalignment
- **What:** In `classify`, every row increments `total_true` (if `same_tm`) or `total_false` (else) **before** the one-token skip check. A skipped row therefore still counts toward the denominator. Verified on the curated fixture: `TP=1, FN=1, FP=2, TN=1, skipped=1`, but `total_true=4` (includes the skipped `uncultured` row whose `same_tm=True`), giving `sensitivity = TP/total_true = 1/4 = 25.0%` and `specificity = TN/total_false = 1/2 = 50.0%`. A reader expecting the textbook `sensitivity = TP/(TP+FN) = 1/2 = 50%` gets a different number, and the value silently changes if a malformed row happens to be same-Tm vs different-Tm.
- **Why it's a problem:** This is the scientific output a researcher uses to choose primers (US1, the P1 story). The denominator currently means "all same-Tm annealings including non-target and unclassifiable rows," which is neither `TP/(TP+FN)` nor cleanly defined. data-model E3 defines `sensitivity = true_positive / total_true * 100` but never defines `total_true` precisely, so the ambiguity is in the spec itself — but the implementation's choice to let *skipped* rows pollute it is the most defensible-to-question part. The task brief explicitly flags this as preserved-from-original and asks for assessment.
- **Suggested fix:** Decide and document the intended denominator in data-model E3. Two clean options: (a) classic diagnostic metrics — `sensitivity = TP/(TP+FN)`, `specificity = TN/(TN+FP)` — which ignore skipped rows entirely; or (b) keep the "fraction of same-Tm hits that are on-target" definition but **exclude skipped rows** by moving the `total_true`/`total_false` increment to *after* the `if row_name is None: continue` guard. Either way, add a value-level assertion in the tests (see M2) so the chosen definition is pinned.

### [MEDIUM] SC-001 not fully tested — sensitivity/specificity *values* never asserted
- **Location:** `tests/test_spec_sens.py:28-42` (asserts counts only); `Classification.sensitivity`/`specificity` untested.
- **Category:** spec-misalignment (test coverage)
- **What:** SC-001 requires the analysis to report "the exact expected ... sensitivity/specificity values (0 discrepancies)." The tests pin `true_positive/false_negative/false_positive/true_negative/skipped/total` but never assert `result.sensitivity` or `result.specificity`. That is precisely the surface where the M1 denominator ambiguity lives, so the green suite does not actually prove SC-001.
- **Why it's a problem:** The headline acceptance criterion of the flagship feature is unverified; a future change to the denominator semantics would pass CI silently.
- **Suggested fix:** After resolving M1, add `assert result.sensitivity == <expected>` and `assert result.specificity == <expected>` to `test_exact_classification_counts` (or a new test), using the hand-computed values for the fixture. Also assert `total_true`/`total_false` explicitly to lock the denominator definition.

### [MEDIUM] Live BLAST subprocess paths have no automated test coverage
- **Location:** `biopytools/qpcr/blast_primers.py:24-64`, `biopytools/blast/blastn.py:21-59`, `biopytools/blast/blastp.py:19-52`.
- **Category:** behaviour (test coverage)
- **What:** The `subprocess`-based BLAST runners — the part that changed most in this refactor (Biopython 1.85 removal of `Ncbiblast*Commandline`) — are exercised by no test. Command-vector construction, the missing-executable `FileNotFoundError`, the non-zero-exit `RuntimeError`, and the `putHeader` call after a successful run are all untested.
- **Why it's a problem:** This is the highest-churn, highest-risk code in the diff and the one most likely to regress (e.g. a wrong flag name, dropping `-remote`, or header insertion order). FR-015 (functionality preservation) for the BLAST path rests entirely on manual checking.
- **Suggested fix:** Add tests that monkeypatch `shutil.which` to return `None` and assert `FileNotFoundError`, and monkeypatch `subprocess.run` to return a fake `CompletedProcess` (returncode 0 with a temp output file, and returncode != 0) to assert the header is inserted on success and `RuntimeError` is raised on failure. This needs no real BLAST+ install and locks the argument vector via the captured `command` list.

### [LOW] Batch script uses the input path as the output prefix → doubled-extension outputs
- **Location:** `examples/run_qpcr_batch.sh:17` (`python -m biopytools.qpcr run "$f" "$f" "$num_alignments"`).
- **Category:** behaviour
- **What:** The second `"$f"` is the `OUTPUT_PREFIX`. For `primers.fasta` the pipeline writes `primers.fasta.tsv`, `primers.fasta.tm.tsv`, and `report_<species>.tsv` into the input directory. Outputs land next to inputs with a `.fasta.tsv` double extension, and re-running the batch over the same directory will then also match the input glob? (No — globs are `*.fasta`/`*.fa`/`*.fas`, and outputs are `.tsv`, so no re-ingestion. But the naming is confusing and pollutes the input dir.)
- **Why it's a problem:** Awkward filenames and outputs interleaved with inputs reintroduce the "hard to tell inputs from outputs" smell the refactor set out to remove; not a correctness bug.
- **Suggested fix:** Derive a clean prefix, e.g. `prefix="${f%.*}"` and pass `"$prefix"`, or write into a dedicated output dir (`out/$(basename "${f%.*}")`).

### [LOW] `blastp` requires `taxdb` for `sscinames` but its docstring omits the prerequisite
- **Location:** `biopytools/blast/blastp.py:5-8` (Requisites) and `:16` (`BLASTP_OUTFMT` includes `sscinames`).
- **Category:** spec-misalignment (FR-009)
- **What:** `BLASTP_OUTFMT = "6 qseqid sscinames pident qcovs evalue"` requests scientific names, which BLAST+ can only resolve with a local `taxdb`. The module docstring lists only "BLAST+ (`blastp` on PATH); network access" and, unlike `blastn`/`blast_primers`, omits the `taxdb` requirement. FR-009 requires external prerequisites to be documented so the tool "fails with an understandable message."
- **Why it's a problem:** A user without `taxdb` gets empty/blank `sscinames` (or a BLAST warning) with no documented explanation, inconsistent with the nucleotide tools that do document it.
- **Suggested fix:** Add the `taxdb` requirement to the `blastp.py` docstring (matching `blastn.py`), or drop `sscinames` from `BLASTP_OUTFMT` if name resolution isn't needed for protein hits.

### [LOW] `extract_proteins` accession can end with a stray trailing dot
- **Location:** `biopytools/fasta_tools/extract_proteins.py:29-30`.
- **Category:** behaviour (FR-016 robustness)
- **What:** `accession = gb_record.annotations["accessions"][0] + "." + str(gb_record.annotations.get("sequence_version", ""))`. When `sequence_version` is absent, `.get(..., "")` yields `""`, producing e.g. `"ABC123."` (verified) and FASTA ids like `lcl|ABC123._prot_...`. Also `annotations["accessions"]` is a hard `[...]` access that raises `KeyError` on a record lacking that annotation — the one un-guarded required-field access left in this otherwise nicely guarded module.
- **Why it's a problem:** Minor malformed identifier; the unguarded `accessions`/`[0]` access can crash on atypical GenBank records, which is the class of failure FR-016 targets.
- **Suggested fix:** Build the accession conditionally: `ver = gb_record.annotations.get("sequence_version"); accession = acc0 if not ver else f"{acc0}.{ver}"`, and guard `accessions` with `.get("accessions", ["unknown"])[0]`.

### [LOW] `getTm` Tm loop raises on missing/short `qseq` instead of a clear message
- **Location:** `biopytools/qpcr/primer_tm.py:66-73`.
- **Category:** behaviour (FR-016)
- **What:** `Seq(str(row["qseq"]))` then `tm.Tm_NN(...)` is called per row with no guard. A `NaN`/empty `qseq` becomes `Seq("nan")` or `Seq("")`; `Tm_NN` on an empty/invalid sequence raises a Biopython error mid-loop with no row context.
- **Why it's a problem:** FR-016 asks for understandable messages over uncaught crashes; a malformed `qseq` aborts the whole table opaquely. Lower severity because real BLAST `qseq` is normally well-formed.
- **Suggested fix:** Skip or warn on empty/`nan` `qseq` rows (mirroring the species-skip pattern), or wrap the call to surface the offending row id.

### [LOW] `excel_to_fasta` assumes fixed IDT column names with no validation
- **Location:** `biopytools/fasta_tools/fasta_handler.py:32-41` (`df["AssaySet"]`, `df["Sequence"]`, `df["Type"]`).
- **Category:** behaviour (FR-016)
- **What:** Hardcoded column names; a sheet missing any of them raises a bare pandas `KeyError`. `df["AssaySet"].str.replace(...)` also assumes that column is string dtype.
- **Why it's a problem:** Opaque failure on a slightly different IDT export, contrary to FR-016's "understandable messages" intent. Low severity — the format is a stable vendor export.
- **Suggested fix:** Validate required columns up front and raise a clear `ValueError("Excel missing required columns: ...")`.

### [INFO] qPCR files were re-created, not `git mv`'d — rename history not preserved
- **Location:** `biopytools/qpcr/primer_tm.py` (and siblings) show as `A` (added) under `git log --follow`, not `R` (renamed).
- **Category:** other (process)
- **What:** `plan.md`/`tasks.md` recommend `git mv` to preserve history (T010-T012). The qPCR modules show as fresh adds in `ec333ff` while the old `qPCR/PrimerTm.py` was deleted, so blame/history doesn't follow across the move. FR-015 concerns *functionality*, not history, and behavior is preserved, so this is informational only.
- **Why it's a problem:** Future `git blame` on the qPCR logic stops at the refactor commit; minor archaeology cost, no functional impact.
- **Suggested fix:** None required. Note the deviation from the stated migration approach for the record.

### [INFO] subprocess BLAST deviation (Biopython 1.85) is correct and injection-safe
- **Location:** `blast_primers.py:38-60`, `blast/blastn.py:33-55`, `blast/blastp.py:31-49`.
- **Category:** security / behaviour (assessment requested)
- **What/assessment:** The replacement of the removed `Ncbiblast*Commandline` wrappers with `subprocess.run([...], capture_output=True, text=True)` is implemented correctly: arguments are passed as a list (no `shell=True`), so query paths, db names, and species-derived values cannot inject shell commands; `outfmt_arg()` is a single token derived from the shared field list; missing executables raise a clear `FileNotFoundError` via `shutil.which`, and non-zero exits raise `RuntimeError` after echoing stderr. The primer-appropriate parameters (`word_size=7, penalty=-3, reward=1, evalue=1000`) match the contract and the original. No shell-injection surface, no secrets, FR-015 preserved. Only gap is the absence of tests (M3 above).

### [INFO] No secrets, credentials, or PII exposure found
- **Category:** security
- **What:** Consistent with v01, no hardcoded secrets/tokens/credentials anywhere in the new package. The only author contact strings are intentional docstring attributions (`gimenezenrico@yahoo.com.br`). BLAST `-remote` correctly depends on network + `taxdb`, both documented (except blastp, L4).

## Positive Notes

- The two v01 Criticals are genuinely fixed: `classify` uses exact normalized-binomial equality with a space separator (no concatenation collisions), one-token rows are skipped and reported, and the `main.py` stub is replaced by a real `argparse` subcommand CLI (`run`/`tm`/`specsens`) per the contract.
- `common/blast.py` is a clean single source of truth: `outfmt_arg()` and `header_line()` both derive from `OUTFMT_FIELDS`, and `put_header`, `blast_primers`, and `blast/blastn` all import it — the FR-011 drift class is genuinely eliminated for the nucleotide path.
- Non-destructive I/O is done right: `getTm` writes `<prefix>.tm.tsv` with `index=False`, and a test asserts the input is byte-for-byte unchanged (FR-003/SC-007).
- `classify` is cleanly separated as a pure, I/O-free function returning a dataclass — directly unit-testable, exactly as the tasks intended (T014).
- `slugify` + `is_fasta_path` + `atomic_write_text` in `common/io.py` are small, correct, and well-targeted at FR-007/FR-008; the FASTA split test even exercises a hostile `gi|123/abc\x` id.
- Every CLI follows one consistent pattern (`parse_args` → `main(argv=None)` → guarded), all argparse-driven with `--help`; no `input()` remains anywhere in the package (SC-002/SC-003).
- The experimental `orthofinder_venn` is handled honestly: importable, side-effect-free, and exits with a clear "not yet implemented" message instead of masquerading as a working tool.

## Open Questions / Needs Clarification

1. **E3 denominator definition (M1):** Should `sensitivity`/`specificity` use classic `TP/(TP+FN)` and `TN/(TN+FP)` (ignoring skipped rows), or the current "fraction of all same-/different-Tm annealings" with skipped rows included? data-model E3 is ambiguous; the answer changes the reported numbers (25% vs 50% on the fixture) and should be pinned by a test.
2. **`separados/` intent:** Is it a runtime output directory (then gitignore + untrack) or stale leftovers (then delete)? Needed to close SC-008.
3. **blastp `sscinames`:** Is taxonomy-name resolution actually wanted for protein hits? If yes, document the `taxdb` prerequisite (L4); if no, drop `sscinames` from `BLASTP_OUTFMT`.

## Verdict

The implementation **substantially satisfies the specification**: all functional requirements are met or partially met, the critical correctness fixes are real and tested, the package is properly installable, and the subprocess BLAST deviation is safe. It is **not yet fully spec-complete** on two acceptance criteria: **SC-008** is contradicted by the tracked `separados/` outputs (High), and **SC-001** is only partially proven because the computed sensitivity/specificity values are unasserted while their denominator semantics are ambiguous (Medium). Resolving H1 (untrack `separados/`), M1 (define and document the E3 denominator), and M2 (assert the sens/spec values) would bring the feature to full spec conformance. No Critical issues remain.
