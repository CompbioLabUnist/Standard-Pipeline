# Data pre-processing for variant discovery

This module follows the GATK data pre-processing workflow:
https://gatk.broadinstitute.org/hc/en-us/articles/360035535912-Data-pre-processing-for-variant-discovery

For each paired-end DNA sample, the pipeline maps reads, sorts BAM files, marks
duplicates, calculates BQSR, and applies BQSR. The final BAM is suitable for
downstream somatic and germline variant calling.

## Tools

### BWA (recommended)

- DOI: [10.1093/bioinformatics/btp324](https://doi.org/10.1093/bioinformatics/btp324)

### Bowtie2

- DOI: [10.1093/bioinformatics/bty648](https://doi.org/10.1093/bioinformatics/bty648)
- DOI: [10.1038/nmeth.1923](https://doi.org/10.1038/nmeth.1923)
- DOI: [10.1186/gb-2009-10-3-r25](https://doi.org/10.1186/gb-2009-10-3-r25)

### GATK steps

- MarkDuplicatesSpark:
  https://gatk.broadinstitute.org/hc/en-us/articles/13832682540699-MarkDuplicatesSpark
- Base quality score recalibration:
  https://gatk.broadinstitute.org/hc/en-us/articles/360035890531-Base-Quality-Score-Recalibration-BQSR-

Executable and reference paths are read from `../config.ini`.

## Setup

Run commands from this directory:

```bash
cd 02_Data_pre-processing_for_variant_discovery
ln -snfv ../pipeline_utils.py .
```

Input FASTQ names are expected to contain `_DNA`; the sample name is derived
from the part before `_DNA`.

## Execute with the example wrappers

Edit the FASTQ paths in the wrapper before running.

BWA:

```bash
bash 02_1_BWA.bash
```

Bowtie2:

```bash
bash 02_2_Bowtie2.bash
```

## Execute BWA directly

Generate the SLURM scripts without submitting:

```bash
python3 -B 02_1_BWA.py --dryrun \
    "$(realpath ../00_Data/WES/merge/C001_TN_DNA_R1.fastq.gz)" \
    "$(realpath ../00_Data/WES/merge/C001_TN_DNA_R2.fastq.gz)" \
    "$(realpath .)"
```

Submit the jobs:

```bash
python3 -B 02_1_BWA.py \
    "$(realpath ../00_Data/WES/merge/C001_TN_DNA_R1.fastq.gz)" \
    "$(realpath ../00_Data/WES/merge/C001_TN_DNA_R2.fastq.gz)" \
    "$(realpath .)"
```

## Execute Bowtie2 directly

```bash
python3 -B 02_2_Bowtie2.py \
    "$(realpath ../00_Data/WES/merge/C001_TN_DNA_R1.fastq.gz)" \
    "$(realpath ../00_Data/WES/merge/C001_TN_DNA_R2.fastq.gz)" \
    "$(realpath .)"
```

Arguments:

- `input`: two paired FASTQ files.
- `output`: output directory for BAM files, generated job scripts, and logs.
- `--config`: config INI file. Defaults to `../config.ini`.
- `--dryrun`: create scripts in `sh/` without calling `sbatch`.

## Submitted job order

BWA mode:

1. `1-1.BWA`
2. `1-2.Sort`
3. `1-3.MarkDup`
4. `1-4.BQSR`
5. `1-5.ApplyBQSR`

Bowtie2 mode:

1. `2-1.Bowtie2`
2. `2-2.Sort`
3. `2-3.MarkDup`
4. `2-4.BQSR`
5. `2-5.ApplyBQSR`

Each job is submitted with an `afterok` dependency on the previous job.

## Expected outputs

For sample `C001_TN`, outputs include:

- `C001_TN.bam`
- `C001_TN.Sort.bam`
- `C001_TN.Sort.MarkDuplicates.bam`
- `C001_TN.Sort.MarkDuplicates.metrics`
- `C001_TN.Sort.MarkDuplicates.BQSR.table`
- `C001_TN.Sort.MarkDuplicates.BQSR.bam`
- generated scripts in `sh/`
- SLURM logs in `stdeo/`
