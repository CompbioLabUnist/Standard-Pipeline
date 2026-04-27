"""
09_2_prepare_pureCN.py: PureCN
"""
import argparse
import os
import os.path
import sys
from pipeline_utils import PipelineManagerBase
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class PipelineManager(PipelineManagerBase):
    def __init__(self, input_list, output, config_file, dryrun):
        super().__init__(config_file, dryrun)
        self.input_list = input_list[:]
        self.input = os.path.realpath(input_list[0])
        self.output = os.path.realpath(output)
        self.name = "PureCN"

    def get_interval(self, dependency_id=None):
        self.name = "PureCN"
        command = f"{os.path.realpath('./conda/bin/Rscript')} --vanilla {os.path.realpath('./conda/lib/R/library/PureCN/extdata/IntervalFile.R')} --in-file {self.config['REFERENCES']['region_bed']} --fasta {self.config['REFERENCES']['fasta']} --genome 'hg38' --out-file {self.output}/baits_hg38_intervals.txt --force"

        self.create_sh("1.get_interval", command)
        return self.submit_job("1.get_interval", dependency_id=dependency_id)

    def calculate_coverage(self, input_file, dependency_id=None):
        self.name = os.path.basename(input_file).split(".")[0]

        command = f"{os.path.realpath('./conda/bin/Rscript')} --vanilla {os.path.realpath('./conda/lib/R/library/PureCN/extdata/Coverage.R')} --bam {input_file} --intervals {self.output}/baits_hg38_intervals.txt --keep-duplicates --out-dir {self.output} --cores {self.config['DEFAULT']['threads']} --seed 123 --force"

        self.create_sh("2.calculate_coverage", command)
        return self.submit_job("2.calculate_coverage", dependency_id=dependency_id)

    def normal_database(self, dependency_id=None):
        self.name = "PureCN"
        command = f"rm -fv {self.output}/normal_coverages.list\n"

        for input_file in self.input_list:
            if "TT" in input_file:
                continue
            command += f"echo {self.output}/{os.path.basename(input_file).replace('.bam', '_coverage_loess.txt.gz')} >> {self.output}/normal_coverages.list\n"

        command += f"{os.path.realpath('./conda/bin/Rscript')} --vanilla {os.path.realpath('./conda/lib/R/library/PureCN/extdata/NormalDB.R')} --coverage-files {self.output}/normal_coverages.list --genome 'hg38' --out-dir {self.output} --force"

        self.create_sh("3.normal_database", command)
        return self.submit_job("3.normal_database", dependency_id=dependency_id)

    def run_purecn(self, input_file, dependency_id=None):
        normal_sample = os.path.basename(input_file).split(".")[0]
        tumor_sample = normal_sample.replace("BU", "TT").replace("TN", "TT")
        self.name = tumor_sample.split("_")[0]

        command = f"{os.path.realpath('./conda/bin/Rscript')} --vanilla {os.path.realpath('./conda/lib/R/library/PureCN/extdata/PureCN.R')} --sampleid {self.name} --normal {self.output}/{normal_sample}.Sort.MarkDuplicates.BQSR_coverage_loess.txt.gz --tumor {self.output}/{tumor_sample}.Sort.MarkDuplicates.BQSR_coverage_loess.txt.gz --normaldb {self.output}/normalDB_hg38.rds --genome 'hg38' --intervals {self.output}/baits_hg38_intervals.txt --post-optimize --out {self.output} --seed 123 --parallel --cores {self.config['DEFAULT']['threads']} --force"

        self.create_sh("4.PureCN", command)
        return self.submit_job("4.PureCN", dependency_id=dependency_id)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="Input BAM file(s)", nargs="+")
    parser.add_argument("output", help="Output directory")
    parser.add_argument("-c", "--config", help="config INI file", default="../config.ini")
    parser.add_argument("-n", "--dryrun", help="Don't actually run any recipe; just make .SH only", default=False, action="store_true")

    return parser.parse_args()


def main():
    args = parse_arguments()

    args.input = sorted(map(os.path.realpath, args.input))

    pipeline = PipelineManager(input_list=args.input, output=args.output, config_file=args.config, dryrun=args.dryrun)

    pipeline.create_dir()

    interval_job_id = pipeline.get_interval()

    coverage_job_id = ""
    for input_file in args.input:
        job_id = pipeline.calculate_coverage(input_file, dependency_id=interval_job_id)
        if job_id is not None:
            coverage_job_id += job_id + ":"

    if coverage_job_id:
        normal_job_id = pipeline.normal_database(dependency_id=coverage_job_id[:-1])
    else:
        normal_job_id = pipeline.normal_database()

    for input_file in args.input:
        if "TT" in input_file:
            continue
        pipeline.run_purecn(input_file, dependency_id=normal_job_id)


if __name__ == "__main__":
    main()
