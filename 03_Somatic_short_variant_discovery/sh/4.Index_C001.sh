#!/bin/bash
/BiO/Share/Tools/gatk-4.6.1.0/gatk IndexFeatureFile --java-options "-XX:+UseSerialGC -Xmx55g" --input /BiO/Teach/Standard-Pipeline/03_Somatic_short_variant_discovery/C001.PASS.vcf --output /BiO/Teach/Standard-Pipeline/03_Somatic_short_variant_discovery/C001.PASS.vcf.idx
status=$?
if [ "$status" -ne 0 ]; then
    echo "SLURM job failed: UID=${UID:-$(id -u)} JOB_ID=${SLURM_JOB_ID:-unknown} JOB_NAME=${SLURM_JOB_NAME:-unknown} EXIT_STATUS=$status" >&2
fi
exit "$status"
