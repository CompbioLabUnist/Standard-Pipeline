# Somatic copy-number variant discovery

This module prepares and runs PureCN for somatic copy-number analysis from BQSR
BAM files.

## Tool

PureCN: https://bioconductor.org/packages/release/bioc/html/PureCN.html

The install wrapper creates a local conda prefix in this directory and installs
PureCN with Bioconductor dependencies.

## Setup

Run commands from this directory:

```bash
cd 09_Somatic_copy_number_variant_discovery
ln -snfv ../pipeline_utils.py .
bash 09_1_install_conda.bash
```

`09_1_install_conda.bash` installs Miniconda under `~/miniconda3` if needed,
creates `./conda`, installs `bioconductor-purecn=2.12.0`, and installs the R
packages used by PureCN.

Tool and reference paths are read from `../config.ini`, especially:

- `[REFERENCES] region_bed`
- `[REFERENCES] fasta`
- `[DEFAULT] threads`

## Input naming convention

The script pairs normal and tumor BAM files by filename:

- Tumor files contain `TT`.
- Normal files contain `TN` or `BU`.
- A normal sample is paired with the tumor sample made by replacing `TN` or
  `BU` with `TT`.

Example:

- normal: `C001_TN.Sort.MarkDuplicates.BQSR.bam`
- tumor: `C001_TT.Sort.MarkDuplicates.BQSR.bam`

Pass both normal and tumor BAM files to the command.

## Execute with the example wrapper

Edit `09_2_prepare_pureCN.bash` if the BAM path pattern is different, then run:

```bash
bash 09_2_prepare_pureCN.bash
```

## Execute directly

Generate scripts without submitting:

```bash
python3 -B 09_2_prepare_pureCN.py --dryrun \
    $(realpath ../02_Data_pre-processing_for_variant_discovery/*.BQSR.bam) \
    "$(realpath .)"
```

Submit the PureCN workflow:

```bash
python3 -B 09_2_prepare_pureCN.py \
    $(realpath ../02_Data_pre-processing_for_variant_discovery/*.BQSR.bam) \
    "$(realpath .)"
```

Arguments:

- `input`: one or more BQSR BAM files. Include both normal and tumor files.
- `output`: output directory.
- `--config`: config INI file. Defaults to `../config.ini`.
- `--dryrun`: create scripts in `sh/` without calling `sbatch`.

## Submitted job order

1. `1.get_interval`
2. `2.calculate_coverage` for each input BAM
3. `3.normal_database`
4. `4.PureCN` for each normal/tumor pair

Coverage jobs depend on interval creation. The normal database depends on all
coverage jobs. Each PureCN tumor run depends on the normal database.

## Expected outputs

- `baits_hg38_intervals.txt`
- `<sample>.Sort.MarkDuplicates.BQSR_coverage_loess.txt.gz`
- `normal_coverages.list`
- `normalDB_hg38.rds`
- PureCN result files in the output directory
- generated scripts in `sh/`
- SLURM logs in `stdeo/`
