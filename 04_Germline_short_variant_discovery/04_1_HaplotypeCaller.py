#!/usr/bin/env python3
"""
04_1_HaplotypeCaller.py: HaplotypeCaller - Call germline SNPs and indels via local re-assembly of haplotypes
"""
from pipeline_utils import PipelineManagerBase
import argparse
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class PipelineManager(PipelineManagerBase):
    def __init__(self, input_file, output, config_file, dryrun):
        super().__init__(config_file, dryrun)
        self.input = os.path.realpath(input_file)
        self.output = os.path.realpath(output)
        self.name = self.output.split("/")[-1].split(".")[0]
        self.output_dir = os.path.dirname(self.output)

    def run_haplotypecaller(self, dependency_id=None):
        command = f"{self.config['TOOLS']['gatk']} HaplotypeCaller --java-options \"{self.config['DEFAULT']['java_options']}\" --reference {self.config['REFERENCES']['fasta']} --input {self.input} --output {self.output_dir}/{self.name}.vcf -ERC GVCF --native-pair-hmm-threads {self.config['DEFAULT']['threads']}"
        self.create_sh("HaplotypeCaller", command)
        return self.submit_job("HaplotypeCaller", dependency_id=dependency_id)

    def run_database(self, dependency_id=None):
        command = f"{self.config['TOOLS']['gatk']} GenomicsDBImport --java-options \"{self.config['DEFAULT']['java_options']}\" --reference {self.config['REFERENCES']['fasta']} --genomicsdb-workspace-path {self.output_dir}/DB --variant {self.output_dir}/{self.name}.vcf --intervals {self.config['REFERENCES']['intervals']} --reader-threads {self.config['DEFAULT']['threads']} --max-num-intervals-to-import-in-parallel {self.config['DEFAULT']['threads']} --overwrite-existing-genomicsdb-workspace true"
        self.create_sh("DB", command)
        return self.submit_job("DB", dependency_id=dependency_id)

    def run_genotypegvcfs(self, dependency_id=None):
        command = f"{self.config['TOOLS']['gatk']} GenotypeGVCFs --java-options \"{self.config['DEFAULT']['java_options']}\" --reference {self.config['REFERENCES']['fasta']} --variant gendb://{self.output_dir}/DB --output {self.output_dir}/{self.name}.DB.vcf"
        self.create_sh("GenotypeGVCFs", command)
        return self.submit_job("GenotypeGVCFs", dependency_id=dependency_id)

    def run_variantrecalibrator(self, mode=None, dependency_id=None):
        if mode == "SNP":
            mode_tag = "snp"
            resource = f"--resource:hapmap,known=false,training=true,truth=true,prior=15.0 {self.config['REFERENCES']['hapmap']} --resource:omni,known=false,training=true,truth=false,prior=12.0 {self.config['REFERENCES']['omni']} --resource:1000G,known=false,training=true,truth=false,prior=10.0 {self.config['REFERENCES']['1000g']} -an QD -an MQ -an MQRankSum -an ReadPosRankSum -an FS -an SOR"
        elif mode == "INDEL":
            mode_tag = "indel"
            resource = f"--resource:mills,known=false,training=true,truth=true,prior=12.0 {self.config['REFERENCES']['mills']} --resource:dbsnp,known=true,training=false,truth=false,prior=2.0 {self.config['REFERENCES']['dbsnp']} -an QD -an MQRankSum -an ReadPosRankSum -an FS -an SOR -an DP"
        command = f"{self.config['TOOLS']['gatk']} VariantRecalibrator --java-options \"{self.config['DEFAULT']['java_options']}\" --reference {self.config['REFERENCES']['fasta']} --variant {self.output_dir}/{self.name}.DB.vcf {resource} -mode {mode} --output {self.output_dir}/{self.name}.{mode_tag}.recal --tranches-file {self.output_dir}/{self.name}.{mode_tag}.tranches --rscript-file {self.output_dir}/{self.name}.{mode_tag}.plots.R"

        self.create_sh(f"VariantRecalibrator_{mode}", command)
        return self.submit_job(f"VariantRecalibrator_{mode}", dependency_id=dependency_id)

    def run_applyvqsr(self, mode=None, dependency_id=None):
        if mode == "SNP":
            variant = f"{self.output_dir}/{self.name}.DB.vcf"
            mode_tag = "snp"
        elif mode == "INDEL":
            variant = f"{self.output_dir}/{self.name}.rc.snp.vcf"
            mode_tag = "indel"

        command = f"{self.config['TOOLS']['gatk']} ApplyVQSR --java-options \"{self.config['DEFAULT']['java_options']}\" --reference {self.config['REFERENCES']['fasta']} --variant {variant} --output {self.output_dir}/{self.name}.rc.{mode_tag}.vcf -mode {mode} --recal-file {self.output_dir}/{self.name}.{mode_tag}.recal --tranches-file {self.output_dir}/{self.name}.{mode_tag}.tranches --truth-sensitivity-filter-level 99.9 --create-output-variant-index true"
        self.create_sh(f"ApplyVQSR_{mode}", command)
        return self.submit_job(f"ApplyVQSR_{mode}", dependency_id=dependency_id)

    def run_pass(self, dependency_id=None):
        command = f"{self.config['TOOLS']['awk']} -F '\t' '{{if($0 ~ /\\#/) print; else if($7 == \"PASS\") print}}' {self.output_dir}/{self.name}.rc.indel.vcf > {self.output_dir}/{self.name}.PASS.vcf"
        self.create_sh("PASS", command)
        return self.submit_job("PASS", dependency_id=dependency_id, cpus=1)

    def run_index(self, make_panel_of_normals=False, dependency_id=None):
        command = f"{self.config['TOOLS']['gatk']} IndexFeatureFile --input {self.output_dir}/{self.name}.PASS.vcf --output {self.output_dir}/{self.name}.PASS.vcf.idx"
        self.create_sh("Index", command)
        return self.submit_job("Index", dependency_id=dependency_id, cpus=1)

    def run_maf(self, dependency_id=None):
        command = f"{self.config['TOOLS']['vcf2maf']} --vep-path {self.config['TOOLS']['vep']} --vep-data {self.config['TOOLS']['vep']} --vep-forks {self.config['DEFAULT']['threads']} --ncbi-build 'GRCh38' --input-vcf {self.output_dir}/{self.name}.PASS.vcf --output {self.output_dir}/{self.name}.PASS.maf --tumor-id {self.name} --ref-fasta {self.config['REFERENCES']['fasta']} --vep-overwrite"
        self.create_sh("MAF", command)
        return self.submit_job("MAF", dependency_id=dependency_id)


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

    # haplotypecaller_job_id = pipeline.run_haplotypecaller()
    # DB_job_id = pipeline.run_database(dependency_id=haplotypecaller_job_id)
    genotypegvcfs_job_id = pipeline.run_genotypegvcfs()
    variantrecalibrator_snp_job_id = pipeline.run_variantrecalibrator(mode="SNP", dependency_id=genotypegvcfs_job_id)
    applyvqsr_snp_job_id = pipeline.run_applyvqsr(mode="SNP", dependency_id=variantrecalibrator_snp_job_id)
    variantrecalibrator_indel_job_id = pipeline.run_variantrecalibrator(mode="INDEL", dependency_id=applyvqsr_snp_job_id)
    applyvqsr_indel_job_id = pipeline.run_applyvqsr(mode="INDEL", dependency_id=variantrecalibrator_indel_job_id)
    pass_job_id = pipeline.run_pass(dependency_id=applyvqsr_indel_job_id)
    index_job_id = pipeline.run_index(dependency_id=pass_job_id)
    maf_job_id = pipeline.run_maf(dependency_id=index_job_id)


if __name__ == "__main__":
    main()
