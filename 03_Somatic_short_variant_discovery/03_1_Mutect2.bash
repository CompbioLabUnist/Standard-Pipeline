#!/bin/bash
set -euo pipefail
#IFS=$'\n\t'

python3 03_1_Mutect2.py /BiO/Research/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/cn95P.Sort.MarkDuplicates.BQSR.bam /BiO/Research/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/cn95N.Sort.MarkDuplicates.BQSR.bam cn95.maf
