#!/bin/bash
#SBATCH --cpus-per-task=10
#SBATCH --error='/BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/stdeo/%x-%A.txt'
#SBATCH --job-name='1.get_interval_PureCN'
#SBATCH --mem=20G
#SBATCH --export=ALL
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=jwlee230@compbio.unist.ac.kr
/BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/conda/bin/Rscript --vanilla /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/conda/lib/R/library/PureCN/extdata/IntervalFile.R --in-file /BiO/Share/Tools/gatk-bundle/hg38/Illumina_Exome_TargetedRegions_v1.2.hg38.bed --fasta /BiO/Share/Tools/gatk-bundle/hg38/Homo_sapiens_assembly38.fasta --genome 'hg38' --out-file /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/baits_hg38_intervals.txt --force
status=$?
if [ "$status" -ne 0 ]; then
    echo "SLURM job failed: UID=${UID:-$(id -u)} JOB_ID=${SLURM_JOB_ID:-unknown} JOB_NAME=${SLURM_JOB_NAME:-unknown} EXIT_STATUS=$status" >&2
fi
exit "$status"
