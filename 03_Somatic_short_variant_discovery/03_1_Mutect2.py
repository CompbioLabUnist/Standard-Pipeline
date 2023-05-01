#!/usr/bin/env python3
"""
03_1_Mutect2.py: Mutect2 - Call somatic SNVs and indels via local assembly of haplotypes
"""
import argparse
import configparser
import os
import subprocess

parser = argparse.ArgumentParser()

parser.add_argument("normal", help="Normal BAM file")
parser.add_argument("tumor", help="Tumor BAM file")
parser.add_argument("output", help="Output MAF file")
parser.add_argument("-c", "--config", help="config INI file", default="../config.ini")

parser.add_argument("-p", "--PON", help="Panel of normal (optional)", default=True, action="store_true")

args = parser.parse_args()

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(args.config)

args.normal = os.path.realpath(args.normal)
args.tumor = os.path.realpath(args.tumor)
args.output = os.path.realpath(args.output)

normal_name = args.normal.split("/")[-1].split(".")[0]
tumor_name = args.tumor.split("/")[-1].split(".")[0]
name = args.output.split("/")[-1].split(".")[0]
output_directory = os.path.dirname(args.output)

# Panel of Normal
if args.PON:
    with open(f"Mutect_{normal_name}.sh", "w") as sh:
        sh.write("#!/bin/bash\n")
        sh.write(f"{config['TOOLS']['gatk']} Mutect2 --reference {config['REFERENCES']['fasta']} --input {args.normal} --output {output_directory}/{normal_name}.vcf --native-pair-hmm-threads {config['DEFAULT']['threads']}")

    mutect_normal_job_id = subprocess.check_output(f"sbatch --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='Mutect_{normal_name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL Mutect_{normal_name}.sh", encoding="utf-8", shell=True).split()[-1]

    with open(f"Filter_{normal_name}.sh", "w") as sh:
        sh.write("#!/bin/bash\n")
        sh.write("{config['TOOLS']['gatk']} FilterMutectCalls --reference {config['REFERENCES']['fasta']} --variant {output_directory}/{normal_name}.vcf --output {output_directory}/{normal_name}.filter.vcf")

    filter_normal_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{mutect_normal_job_id} --chdir=$(realpath .) --cpus-per-task=1 --error='%x-%A.txt' --job-name='Filter_{normal_name}' --mem={int(config['DEFAULT']['memory']) // int(config['DEFAULT']['threads'])}G --output='%x-%A.txt' --export=ALL Filter_{normal_name}.sh", encoding="utf-8", shell=True).split()[-1]

    with open(f"PASS_{normal_name}.sh", "w") as sh:
        sh.write("#!/bin/bash\n")
        sh.write(f"{config['TOOLS']['awk']} -F '\t' '{{if($0 ~ /\\#/) print; else if($7 == \"PASS\") print}}' {output_directory}/{normal_name}.filter.vcf > {output_directory}/{normal_name}.PASS.vcf")

    PASS_normal_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{filter_normal_job_id} --chdir=$(realpath .) --cpus-per-task=1 --error='%x-%A.txt' --job-name='PASS_{normal_name}' --mem={int(config['DEFAULT']['memory']) // int(config['DEFAULT']['threads'])}G --output='%x-%A.txt' --export=ALL PASS_{normal_name}.sh", encoding="utf-8", shell=True).split()[-1]
