#!/bin/bash
/usr/bin/awk -F '	' '{if($0 ~ /\#/) print; else if($7 == "PASS") print}' /BiO/Teach/Standard-Pipeline/03_Somatic_short_variant_discovery/C001.filter.vcf > /BiO/Teach/Standard-Pipeline/03_Somatic_short_variant_discovery/C001.PASS.vcf
status=$?
if [ "$status" -ne 0 ]; then
    echo "SLURM job failed: UID=${UID:-$(id -u)} JOB_ID=${SLURM_JOB_ID:-unknown} JOB_NAME=${SLURM_JOB_NAME:-unknown} EXIT_STATUS=$status" >&2
fi
exit "$status"
