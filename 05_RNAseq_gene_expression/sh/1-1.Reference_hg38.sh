#!/bin/bash
#SBATCH --cpus-per-task=10
#SBATCH --error='/BiO/Teach/Standard-Pipeline/05_RNAseq_gene_expression/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/05_RNAseq_gene_expression/stdeo/%x-%A.txt'
#SBATCH --job-name='1-1.Reference_hg38'
#SBATCH --mem=20G
#SBATCH --export=ALL
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=jwlee230@compbio.unist.ac.kr
/BiO/Share/Tools/RSEM-1.3.3/rsem-prepare-reference --gtf /BiO/Share/Tools/gatk-bundle/hg38/hg38.refGene.gtf --bowtie2 --bowtie2-path /BiO/Share/Tools/bowtie2-2.5.4-linux-x86_64 --star --star-path /BiO/Share/Tools/STAR_2.7.11b/Linux_x86_64_static --num-threads 10 /BiO/Share/Tools/gatk-bundle/hg38/Homo_sapiens_assembly38.fasta /BiO/Teach/Standard-Pipeline/05_RNAseq_gene_expression/hg38
