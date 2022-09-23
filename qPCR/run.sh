#!/bin/bash

for f in *; do ~/Documentos/BioPyTools/qPCR/blastPrimers.py $f $f 5000 toxoplasmagondii wait; done

