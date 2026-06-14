#!/bin/bash
/BiO/Share/Tools/gatk-4.6.1.0/gatk GenomicsDBImport --java-options "-XX:+UseSerialGC -Xmx55g" --reference /BiO/Share/Tools/gatk-bundle/hg38/Homo_sapiens_assembly38.fasta --genomicsdb-workspace-path /BiO/Teach/Standard-Pipeline/04_Germline_short_variant_discovery/C001_TN-DB --variant /BiO/Teach/Standard-Pipeline/04_Germline_short_variant_discovery/C001_TN.vcf --intervals /BiO/Share/Tools/gatk-bundle/hg38/wgs_calling_regions.hg38.interval_list --reader-threads 30 --max-num-intervals-to-import-in-parallel 30 --overwrite-existing-genomicsdb-workspace true
status=$?
if [ "$status" -ne 0 ]; then
    echo "SLURM job failed: UID=${UID:-$(id -u)} JOB_ID=${SLURM_JOB_ID:-unknown} JOB_NAME=${SLURM_JOB_NAME:-unknown} EXIT_STATUS=$status" >&2
fi
exit "$status"
