#!/bin/bash
#SBATCH --cpus-per-task=10
#SBATCH --error='/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/stdeo/%x-%A.txt'
#SBATCH --output='/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/stdeo/%x-%A.txt'
#SBATCH --job-name='4.plotting_Signatures'
#SBATCH --mem=20G
#SBATCH --export=ALL
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=jwlee230@compbio.unist.ac.kr
/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/bin/SigProfilerPlotting plotSBS --savefig_format 'png' --dpi 600 /BiO/Teach/Standard-Pipeline/08_Mutational_signatures/SBS/Signatures.SBS96.exome /BiO/Teach/Standard-Pipeline/08_Mutational_signatures/Plot Signatures '96'
/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/bin/SigProfilerPlotting plotSBS --savefig_format 'png' --dpi 600 /BiO/Teach/Standard-Pipeline/08_Mutational_signatures/SBS/Signatures.SBS6.exome /BiO/Teach/Standard-Pipeline/08_Mutational_signatures/'Plot' Signatures '6'
/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/bin/SigProfilerPlotting plotDBS --savefig_format 'png' --dpi 600 /BiO/Teach/Standard-Pipeline/08_Mutational_signatures/DBS/Signatures.DBS78.exome /BiO/Teach/Standard-Pipeline/08_Mutational_signatures/'Plot' Signatures '78'
/BiO/Teach/Standard-Pipeline/08_Mutational_signatures/bin/SigProfilerPlotting plotID --savefig_format 'png' --dpi 600 /BiO/Teach/Standard-Pipeline/08_Mutational_signatures/ID/Signatures.ID28.exome /BiO/Teach/Standard-Pipeline/08_Mutational_signatures/'Plot' Signatures '28'
status=$?
if [ "$status" -ne 0 ]; then
    echo "SLURM job failed: UID=${UID:-$(id -u)} JOB_ID=${SLURM_JOB_ID:-unknown} JOB_NAME=${SLURM_JOB_NAME:-unknown} EXIT_STATUS=$status" >&2
fi
exit "$status"
