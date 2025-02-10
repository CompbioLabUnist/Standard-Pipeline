#!/bin/bash
set -euo pipefail
#IFS=$'\n\t'

python3 -B 03_1_Mutect2.py $(realpath ../02_Data_pre-processing_for_variant_discovery/C001_TN.Sort.MarkDuplicates.BQSR.bam ../02_Data_pre-processing_for_variant_discovery/C001_TT.Sort.MarkDuplicates.BQSR.bam) $(realpath ./cn95.maf)
