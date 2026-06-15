# Code Review v01

- **Date:** 2026-06-14
- **Feature / Scope:** Whole-project review of BioPyTools — a collection of standalone bioinformatics scripts (BLAST helpers, FASTA/GenBank parsers, a qPCR primer-specificity pipeline, Rosalind exercises, and experiment scratch files). No `specs/` folder exists, so this is a general code-quality / correctness / security review, not a spec-alignment review.
- **Specs referenced:** None present. Source of truth = the code itself plus inferred intent from docstrings/comments.
- **Trigger:** manual /code-reviewer

## Summary

BioPyTools is a set of ~20 loosely related Python scripts accumulated over time. The bioinformatics ideas are sound and several scripts are genuinely useful (BLAST wrappers, CDS extraction, the qPCR primer-specificity checker). However the project has **no packaging, no `requirements.txt`, no README, no `.gitignore`, no tests, and no shared utilities**. Many scripts run top-level code on import, mix English/Portuguese, hardcode filenames and absolute paths, and several contain outright bugs that will crash or silently produce wrong results.

Findings by severity: **2 Critical, 6 High, 11 Medium, 9 Low.**

Headline risks:
- The qPCR pipeline entrypoint (`qPCR/main.py`) is a 3-line stub that does nothing — the actual workflow only runs via `qPCR/blastPrimers.py` + a fragile `run.sh`. This is the project's flagship feature and it is effectively broken as advertised.
- The sensitivity/specificity computation in `PrimerTm.checkSpecSens` has a **substring-matching logic bug** that will misclassify species (e.g. "Toxoplasma gondii" matches "Toxoplasma gondiii" or any superstring), corrupting the core scientific output.
- A broken `except pd.errors` clause will raise `TypeError` instead of catching anything.
- Committed `__pycache__/`, `.pyc`, a redundant `qPCR.zip`, absolute home-directory paths, and duplicated data folders (`separados/`, scattered `.tsv`/`.fasta`) pollute the repo.
- No secrets/credentials were found (good) — but BLAST `remote=True` calls silently depend on network and an undocumented local `taxdb`.

## Requirements Coverage Map

Since there are no specs, this maps each script to its **inferred purpose** and whether it fulfils it.

| Script | Inferred purpose | Status | Notes |
|---|---|---|---|
| `AcessionNumbers.py` | Extract accession IDs from FASTA headers to a txt | Met (fragile) | Runs on import; interactive `input()`; hardcoded output name |
| `blastn.py` | CLI BLASTn of primers vs `nt`, add header | Met (fragile) | Top-level code; reads result but never uses it; `remote=True` |
| `blastp.py` | BLASTp protein FASTA vs `nr` | Partial | `import *`; interactive input; prints whole file to stdout |
| `Exclue_multispecies.py` | Split MULTISPECIES records from a multifasta | Met (buggy) | `.close` not called (no `()`); dead imports |
| `ExtractFirstSequence.py` | Extract consensus (1st seq) from each NCBI Virus alignment | Met (risky) | `chdir` + `listdir()` treats *every* file as FASTA; append-mode accumulates |
| `ExtractProteins.py` | Extract CDS translations from a GenBank file | Met (narrow) | Hardcoded assumptions (`strain` always present); bracket typo in description |
| `removeAspas.py` | Strip double quotes from a text file | Met | Writes `.tmp` sibling; never replaces original |
| `RosalindProblems.py` | Personal Rosalind exercise scratchpad | Broken | Contains syntax errors (lines 82-83) — not importable/runnable |
| `Teste_pandas.py` | Scratch: filter BLAST tsv by species | Scratch | Hardcoded filename; `import flash` from curses; not a tool |
| `testes.py` | Biopython learning scratch | Scratch | Hardcoded `arquivo.fasta`; `str + Seq` concat will error |
| `trasnlate.py` | Translate a hardcoded DNA seq | Scratch | Misspelled filename; single hardcoded sequence |
| `DataView/Orthofinder-venn.py` | Venn diagrams of OrthoFinder gene counts | Incomplete | Loop body fully commented out; hardcoded absolute path |
| `qPCR/main.py` | Intended unified CLI entrypoint | Missing | 3-line stub, imports modules and exits; does nothing |
| `qPCR/blastPrimers.py` | Real qPCR workflow: BLAST + Tm + spec/sens | Met (buggy) | The de-facto entrypoint; depends on buggy `PrimerTm` |
| `qPCR/PrimerTm.py` | Compute Tm, classify spec/sens | Partial (buggy) | Core logic bugs (see findings H2, H3, C2) |
| `qPCR/putHeader.py` | Prepend column header to BLAST tsv | Met (buggy) | `__main__` guard typo `"-_main__"`; glob path bug |
| `qPCR/ExtractSequences.py` | (unknown) | Empty | Only a shebang |
| `qPCR/fasta_handler.py` | IDT excel -> fasta; split multifasta | Met (buggy) | `sep_seqs(arq)` ignores its arg and re-prompts |
| `qPCR/run.sh` | Batch-run blastPrimers over a folder | Buggy | Passes 4 positional args + `wait`; script accepts 3 |

