#!/bin/bash
#SBATCH --cpus-per-task=10
#SBATCH --error='/BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/stdeo/%x-%A.txt'
#SBATCH --job-name='3.normal_database_PureCN'
#SBATCH --mem=20G
#SBATCH --export=ALL
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=jwlee230@compbio.unist.ac.kr
rm -fv /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/normal_coverages.list
echo /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/C001_TN.Sort.MarkDuplicates.BQSR_coverage_loess.txt.gz >> /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/normal_coverages.list
echo /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/C002_TN.Sort.MarkDuplicates.BQSR_coverage_loess.txt.gz >> /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/normal_coverages.list
echo /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/C003_TN.Sort.MarkDuplicates.BQSR_coverage_loess.txt.gz >> /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/normal_coverages.list
echo /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/K001_BU.Sort.MarkDuplicates.BQSR_coverage_loess.txt.gz >> /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/normal_coverages.list
echo /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/K002_BU.Sort.MarkDuplicates.BQSR_coverage_loess.txt.gz >> /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/normal_coverages.list
echo /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/K003_BU.Sort.MarkDuplicates.BQSR_coverage_loess.txt.gz >> /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/normal_coverages.list
/BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/conda/bin/Rscript --vanilla /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/conda/lib/R/library/PureCN/extdata/NormalDB.R --coverage-files /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery/normal_coverages.list --genome 'hg38' --out-dir /BiO/Teach/Standard-Pipeline/09_Somatic_copy_number_variant_discovery --force
