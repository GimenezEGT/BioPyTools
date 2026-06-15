# Quickstart: BioPyTools (post-refactor)

## Install

```bash
git clone <repo> && cd BioPyTools
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -e .          # installs biopytools + console scripts
# or, without packaging:
pip install -r requirements.txt
```

External prerequisites (not installed by pip):
- NCBI BLAST+ (`blastn`, `blastp`) on PATH
- A local `taxdb` (in the working dir or referenced from your shell profile)

## Run the qPCR primer checker

```bash
biopytools-qpcr run primers.fasta my_run 5000
#  -> my_run.tsv          (raw BLAST, header added)
#  -> my_run.tm.tsv       (Tm-annotated; raw preserved)
#  -> report_<species>.tsv (sensitivity/specificity)
```

Re-running on the same input is safe — the raw `.tsv` is never overwritten
(SC-007). Target species is inferred from the first BLAST hit.

## Other tools (examples)

```bash
biopytools-blastn primers.fasta out --num-alignments 1000
biopytools-extract-proteins genome.gb -o proteins.fasta
biopytools-extract-first ./alignments -o consensos.fasta
biopytools-exclude-multispecies seqs.fasta --prefix clean
```

Every tool supports `--help`.

## Run the tests

```bash
pip install pytest
pytest            # covers species classification (SC-001), Tm, FASTA parsing
```

## Validate the acceptance criteria

| Check | How |
|-------|-----|
| SC-001 exact classification | `pytest tests/test_spec_sens.py` |
| SC-002 no interactive prompts | run any tool with args; it never blocks |
| SC-003 help text | `biopytools-<tool> --help` |
| SC-007 non-destructive | run `qpcr run` twice; raw `.tsv` unchanged |
| SC-008 clean VCS | `git status` shows no generated outputs/artifacts |
