#!/bin/bash
#SBATCH --cpus-per-task=10
#SBATCH --error='/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/stdeo/%x-%A.txt'
#SBATCH --job-name='3.extractor_Signatures'
#SBATCH --mem=20G
#SBATCH --export=ALL
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=jwlee230@compbio.unist.ac.kr
/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/bin/SigProfilerExtractor sigprofilerextractor --reference_genome 'GRCh38' --exome --cpu 10 --assignment_cpu 10 'vcf' /BiO/Teach/Standard-Pipeline/08_Mutational_signatures /BiO/Teach/Standard-Pipeline/08_Mutational_signatures
