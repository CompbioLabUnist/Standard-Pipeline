# Somatic short variant discovery

This module follows the GATK somatic SNV/indel workflow:
https://gatk.broadinstitute.org/hc/en-us/articles/360035894731-Somatic-short-variant-discovery-SNVs-Indels-

It runs Mutect2 on a matched normal/tumor BAM pair, filters calls, keeps PASS
variants, indexes the PASS VCF, and converts variants to MAF with vcf2maf.

## References

- Panel of normals:
  https://gatk.broadinstitute.org/hc/en-us/articles/360035890631-Panel-of-Normals-PON
- Mutect2:
  https://gatk.broadinstitute.org/hc/en-us/articles/13832710384155-Mutect2
- FilterMutectCalls:
  https://gatk.broadinstitute.org/hc/en-us/articles/13832694001563-FilterMutectCalls
- vcf2maf: https://github.com/mskcc/vcf2maf

Tool and reference paths are read from `../config.ini`.

## Workflow objectives and result interpretation

The objective of this module is to identify candidate somatic SNVs and indels
from a matched normal/tumor pair. The usual final output is:

```text
<sample>.PASS.maf
```

The MAF file is the most convenient output for downstream visualization and
summary analysis. Keep the VCF files as well, because they contain filtering
annotations and genotype-level details that are not fully represented in MAF.

### 1. Optional panel of normals

A panel of normals (PON) is a resource built from normal samples. It is used to
remove recurrent technical artifacts and sequencing-context artifacts that can
look like somatic variants.

When `--panel_of_normals` is used, this wrapper first creates an intermediate
PON in the output directory:

```text
<sample>_panel_of_normals.vcf
<sample>_panel_of_normals.filter.vcf
<sample>_panel_of_normals.PASS.vcf
<sample>_panel_of_normals.PASS.vcf.idx
DB/
panel_of_normals.vcf.gz
```

Main purpose:

- call candidate sites from the normal sample
- filter those normal-sample calls
- import the PASS normal calls into a GenomicsDB workspace
- create `panel_of_normals.vcf.gz`
- pass that PON to the final tumor/normal Mutect2 call

How to interpret the result:

- `panel_of_normals.vcf.gz` is a filtering resource, not the final mutation
  result.
- Variants found in the PON are treated as likely recurrent artifacts during
  the tumor call.
- A stronger production PON should be built from multiple normal samples from
  the same assay, capture kit, sequencing platform, and processing pipeline.
- This wrapper builds the PON from the provided normal input for the current
  run, which is useful for documenting and testing the workflow but may be less
  robust than a multi-sample PON.

### 2. Somatic mutation discovery with Mutect2

Mutect2 compares the tumor BAM and matched normal BAM against the reference
genome. It performs local assembly around candidate variant sites and reports
candidate somatic SNVs and indels.

Inputs:

```text
<normal>.Sort.MarkDuplicates.BQSR.bam
<tumor>.Sort.MarkDuplicates.BQSR.bam
```

Output:

```text
<sample>.vcf
```

Main purpose:

- detect candidate somatic variants in the tumor sample
- use the matched normal sample to reduce germline and sample-specific
  background calls
- optionally use `panel_of_normals.vcf.gz` to reduce recurrent technical
  artifacts
- write a VCF containing candidate calls before final filtering

How to interpret the result:

- `<sample>.vcf` is an unfiltered candidate-call file.
- Do not treat all records in this file as final somatic mutations.
- The file may include true somatic variants, germline leakage, sequencing
  artifacts, mapping artifacts, contamination-related calls, or low-confidence
  candidates.
- The tumor and normal sample names are derived from the BAM filenames before
  the first dot.

### 3. Filtering Mutect2 results

`FilterMutectCalls` reads the unfiltered Mutect2 VCF and annotates each variant
with a filtering decision.

Input:

```text
<sample>.vcf
```

Output:

```text
<sample>.filter.vcf
```

Main purpose:

- classify candidate calls as `PASS` or filtered
- mark likely artifacts in the VCF `FILTER` column
- preserve filtered records so reviewers can inspect why a candidate was
  rejected

How to interpret the result:

- `PASS` records are the primary high-confidence somatic calls for this module.
- Non-`PASS` records are retained in `<sample>.filter.vcf` but should not be
  used as final somatic mutation calls without manual review.
- Common filter reasons can reflect weak evidence, strand bias, mapping
  artifacts, contamination, normal-sample support, or panel-of-normals support.
