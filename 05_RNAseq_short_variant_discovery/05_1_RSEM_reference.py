#!/usr/bin/env python3
"""
05_1_RSEM_reference.py: RSEM - prepare RSEM reference
"""
import argparse
import os
import sys
from pipeline_utils import PipelineManagerBase
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class PipelineManager(PipelineManagerBase):
    def __init__(self, output, config_file, dryrun):
        super().__init__(config_file, dryrun)
        self.output = os.path.realpath(output)
        self.name = self.output.split("/")[-1]
        self.output_dir = os.path.dirname(self.output)

    def run_reference(self, dependency_id=None):
        command = f"{self.config['TOOLS']['rsem_directory']}/rsem-prepare-reference --gtf {self.config['REFERENCES']['ref_gene']} --bowtie2 --bowtie2-path {self.config['TOOLS']['bowtie2']} --star --star-path {self.config['TOOLS']['star']} --num-threads {self.config['DEFAULT']['threads']} {self.config['REFERENCES']['fasta']} {self.output}"
        self.create_sh("Reference", command)
        return self.submit_job("Reference", dependency_id=dependency_id)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("output", help="Output file (location) basename (without extention)")
    parser.add_argument("-c", "--config", help="config INI file", default="../config.ini")
    parser.add_argument("-n", "--dryrun", help="Don't actually run any recipe; just make .SH only", default=False, action="store_true")

    return parser.parse_args()


def main():
    args = parse_arguments()

    pipeline = PipelineManager(output=args.output, config_file=args.config, dryrun=args.dryrun)

    pipeline.create_dir()

    pipeline.run_reference()


if __name__ == "__main__":
    main()
