#!/bin/bash
#SBATCH --cpus-per-task=10
#SBATCH --error='/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/stdeo/%x-%A.txt'
#SBATCH --job-name='2.matrix_generator_Signatures'
#SBATCH --mem=20G
#SBATCH --export=ALL
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=jwlee230@compbio.unist.ac.kr
/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/bin/SigProfilerMatrixGenerator matrix_generator --exome --output_directory /BiO/Teach/Standard-Pipeline/08_Mutational_signatures Signatures 'GRCh38' '/BiO/Teach/Standard-Pipeline/08_Mutational_signatures'
status=$?
if [ "$status" -ne 0 ]; then
    echo "SLURM job failed: UID=${UID:-$(id -u)} JOB_ID=${SLURM_JOB_ID:-unknown} JOB_NAME=${SLURM_JOB_NAME:-unknown} EXIT_STATUS=$status" >&2
fi
exit "$status"
