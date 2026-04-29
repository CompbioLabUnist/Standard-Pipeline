#!/bin/bash
#SBATCH --cpus-per-task=10
#SBATCH --error='/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/stdeo/%x-%A.txt'
#SBATCH --job-name='1.install_reference_Signatures'
#SBATCH --mem=20G
#SBATCH --export=ALL
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=jwlee230@compbio.unist.ac.kr
/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/bin/SigProfilerMatrixGenerator install GRCh38
rm -rfv /BiO/Teach/Standard-Pipeline/08_Mutational_signatures/input
mkdir -p /BiO/Teach/Standard-Pipeline/08_Mutational_signatures/input
ln -sfv /BiO/Teach/Standard-Pipeline/03_Somatic_short_variant_discovery/*.PASS.vcf /BiO/Teach/Standard-Pipeline/08_Mutational_signatures/input
