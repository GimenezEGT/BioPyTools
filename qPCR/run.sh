#!/bin/bash
# Run blastPrimers over every file in the current directory.
# The target species is inferred from the first BLAST hit of each file,
# so it is not passed as an argument.
script_dir="$(cd "$(dirname "$0")" && pwd)"

for f in *; do
    [ -f "$f" ] || continue
    python3 "$script_dir/blastPrimers.py" "$f" "$f" 5000
done

