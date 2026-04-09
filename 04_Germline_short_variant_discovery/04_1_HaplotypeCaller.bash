#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

python3 -B 04_1_HaplotypeCaller.py "$(realpath ../02_Data_pre-processing_for_variant_discovery/C001_TN.Sort.MarkDuplicates.BQSR.bam)" "$(realpath ./C001_TN.maf)"
python3 -B 04_1_HaplotypeCaller.py "$(realpath ../02_Data_pre-processing_for_variant_discovery/C002_TN.Sort.MarkDuplicates.BQSR.bam)" "$(realpath ./C002_TN.maf)"
python3 -B 04_1_HaplotypeCaller.py "$(realpath ../02_Data_pre-processing_for_variant_discovery/C003_TN.Sort.MarkDuplicates.BQSR.bam)" "$(realpath ./C003_TN.maf)"
python3 -B 04_1_HaplotypeCaller.py "$(realpath ../02_Data_pre-processing_for_variant_discovery/K001_BU.Sort.MarkDuplicates.BQSR.bam)" "$(realpath ./K001_BU.maf)"
python3 -B 04_1_HaplotypeCaller.py "$(realpath ../02_Data_pre-processing_for_variant_discovery/K002_BU.Sort.MarkDuplicates.BQSR.bam)" "$(realpath ./K002_BU.maf)"
python3 -B 04_1_HaplotypeCaller.py "$(realpath ../02_Data_pre-processing_for_variant_discovery/K003_BU.Sort.MarkDuplicates.BQSR.bam)" "$(realpath ./K003_BU.maf)"
