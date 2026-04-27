#!/bin/bash
set -euo pipefail
IFS=$'\n\t'
bash /BiO/Share/Tools/Miniconda3-latest-Linux-x86_64.sh -b -f
~/miniconda3/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
~/miniconda3/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
~/miniconda3/bin/conda create --channel conda-forge --channel bioconda --prefix "$(realpath .)/conda" --yes
~/miniconda3/bin/conda install --channel conda-forge --channel bioconda bioconductor-purecn=2.12.0 --prefix "$(realpath .)/conda" --yes
PATH="$(realpath ./conda/bin):$PATH" "$(realpath .)/conda/bin/Rscript" --vanilla -e 'install.packages(c("BiocManager", "MASS"), repos="https://cloud.r-project.org")' -e 'BiocManager::install(c("PureCN", "optparse", "R.utils", "TxDb.Hsapiens.UCSC.hg38.knownGene", "org.Hs.eg.db", "BiocParallel"))'
