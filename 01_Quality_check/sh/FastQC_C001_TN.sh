#!/bin/bash
#SBATCH --cpus-per-task=10
#SBATCH --error='/BiO/Teach/Standard-Pipeline/01_Quality_check/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/01_Quality_check/stdeo/%x-%A.txt'
#SBATCH --job-name='FastQC_C001_TN'
#SBATCH --mem=20G
#SBATCH --export=ALL
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=jwlee230@compbio.unist.ac.kr
/BiO/Share/Tools/FastQC_v0.12.1/fastqc --outdir /BiO/Teach/Standard-Pipeline/01_Quality_check --format fastq --noextract --threads 10 /BiO/Store/UNIST-ApocrineCarcinoma-SMC-2021-04/WES/C001_TN_DNA_R1.fastq.gz
status=$?
if [ "$status" -ne 0 ]; then
    echo "SLURM job failed: UID=${UID:-$(id -u)} JOB_ID=${SLURM_JOB_ID:-unknown} JOB_NAME=${SLURM_JOB_NAME:-unknown} EXIT_STATUS=$status" >&2
fi
exit "$status"
