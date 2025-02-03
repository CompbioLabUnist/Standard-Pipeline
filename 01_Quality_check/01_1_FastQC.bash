#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

python3 -B 01_1_FastQC.py $(realpath ../00_Data/WES/C001_TN_DNA_R1.fastq.gz)
