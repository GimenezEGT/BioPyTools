#!/usr/bin/python3.8
# *-* coding: utf-8 -*-
# Add header on the first line of the result from blast.py

import os


def putHeader():
    directory = './'
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        file = open(f, 'r', encoding='iso8859-1')
        line = 0
        header = ('qseqid	sscinames	qcovs	pident	evalue	staxids	qseq')
        lines = file.readlines()
        file.close()
        lines.insert(line, header + "\n")
        file = open(f, "w", encoding='iso8859-1')
        file.writelines(lines)
        file.close()


if __name__ == "__main__":
    putHeader()
