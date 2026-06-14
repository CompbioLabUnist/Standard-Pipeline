#!/bin/bash
/BiO/Share/Tools/samtools-1.21/samtools sort -l 9 --threads 30 --reference /BiO/Share/Tools/gatk-bundle/hg38/Homo_sapiens_assembly38.fasta --write-index -o /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TN.Sort.bam /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TN.bam
status=$?
if [ "$status" -ne 0 ]; then
    echo "SLURM job failed: UID=${UID:-$(id -u)} JOB_ID=${SLURM_JOB_ID:-unknown} JOB_NAME=${SLURM_JOB_NAME:-unknown} EXIT_STATUS=$status" >&2
fi
exit "$status"
