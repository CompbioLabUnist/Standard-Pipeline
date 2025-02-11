#!/bin/bash
set -euo pipefail
#IFS=$'\n\t'

python3 -B 04_1_HaplotypeCaller.py $(realpath ../02_Data_pre-processing_for_variant_discovery/C001_TN.Sort.MarkDuplicates.BQSR.bam) $(realpath C001_TN.maf)
python3 -B 04_1_HaplotypeCaller.py $(realpath ../02_Data_pre-processing_for_variant_discovery/C001_TT.Sort.MarkDuplicates.BQSR.bam) $(realpath C001_TT.maf)