## Findings

### [CRITICAL] qPCR pipeline entrypoint `main.py` is a non-functional stub
- **Location:** `qPCR/main.py:1-3`
- **Category:** behaviour
- **What:** The file imports `blastPrimers, fasta_handler, PrimerTm, putHeader` and `argparse`, then ends. It defines no `argparse` parser, calls nothing, and produces no output. Because `blastPrimers.py` executes BLAST at module top-level, merely importing it here would *also* trigger an `argparse` parse of `main.py`'s own argv and immediately error or run an unintended BLAST.
- **Why it's a problem:** This is presented as the entrypoint of the project's most developed feature (the qPCR primer checker). A user running `python main.py` gets nothing, or a confusing crash from the imported module's top-level code. The real workflow is only reachable through `blastPrimers.py` + the brittle `run.sh`.
- **Suggested fix:** Make `main.py` the single CLI. Refactor `blastPrimers.py` so its BLAST logic lives in a function (e.g. `run_blast(query, output, num_alignments, target)`) guarded by `if __name__ == "__main__":`, then have `main.py` build one `argparse` parser with subcommands (`blast`, `extract`, `tm`) and dispatch. Remove top-level execution from all imported modules.

### [CRITICAL] `checkSpecSens` species matching uses substring `in`, producing wrong sensitivity/specificity
- **Location:** `qPCR/PrimerTm.py:56-77` (the `in target_ssciname` / `not in target_ssciname` comparisons)
- **Category:** logic
- **What:** `target_ssciname` is a concatenated lowercase genus+species string, and each row is tested with `... in target_ssciname`. Substring containment is not equality: e.g. target `"toxoplasmagondii"` will report a row species `"toxoplasmagond"` (truncated/partial name) as a match, and conversely a target that is a substring of a longer name behaves unpredictably. Names are also concatenated without a separator, so `"homo"`+`"sapiens"` = `"homosapiens"` can collide with unrelated concatenations.
- **Why it's a problem:** This is the scientific core of the tool — deciding whether a BLAST hit is the intended target species. Substring logic silently mis-buckets hits into false-positive/true-positive counts, corrupting the reported sensitivity and specificity that a researcher would use to choose qPCR primers. Wrong primers selected from wrong stats is a real lab/cost consequence.
- **Suggested fix:** Compare normalized full binomial names for **equality**, not containment: build `row_name = " ".join(row['sscinames'].split()[:2]).lower()` and `target = " ".join(df['sscinames'][0].split()[:2]).lower()` and test `row_name == target`. Keep the space so `genus species` cannot collide with concatenations. Add a unit test with a curated tsv asserting exact counts.

### [HIGH] `except pd.errors` is not a valid exception and will raise `TypeError`
- **Location:** `qPCR/PrimerTm.py:78`
- **Category:** logic
- **What:** `except pd.errors as e:` — `pd.errors` is a *module*, not an exception class. When the `try` body raises (e.g. a one-word species name causing `IndexError` on `split()[1]`, or a NaN), Python evaluates the `except` and raises `TypeError: catching classes that do not inherit from BaseException is not allowed`, masking the original error.
- **Why it's a problem:** The intended robustness is absent; instead the program crashes with a misleading error precisely on the malformed rows the author tried to guard against. The real risk (one-token species names like "uncultured") is exactly what triggers it.
- **Suggested fix:** Catch concrete exceptions: `except (IndexError, AttributeError, KeyError) as e:`. Better, pre-filter rows whose `sscinames` does not contain at least two tokens, and log how many were skipped.

