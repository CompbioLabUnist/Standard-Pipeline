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

## Workflow objectives and result interpretation

The objective of this module is to call germline SNVs and indels from one
analysis-ready BAM file produced by
`02_Data_pre-processing_for_variant_discovery`. The main downstream outputs are:

```text
<sample>.VQSR.PASS.vcf.gz
<sample>.VQSR.PASS.maf.gz
```

The PASS VCF keeps the variant-level evidence and filter annotations. The MAF
is a compressed annotation table that is easier to review by gene and transcript.

### 1. HaplotypeCaller in GVCF mode

`HaplotypeCaller` performs local re-assembly around candidate sites and writes a
single-sample GVCF.

Input:

```text
<sample>.Sort.MarkDuplicates.BQSR.bam
```

Output:

```text
<sample>.vcf.gz
```

Main purpose:

- call candidate germline SNPs and indels from the recalibrated BAM
- emit a GVCF with `-ERC GVCF` so genotyping can happen in a later step
- use the reference FASTA and native PairHMM thread count from `../config.ini`

How to interpret the result:

- This file is an intermediate GVCF, not the final PASS variant set.
- It can include non-variant reference blocks and genotype likelihood
  information used by `GenotypeGVCFs`.
- Keep it if you need to audit the pre-genotyping HaplotypeCaller result.

### 2. GenomicsDB import

`GenomicsDBImport` imports the GVCF into a GenomicsDB workspace over the
intervals configured in `[REFERENCES] intervals`.

Input:

```text
<sample>.vcf.gz
```

Output:

```text
<sample>-DB/
```

Main purpose:

- prepare the GVCF for joint-genotyping style access by GATK
- organize variant records by genomic interval
- overwrite any existing workspace with the same output prefix

How to interpret the result:

- `<sample>-DB/` is a GATK workspace directory, not a VCF file.
- If this directory is incomplete or stale, downstream genotyping should be
  rerun after removing or overwriting the workspace.

### 3. GenotypeGVCFs

`GenotypeGVCFs` reads the GenomicsDB workspace and emits a regular genotyped
VCF.

Input:

```text
gendb://<sample>-DB
```

Output:

```text
<sample>.DB.vcf.gz
```

Main purpose:

- convert GVCF likelihoods into genotype calls
- produce a VCF that can be recalibrated and filtered

How to interpret the result:

- `<sample>.DB.vcf.gz` is the genotyped call set before VQSR filtering.
- Do not treat every record in this file as a final high-confidence germline
  variant.

### 4. Variant quality score recalibration

`VariantRecalibrator` builds a VQSR model with the HapMap, Omni, and 1000
Genomes resources configured in `../config.ini`. `ApplyVQSR` applies the model
with a truth-sensitivity filter level of `99.9`.

Inputs:

```text
<sample>.DB.vcf.gz
```

Outputs:

```text
<sample>.VQSR.recal
<sample>.VQSR.tranches
<sample>.VQSR.vcf.gz
```

Main purpose:

- model variant quality using known training and truth resources
- annotate variants with VQSR filtering decisions
- keep the recalibration table and tranche thresholds for review

How to interpret the result:

- `<sample>.VQSR.recal` stores the recalibration model.
- `<sample>.VQSR.tranches` records the tranche thresholds used by VQSR.
- `<sample>.VQSR.vcf.gz` contains the recalibrated VCF with `PASS` and
  non-`PASS` records.
- VQSR works best when enough variants are available for modeling. For very
  small cohorts or restricted target regions, review whether the configured
  VQSR resources and thresholds are appropriate.

### 5. PASS extraction and indexing

The wrapper extracts header lines and records whose VCF `FILTER` column is
`PASS`, compresses the result with `bgzip`, and indexes it with `tabix`.

Input:

```text
<sample>.VQSR.vcf.gz
```

Outputs:

```text
<sample>.VQSR.PASS.vcf.gz
<sample>.VQSR.PASS.vcf.gz.tbi
```

Main purpose:

- create a compact VCF containing high-confidence germline calls
- make the PASS VCF queryable by genomic interval

How to interpret the result:

- `<sample>.VQSR.PASS.vcf.gz` is the main filtered germline VCF.
- Use `<sample>.VQSR.vcf.gz` if you need to inspect variants that failed VQSR.

### 6. VCF to MAF conversion

The final job decompresses the PASS VCF temporarily, runs vcf2maf with VEP, and
compresses the MAF output.

Input:

```text
<sample>.VQSR.PASS.vcf.gz
```

Output:

```text
<sample>.VQSR.PASS.maf.gz
```

Main purpose:

- add gene and transcript annotations through VEP
- create a compressed tabular variant file for review
- use the output prefix as the vcf2maf sample identifier

How to interpret the result:

- The MAF is convenient for gene-level annotation review.
- The VCF remains the better source for genotype fields, site-level VQSR
  annotations, and raw filter context.
- The script removes the temporary decompressed PASS VCF and uncompressed MAF
  after creating the final `.maf.gz`.

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

The wrapper currently submits one workflow per listed BAM and uses sample
prefixes such as `C001_TN`, `C002_TN`, and `K001_BU`. Add, remove, or edit those
lines to match the germline samples you want to process.

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

- `input`: BQSR BAM file from
  `02_Data_pre-processing_for_variant_discovery`.
- `output`: output MAF path used to derive the sample prefix and output
  directory. The script uses the filename before the first dot as the prefix,
  so `C001_TN.maf` produces files named `C001_TN.*`.
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

- `C001_TN.vcf.gz`: single-sample GVCF from HaplotypeCaller.
- `C001_TN-DB/`: GenomicsDB workspace imported from the GVCF.
- `C001_TN.DB.vcf.gz`: genotyped VCF before VQSR.
- `C001_TN.VQSR.recal`: VQSR recalibration model.
- `C001_TN.VQSR.tranches`: VQSR tranche thresholds.
- `C001_TN.VQSR.vcf.gz`: recalibrated VCF with PASS and non-PASS records.
- `C001_TN.VQSR.PASS.vcf.gz`: filtered PASS germline VCF.
- `C001_TN.VQSR.PASS.vcf.gz.tbi`: tabix index for the PASS VCF.
- `C001_TN.VQSR.PASS.maf.gz`: compressed vcf2maf annotation table.
- generated SLURM scripts in `sh/`.
- SLURM logs in `stdeo/`.
