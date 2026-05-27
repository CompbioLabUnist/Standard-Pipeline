# Quality check

This module runs FastQC on raw FASTQ files. The Python entry point creates a
SLURM job script and submits it unless `--dryrun` is used.

## Tool

FastQC: https://www.bioinformatics.babraham.ac.uk/projects/fastqc/

The FastQC executable is read from `[TOOLS] fastqc` in `../config.ini`.

## Setup

Run commands from this directory:

```bash
cd 01_Quality_check
ln -snfv ../pipeline_utils.py .
```

The default config path is `../config.ini`. Pass `--config` if you use another
configuration file.

## Execute with the example wrapper

Edit `01_1_FastQC.bash` if the FASTQ path is different, then run:

```bash
bash 01_1_FastQC.bash
```

## Execute directly

Generate the SLURM script without submitting:

```bash
python3 -B 01_1_FastQC.py --dryrun \
    --output "$(realpath .)" \
    "$(realpath ../00_Data/WES/merge/C001_TN_DNA_R1.fastq.gz)"
```

Submit the FastQC job:

```bash
python3 -B 01_1_FastQC.py \
    --output "$(realpath .)" \
    "$(realpath ../00_Data/WES/merge/C001_TN_DNA_R1.fastq.gz)"
```

Arguments:

- `input`: FASTQ file. Run one sample/read file per command.
- `--output`: output directory. Defaults to the current directory.
- `--config`: config INI file. Defaults to `../config.ini`.
- `--dryrun`: create `sh/FastQC_<sample>.sh` without calling `sbatch`.

## Expected outputs

- `sh/FastQC_<sample>.sh`
- `stdeo/FastQC_<sample>-<job_id>.txt`
- FastQC HTML and ZIP files in the selected output directory
