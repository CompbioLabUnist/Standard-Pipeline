#!/bin/bash
#SBATCH --cpus-per-task=30
#SBATCH --error='/BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/stdeo/%x-%A.txt'
#SBATCH --job-name='1-1.BWA_C001_TN'
#SBATCH --mem=55G
#SBATCH --export=ALL
/BiO/Share/Tools/bwa-0.7.18/bwa mem -M -t 30 -R '@RG\tID:C001_TN\tPL:ILLUMINA\tLB:C001_TN\tSM:C001_TN\tCN:UNIST' -v 3 /BiO/Share/Tools/gatk-bundle/hg38/Homo_sapiens_assembly38.fasta /BiO/Store/UNIST-ApocrineCarcinoma-SMC-2021-04/WES/merge/C001_TN_DNA_R1.fastq.gz /BiO/Store/UNIST-ApocrineCarcinoma-SMC-2021-04/WES/merge/C001_TN_DNA_R2.fastq.gz | /BiO/Share/Tools/samtools-1.21/samtools view --bam --with-header --threads 30 --reference /BiO/Share/Tools/gatk-bundle/hg38/Homo_sapiens_assembly38.fasta --output /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TN.bam