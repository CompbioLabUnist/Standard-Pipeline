#!/usr/bin/env python3
"""
01_1_FastQC.py: Quality check with FastQC
"""
import argparse
import configparser
import os

parser = argparse.ArgumentParser()

parser.add_argument("input", help="FASTQ file", nargs="+")
parser.add_argument("-o", "--output", help="Output directory", default=os.getcwd())
parser.add_argument("-c", "--config", help="config INI file", default="../config.ini")

parser.add_argument("-n", "--dryrun", help="Don't actually run any recipe; just make .SH only", default=False, action="store_true")

args = parser.parse_args()

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(args.config)

for i, f in enumerate(args.input):
    with open(f"FastQC_{i}.sh", "w") as sh:
        sh.write("#!/bin/bash\n")
        sh.write(f"{config['TOOLS']['fastqc']} --outdir {args.output} --format fastq --noextract --threads {config['DEFAULT']['threads']} {f}")

    if not args.dryrun:
        os.system(f"sbatch --chdir=$(realpath .) --cpus-per-task={config['DEFAULT']['threads']} --error='%x-%A.txt' --job-name='FastQC_{i}' --mem={config['DEFAULT']['memory']}G --output='%x-%A.txt' --export=ALL FastQC_{i}.sh")
