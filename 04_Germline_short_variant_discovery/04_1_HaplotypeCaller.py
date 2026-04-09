#!/usr/bin/env python3
"""
04_1_HaplotypeCaller.py: HaplotypeCaller - Call germline SNPs and indels via local re-assembly of haplotypes
"""
import argparse
import os
import sys
from pipeline_utils import PipelineManagerBase
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class PipelineManager(PipelineManagerBase):
    def __init__(self, input_file, output, config_file, dryrun):
        super().__init__(config_file, dryrun)
        self.input = os.path.realpath(input_file)
        self.output = os.path.realpath(output)
        self.name = self.output.split("/")[-1].split(".")[0]
        self.output_dir = os.path.dirname(self.output)

    def run_haplotypecaller(self, dependency_id=None):
        command = f"{self.config['TOOLS']['gatk']} HaplotypeCaller --java-options \"{self.config['DEFAULT']['java_options']}\" --reference {self.config['REFERENCES']['fasta']} --input {self.input} --output {self.output_dir}/{self.name}.vcf.gz -ERC GVCF --native-pair-hmm-threads {self.config['DEFAULT']['threads']}"
        self.create_sh("1.HaplotypeCaller", command)
        return self.submit_job("1.HaplotypeCaller", dependency_id=dependency_id)

    def run_database(self, dependency_id=None):
        command = f"{self.config['TOOLS']['gatk']} GenomicsDBImport --java-options \"{self.config['DEFAULT']['java_options']}\" --reference {self.config['REFERENCES']['fasta']} --genomicsdb-workspace-path {self.output_dir}/{self.name}-DB --variant {self.output_dir}/{self.name}.vcf.gz --intervals {self.config['REFERENCES']['intervals']} --reader-threads {self.config['DEFAULT']['threads']} --max-num-intervals-to-import-in-parallel {self.config['DEFAULT']['threads']} --overwrite-existing-genomicsdb-workspace true"
        self.create_sh("2.DB", command)
        return self.submit_job("2.DB", dependency_id=dependency_id)

    def run_genotypegvcfs(self, dependency_id=None):
        command = f"{self.config['TOOLS']['gatk']} GenotypeGVCFs --java-options \"{self.config['DEFAULT']['java_options']}\" --reference {self.config['REFERENCES']['fasta']} --variant gendb://{self.output_dir}/{self.name}-DB --output {self.output_dir}/{self.name}.DB.vcf.gz"
        self.create_sh("3.GenotypeGVCFs", command)
        return self.submit_job("3.GenotypeGVCFs", dependency_id=dependency_id)

    def run_variantrecalibrator(self, dependency_id=None):
        resource = f"--resource:hapmap,known=false,training=true,truth=true,prior=15.0 {self.config['REFERENCES']['hapmap']} --resource:omni,known=false,training=true,truth=false,prior=12.0 {self.config['REFERENCES']['omni']} --resource:1000G,known=false,training=true,truth=false,prior=10.0 {self.config['REFERENCES']['1000g']} -an QD -an MQ -an MQRankSum -an ReadPosRankSum -an FS -an SOR"

        command = f"{self.config['TOOLS']['gatk']} VariantRecalibrator --java-options \"{self.config['DEFAULT']['java_options']}\" --reference {self.config['REFERENCES']['fasta']} --variant {self.output_dir}/{self.name}.DB.vcf.gz {resource} -mode 'BOTH' --output {self.output_dir}/{self.name}.VQSR.recal --tranches-file {self.output_dir}/{self.name}.VQSR.tranches"

        self.create_sh("4.VariantRecalibrator", command)
        return self.submit_job("4.VariantRecalibrator", dependency_id=dependency_id)

    def run_applyvqsr(self, dependency_id=None):
        command = f"{self.config['TOOLS']['gatk']} ApplyVQSR --java-options \"{self.config['DEFAULT']['java_options']}\" --reference {self.config['REFERENCES']['fasta']} --variant {self.output_dir}/{self.name}.DB.vcf.gz --output {self.output_dir}/{self.name}.VQSR.vcf.gz -mode 'BOTH' --recal-file {self.output_dir}/{self.name}.VQSR.recal --tranches-file {self.output_dir}/{self.name}.VQSR.tranches --truth-sensitivity-filter-level 99.9 --create-output-variant-index true"
        self.create_sh("5.ApplyVQSR", command)
        return self.submit_job("5.ApplyVQSR", dependency_id=dependency_id)

    def run_pass(self, dependency_id=None):
        command = f"{self.config['TOOLS']['gzip']} --stdout --decompress {self.output_dir}/{self.name}.VQSR.vcf.gz | {self.config['TOOLS']['awk']} -F '\t' '{{if($0 ~ /\\#/) print; else if($7 == \"PASS\") print}}' | {self.config['TOOLS']['bgzip']} --stdout --force --compress-level 9 --threads {self.config['DEFAULT']['threads']} > {self.output_dir}/{self.name}.VQSR.PASS.vcf.gz"
        self.create_sh("6.PASS", command)
        return self.submit_job("6.PASS", dependency_id=dependency_id, cpus=1)

    def run_index(self, dependency_id=None):
        command = f"{self.config['TOOLS']['tabix']} --preset vcf --force --threads {self.config['DEFAULT']['threads']} {self.output_dir}/{self.name}.VQSR.PASS.vcf.gz"
        self.create_sh("7.Index", command)
        return self.submit_job("7.Index", dependency_id=dependency_id, cpus=1)

    def run_maf(self, dependency_id=None):
        command = f"{self.config['TOOLS']['vcf2maf']} --vep-path {self.config['TOOLS']['vep']} --vep-data {self.config['TOOLS']['vep']} --vep-forks {self.config['DEFAULT']['threads']} --ncbi-build 'GRCh38' --input-vcf {self.output_dir}/{self.name}.PASS.vcf.gz --output {self.output_dir}/{self.name}.PASS.maf --tumor-id {self.name} --ref-fasta {self.config['REFERENCES']['fasta']} --vep-overwrite"
        self.create_sh("8.MAF", command)
        return self.submit_job("8.MAF", dependency_id=dependency_id)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="Tumor BAM file")
    parser.add_argument("output", help="Output MAF file")
    parser.add_argument("-c", "--config", help="config INI file", default="../config.ini")
    parser.add_argument("-n", "--dryrun", help="Don't actually run any recipe; just make .SH only", default=False, action="store_true")

    return parser.parse_args()


def main():
    args = parse_arguments()

    pipeline = PipelineManager(input_file=args.input, output=args.output, config_file=args.config, dryrun=args.dryrun)

    pipeline.create_dir()

    haplotypecaller_job_id = pipeline.run_haplotypecaller()
    db_job_id = pipeline.run_database(dependency_id=haplotypecaller_job_id)
    genotypegvcfs_job_id = pipeline.run_genotypegvcfs(dependency_id=db_job_id)
    variantrecalibrator_snp_job_id = pipeline.run_variantrecalibrator(dependency_id=genotypegvcfs_job_id)
    applyvqsr_snp_job_id = pipeline.run_applyvqsr(dependency_id=variantrecalibrator_snp_job_id)
    pass_job_id = pipeline.run_pass(dependency_id=applyvqsr_snp_job_id)
    index_job_id = pipeline.run_index(dependency_id=pass_job_id)
    pipeline.run_maf(dependency_id=index_job_id)


if __name__ == "__main__":
    main()
