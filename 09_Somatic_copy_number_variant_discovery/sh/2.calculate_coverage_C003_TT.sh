#!/bin/bash
#SBATCH --cpus-per-task=10
#SBATCH --error='/BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/stdeo/%x-%A.txt'
#SBATCH --job-name='2.calculate_coverage_C003_TT'
#SBATCH --mem=20G
#SBATCH --export=ALL
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=jwlee230@compbio.unist.ac.kr
/BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/conda/bin/Rscript --vanilla /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/conda/lib/R/library/PureCN/extdata/Coverage.R --bam /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C003_TT.Sort.MarkDuplicates.BQSR.bam --intervals /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/baits_hg38_intervals.txt --keep-duplicates --out-dir /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery --cores 10 --seed 123 --force
