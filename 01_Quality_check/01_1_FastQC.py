#!/usr/bin/env python3
"""
01_1_FastQC.py: Quality check with FastQC
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
        file_name = os.path.basename(input_files[0])
        self.name = file_name[:file_name.rfind("_DNA")]

    def run_fastqc(self):
        command = f"{self.config['TOOLS']['fastqc']} --outdir {self.output_dir} --format fastq --noextract --threads {self.config['DEFAULT']['threads']} {self.input_files[0]}"
        self.create_sh("FastQC", command)
        return self.submit_job("FastQC")


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="FASTQ file", nargs="+")
    parser.add_argument("-o", "--output", help="Output directory", default=os.getcwd())
    parser.add_argument("-c", "--config", help="config INI file", default="../config.ini")
    parser.add_argument("-n", "--dryrun", help="Don't actually run any recipe; just make .SH only", default=False, action="store_true")

    return parser.parse_args()


def main():
    args = parse_arguments()

    pipeline = PipelineManager(input_files=args.input, output=args.output, config_file=args.config, dryrun=args.dryrun)

    pipeline.create_dir()
    pipeline.run_fastqc()


if __name__ == "__main__":
    main()
