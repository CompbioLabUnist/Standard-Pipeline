#!/bin/bash
#SBATCH --cpus-per-task=10
#SBATCH --error='/BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/stdeo/%x-%A.txt'
#SBATCH --job-name='1-3.MarkDup_C001_TT'
#SBATCH --mem=20G
#SBATCH --export=ALL
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=jwlee230@compbio.unist.ac.kr
/BiO/Share/Tools/gatk-4.6.1.0/gatk MarkDuplicatesSpark --input /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TT.Sort.bam --output /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TT.Sort.MarkDuplicates.bam --reference /BiO/Share/Tools/gatk-bundle/hg38/Homo_sapiens_assembly38.fasta --metrics-file /BiO/Teach/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/C001_TT.Sort.MarkDuplicates.metrics --duplicate-tagging-policy 'OpticalOnly' --tmp-dir /BiO/Temp -- --spark-master 'local[10]' --spark-verbosity 'INFO'