### [HIGH] `run.sh` passes arguments that `blastPrimers.py` does not accept
- **Location:** `qPCR/run.sh:3` vs `qPCR/blastPrimers.py:20-28`
- **Category:** behaviour
- **What:** `run.sh` invokes `blastPrimers.py $f $f 5000 toxoplasmagondii wait` — five positional tokens. `blastPrimers.py` defines exactly three positional args (`query`, `output_name`, `num_alignments`). argparse will reject the extra `toxoplasmagondii` and `wait` with `error: unrecognized arguments`, so the batch loop fails on every file.
- **Why it's a problem:** The documented batch-execution path is broken; the `target` species the user clearly intended to pass is silently unsupported by the script, which instead infers the target from row 0 of the BLAST output (an unreliable heuristic).
- **Suggested fix:** Add a `target` argument to the script's parser and remove the stray `wait`. Pass it through to `checkSpecSens(file, target)` instead of inferring the target from `df[...][0]`. Quote `"$f"` in the loop to survive spaces in filenames.

### [HIGH] `RosalindProblems.py` contains syntax errors — file cannot be imported or run
- **Location:** `RosalindProblems.py:82-83`
- **Category:** logic
- **What:** `homodom = #...` and `heter = #...` are assignments with no right-hand side (comment only). This is a `SyntaxError`; the entire module fails to parse.
- **Why it's a problem:** Any tooling that imports/collects the package (test runners, linters, `python -m compileall`) will error on this file. It is committed scratch work left mid-edit.
- **Suggested fix:** This is a personal exercise log, not a tool. Move it out of the importable tree into a `notebooks/` or `scratch/` folder (excluded from packaging), or finish/comment the lines. At minimum give the names placeholder values (`homodom = None`).

### [HIGH] `Exclue_multispecies.py` never closes output files (missing `()`)
- **Location:** `Exclue_multispecies.py:17-18`
- **Category:** logic
- **What:** `saida.close` and `excluded.close` reference the method but never call it. Files are opened with `w+` at top level and only flushed/closed when the interpreter exits (or possibly truncated on the next open). On some platforms/buffering, the last writes may not be flushed if the process is interrupted.
- **Why it's a problem:** Risk of truncated/empty output FASTA files — data loss for a deduplication step. Also `from os import pread` and `from importlib.resources import path` are unused dead imports.
- **Suggested fix:** Use `with open(...) as saida, open(...) as excluded:` context managers so closing is guaranteed, and delete the unused imports.

### [HIGH] No `requirements.txt` / packaging / pinned dependencies
- **Location:** repo root (absent)
- **Category:** other (reproducibility)
- **What:** The scripts depend on Biopython, pandas, numpy, openpyxl (for `read_excel`), matplotlib, matplotlib-venn, and external `blast+` binaries plus a local `taxdb`, with no declaration anywhere. Shebangs hardcode `/usr/bin/python3.8`.
- **Why it's a problem:** A new user (or future you) cannot reproduce the environment. `pd.read_excel` silently needs `openpyxl`; missing it gives an opaque error. The pinned 3.8 shebang will break on machines without that exact interpreter.
- **Suggested fix:** Add `requirements.txt` (or `pyproject.toml`) listing `biopython`, `pandas`, `numpy`, `openpyxl`, `matplotlib`, `matplotlib-venn`. Document the non-pip prerequisites (BLAST+, taxdb) in the README. Replace `#!/usr/bin/python3.8` with `#!/usr/bin/env python3`.

### [HIGH] Committed build artifacts, archive, and absent `.gitignore`
- **Location:** `__pycache__/`, `qPCR/__pycache__/`, `*.pyc`, `qPCR.zip`
- **Category:** other (hygiene / data integrity)
- **What:** Compiled `.pyc` for both cpython-310 and cpython-38, a `qPCR.zip` snapshot duplicating the live `qPCR/` folder, and numerous generated data files (`report_*.tsv`, `teste*.tsv`, `*.fasta`) are tracked. There is no `.gitignore`.
- **Why it's a problem:** Build artifacts cause noisy diffs and can mask source/byte-code drift; the zip is a stale duplicate that will diverge from `qPCR/`; tracked outputs blur which files are inputs vs results. This is the root cause of the "messy and hard to understand" complaint.
- **Suggested fix:** Add a `.gitignore` (`__pycache__/`, `*.pyc`, `*.zip`, output patterns). `git rm -r --cached __pycache__ qPCR/__pycache__ qPCR.zip`. Move sample inputs to `examples/` and stop tracking generated reports.

