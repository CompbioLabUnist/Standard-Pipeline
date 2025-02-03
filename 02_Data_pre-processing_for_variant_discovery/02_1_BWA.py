#!/usr/bin/env python3
"""
02_1_BWA.py: Mapping with BWA
"""
import argparse
import os
import sys
from pipeline_utils import PipelineManagerBase

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class PipelineManager(PipelineManagerBase):
    def __init__(self, input_files, output, config_file, dryrun):
        super().__init__(config_file, dryrun, output_dir=output)
        self.input_files = sorted(input_files)
        self.name = self.input_files[0][self.input_files[0].rfind("/") + 1:self.input_files[0].find("_DNA")]

    def run_bwa(self):
        command = f"{self.config['TOOLS']['bwa']} mem -M -t {self.config['DEFAULT']['threads']} -R '@RG\\tID:{self.name}\\tPL:ILLUMINA\\tLB:{self.name}\\tSM:{self.name}\\tCN:UNIST' -v 3 {self.config['REFERENCES']['fasta']} {self.input_files[0]} {self.input_files[0]} | {self.config['TOOLS']['samtools']} view --bam --with-header --threads {self.config['DEFAULT']['threads']} --reference {self.config['REFERENCES']['fasta']} --output {self.output_dir}/{self.name}.bam"
        self.create_sh("BWA", command)
        return self.submit_job("BWA")

    def run_sort(self, dependency_id=None):
        command = f"{self.config['TOOLS']['samtools']} sort -l 9 --threads {self.config['DEFAULT']['threads']} --reference {self.config['REFERENCES']['fasta']} --write-index -o {self.output_dir}/{self.name}.Sort.bam {self.output_dir}/{self.name}.bam"
        self.create_sh("Sort", command)
        return self.submit_job("Sort", dependency_id=dependency_id)

    def run_mark_duplicates(self, dependency_id=None):
        command = f"{self.config['TOOLS']['gatk']} MarkDuplicatesSpark --input {self.output_dir}/{self.name}.Sort.bam --output {self.output_dir}/{self.name}.Sort.MarkDuplicates.bam --reference {self.config['REFERENCES']['fasta']} --metrics-file {self.output_dir}/{self.name}.Sort.MarkDuplicates.metrics --duplicate-tagging-policy 'OpticalOnly' -- --spark-master 'local[{self.config['DEFAULT']['threads']}]' --spark-verbosity 'INFO'"
        self.create_sh("MarkDup", command)
        return self.submit_job("MarkDup", dependency_id=dependency_id)

    def run_bqsr(self, dependency_id=None):
        known_sites = " ".join([f"--known-sites {site}" for site in self.config["REFERENCES"]["sites"].split(" ")])
        command = f"{self.config['TOOLS']['gatk']} BaseRecalibrator --input {self.output_dir}/{self.name}.Sort.MarkDuplicates.bam --reference {self.config['REFERENCES']['fasta']} --output {self.output_dir}/{self.name}.Sort.MarkDuplicates.BQSR.table --create-output-bam-index true {known_sites}"
        self.create_sh("BQSR", command)
        return self.submit_job("BQSR", dependency_id=dependency_id)

    def run_apply_bqsr(self, dependency_id=None):
        command = f"{self.config['TOOLS']['gatk']} ApplyBQSR --bqsr-recal-file {self.output_dir}/{self.name}.Sort.MarkDuplicates.BQSR.table --input {self.output_dir}/{self.name}.Sort.MarkDuplicates.bam --output {self.output_dir}/{self.name}.Sort.MarkDuplicates.BQSR.bam --reference {self.config['REFERENCES']['fasta']} --create-output-bam-index true"
        self.create_sh("ApplyBQSR", command)
        return self.submit_job("ApplyBQSR", dependency_id=dependency_id)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="Input FASTQ file", nargs=2)
    parser.add_argument("output", help="Output directory", default=os.getcwd())
    parser.add_argument("-c", "--config", help="config INI file", default="../config.ini")
    parser.add_argument("-n", "--dryrun", help="Don't actually run any recipe; just make .SH only", default=False, action="store_true")

    return parser.parse_args()


def main():
    args = parse_arguments()

    pipeline = PipelineManager(input_files=args.input, output=args.output, config_file=args.config, dryrun=args.dryrun)

    pipeline.create_dir()
    mapping_job_id = pipeline.run_bwa()
    sort_job_id = pipeline.run_sort(dependency_id=mapping_job_id)
    mark_duplicates_job_id = pipeline.run_mark_duplicates(dependency_id=sort_job_id)
    bqsr_job_id = pipeline.run_bqsr(dependency_id=mark_duplicates_job_id)
    pipeline.run_apply_bqsr(dependency_id=bqsr_job_id)


if __name__ == "__main__":
    main()
