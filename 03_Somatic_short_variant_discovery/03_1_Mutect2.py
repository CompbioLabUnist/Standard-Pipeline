#!/usr/bin/env python3
"""
03_1_Mutect2.py: Mutect2 - Call somatic SNVs and indels via local assembly of haplotypes
"""
import argparse
import os
import sys
from pipeline_utils import PipelineManagerBase
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class PipelineManager(PipelineManagerBase):
    def __init__(self, normal, tumor, output, config_file, panel_of_normals, dryrun):
        super().__init__(config_file, dryrun)
        self.normal = os.path.realpath(normal)
        self.tumor = os.path.realpath(tumor)
        self.output = os.path.realpath(output)
        self.normal_name = self.normal.split("/")[-1].split(".")[0]
        self.tumor_name = self.tumor.split("/")[-1].split(".")[0]
        self.name = self.output.split("/")[-1].split(".")[0]
        self.output_dir = os.path.dirname(self.output)
        self.panel_of_normals = panel_of_normals

    def run_mutect(self, make_panel_of_normals=False, dependency_id=None):
        input_tumor = f"--input {self.tumor} --normal-sample {self.normal_name} "
        panel_of_normals_path = ""
        panel_of_normals_label = ""
        if self.panel_of_normals:
            if make_panel_of_normals:
                input_tumor = ""
                panel_of_normals_label = "_panel_of_normals"
            else:
                panel_of_normals_path = f"--panel-of-normals {self.output_dir}/panel_of_normals.vcf.gz"

        command = f"{self.config['TOOLS']['gatk']} Mutect2 --java-options \"{self.config['DEFAULT']['java_options']}\" --reference {self.config['REFERENCES']['fasta']} --input {self.normal} {input_tumor}--output {self.output_dir}/{self.name}{panel_of_normals_label}.vcf {panel_of_normals_path}--native-pair-hmm-threads {self.config['DEFAULT']['threads']} --max-mnp-distance 0"
        self.create_sh(f"Mutect{panel_of_normals_label}", command)
        return self.submit_job(f"Mutect{panel_of_normals_label}", dependency_id=dependency_id)

    def run_filter(self, make_panel_of_normals=False, dependency_id=None):
        panel_of_normals_label = "_panel_of_normals" if make_panel_of_normals else ""
        command = f"{self.config['TOOLS']['gatk']} FilterMutectCalls --java-options \"{self.config['DEFAULT']['java_options']}\" --reference {self.config['REFERENCES']['fasta']} --variant {self.output_dir}/{self.name}{panel_of_normals_label}.vcf --output {self.output_dir}/{self.name}{panel_of_normals_label}.filter.vcf"
        self.create_sh(f"Filter{panel_of_normals_label}", command)
        return self.submit_job(f"Filter{panel_of_normals_label}", dependency_id=dependency_id, cpus=1)

    def run_pass(self, make_panel_of_normals=False, dependency_id=None):
        panel_of_normals_label = "_panel_of_normals" if make_panel_of_normals else ""
        command = f"{self.config['TOOLS']['awk']} -F '\t' '{{if($0 ~ /\\#/) print; else if($7 == \"PASS\") print}}' {self.output_dir}/{self.name}{panel_of_normals_label}.filter.vcf > {self.output_dir}/{self.name}{panel_of_normals_label}.PASS.vcf"
        self.create_sh(f"PASS{panel_of_normals_label}", command)
        return self.submit_job(f"PASS{panel_of_normals_label}", dependency_id=dependency_id, cpus=1)

    def run_index(self, make_panel_of_normals=False, dependency_id=None):
        panel_of_normals_label = "_panel_of_normals" if make_panel_of_normals else ""
        command = f"{self.config['TOOLS']['gatk']} IndexFeatureFile --java-options \"{self.config['DEFAULT']['java_options']}\" --input {self.output_dir}/{self.name}{panel_of_normals_label}.PASS.vcf --output {self.output_dir}/{self.name}{panel_of_normals_label}.PASS.vcf.idx"
        self.create_sh(f"Index{panel_of_normals_label}", command)
        return self.submit_job(f"Index{panel_of_normals_label}", dependency_id=dependency_id, cpus=1)

    def run_database(self, dependency_id=None):
        command = f"{self.config['TOOLS']['gatk']} GenomicsDBImport --java-options \"{self.config['DEFAULT']['java_options']}\" --reference {self.config['REFERENCES']['fasta']} --genomicsdb-workspace-path {self.output_dir}/DB --variant {self.output_dir}/{self.name}_panel_of_normals.PASS.vcf --intervals {self.config['REFERENCES']['intervals']} --reader-threads {self.config['DEFAULT']['threads']} --max-num-intervals-to-import-in-parallel {self.config['DEFAULT']['threads']} --overwrite-existing-genomicsdb-workspace true"
        self.create_sh("DB", command)
        return self.submit_job("DB", dependency_id=dependency_id)

    def run_create_panel_of_normals(self, dependency_id=None):
        command = f"{self.config['TOOLS']['gatk']} CreateSomaticPanelOfNormals --java-options \"{self.config['DEFAULT']['java_options']}\" --reference {self.config['REFERENCES']['fasta']} --variant 'gendb://{self.output_dir}/DB' --output {self.output_dir}/panel_of_normals.vcf.gz"
        self.create_sh("Create_panel_of_normals", command)
        return self.submit_job("Create_panel_of_normals", dependency_id=dependency_id, cpus=1)

    def run_maf(self, dependency_id=None):
        command = f"{self.config['TOOLS']['vcf2maf']} --vep-path {self.config['TOOLS']['vep']} --vep-data {self.config['TOOLS']['vep']} --vep-forks {self.config['DEFAULT']['threads']} --ncbi-build 'GRCh38' --input-vcf {self.output_dir}/{self.name}.PASS.vcf --output {self.output_dir}/{self.name}.PASS.maf --tumor-id {self.tumor_name} --normal-id {self.normal_name} --ref-fasta {self.config['REFERENCES']['fasta']} --vep-overwrite"
        self.create_sh("MAF", command)
        return self.submit_job("MAF", dependency_id=dependency_id)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("normal", help="Normal BAM file")
    parser.add_argument("tumor", help="Tumor BAM file")
    parser.add_argument("output", help="Output MAF file")
    parser.add_argument("-c", "--config", help="config INI file", default="../config.ini")
    parser.add_argument("-p", "--panel_of_normals", help="Panel of normal (optional)", default=False, action="store_true")
    parser.add_argument("-n", "--dryrun", help="Don't actually run any recipe; just make .SH only", default=False, action="store_true")

    return parser.parse_args()


