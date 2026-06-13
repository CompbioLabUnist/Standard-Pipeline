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

## Workflow objectives and result interpretation

The objective of this module is to build an RSEM reference and quantify
paired-end RNA-seq reads as gene-level and isoform-level expression estimates.
The main downstream output is:

```text
<sample>.genes.results
```

`07_Pathway_prediction` consumes `../05_RNAseq_gene_expression/*.genes.results`
and merges the TPM and FPKM columns into `expression.tsv`.

### 1. RSEM reference build

`05_1_RSEM_reference.py` runs `rsem-prepare-reference` with the reference FASTA
and `[REFERENCES] ref_gene` GTF from `../config.ini`. The command enables both
Bowtie2 and STAR support in the same RSEM reference.

Output prefix:

```text
hg38
```

Main output:

```text
hg38.grp
```

Main purpose:

- combine the reference genome and transcript annotation into RSEM reference
  files
- prepare Bowtie2 and STAR index support for later expression quantification
- create a reusable reference prefix for all samples processed with the same
  genome and annotation

How to interpret the result:

- `hg38.grp` is the reference handle passed to the quantification scripts.
- The scripts strip the `.grp` extension before passing the reference prefix to
  RSEM.
- Rebuild the reference if the FASTA, GTF, RSEM version, STAR path, or Bowtie2
  path changes.

### 2. Expression quantification

`05_2_RSEM_bowtie2.py` and `05_3_RSEM_star.py` both call
`rsem-calculate-expression` on a paired FASTQ set. STAR is the recommended path
for this README, while Bowtie2 is available as an alternative.

Inputs:

```text
<sample>_R1.fastq.gz
<sample>_R2.fastq.gz
hg38.grp
```

Outputs:

```text
<sample>.genes.results
<sample>.isoforms.results
```

Main purpose:

- align paired RNA-seq reads through RSEM with either STAR or Bowtie2
- estimate gene-level and isoform-level abundance
- calculate posterior mean estimates and confidence intervals with
  `--calc-pme` and `--calc-ci`
- write genome-aligned BAM output and sort it by coordinate for inspection
- estimate the read start position distribution with `--estimate-rspd`

How to interpret the result:

- `<sample>.genes.results` is the primary gene-level expression table. It
  contains identifiers plus abundance columns such as `expected_count`, `TPM`,
  and `FPKM`.
- `expected_count` is RSEM's estimated read support for a gene and can be
  fractional because reads may be probabilistically assigned.
- `TPM` is the preferred within-sample normalized abundance value for comparing
  expression profiles.
- `FPKM` is retained because the downstream pathway plotting scripts currently
  generate both TPM and FPKM views.
- `<sample>.isoforms.results` reports transcript-level estimates and is useful
  when isoform usage matters.
- Genome BAM outputs from RSEM are useful for alignment inspection, but the
  expression tables are the expected inputs for downstream expression analysis
  in this repository.

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

Use `--dryrun` before the FASTQ arguments to create the SLURM script without
submitting it.

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

Use `--dryrun` before the FASTQ arguments to create the SLURM script without
submitting it.

Arguments for quantification:

- `input`: two paired FASTQ files.
- `reference`: RSEM reference `.grp` file. The script strips the extension and
  passes the basename to RSEM.
- `output`: RSEM output basename.
- `--config`: config INI file. Defaults to `../config.ini`.
- `--dryrun`: create scripts in `sh/` without calling `sbatch`.

## Submitted jobs

Each entry point creates one script in `sh/` and submits one SLURM job unless
`--dryrun` is used:

- reference build: `sh/1-1.Reference_<reference>.sh`
- Bowtie2 quantification: `sh/2-1.Bowtie2_<sample>.sh`
- STAR quantification: `sh/3-1.star_<sample>.sh`

These jobs are independent. Build the RSEM reference before running the
quantification jobs that use it.

## Expected outputs

Reference build:

- `hg38.grp`: RSEM reference handle used by quantification commands.
- `hg38.*`: related RSEM reference and aligner-index files created from the
  configured FASTA and GTF.
- `sh/1-1.Reference_hg38.sh`: generated SLURM script for the reference build.
- SLURM logs in `stdeo/`.

Expression quantification:

- `<sample>.genes.results`: gene-level expression estimates; this is the input
  consumed by `07_Pathway_prediction`.
- `<sample>.isoforms.results`: transcript-level expression estimates.
- RSEM statistics and model files using the same output prefix.
- genome-aligned and coordinate-sorted BAM outputs from RSEM.
- generated SLURM scripts in `sh/`.
- SLURM logs in `stdeo/`.
