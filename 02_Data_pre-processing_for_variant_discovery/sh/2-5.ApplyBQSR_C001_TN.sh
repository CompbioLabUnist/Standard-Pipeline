#!/bin/bash
/BiO/Share/Tools/gatk-4.6.1.0/gatk ApplyBQSR --bqsr-recal-file /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TN.Sort.MarkDuplicates.BQSR.table --input /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TN.Sort.MarkDuplicates.bam --output /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TN.Sort.MarkDuplicates.BQSR.bam --reference /BiO/Share/Tools/gatk-bundle/hg38/Homo_sapiens_assembly38.fasta --create-output-bam-index true
status=$?
if [ "$status" -ne 0 ]; then
    echo "SLURM job failed: UID=${UID:-$(id -u)} JOB_ID=${SLURM_JOB_ID:-unknown} JOB_NAME=${SLURM_JOB_NAME:-unknown} EXIT_STATUS=$status" >&2
fi
exit "$status"
