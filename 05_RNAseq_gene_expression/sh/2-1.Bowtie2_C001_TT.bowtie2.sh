#!/bin/bash
#SBATCH --cpus-per-task=10
#SBATCH --error='/BiO/Teach/Standard-Pipeline/05_RNAseq_gene_expression/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/05_RNAseq_gene_expression/stdeo/%x-%A.txt'
#SBATCH --job-name='2-1.Bowtie2_C001_TT.bowtie2'
#SBATCH --mem=20G
#SBATCH --export=ALL
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=jwlee230@compbio.unist.ac.kr
/BiO/Share/Tools/RSEM-1.3.3/rsem-calculate-expression --num-threads 10 --calc-pme --calc-ci --bowtie2 --bowtie2-path /BiO/Share/Tools/bowtie2-2.5.4-linux-x86_64 --output-genome-bam --sort-bam-by-coordinate --estimate-rspd --time --paired-end /BiO/Store/UNIST-ApocrineCarcinoma-SMC-2021-04/WTS/C001_TT_RNA_R1.fastq.gz /BiO/Store/UNIST-ApocrineCarcinoma-SMC-2021-04/WTS/C001_TT_RNA_R2.fastq.gz /BiO/Teach/Standard-Pipeline/05_RNAseq_gene_expression/hg38 /BiO/Teach/Standard-Pipeline/05_RNAseq_gene_expression/C001_TT.bowtie2
