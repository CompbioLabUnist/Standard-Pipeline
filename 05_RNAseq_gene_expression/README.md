# RNAseq gene expression

This module builds an RSEM reference and quantifies paired-end RNA-seq reads
with either STAR or Bowtie2 through `rsem-calculate-expression`.

## Tools

### RSEM

- GitHub: https://github.com/deweylab/RSEM
- DOI: https://doi.org/10.1186/1471-2105-12-323

### STAR (recommended)

- GitHub: https://github.com/alexdobin/STAR
- DOI: https://doi.org/10.1093/bioinformatics/bts635

### Bowtie2

- GitHub: https://github.com/BenLangmead/bowtie2
- DOI: https://doi.org/10.1038/nmeth.1923

Executable and reference paths are read from `../config.ini`.

## Setup

Run commands from this directory:

```bash
cd 05_RNAseq_gene_expression
ln -snfv ../pipeline_utils.py .
```

The default config path is `../config.ini`.

## 1. Build the RSEM reference

Execute the example wrapper:

```bash
bash 05_1_RSEM_reference.bash
```

Or run the Python entry point directly:

```bash
python3 -B 05_1_RSEM_reference.py "$PWD/hg38"
```

Use `--dryrun` to create the SLURM script without submitting:

```bash
python3 -B 05_1_RSEM_reference.py --dryrun "$PWD/hg38"
```

The output argument is a reference basename without extension. The wrapper uses
`hg38`, which creates RSEM reference files such as `hg38.grp`.

## 2. Quantify expression with STAR

Edit `05_3_RSEM_star.bash` for your sample paths, then run:

```bash
bash 05_3_RSEM_star.bash
```

Direct command:

```bash
python3 -B 05_3_RSEM_star.py \
    "$(realpath ../00_Data/WTS/C001_TT_RNA_R1.fastq.gz)" \
    "$(realpath ../00_Data/WTS/C001_TT_RNA_R2.fastq.gz)" \
    "$(realpath ./hg38.grp)" \
    "$PWD/C001_TT.STAR"
```

## 3. Quantify expression with Bowtie2

Edit `05_2_RSEM_bowtie2.bash` for your sample paths, then run:

```bash
bash 05_2_RSEM_bowtie2.bash
```

Direct command:

```bash
python3 -B 05_2_RSEM_bowtie2.py \
    "$(realpath ../00_Data/WTS/C001_TT_RNA_R1.fastq.gz)" \
    "$(realpath ../00_Data/WTS/C001_TT_RNA_R2.fastq.gz)" \
    "$(realpath ./hg38.grp)" \
    "$PWD/C001_TT.bowtie2"
```

Arguments for quantification:

- `input`: two paired FASTQ files.
- `reference`: RSEM reference `.grp` file. The script strips the extension and
  passes the basename to RSEM.
- `output`: RSEM output basename.
- `--config`: config INI file. Defaults to `../config.ini`.
- `--dryrun`: create scripts in `sh/` without calling `sbatch`.

## Expected outputs

Reference build:

- `hg38.grp` and related RSEM reference files
- `sh/1-1.Reference_<sample>.sh`
- SLURM logs in `stdeo/`

Expression quantification:

- `<sample>.genes.results`
- `<sample>.isoforms.results`
- sorted genome BAM outputs from RSEM
- generated scripts in `sh/`
- SLURM logs in `stdeo/`
