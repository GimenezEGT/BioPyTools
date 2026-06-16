#!/bin/bash
# Run the qPCR primer pipeline over every FASTA file in a directory.
#
# The target species is inferred from the first BLAST hit of each file, so it is
# not passed as an argument. Requires `biopytools` to be importable (e.g. after
# `pip install -e .`) and NCBI BLAST+ on PATH.
#
# Usage: ./run_qpcr_batch.sh [INPUT_DIR] [NUM_ALIGNMENTS]
set -euo pipefail

input_dir="${1:-.}"
num_alignments="${2:-5000}"

for f in "$input_dir"/*.fasta "$input_dir"/*.fa "$input_dir"/*.fas; do
    [ -f "$f" ] || continue
    echo "Processing $f ..."
    python -m biopytools.qpcr run "$f" "$f" "$num_alignments"
done
