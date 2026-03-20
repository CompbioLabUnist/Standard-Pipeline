#!/bin/bash
#SBATCH --cpus-per-task=10
#SBATCH --error='/BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/stdeo/%x-%A.txt'
#SBATCH --job-name='1-4.BQSR_C001_TN'
#SBATCH --mem=20G
#SBATCH --export=ALL
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=jwlee230@compbio.unist.ac.kr
/BiO/Share/Tools/gatk-4.6.1.0/gatk BaseRecalibrator --input /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TN.Sort.MarkDuplicates.bam --reference /BiO/Share/Tools/gatk-bundle/hg38/Homo_sapiens_assembly38.fasta --output /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TN.Sort.MarkDuplicates.BQSR.table --create-output-bam-index true --known-sites /BiO/Share/Tools/gatk-bundle/hg38/1000G_phase1.snps.high_confidence.hg38.vcf --known-sites /BiO/Share/Tools/gatk-bundle/hg38/1000G_omni2.5.hg38.vcf.gz --known-sites /BiO/Share/Tools/gatk-bundle/hg38/Homo_sapiens_assembly38.dbsnp138.vcf --known-sites /BiO/Share/Tools/gatk-bundle/hg38/Mills_and_1000G_gold_standard.indels.hg38.vcf
