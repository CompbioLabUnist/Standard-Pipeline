#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

python3 01_1_FastQC.py /BiO/Store/Standard-Pipeline/cn95N_S0_L009_R1_001.fastq.gz /BiO/Store/Standard-Pipeline/cn95N_S0_L009_R2_001.fastq.gz /BiO/Store/Standard-Pipeline/cn95P_S0_L009_R1_001.fastq.gz /BiO/Store/Standard-Pipeline/cn95P_S0_L009_R2_001.fastq.gz
