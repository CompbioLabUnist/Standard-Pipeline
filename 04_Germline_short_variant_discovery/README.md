# Germline short variant discovery

This module follows the GATK germline SNP/indel workflow:
https://gatk.broadinstitute.org/hc/en-us/articles/360035535932-Germline-short-variant-discovery-SNPs-Indels-

It runs HaplotypeCaller in GVCF mode, imports the sample into GenomicsDB,
genotypes the GVCF, applies VQSR, keeps PASS variants, indexes the PASS VCF,
and converts the result to MAF with vcf2maf.

## References

- HaplotypeCaller:
  https://gatk.broadinstitute.org/hc/en-us/articles/360037225632-HaplotypeCaller
- GenotypeGVCFs:
  https://gatk.broadinstitute.org/hc/en-us/articles/360037057852-GenotypeGVCFs

Tool and reference paths are read from `../config.ini`.

## Setup

Run commands from this directory:

```bash
cd 04_Germline_short_variant_discovery
ln -snfv ../pipeline_utils.py .
```

The input BAM files usually come from
`02_Data_pre-processing_for_variant_discovery`.

## Execute with the example wrapper

Edit `04_1_HaplotypeCaller.bash` so the BAM paths match your samples, then run:

```bash
bash 04_1_HaplotypeCaller.bash
```

## Execute directly

Generate scripts without submitting:

```bash
python3 -B 04_1_HaplotypeCaller.py --dryrun \
    "$(realpath ../02_Data_pre-processing_for_variant_discovery/C001_TN.Sort.MarkDuplicates.BQSR.bam)" \
    "$PWD/C001_TN.maf"
```

Submit the germline workflow:

```bash
python3 -B 04_1_HaplotypeCaller.py \
    "$(realpath ../02_Data_pre-processing_for_variant_discovery/C001_TN.Sort.MarkDuplicates.BQSR.bam)" \
    "$PWD/C001_TN.maf"
```

Arguments:

- `input`: BQSR BAM file.
- `output`: output MAF basename. The script derives the sample prefix from this
  path and writes outputs in the same directory.
- `--config`: config INI file. Defaults to `../config.ini`.
- `--dryrun`: create scripts in `sh/` without calling `sbatch`.

## Submitted job order

1. `1.HaplotypeCaller`
2. `2.DB`
3. `3.GenotypeGVCFs`
4. `4.VariantRecalibrator`
5. `5.ApplyVQSR`
6. `6.PASS`
7. `7.Index`
8. `8.MAF`

Each job is submitted with an `afterok` dependency on the previous job.

## Expected outputs

For output prefix `C001_TN`, outputs include:

- `C001_TN.vcf.gz`
- `C001_TN-DB/`
- `C001_TN.DB.vcf.gz`
- `C001_TN.VQSR.recal`
- `C001_TN.VQSR.tranches`
- `C001_TN.VQSR.vcf.gz`
- `C001_TN.VQSR.PASS.vcf.gz`
- `C001_TN.VQSR.PASS.vcf.gz.tbi`
- `C001_TN.VQSR.PASS.maf.gz`
- generated scripts in `sh/`
- SLURM logs in `stdeo/`
