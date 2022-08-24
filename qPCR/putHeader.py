#!/usr/bin/python3
# *-* coding: utf-8 -*-
# Add header on the first line of the result from blast.py
def putHeader(file):
    with open(file, 'r') as input_file:
        line = 0
        header = (
            'qseqid   sscinames   qcovs   pident  evalue  staxids qseq  sblastnames salltitles  stitle')
        lines = input_file.readlines()
        lines.insert(line, header + "\n")
    with open(file, "w") as output_file:
        output_file.writelines(lines)
