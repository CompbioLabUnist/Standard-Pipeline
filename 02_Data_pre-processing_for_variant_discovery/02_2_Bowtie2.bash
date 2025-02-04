#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

python3 -B 02_2_Bowtie2.py $(realpath ../00_Data/WES/C001_TN_DNA_R1.fastq.gz ../00_Data/WES/C001_TN_DNA_R2.fastq.gz) $(realpath .)
python3 -B 02_2_Bowtie2.py $(realpath ../00_Data/WES/merge/C001_TT_DNA_R1.fastq.gz ../00_Data/WES/merge/C001_TT_DNA_R2.fastq.gz) $(realpath .)
