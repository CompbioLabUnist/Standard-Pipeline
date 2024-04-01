#!/bin/bash
set -euo pipefail
#IFS=$'\n\t'

python3 04_1_HaplotypeCaller.py /BiO/Research/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/cn95P.Sort.MarkDuplicates.BQSR.bam cn95.maf
