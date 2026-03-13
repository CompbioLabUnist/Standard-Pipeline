#!/bin/bash
#SBATCH --cpus-per-task=30
#SBATCH --error='/BiO/Teach/Standard-Pipeline/01_Quality_check/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/01_Quality_check/stdeo/%x-%A.txt'
#SBATCH --job-name='FastQC_C001_TN'
#SBATCH --mem=55G
#SBATCH --export=ALL
/BiO/Share/Tools/FastQC_v0.12.1/fastqc --outdir /BiO/Teach/Standard-Pipeline/01_Quality_check --format fastq --noextract --threads 30 /BiO/Store/UNIST-ApocrineCarcinoma-SMC-2021-04/WES/C001_TN_DNA_R1.fastq.gz