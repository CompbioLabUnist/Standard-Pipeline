#!/bin/bash
/BiO/Share/Tools/gatk-4.6.1.0/gatk CreateSomaticPanelOfNormals --java-options "-XX:+UseSerialGC -Xmx55g" --reference /BiO/Share/Tools/gatk-bundle/hg38/Homo_sapiens_assembly38.fasta --variant 'gendb:///BiO/Teach/Standard-Pipeline/03_Somatic_short_variant_discovery/DB' --output /BiO/Teach/Standard-Pipeline/03_Somatic_short_variant_discovery/panel_of_normals.vcf.gz
status=$?
if [ "$status" -ne 0 ]; then
    echo "SLURM job failed: UID=${UID:-$(id -u)} JOB_ID=${SLURM_JOB_ID:-unknown} JOB_NAME=${SLURM_JOB_NAME:-unknown} EXIT_STATUS=$status" >&2
fi
exit "$status"