- Filtering is context-dependent. A filtered call may still be biologically
  interesting in special cases, but it should be treated as lower confidence.

### 4. PASS VCF extraction and indexing

This wrapper extracts only header lines and `PASS` variants from
`<sample>.filter.vcf`:

```text
<sample>.PASS.vcf
```

It then indexes the PASS VCF:

```text
<sample>.PASS.vcf.idx
```

Main purpose:

- create a compact VCF containing only high-confidence calls
- make the PASS VCF available for tools that require an indexed variant file

How to interpret the result:

- `<sample>.PASS.vcf` is the filtered somatic VCF used by downstream steps.
- It excludes non-`PASS` candidates, so use `<sample>.filter.vcf` if you need
  to audit rejected variants.

### 5. VCF to MAF conversion

The final step converts the PASS VCF into MAF format using vcf2maf and VEP.

Input:

```text
<sample>.PASS.vcf
```

Output:

```text
<sample>.PASS.maf
```

Main purpose:

- add gene and transcript annotations
- represent somatic variants in a tabular format commonly used in cancer
  genomics
- prepare inputs for visualization modules such as
  `06_Somatic_variant_visualization`

How to interpret the result:

- `<sample>.PASS.maf` is the main downstream table for mutation summary plots.
- MAF is convenient for gene-level interpretation, but the VCF remains the
  better source for raw genotype fields and filtering annotations.

## Setup

Run commands from this directory:

```bash
cd 03_Somatic_short_variant_discovery
ln -snfv ../pipeline_utils.py .
```

The normal and tumor BAM files usually come from
`02_Data_pre-processing_for_variant_discovery`.

## Execute with the example wrapper

Edit `03_1_Mutect2.bash` so the normal and tumor BAM paths match your sample,
then run:

```bash
bash 03_1_Mutect2.bash
```

## Execute directly

Generate scripts without submitting:

```bash
python3 -B 03_1_Mutect2.py --dryrun \
    "$(realpath ../02_Data_pre-processing_for_variant_discovery/C001_TN.Sort.MarkDuplicates.BQSR.bam)" \
    "$(realpath ../02_Data_pre-processing_for_variant_discovery/C001_TT.Sort.MarkDuplicates.BQSR.bam)" \
    "$PWD/C001.maf"
```

Submit the Mutect2 workflow:

```bash
python3 -B 03_1_Mutect2.py \
    "$(realpath ../02_Data_pre-processing_for_variant_discovery/C001_TN.Sort.MarkDuplicates.BQSR.bam)" \
    "$(realpath ../02_Data_pre-processing_for_variant_discovery/C001_TT.Sort.MarkDuplicates.BQSR.bam)" \
    "$PWD/C001.maf"
```

Arguments:

- `normal`: matched normal BAM file.
- `tumor`: tumor BAM file.
- `output`: output MAF basename. The script derives the sample prefix from this
  path and writes outputs in the same directory.
- `--panel_of_normals`: also build `panel_of_normals.vcf.gz` in the output
  directory and use it for the tumor call.
- `--config`: config INI file. Defaults to `../config.ini`.
- `--dryrun`: create scripts in `sh/` without calling `sbatch`.

## Submitted job order

Default mode:

1. `1.Mutect`
2. `2.Filter`
3. `3.PASS`
4. `4.Index`
5. `7.MAF`

With `--panel_of_normals`, the script first creates a panel of normals:

1. `1.Mutect_panel_of_normals`
2. `2.Filter_panel_of_normals`
3. `3.PASS_panel_of_normals`
4. `4.Index_panel_of_normals`
5. `5.DB`
6. `6.Create_panel_of_normals`
7. default tumor workflow

## Expected outputs

For output prefix `C001`, outputs include:

- `C001.vcf`: unfiltered Mutect2 candidate somatic calls.
- `C001.filter.vcf`: Mutect2 calls after `FilterMutectCalls`, including both
  `PASS` and filtered records.
- `C001.PASS.vcf`: filtered VCF containing only header lines and `PASS`
  variants.
- `C001.PASS.vcf.idx`: index for the PASS VCF.
- `C001.PASS.maf`: annotated PASS variants in MAF format.
- `panel_of_normals.vcf.gz`: optional PON resource created when
  `--panel_of_normals` is used.
- generated scripts in `sh/`
- SLURM logs in `stdeo/`
