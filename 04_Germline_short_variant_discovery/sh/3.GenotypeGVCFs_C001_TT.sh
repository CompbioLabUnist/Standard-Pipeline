#!/bin/bash
/BiO/Share/Tools/gatk-4.6.1.0/gatk GenotypeGVCFs --java-options "-XX:+UseSerialGC -Xmx55g" --reference /BiO/Share/Tools/gatk-bundle/hg38/Homo_sapiens_assembly38.fasta --variant gendb:///BiO/Teach/Standard-Pipeline/04_Germline_short_variant_discovery/C001_TT-DB --output /BiO/Teach/Standard-Pipeline/04_Germline_short_variant_discovery/C001_TT.DB.vcf
status=$?
if [ "$status" -ne 0 ]; then
    echo "SLURM job failed: UID=${UID:-$(id -u)} JOB_ID=${SLURM_JOB_ID:-unknown} JOB_NAME=${SLURM_JOB_NAME:-unknown} EXIT_STATUS=$status" >&2
fi
exit "$status"
