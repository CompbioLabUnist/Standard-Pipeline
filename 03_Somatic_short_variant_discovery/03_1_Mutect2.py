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

parser.add_argument("-p", "--PON", help="Panel of normal (optional)", default=False, action="store_true")
parser.add_argument("-n", "--dryrun", help="Don't actually run any recipe; just make .SH only", default=False, action="store_true")

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

    if not args.dryrun:
        mutect_normal_job_id = subprocess.check_output(f"sbatch --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='Mutect_{normal_name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL Mutect_{normal_name}.sh", encoding="utf-8", shell=True).split()[-1]

    with open(f"Filter_{normal_name}.sh", "w") as sh:
        sh.write("#!/bin/bash\n")
        sh.write(f"{config['TOOLS']['gatk']} FilterMutectCalls --reference {config['REFERENCES']['fasta']} --variant {output_directory}/{normal_name}.vcf --output {output_directory}/{normal_name}.filter.vcf")

    if not args.dryrun:
        filter_normal_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{mutect_normal_job_id} --chdir=$(realpath .) --cpus-per-task=1 --error='%x-%A.txt' --job-name='Filter_{normal_name}' --mem={int(config['DEFAULT']['memory']) // int(config['DEFAULT']['threads'])}G --output='%x-%A.txt' --export=ALL Filter_{normal_name}.sh", encoding="utf-8", shell=True).split()[-1]

    with open(f"PASS_{normal_name}.sh", "w") as sh:
        sh.write("#!/bin/bash\n")
        sh.write(f"{config['TOOLS']['awk']} -F '\t' '{{if($0 ~ /\\#/) print; else if($7 == \"PASS\") print}}' {output_directory}/{normal_name}.filter.vcf > {output_directory}/{normal_name}.PASS.vcf")

    if not args.dryrun:
        PASS_normal_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{filter_normal_job_id} --chdir=$(realpath .) --cpus-per-task=1 --error='%x-%A.txt' --job-name='PASS_{normal_name}' --mem={int(config['DEFAULT']['memory']) // int(config['DEFAULT']['threads'])}G --output='%x-%A.txt' --export=ALL PASS_{normal_name}.sh", encoding="utf-8", shell=True).split()[-1]

    with open(f"Index_{normal_name}.sh", "w") as sh:
        sh.write("#!/bin/bash\n")
        sh.write(f"{config['TOOLS']['gatk']} IndexFeatureFile --input {output_directory}/{normal_name}.PASS.vcf --output {output_directory}/{normal_name}.PASS.vcf.idx")

    if not args.dryrun:
        Index_normal_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{PASS_normal_job_id} --chdir=$(realpath .) --cpus-per-task=1 --error='%x-%A.txt' --job-name='Index_{normal_name}' --mem={int(config['DEFAULT']['memory']) // int(config['DEFAULT']['threads'])}G --output='%x-%A.txt' --export=ALL Index_{normal_name}.sh", encoding="utf-8", shell=True).split()[-1]

    with open("DB.sh", "w") as sh:
        sh.write("#!/bin/bash\n")
        sh.write(f"{config['TOOLS']['gatk']} GenomicsDBImport --reference {config['REFERENCES']['fasta']} --genomicsdb-workspace-path {output_directory}/DB --variant {output_directory}/{normal_name}.PASS.vcf --reader-threads {config['DEFAULT']['threads']} --max-num-intervals-to-import-in-parallel {config['DEFAULT']['threads']} --overwrite-existing-genomicsdb-workspace true")

    if not args.dryrun:
        DB_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{Index_normal_job_id} --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='DB_{normal_name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL DB_{normal_name}.sh", encoding="utf-8", shell=True).split()[-1]

    with open("PON.sh", "w") as sh:
        sh.write("#!/bin/bash\n")
        sh.write(f"{config['TOOLS']['gatk']} CreateSomaticPanelOfNormals --reference {config['REFERENCES']['fasta']} --variant 'gendb://{output_directory}/DB' --output {output_directory}/PON.vcf.gz")

    if not args.dryrun:
        PON_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{DB_job_id} --chdir=$(realpath .) --cpus-per-task=1 --error='%x-%A.txt' --job-name='PON_{normal_name}' --mem={int(config['DEFAULT']['memory']) // int(config['DEFAULT']['threads'])}G --output='%x-%A.txt' --export=ALL PON_{normal_name}.sh", encoding="utf-8", shell=True).split()[-1]

if args.PON:
    with open(f"Mutect_{tumor_name}.sh", "w") as sh:
        sh.write("#!/bin/bash\n")
        sh.write(f"{config['TOOLS']['gatk']} Mutect2 --reference {config['REFERENCES']['fasta']} --input {args.normal} --input {args.tumor} --normal-sample {normal_name} --output {output_directory}/{tumor_name}.vcf --panel-of-normals {output_directory}/PON.vcf.gz --native-pair-hmm-threads {config['DEFAULT']['threads']}")

    if not args.dryrun:
        mutect_tumor_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{PON_job_id} --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='Mutect_{tumor_name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL Mutect_{tumor_name}.sh", encoding="utf-8", shell=True).split()[-1]
else:
    with open(f"Mutect_{tumor_name}.sh", "w") as sh:
        sh.write("#!/bin/bash\n")
        sh.write(f"{config['TOOLS']['gatk']} Mutect2 --reference {config['REFERENCES']['fasta']} --input {args.normal} --input {args.tumor} --normal-sample {normal_name} --output {output_directory}/{tumor_name}.vcf --native-pair-hmm-threads {config['DEFAULT']['threads']}")

    if not args.dryrun:
        mutect_tumor_job_id = subprocess.check_output(f"sbatch --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='Mutect_{tumor_name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL Mutect_{tumor_name}.sh", encoding="utf-8", shell=True).split()[-1]

with open(f"Filter_{tumor_name}.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"{config['TOOLS']['gatk']} FilterMutectCalls --reference {config['REFERENCES']['fasta']} --variant {output_directory}/{tumor_name}.vcf --output {output_directory}/{tumor_name}.filter.vcf")

if not args.dryrun:
    filter_tumor_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{mutect_tumor_job_id} --chdir=$(realpath .) --cpus-per-task=1 --error='%x-%A.txt' --job-name='Filter_{tumor_name}' --mem={int(config['DEFAULT']['memory']) // int(config['DEFAULT']['threads'])}G --output='%x-%A.txt' --export=ALL Filter_{tumor_name}.sh", encoding="utf-8", shell=True).split()[-1]

with open(f"PASS_{tumor_name}.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"{config['TOOLS']['awk']} -F '\t' '{{if($0 ~ /\\#/) print; else if($7 == \"PASS\") print}}' {output_directory}/{tumor_name}.filter.vcf > {output_directory}/{tumor_name}.PASS.vcf")

if not args.dryrun:
    PASS_tumor_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{filter_tumor_job_id} --chdir=$(realpath .) --cpus-per-task=1 --error='%x-%A.txt' --job-name='PASS_{tumor_name}' --mem={int(config['DEFAULT']['memory']) // int(config['DEFAULT']['threads'])}G --output='%x-%A.txt' --export=ALL PASS_{tumor_name}.sh", encoding="utf-8", shell=True).split()[-1]

with open(f"Index_{tumor_name}.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"{config['TOOLS']['gatk']} IndexFeatureFile --input {output_directory}/{tumor_name}.PASS.vcf --output {output_directory}/{tumor_name}.PASS.vcf.idx")

if not args.dryrun:
    Index_tumor_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{PASS_tumor_job_id} --chdir=$(realpath .) --cpus-per-task=1 --error='%x-%A.txt' --job-name='Index_{tumor_name}' --mem={int(config['DEFAULT']['memory']) // int(config['DEFAULT']['threads'])}G --output='%x-%A.txt' --export=ALL Index_{tumor_name}.sh", encoding="utf-8", shell=True).split()[-1]

with open(f"MAF_{tumor_name}.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"{config['TOOLS']['vcf2maf']} --vep-path {config['TOOLS']['vep']} --vep-data {config['TOOLS']['vep']} --vep-forks {config['DEFAULT']['threads']} --ncbi-build 'GRCh38' --input-vcf {output_directory}/{tumor_name}.PASS.vcf --output {output_directory}/{tumor_name}.PASS.maf --tumor-id {tumor_name} --normal-id {normal_name} --ref-fasta {config['REFERENCES']['fasta']} --vep-overwrite")

if not args.dryrun:
    MAF_job_id = subprocess.check_output(f"sbatch --dependency=afterok:{Index_tumor_job_id} --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='MAF_{tumor_name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL MAF_{tumor_name}.sh", encoding="utf-8", shell=True).split()[-1]
