#!/bin/bash
/BiO/Share/Tools/gatk-4.6.1.0/gatk Mutect2 --java-options "-XX:+UseSerialGC -Xmx55g" --reference /BiO/Share/Tools/gatk-bundle/hg38/Homo_sapiens_assembly38.fasta --input /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TN.Sort.MarkDuplicates.BQSR.bam --input /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TT.Sort.MarkDuplicates.BQSR.bam --normal-sample C001_TN --output /BiO/Teach/Standard-Pipeline/03_Somatic_short_variant_discovery/C001.vcf --panel-of-normals /BiO/Teach/Standard-Pipeline/03_Somatic_short_variant_discovery/panel_of_normals.vcf.gz--native-pair-hmm-threads 30 --max-mnp-distance 0
status=$?
if [ "$status" -ne 0 ]; then
    echo "SLURM job failed: UID=${UID:-$(id -u)} JOB_ID=${SLURM_JOB_ID:-unknown} JOB_NAME=${SLURM_JOB_NAME:-unknown} EXIT_STATUS=$status" >&2
fi
exit "$status"
