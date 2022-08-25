#!/usr/bin/python3
# *-* coding: utf-8 -*-
# Add header on the first line of the result from blast.py
def putHeader(file):
    with open(file, 'r') as input_file:
        line = 0
        header = (
            'qseqid\tsscinames\tqcovs\tpident\tevalue\tstaxids\tqseq\tsblastnames\tsalltitles\tstitle')
        lines = input_file.readlines()
        lines.insert(line, header + "\n")
    with open(file, "w") as output_file:
        output_file.writelines(lines)
