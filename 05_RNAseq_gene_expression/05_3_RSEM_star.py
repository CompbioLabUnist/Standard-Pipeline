#!/usr/bin/env python3
"""
05_3_RSEM_star.py: RSEM - align reads with STAR
"""
import argparse
import os
import sys
from pipeline_utils import PipelineManagerBase
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class PipelineManager(PipelineManagerBase):
    def __init__(self, input_file_list, reference, output, config_file, dryrun):
        super().__init__(config_file, dryrun)
        self.input = list(map(os.path.realpath, sorted(input_file_list)))
        self.reference = os.path.realpath(reference)
        self.reference = self.reference[:self.reference.rfind(".")]
        self.output = os.path.realpath(output)
        self.name = self.output.split("/")[-1]

    def run_star(self, dependency_id=None):
        command = f"{self.config['TOOLS']['rsem_directory']}/rsem-calculate-expression --num-threads {self.config['DEFAULT']['threads']} --calc-pme --calc-ci --star --star-path {os.path.dirname(self.config['TOOLS']['star'])} --star-gzipped-read-file --output-genome-bam --sort-bam-by-coordinate --estimate-rspd --time --paired-end {self.input[0]} {self.input[1]} {self.reference} {self.output}"

        self.create_sh("3-1.star", command)
        return self.submit_job("3-1.star", dependency_id=dependency_id)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="Input FASTQ files", nargs=2)
    parser.add_argument("reference", help="Reference GRP file")
    parser.add_argument("output", help="Output file basename")
    parser.add_argument("-c", "--config", help="config INI file", default="../config.ini")
    parser.add_argument("-n", "--dryrun", help="Don't actually run any recipe; just make .SH only", default=False, action="store_true")

    return parser.parse_args()


def main():
    args = parse_arguments()

    pipeline = PipelineManager(input_file_list=args.input, reference=args.reference, output=args.output, config_file=args.config, dryrun=args.dryrun)

    pipeline.create_dir()

    pipeline.run_star()


if __name__ == "__main__":
    main()
