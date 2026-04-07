"""
08_3_SigProfiler.py: SigProfiler
"""
import argparse
import os
import sys
from pipeline_utils import PipelineManagerBase
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class PipelineManager(PipelineManagerBase):
    def __init__(self, input, output, config_file, dryrun):
        super().__init__(config_file, dryrun)
        self.input = os.path.realpath(input)
        self.output = os.path.realpath(output)
        self.name = "Signatures"

    def install_reference(self, dependency_id=None):
        command = f"{os.path.realpath('./bin/SigProfilerMatrixGenerator')} install GRCh38"
        self.create_sh("1.install_reference", command)
        return self.submit_job("1.install_reference", dependency_id=dependency_id)

    def refer_reference(self, dependency_id=None):
        command = f"rm -rfv {os.path.realpath(self.input)}/lib/python3.10/site-packages/SigProfilerMatrixGenerator/references/*\n"
        for folder in ["chromosomes", "CNV", "matrix", "SV", "vcf_files"]:
            command += f"ln -sfv /BiO/Teach/Standard-Pipeline/08_Mutational_signatures/lib/python3.10/site-packages/SigProfilerMatrixGenerator/references/{folder} {os.path.realpath(self.input)}/lib/python3.10/site-packages/SigProfilerMatrixGenerator/references/{folder}\n"

        command += f"rm -rfv {os.path.realpath(self.input)}/input\n"
        command += f"mkdir -p {os.path.realpath(self.input)}/input\n"
        command += f"ln -sfv {os.path.realpath('../03_Somatic_short_variant_discovery')}/*.PASS.vcf {os.path.realpath(self.input)}/input"

        self.create_sh("1.refer_reference", command)
        return self.submit_job("1.refer_reference", dependency_id=dependency_id)

    def matrix_generator(self, dependency_id=None):
        command = f"{os.path.realpath('./bin/SigProfilerMatrixGenerator')} matrix_generator --exome --output_directory {self.output} {self.name} 'GRCh38' '{os.path.realpath('.')}'"

        self.create_sh("2.matrix_generator", command)
        return self.submit_job("2.matrix_generator", dependency_id=dependency_id)

    def extractor(self, dependency_id=None):
        command = f"{os.path.realpath('./bin/SigProfilerExtractor')} sigprofilerextractor --reference_genome 'GRCh38' --exome --cpu {self.config['DEFAULT']['threads']} --assignment_cpu {self.config['DEFAULT']['threads']} 'vcf' {self.output} {os.path.realpath('.')}"

        self.create_sh("3.extractor", command)
        return self.submit_job("3.extractor", dependency_id=dependency_id)

    def plotting(self, dependency_id=None):
        command = f"{os.path.realpath('./bin/SigProfilerPlotting')} plotSBS --savefig_format 'png' --dpi 600 {os.path.realpath('./SBS/Signatures.SBS96.exome')} 'Plot' {self.name} '96'\n"
        command += f"{os.path.realpath('./bin/SigProfilerPlotting')} plotSBS --savefig_format 'png' --dpi 600 {os.path.realpath('./SBS/Signatures.SBS6.exome')} 'Plot' {self.name} '6'\n"
        command += f"{os.path.realpath('./bin/SigProfilerPlotting')} plotDBS --savefig_format 'png' --dpi 600 {os.path.realpath('./DBS/Signatures.DBS78.exome')} 'Plot' {self.name} '78'\n"
        command += f"{os.path.realpath('./bin/SigProfilerPlotting')} plotID --savefig_format 'png' --dpi 600 {os.path.realpath('./ID/Signatures.DBS28.exome')} 'Plot' {self.name} '28'"

        self.create_sh("4.plotting", command)
        return self.submit_job("4.plotting", dependency_id=dependency_id)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="Input directory")
    parser.add_argument("output", help="Output directory")
    parser.add_argument("-c", "--config", help="config INI file", default="../config.ini")
    parser.add_argument("-n", "--dryrun", help="Don't actually run any recipe; just make .SH only", default=False, action="store_true")

    return parser.parse_args()


def main():
    args = parse_arguments()

    pipeline = PipelineManager(input=args.input, output=args.output, config_file=args.config, dryrun=args.dryrun)

    pipeline.create_dir()

    refer_job_id = pipeline.refer_reference()
    matrix_job_id = pipeline.matrix_generator(dependency_id=refer_job_id)
    extractor_job_id = pipeline.extractor(dependency_id=matrix_job_id)
    pipeline.plotting(dependency_id=extractor_job_id)


if __name__ == "__main__":
    main()
