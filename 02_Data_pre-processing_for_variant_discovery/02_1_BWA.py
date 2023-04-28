#!/usr/bin/env python3
"""
01_1_FastQC.py: Quality check with FastQC
"""
import argparse
import configparser
import os

parser = argparse.ArgumentParser()

parser.add_argument("input", help="FASTQ file", nargs=2)
parser.add_argument("output", help="Output BAM directory", default=os.getcwd())
parser.add_argument("-c", "--config", help="config INI file", default="../config.ini")

args = parser.parse_args()

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(args.config)

args.input.sort()
name = args.output.split(".")[0]

with open(f"BWA_{name}.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"bwa mem -M -t {config['DEFAULT']['threads']} -R '@RG\\tID:{name}\\tPL:ILLUMINA\\tLB:{name}\\tSM:{name}\\tCN:UNIST' -v 3 {config['REFERENCES']['fasta']} {args.input[0]} {args.input[0]} | samtools view -b -h --threads {config['DEFAULT']['threads']} --reference {config['REFERENCES']['fasta']} --output {args.output}")

os.system(f"sbatch --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='BWA_{name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL BWA_{name}.sh")
