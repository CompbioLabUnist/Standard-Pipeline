# Quality check

This module runs FastQC on raw FASTQ files. The Python entry point creates a
SLURM job script and submits it unless `--dryrun` is used.

## Tool

FastQC: https://www.bioinformatics.babraham.ac.uk/projects/fastqc/

The FastQC executable is read from `[TOOLS] fastqc` in `../config.ini`.

FastQC is a first-pass quality-control tool for high-throughput sequencing
FASTQ files. It does not modify reads. It summarizes whether raw sequencing
data look technically usable and helps identify problems such as low base
quality, adapter contamination, unusual GC content, overrepresented sequences,
or uneven read composition.

Run FastQC before downstream alignment so obvious sequencing or library issues
are visible early. For paired-end data, run FastQC separately for `R1` and
`R2`, because the two read directions can have different quality profiles.

## Meaning of FastQC results

FastQC writes an HTML report and a ZIP archive for each input FASTQ file. The
HTML file is the easiest report to inspect manually. The ZIP file contains the
same report data in text and image form; this pipeline runs FastQC with
`--noextract`, so the ZIP is kept compressed.

FastQC marks each module with pass, warning, or fail icons. Treat these as
screening flags, not absolute decisions. Some warnings are expected for
specific assays or organisms, while some passing modules can still hide
sample-specific issues. Review the plots together with the library type and the
downstream analysis goal.

Common report sections:

- `Basic Statistics`: Shows filename, encoding, read count, read length, GC
  percentage, and whether the reads are marked as filtered. Use this to confirm
  that the expected file and read count were analyzed.
- `Per base sequence quality`: Shows quality-score distribution at each base
  position. Good data usually have high scores across most positions. A quality
  drop near the 3-prime end is common, but severe drops may require trimming or
  closer inspection.
- `Per tile sequence quality`: Detects flow-cell tile-specific quality
  problems. Localized low-quality tiles can indicate sequencing-instrument
  issues rather than sample biology.
- `Per sequence quality scores`: Summarizes average read quality across all
  reads. A strong low-quality peak can indicate a poor sequencing run, failed
  cluster detection, or reads that should be filtered.
- `Per base sequence content`: Shows A, C, G, and T proportions by base
  position. Strong imbalance at the start of reads can be normal for some
  protocols, but persistent imbalance may indicate biased libraries or technical
  artifacts.
- `Per sequence GC content`: Compares observed GC distribution against the
  expected distribution. Extra peaks or shifted distributions can suggest
  contamination, biased enrichment, or mixed sample content.
- `Per base N content`: Shows the percentage of bases called as `N`. High `N`
  content means the sequencer could not confidently call bases at those
  positions.
- `Sequence Length Distribution`: Confirms read lengths. Multiple lengths can
  be expected after trimming, but unexpected length patterns may indicate
  mixed inputs or preprocessing artifacts.
- `Sequence Duplication Levels`: Estimates duplicated reads. High duplication
  can indicate low library complexity, PCR duplication, or targeted sequencing
  where repeated coverage is expected.
- `Overrepresented sequences`: Lists sequences that appear more often than
  expected. These may be adapters, primers, rRNA, contamination, or highly
  enriched biological fragments.
- `Adapter Content`: Detects known adapter sequences across read positions.
  Rising adapter content toward the read end usually means insert sizes are
  shorter than read length and adapter trimming should be considered.
- `Kmer Content`: Highlights short sequence motifs that occur at biased
  positions. This can indicate adapter remnants, primers, or protocol-specific
  sequence bias.

For this pipeline, the most important checks before alignment are usually read
count, per-base quality, adapter content, overrepresented sequences, GC content,
and duplication level.

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
- `<input_basename>_fastqc.html`
- `<input_basename>_fastqc.zip`
