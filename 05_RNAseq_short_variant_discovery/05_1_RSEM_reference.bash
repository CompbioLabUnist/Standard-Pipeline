#!/bin/bash
set -euo pipefail
#IFS=$'\n\t'

python3 -B 05_1_RSEM_reference.py $(realpath ./Reference)/hg38
