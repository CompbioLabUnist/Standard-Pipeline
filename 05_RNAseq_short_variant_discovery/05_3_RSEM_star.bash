#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

python3 -B 05_3_RSEM_star.py $(realpath ../00_Data/WTS/C001_TT_RNA_R1.fastq.gz ../00_Data/WTS/C001_TT_RNA_R2.fastq.gz) $(realpath hg38.grp) $(realpath C001_TT)