def main():
    args = parse_arguments()

    pipeline = PipelineManager(normal=args.normal, tumor=args.tumor, output=args.output, config_file=args.config, panel_of_normals=args.panel_of_normals, dryrun=args.dryrun)

    pipeline.create_dir()

    if pipeline.panel_of_normals:
        panel_of_normals_mutect_job_id = pipeline.run_mutect(make_panel_of_normals=True)
        panel_of_normals_filter_job_id = pipeline.run_filter(make_panel_of_normals=True, dependency_id=panel_of_normals_mutect_job_id)
        panel_of_normals_pass_job_id = pipeline.run_pass(make_panel_of_normals=True, dependency_id=panel_of_normals_filter_job_id)
        panel_of_normals_index_job_id = pipeline.run_index(make_panel_of_normals=True, dependency_id=panel_of_normals_pass_job_id)
        panel_of_normals_db_job_id = pipeline.run_database(dependency_id=panel_of_normals_index_job_id)
        create_panel_of_normals_job_id = pipeline.run_create_panel_of_normals(dependency_id=panel_of_normals_db_job_id)

    mutect_job_id = pipeline.run_mutect(dependency_id=create_panel_of_normals_job_id) if pipeline.panel_of_normals else pipeline.run_mutect()
    filter_job_id = pipeline.run_filter(dependency_id=mutect_job_id)
    pass_job_id = pipeline.run_pass(dependency_id=filter_job_id)
    index_job_id = pipeline.run_index(dependency_id=pass_job_id)
    pipeline.run_maf(dependency_id=index_job_id)


if __name__ == "__main__":
    main()
