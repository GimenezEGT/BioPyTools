#!/bin/bash
# Run the qPCR primer pipeline over every FASTA file in a directory.
#
# The target species is inferred from the first BLAST hit of each file, so it is
# not passed as an argument. Requires `biopytools` to be importable (e.g. after
# `pip install -e .`) and NCBI BLAST+ on PATH.
#
# Outputs are written under OUTPUT_DIR (default: ./qpcr_out) with a clean prefix
# per input, keeping generated files separate from the inputs.
#
# Usage: ./run_qpcr_batch.sh [INPUT_DIR] [NUM_ALIGNMENTS] [OUTPUT_DIR]
set -euo pipefail

input_dir="${1:-.}"
num_alignments="${2:-5000}"
output_dir="${3:-./qpcr_out}"
mkdir -p "$output_dir"

for f in "$input_dir"/*.fasta "$input_dir"/*.fa "$input_dir"/*.fas; do
    [ -f "$f" ] || continue
    base="$(basename "$f")"          # strip directory
    prefix="$output_dir/${base%.*}"  # strip extension; write into output_dir
    echo "Processing $f -> $prefix.* ..."
    python -m biopytools.qpcr run "$f" "$prefix" "$num_alignments"
done
