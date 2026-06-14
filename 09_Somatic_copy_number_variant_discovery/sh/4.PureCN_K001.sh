#!/bin/bash
#SBATCH --cpus-per-task=10
#SBATCH --error='/BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/stdeo/%x-%A.txt'
#SBATCH --job-name='4.PureCN_K001'
#SBATCH --mem=20G
#SBATCH --export=ALL
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=jwlee230@compbio.unist.ac.kr
/BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/conda/bin/Rscript --vanilla /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/conda/lib/R/library/PureCN/extdata/PureCN.R --sampleid K001 --normal /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/K001_BU.Sort.MarkDuplicates.BQSR_coverage_loess.txt.gz --tumor /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/K001_TT.Sort.MarkDuplicates.BQSR_coverage_loess.txt.gz --normaldb /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/normalDB_hg38.rds --genome 'hg38' --intervals /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/baits_hg38_intervals.txt --post-optimize --out /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery --seed 123 --parallel --cores 10 --force
status=$?
if [ "$status" -ne 0 ]; then
    echo "SLURM job failed: UID=${UID:-$(id -u)} JOB_ID=${SLURM_JOB_ID:-unknown} JOB_NAME=${SLURM_JOB_NAME:-unknown} EXIT_STATUS=$status" >&2
fi
exit "$status"
