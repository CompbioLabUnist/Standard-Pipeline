#!/usr/bin/env python3
"""
02_2_Bowtie2.py: Mapping with Bowtie2
"""
import argparse
import configparser
import os
import subprocess

parser = argparse.ArgumentParser()

parser.add_argument("input", help="Input FASTQ file", nargs=2)
parser.add_argument("output", help="Output directory", default=os.getcwd())
parser.add_argument("-c", "--config", help="config INI file", default="../config.ini")

parser.add_argument("-n", "--dryrun", help="Don't actually run any recipe; just make .SH only", default=False, action="store_true")

args = parser.parse_args()

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(args.config)

args.input.sort()
name = args.input[0].split("/")[-1].split("_")[0]
args.output = os.path.realpath(args.output)

with open(f"Bowtie2_{name}.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"{config['TOOLS']['bowtie2']} --threads {config['DEFAULT']['threads']} --rg-id {name} --rg 'ID:{name}' --rg 'PL:ILLUMINA' --rg 'LB:{name}' --rg 'SM:{name}' --rg 'CN:UNIST' --time --qc-filter -x {config['REFERENCES']['fasta'][:-6]} -1 {args.input[0]} -2 {args.input[1]} | {config['TOOLS']['samtools']} view --bam --with-header --threads {config['DEFAULT']['threads']} --reference {config['REFERENCES']['fasta']} --output {args.output}/{name}.Bowtie2.bam")

if not args.dryrun:
    mapping_job_id = subprocess.check_output(f"sbatch --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='Bowtie2_{name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL Bowtie2_{name}.sh", encoding="utf-8", shell=True).split()[-1]

# Sort
with open(f"Sort_{name}.Bowtie2.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"{config['TOOLS']['samtools']} sort -l 9 --threads {config['DEFAULT']['threads']} -m {int(config['DEFAULT']['memory']) // int(config['DEFAULT']['threads'])}G --reference {config['REFERENCES']['fasta']} --write-index -o {args.output}/{name}.Bowtie2.Sort.bam {args.output}/{name}.Bowtie2.bam")

if not args.dryrun:
    sorting_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{mapping_job_id} --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='Sort_{name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL Sort_{name}.Bowtie2.sh", encoding="utf-8", shell=True).split()[-1]

# Mark Duplicates
with open(f"MarkDup_{name}.Bowtie2.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"{config['TOOLS']['gatk']} MarkDuplicatesSpark --input {args.output}/{name}.Bowtie2.Sort.bam --output {args.output}/{name}.Bowtie2.Sort.MarkDuplicates.bam --reference {config['REFERENCES']['fasta']} --metrics-file {args.output}/{name}.Sort.MarkDuplicates.metrics --duplicate-tagging-policy 'OpticalOnly' -- --spark-master 'local[{config['DEFAULT']['threads']}]' --spark-verbosity 'INFO'")

if not args.dryrun:
    markduplicates_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{sorting_job_id} --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='MarkDup_{name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL MarkDup_{name}.Bowtie2.sh", encoding="utf-8", shell=True).split()[-1]

# Base Quality Score Recalibration (BQSR)
with open(f"BQSR_{name}.Bowtie2.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"{config['TOOLS']['gatk']} BaseRecalibrator --input {args.output}/{name}.Bowtie2.Sort.MarkDuplicates.bam --reference {config['REFERENCES']['fasta']} --output {args.output}/{name}.Bowtie2.Sort.MarkDuplicates.BQSR.table --create-output-bam-index true")
    for site in config['REFERENCES']['sites'].split(" "):
        sh.write(f" --known-sites {site}")

if not args.dryrun:
    BQSR_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{markduplicates_job_id} --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='BQSR_{name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL BQSR_{name}.Bowtie2.sh", encoding="utf-8", shell=True).split()[-1]

with open(f"ApplyBQSR_{name}.Bowtie2.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"{config['TOOLS']['gatk']} ApplyBQSR --bqsr-recal-file {args.output}/{name}.Bowtie2.Sort.MarkDuplicates.BQSR.table --input {args.output}/{name}.Bowtie2.Sort.MarkDuplicates.bam --output {args.output}/{name}.Bowtie2.Sort.MarkDuplicates.BQSR.bam --reference {config['REFERENCES']['fasta']} --create-output-bam-index true")

if not args.dryrun:
    ApplyBQSR_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{BQSR_job_id} --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='ApplyBQSR_{name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL ApplyBQSR_{name}.Bowtie2.sh", encoding="utf-8", shell=True).split()[-1]