### [MEDIUM] BLAST result files are read but never used (dead I/O)
- **Location:** `blastn.py:34-35`, `qPCR/blastPrimers.py:36,41`, `blastp.py:20-22`
- **Category:** behaviour
- **What:** Each opens the result tsv and reads it into `lines`, then never uses `lines` (except `blastp.py`, which prints the entire file to stdout). Files opened with `open(...)` are not closed.
- **Why it's a problem:** Wasted memory on large BLAST outputs, leaked file handles, and dead code that confuses readers about intent.
- **Suggested fix:** Remove the unused reads; if a preview is desired, read a bounded number of lines inside a `with`. Close/`with` all file handles.

### [MEDIUM] `getTm` overwrites the input tsv in place, losing original BLAST output
- **Location:** `qPCR/PrimerTm.py:49-50`
- **Category:** data-integrity
- **What:** After computing Tm, the function does `df.to_csv(archive ...)` over the same path passed in. The raw BLAST output is destroyed and replaced with an augmented one (also gaining a pandas index column because `index=False` is not set).
- **Why it's a problem:** Irreversible mutation of source data; re-running the pipeline on the same file double-processes an already-augmented file (now containing `tm`/`same_tm` columns and an unnamed index), corrupting `checkSpecSens` which `read_csv`s it again with `header=0`.
- **Suggested fix:** Write to a new file (e.g. `<prefix>.tm.tsv`) and pass that to `checkSpecSens`. Use `to_csv(..., index=False)`. Make the function return the dataframe so callers can chain without re-reading.

### [MEDIUM] `np.resize` is the wrong tool for attaching per-row columns
- **Location:** `qPCR/PrimerTm.py:28,45`
- **Category:** logic
- **What:** `df['tm'] = np.resize(Tm_values, len(df))` — `Tm_values` already has exactly `len(df)` elements, so `np.resize` is a no-op at best; if a row were ever skipped it would silently *tile/repeat* values to fit, attaching wrong Tm to wrong rows with no error.
- **Why it's a problem:** Fragile and surprising: a length mismatch (the exact failure mode you'd want to catch) is hidden by silent recycling, mis-associating Tm values with sequences.
- **Suggested fix:** Assign the list directly: `df['tm'] = Tm_values`. Pandas will raise if lengths differ — which is the correct, loud behaviour.

### [MEDIUM] `sep_seqs(arq)` ignores its parameter and re-prompts interactively
- **Location:** `qPCR/fasta_handler.py:49-51`
- **Category:** behaviour
- **What:** The function takes `arq` but immediately overwrites it with `input('Digite o caminho...')`, so any caller-supplied path is discarded.
- **Why it's a problem:** Makes the function non-scriptable and untestable; a programmatic caller's argument is silently ignored. Also writes one file per record into the CWD with no output-dir control, risking collisions/clobbering.
- **Suggested fix:** Remove the `input()`; use the parameter. Add an `output_dir` argument and create it if missing. Sanitize `rec.id` for filesystem-unsafe characters before using it as a filename.

### [MEDIUM] `ExtractFirstSequence.py` treats every file in the directory as FASTA
- **Location:** `ExtractFirstSequence.py:11-21`
- **Category:** behaviour
- **What:** `chdir(cam)` then `listdir()` iterates *all* entries (including subdirectories, hidden files, the output `consensos.fasta` itself once created). Each is opened and parsed as FASTA; a non-FASTA or a directory yields an empty parse and `records[0]` raises `IndexError`.
- **Why it's a problem:** Crashes on any non-FASTA file in the folder, and may re-read its own growing output. The reported count ("Existem N arquivos de alinhamento") is wrong because it counts everything.
- **Suggested fix:** Filter by extension (`glob('*.fasta')` / `*.fa`), skip the output file, and guard `if records:` before indexing. Pass the directory as an argparse argument rather than `chdir`+`input`.

