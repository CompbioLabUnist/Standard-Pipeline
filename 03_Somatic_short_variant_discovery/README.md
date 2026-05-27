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

- `C001.vcf`
- `C001.filter.vcf`
- `C001.PASS.vcf`
- `C001.PASS.vcf.idx`
- `C001.PASS.maf`
- generated scripts in `sh/`
- SLURM logs in `stdeo/`
