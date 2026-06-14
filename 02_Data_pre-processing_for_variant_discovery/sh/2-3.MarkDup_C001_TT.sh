#!/bin/bash
/BiO/Share/Tools/gatk-4.6.1.0/gatk MarkDuplicatesSpark --input /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TT.Sort.bam --output /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TT.Sort.MarkDuplicates.bam --reference /BiO/Share/Tools/gatk-bundle/hg38/Homo_sapiens_assembly38.fasta --metrics-file /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TT.Sort.MarkDuplicates.metrics --duplicate-tagging-policy 'OpticalOnly' -- --spark-master 'local[30]' --spark-verbosity 'INFO'
status=$?
if [ "$status" -ne 0 ]; then
    echo "SLURM job failed: UID=${UID:-$(id -u)} JOB_ID=${SLURM_JOB_ID:-unknown} JOB_NAME=${SLURM_JOB_NAME:-unknown} EXIT_STATUS=$status" >&2
fi
exit "$status"