### [MEDIUM] Pervasive interactive `input()` instead of CLI arguments
- **Location:** `AcessionNumbers.py:5`, `blastp.py:11-12`, `Exclue_multispecies.py:5-6`, `ExtractFirstSequence.py:10`, `removeAspas.py:3`, `fasta_handler.py:50`
- **Category:** behaviour / quality
- **What:** Half the scripts block on `input()` prompts, mixing Portuguese and English, instead of using `argparse` (which the other half already use).
- **Why it's a problem:** Cannot be run non-interactively, in batch, in CI, or tested. Inconsistent UX across the toolkit.
- **Suggested fix:** Standardize on `argparse` everywhere with a consistent language (pick English for code-facing UX). Provide `--help` for each tool.

### [MEDIUM] Top-level execution on import across most scripts
- **Location:** `AcessionNumbers.py:21`, `blastn.py` (module body), `blastp.py`, `Exclue_multispecies.py`, `ExtractProteins.py`, `Teste_pandas.py`, `testes.py`, `trasnlate.py`, `qPCR/blastPrimers.py`
- **Category:** quality
- **What:** Logic runs at module top level with no `if __name__ == "__main__":` guard. Importing any of these (as `main.py` tries to) executes BLAST calls, prompts, or file writes as a side effect.
- **Why it's a problem:** Makes modules un-importable/un-testable and is the direct cause of the `main.py` Critical. Side effects on import are a classic foot-gun.
- **Suggested fix:** Wrap each script's procedural body in a `main()` function under an `if __name__ == "__main__":` guard. This is the single highest-leverage refactor for the whole repo.

### [MEDIUM] Hardcoded absolute / home-directory paths
- **Location:** `DataView/Orthofinder-venn.py:11` (`/home/enrico/Documentos/...`), `qPCR/run.sh:3` (`~/Documentos/BioPyTools/...`)
- **Category:** quality / portability
- **What:** Paths are pinned to one user's machine.
- **Why it's a problem:** Non-portable; nobody else (or the same user on another machine) can run them.
- **Suggested fix:** Accept paths as arguments. For `run.sh`, resolve the script dir with `$(dirname "$0")`.

### [MEDIUM] `DataView/Orthofinder-venn.py` does nothing — entire loop body commented out
- **Location:** `DataView/Orthofinder-venn.py:14-21`
- **Category:** behaviour
- **What:** The script reads a TSV then enters a `for row in df.iterrows():` whose body is 100% comments. No Venn diagram is produced.
- **Why it's a problem:** Dead/unfinished feature masquerading as a tool; also `iterrows()` here is unused work.
- **Suggested fix:** Either implement (compute genome-presence sets and call `venn2`/`venn3`) or move to `scratch/`. Note `from ast import increment_lineno` is an erroneous dead import.

### [MEDIUM] No tests anywhere
- **Location:** repo-wide (absent)
- **Category:** quality
- **What:** Zero tests despite the qPCR pipeline performing quantitative scientific computation (Tm, sensitivity/specificity).
- **Why it's a problem:** The C2/H2 logic bugs would have been caught instantly by a single fixture-based test. No safety net for refactoring.
- **Suggested fix:** Add `pytest` with small curated `.tsv`/`.fasta` fixtures asserting exact counts from `checkSpecSens`, Tm ranges from `getTm`, and parsing from `fasta_handler`. Start with the species-classification logic.

