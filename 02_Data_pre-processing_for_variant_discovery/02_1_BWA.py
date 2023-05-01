#!/usr/bin/env python3
"""
02_1_BWA.py: Mapping with BWA
"""
import argparse
import configparser
import os
import subprocess

parser = argparse.ArgumentParser()

parser.add_argument("input", help="Input FASTQ file", nargs=2)
parser.add_argument("output", help="Output directory", default=os.getcwd())
parser.add_argument("-c", "--config", help="config INI file", default="../config.ini")

args = parser.parse_args()

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(args.config)

args.input.sort()
name = args.input[0].split("/")[-1].split("_")[0]
args.output = os.path.realpath(args.output)

# Mapping
with open(f"BWA_{name}.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"{config['TOOLS']['bwa']} mem -M -t {config['DEFAULT']['threads']} -R '@RG\\tID:{name}\\tPL:ILLUMINA\\tLB:{name}\\tSM:{name}\\tCN:UNIST' -v 3 {config['REFERENCES']['fasta']} {args.input[0]} {args.input[0]} | {config['TOOLS']['samtools']} view --bam --with-header --threads {config['DEFAULT']['threads']} --reference {config['REFERENCES']['fasta']} --output {args.output}/{name}.bam")

mapping_job_id = subprocess.check_output(f"sbatch --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='BWA_{name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL BWA_{name}.sh", encoding="utf-8", shell=True).split()[-1]

# Sort
with open(f"Sort_{name}.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"{config['TOOLS']['samtools']} sort -l 9 --threads {config['DEFAULT']['threads']} -m {int(config['DEFAULT']['memory']) // int(config['DEFAULT']['threads'])}G --reference {config['REFERENCES']['fasta']} --write-index -o {args.output}/{name}.Sort.bam {args.output}/{name}.bam")

sorting_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{mapping_job_id} --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='Sort_{name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL Sort_{name}.sh", encoding="utf-8", shell=True).split()[-1]

# Mark Duplicates
with open(f"MarkDup_{name}.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"{config['TOOLS']['gatk']} MarkDuplicatesSpark --input {args.output}/{name}.Sort.bam --output {args.output}/{name}.Sort.MarkDuplicates.bam --reference {config['REFERENCES']['fasta']} --metrics-file {args.output}/{name}.Sort.MarkDuplicates.metrics --duplicate-tagging-policy 'OpticalOnly' -- --spark-master 'local[{config['DEFAULT']['threads']}]' --spark-verbosity 'INFO'")

markduplicates_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{sorting_job_id} --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='MarkDup_{name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL MarkDup_{name}.sh", encoding="utf-8", shell=True).split()[-1]

# Base Quality Score Recalibration (BQSR)
with open(f"BQSR_{name}.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"{config['TOOLS']['gatk']} BaseRecalibrator --input {args.output}/{name}.Sort.MarkDuplicates.bam --reference {config['REFERENCES']['fasta']} --output {args.output}/{name}.Sort.MarkDuplicates.BQSR.table --create-output-bam-index true")
    for site in config['REFERENCES']['sites'].split(" "):
        sh.write(f" --known-sites {site}")

BQSR_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{markduplicates_job_id} --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='BQSR_{name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL BQSR_{name}.sh", encoding="utf-8", shell=True).split()[-1]

with open(f"ApplyBQSR_{name}.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"{config['TOOLS']['gatk']} ApplyBQSR --bqsr-recal-file {args.output}/{name}.Sort.MarkDuplicates.BQSR.table --input {args.output}/{name}.Sort.MarkDuplicates.bam --output {args.output}/{name}.Sort.MarkDuplicates.BQSR.bam --reference {config['REFERENCES']['fasta']} --create-output-bam-index true")

ApplyBQSR_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{BQSR_job_id} --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='ApplyBQSR_{name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL ApplyBQSR_{name}.sh", encoding="utf-8", shell=True).split()[-1]
