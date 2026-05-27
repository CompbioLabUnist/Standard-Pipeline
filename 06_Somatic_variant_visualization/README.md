# Somatic variant visualization

This module merges somatic MAF files and draws mutation summary plots.

## Plot types

### Comut plot

- GitHub: https://github.com/vanallenlab/comut
- Paper: https://doi.org/10.1093/bioinformatics/btaa554

### Rainfall plot

- Example: https://bernatgel.github.io/karyoploter_tutorial/Examples/Rainfall/Rainfall.html
- Paper: https://doi.org/10.1186/s12859-017-1679-8

### Lollipop plot

- GitHub: https://github.com/joiningdata/lollipops
- Paper: https://doi.org/10.1371/journal.pone.0294236

## Setup

Run commands from this directory:

```bash
cd 06_Somatic_variant_visualization
bash 06_1_setup_venv.bash
source ./bin/activate
bash 06_2_install_dependency.bash
```

Useful commands:

- Activate: `source ./bin/activate`
- Deactivate: `deactivate`

The lollipop step also calls `/BiO/Share/Tools/lollipops`, so confirm that tool
exists before running `06_6_draw_lollipop.py`.

## 1. Merge MAF files

Execute the example wrapper:

```bash
bash 06_3_merge_maf.bash
```

Or run directly:

```bash
python3 06_3_merge_maf.py \
    $(realpath ../03_Somatic_short_variant_discovery/*.PASS.maf) \
    "$PWD/merged.tsv"
```

The merge step keeps nonsynonymous mutations on chromosomes `chr1` through
`chr22` and `chrX`.

## 2. Draw a comut plot

```bash
python3 06_4_draw_comut.py \
    "$(realpath ./merged.tsv)" \
    "$PWD/comut.pdf"
```

This writes both `comut.pdf` and `comut.png`.

## 3. Draw rainfall plots

Create the output directory first:

```bash
mkdir -p Rainfall
python3 06_5_draw_rainfall.py \
    "$(realpath ./merged.tsv)" \
    "$(realpath ./Rainfall)"
```

This writes one PDF and one PNG per chromosome.

## 4. Draw lollipop plots

Create the output directory first and pass one or more genes with `--gene`:

```bash
mkdir -p Lollipop
python3 06_6_draw_lollipop.py \
    "$(realpath ./merged.tsv)" \
    "$(realpath ./Lollipop)" \
    --gene TP53 GZMB
```

This writes one PNG per requested gene when that gene has protein-change
annotations in the merged MAF.

## Expected outputs

- `merged.tsv`
- `comut.pdf` and `comut.png`
- `Rainfall/<chromosome>.pdf` and `Rainfall/<chromosome>.png`
- `Lollipop/<gene>.png`