### [LOW] `putHeader.py` `__main__` guard typo and unsafe default
- **Location:** `qPCR/putHeader.py:15-16`
- **Category:** logic
- **What:** `if __name__ == "-_main__":` (note `-_`) can never be true, so the guard is dead. Were it correct, `putHeader("./*")` would try to open a literal file named `./*`.
- **Why it's a problem:** Misleading dead code; the literal-glob call would crash.
- **Suggested fix:** Fix to `"__main__"` and remove/replace the `"./*"` call with a proper argparse path, or drop the block entirely (it's a library function).

### [LOW] Header column count can mismatch actual BLAST `outfmt`
- **Location:** `qPCR/putHeader.py:7-8` vs callers' `outfmt`
- **Category:** data-integrity
- **What:** `putHeader` hardcodes a 10-column header. `blastn.py` and `blastPrimers.py` use the matching 10-field outfmt, but `Teste_pandas.py`/older outputs use 5 columns. If outfmt and header drift, columns silently misalign.
- **Why it's a problem:** Silent column-misalignment corrupts downstream pandas access by name.
- **Suggested fix:** Define the outfmt fields once as a shared constant and derive both the BLAST `outfmt` string and the header from it.

### [LOW] `report_*.tsv` filename built from unsanitized species name
- **Location:** `qPCR/PrimerTm.py:87`
- **Category:** behaviour
- **What:** Output file is `report_{target_ssciname}.tsv` where the name comes from BLAST data. Spaces/slashes in a species string (e.g. "Human papillomavirus", seen in committed `report_Human papillomavirus.tsv`) create awkward or path-breaking filenames.
- **Why it's a problem:** Spaces/slashes in filenames break shell loops (`run.sh` uses unquoted `$f`) and can escape the intended directory.
- **Suggested fix:** Slugify the name (`re.sub(r'[^\w]+', '_', name)`) before using in a path.

### [LOW] `blastp.py` uses `from ... import *` and prints whole result to stdout
- **Location:** `blastp.py:9,22`
- **Category:** quality
- **What:** Wildcard import pollutes the namespace; printing the full BLAST tsv to stdout is unhelpful for large results.
- **Why it's a problem:** Wildcard imports hide names and risk collisions; dumping megabytes to terminal is impractical.
- **Suggested fix:** Import only `NcbiblastpCommandline`; remove the full-file print or cap it.

### [LOW] `testes.py` will crash on `str + Seq` concatenation
- **Location:** `testes.py:7,10`
- **Category:** logic
- **What:** `"RNA: " + rna` where `rna` is a Biopython `Seq`; depending on Biopython version this raises `TypeError`. Also reads hardcoded `arquivo.fasta` that isn't present.
- **Why it's a problem:** Scratch file that errors; clutters the root.
- **Suggested fix:** Move to `scratch/`; if kept, wrap with `str(rna)`.

### [LOW] Misspelled / inconsistent filenames and identifiers
- **Location:** `trasnlate.py` (translate), `Exclue_multispecies.py` (Exclude), variable `pippo`, `diference`/`Specifivity` typos in `PrimerTm.py`
- **Category:** quality
- **What:** Typos in filenames, output labels ("Specifivity"), and variables.
- **Why it's a problem:** Hard to discover/import; typos appear in user-facing report output, looking unprofessional.
- **Suggested fix:** Rename consistently (snake_case modules), fix output strings.

### [LOW] Mixed-language and absent docstrings/comments
- **Location:** repo-wide
- **Category:** quality
- **What:** Comments/prompts mix Portuguese and English; many scripts have no module docstring describing inputs/outputs.
- **Why it's a problem:** This is the user's stated pain ("uncommented and hard to understand").
- **Suggested fix:** Add a one-paragraph docstring to every script (purpose, inputs, outputs, example invocation). Pick one language for user-facing text.

### [LOW] `removeAspas.py` writes `.tmp` and never replaces the original
- **Location:** `removeAspas.py:4`
- **Category:** behaviour
- **What:** Output goes to `arq + ".tmp"`; the user must manually rename. Also prints every line (noisy).
- **Why it's a problem:** Surprising; the tool's job ("remove quotes from the file") isn't completed.
- **Suggested fix:** Offer `--in-place` (atomic `os.replace`) or an explicit `-o` output path; drop the per-line print.

### [LOW] `ExtractProteins.py` assumes `strain` qualifier always exists
- **Location:** `ExtractProteins.py:37`
- **Category:** logic
- **What:** `strain = seq_feature.qualifiers['strain'][0]` with no guard; many GenBank records lack `strain`, raising `KeyError`. Also `organism`/`strain` are computed but never used in output, and the description has an unbalanced bracket: `[locus_tag={locus_tag}[protein=...]`.
- **Why it's a problem:** Crashes on common records; malformed FASTA header brackets break downstream parsers that key on `[k=v]` tags.
- **Suggested fix:** Use the same `if 'strain' in qualifiers` guard pattern used elsewhere; fix the bracket; remove unused vars or include them in the description.

## Positive Notes

- The BLAST wrappers (`blastn.py`, `qPCR/blastPrimers.py`) choose sensible short-sequence parameters (`word_size=7`, `penalty=-3`, `reward=1`, high evalue) appropriate for primer/probe specificity — the domain reasoning is correct.
- `ExtractProteins.py` handles the genuinely tricky case of extracting CDS translations from legacy GenBank records and builds NCBI-style `lcl|` FASTA IDs — useful, non-trivial work.
- Several scripts already use `argparse` cleanly (`blastn.py`, `ExtractProteins.py`), giving a good template to standardize the rest.
- `getTm` correctly uses nearest-neighbour thermodynamics (`Tm_NN`) with salt/Mg corrections rather than naive Wallace rule — scientifically appropriate.
- No hardcoded secrets, tokens, or credentials were found anywhere in the repo.

## Open Questions / Needs Clarification

1. **Is `qPCR/main.py` meant to be the unified CLI?** If yes, confirm the desired subcommands so the refactor (C1) can be scoped. If the real entrypoint is `blastPrimers.py`, `main.py` should be deleted to avoid confusion.
2. **Target-species source of truth:** should the qPCR tool take the target species as an explicit argument (as `run.sh` implies) or keep inferring it from BLAST row 0? This decides the H4/C2 fixes.
3. **Which scripts are "tools" vs "personal scratch"?** `testes.py`, `Teste_pandas.py`, `trasnlate.py`, `RosalindProblems.py`, and the commented-out `Orthofinder-venn.py` look like scratch. Confirm so they can be moved to `scratch/` (excluded from packaging) rather than fixed.
4. **`qPCR/ExtractSequences.py` is empty (only a shebang)** — intended placeholder, or leftover? Delete or implement?
5. **Should generated outputs (`report_*.tsv`, `separados/`, sample `.fasta`/`.tsv`) be tracked?** Recommend moving inputs to `examples/` and gitignoring outputs.

## Proposed Reorganization Strategy

A concrete target layout to address the "disorganized" complaint:

```
BioPyTools/
  README.md                  # what each tool does + install + examples
  requirements.txt           # biopython, pandas, numpy, openpyxl, matplotlib, matplotlib-venn
  pyproject.toml             # optional: make it pip-installable with console_scripts
  .gitignore                 # __pycache__/, *.pyc, *.zip, generated reports
  biopytools/                # the importable package
    __init__.py
    common/                  # shared utilities (eliminate duplication)
      blast.py               #   one place for outfmt fields + header + NcbiblastnCommandline setup
      fasta.py               #   shared FASTA read/write/split helpers
      io.py                  #   path handling, slugify, safe file replace
    blast/                   # blastn.py, blastp.py (refactored, argparse, main())
    fasta_tools/             # AcessionNumbers, Exclue_multispecies, ExtractFirstSequence,
                             #   ExtractProteins, fasta_handler  (deduplicate SeqIO logic)
    qpcr/                    # blastPrimers -> run_blast(), PrimerTm, putHeader, main.py CLI
    text_tools/              # removeAspas
    orthofinder/             # Orthofinder-venn (finish or mark experimental)
  examples/                  # sample inputs only (exemplo.fasta, primers_example.fasta, *.tsv)
  scratch/                   # RosalindProblems, testes, Teste_pandas, trasnlate (NOT packaged)
  tests/                     # pytest fixtures + tests for qpcr classification & Tm
```

Key consolidation wins:
- The BLAST `outfmt` field list and the `putHeader` header are duplicated/coupled across `blastn.py`, `blastPrimers.py`, `Teste_pandas.py` — define **once** in `common/blast.py` and import everywhere (fixes L2).
- FASTA read/parse/write boilerplate recurs in 6+ scripts — centralize in `common/fasta.py`.
- Adopt one CLI convention (`argparse` + `main()` guard) so every tool is importable and testable, unblocking `main.py` (C1).
- Add `console_scripts` entry points in `pyproject.toml` so tools install as `biopytools-qpcr`, `biopytools-blastn`, etc., removing the need for hardcoded shebangs and `run.sh` absolute paths.

Suggested fix order: (1) `.gitignore` + remove artifacts/zip; (2) fix the two Critical + four High correctness bugs; (3) add `requirements.txt` + README; (4) introduce `main()` guards and the package skeleton; (5) extract shared utilities and add tests.
