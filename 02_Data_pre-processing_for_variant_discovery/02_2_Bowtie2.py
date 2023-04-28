#!/usr/bin/env python3
"""
02_2_Bowtie2.py: Mapping with Bowtie2
"""
import argparse
import configparser
import os

parser = argparse.ArgumentParser()

parser.add_argument("input", help="FASTQ file", nargs=2)
parser.add_argument("output", help="Output BAM file", default=os.getcwd())
parser.add_argument("-c", "--config", help="config INI file", default="../config.ini")

args = parser.parse_args()

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(args.config)

args.input.sort()
name = args.output.split(".")[0]

with open(f"Bowtie2_{name}.sh", "w") as sh:
    sh.write("#!/bin/bash\n")
    sh.write(f"bowtie2 --threads {config['DEFAULT']['threads']} --rg-id {name} --rg 'ID:{name}' --rg 'PL:ILLUMINA' --rg 'LB:{name}' --rg 'SM:{name}' --rg 'CN:UNIST' --time --qc-filter -x {config['REFERENCES']['fasta'][:-6]} -1 {args.input[0]} -2 {args.input[1]} | samtools view -b -h --threads {config['DEFAULT']['threads']} --reference {config['REFERENCES']['fasta']} --output {args.output}")

os.system(f"sbatch --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='Bowtie2_{name}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL Bowtie2_{name}.sh")
